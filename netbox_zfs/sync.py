# SPDX-License-Identifier: AGPL-3.0-or-later
"""Copy the latest observed ZFS health from OpenObserve into NetBox.

The hypervisors' collector (tofu-providers ``modules/services/hv_alloy``) writes these Prometheus
series from ``zpool status -j`` / ``zpool list -j``, which Alloy ships to OpenObserve:

- ``zfs_pool_metric{pool_guid, pool, field}``: a pool value; ``field`` is a ZFSPoolHealth field name,
  except ``scrub_end_seconds`` (Unix time); ``health`` / ``scrub_state`` are indexes into
  ``ZFSHealthChoices.CODES`` / ``ZFSScanStateChoices.CODES``;
- ``zfs_member_metric{pool_guid, serial, partition, field}``: a leaf vdev's value, keyed by its drive's
  serial and partition number; ``state`` is an index into ``ZFSHealthChoices.CODES``;
- ``zfs_captured_at_seconds{pool_guid}``: when the pool was read.

Pools match ``ZFSPool.pool_guid``; members match the ``ZFSVdevMember`` in that pool whose partition
is that number on the netbox-fs Disk of the Asset with that serial. Anything that does not match
exactly one object is reported, never guessed. A pool whose capture time has not moved is left alone.
"""
import base64
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from .choices import ZFSHealthChoices, ZFSScanStateChoices
from .models import (
    MemberHealthMetrics, PoolHealthMetrics, ZFSPool, ZFSPoolHealth, ZFSVdevMember, ZFSVdevMemberHealth,
)

QUERIES = ("zfs_pool_metric", "zfs_member_metric", "zfs_captured_at_seconds")
ENV_PREFIX = "NETBOX_ZFS_OPENOBSERVE_"
_CODED = {"health": ZFSHealthChoices.CODES, "scrub_state": ZFSScanStateChoices.CODES, "state": ZFSHealthChoices.CODES}
POOL_FIELDS = set(PoolHealthMetrics.METRIC_FIELDS) - {"scrub_end"} | {"scrub_end_seconds"}
MEMBER_FIELDS = set(MemberHealthMetrics.METRIC_FIELDS)


@dataclass(frozen=True)
class OpenObserveConfig:
    url: str
    organization: str
    username: str
    password: str

    @classmethod
    def from_env(cls, environ=os.environ):
        """The OpenObserve connection from the environment, or None when the sync is not configured."""
        values = {k: environ.get(ENV_PREFIX + k.upper(), "") for k in ("url", "username", "password")}
        if not all(values.values()):
            return None
        return cls(organization=environ.get(ENV_PREFIX + "ORGANIZATION", "default"), **values)


def fetch(config, timeout=60):
    """The current value of each ZFS series, as the Prometheus instant-query results."""
    token = base64.b64encode(f"{config.username}:{config.password}".encode()).decode()
    results = {}
    for query in QUERIES:
        url = f"{config.url.rstrip('/')}/api/{config.organization}/prometheus/api/v1/query?" + urlencode(
            {"query": query}
        )
        with urlopen(Request(url, headers={"Authorization": f"Basic {token}"}), timeout=timeout) as resp:
            body = json.load(resp)
        if body.get("status") != "success":
            raise RuntimeError(f"OpenObserve query {query!r} failed: {body.get('error', body)}")
        results[query] = body["data"]["result"]
    return results


def _value(name, raw):
    number = Decimal(raw)
    if name in _CODED:
        codes = _CODED[name]
        return codes[int(number)] if 0 <= number < len(codes) else ""
    if name == "scrub_end_seconds":
        return datetime.fromtimestamp(int(number), tz=timezone.utc) if number > 0 else None
    return int(number)


@dataclass
class Pool:
    guid: str
    values: dict = field(default_factory=dict)
    members: dict = field(default_factory=dict)  # (serial, partition number) -> values
    captured_at: datetime | None = None


def parse(results):
    """Pools by GUID from `fetch`'s results; a pool without a capture time is dropped."""
    pools = {}

    def pool(sample):
        guid = sample["metric"].get("pool_guid", "").strip()
        return pools.setdefault(guid, Pool(guid)) if guid else None

    for sample in results.get("zfs_pool_metric", []):
        name = sample["metric"].get("field")
        if (p := pool(sample)) is not None and name in POOL_FIELDS:
            value = _value(name, sample["value"][1])
            p.values["scrub_end" if name == "scrub_end_seconds" else name] = value
    for sample in results.get("zfs_member_metric", []):
        labels = sample["metric"]
        serial = " ".join(labels.get("serial", "").split())
        name = labels.get("field")
        if (p := pool(sample)) is not None and serial and labels.get("partition", "").isdigit() and name in MEMBER_FIELDS:
            p.members.setdefault((serial, int(labels["partition"])), {})[name] = _value(name, sample["value"][1])
    for sample in results.get("zfs_captured_at_seconds", []):
        if (p := pool(sample)) is not None:
            p.captured_at = datetime.fromtimestamp(int(Decimal(sample["value"][1])), tz=timezone.utc)
    return {g: p for g, p in pools.items() if p.captured_at is not None}


@dataclass
class SyncResult:
    pools_written: list = field(default_factory=list)
    pools_unchanged: list = field(default_factory=list)
    pools_unmatched: list = field(default_factory=list)
    members_written: int = 0
    members_unmatched: list = field(default_factory=list)  # (pool guid, serial, partition)
    members_ambiguous: list = field(default_factory=list)


def _write(model, owner_field, owner, values, captured_at):
    health = model.objects.filter(**{owner_field: owner}).first() or model(**{owner_field: owner})
    for name, value in values.items():
        setattr(health, name, value)
    health.captured_at = captured_at
    health.full_clean()
    health.save()


def apply(pools):
    """Write each pool's and member's reading to its health snapshot (which records the history)."""
    result = SyncResult()
    for guid, p in sorted(pools.items()):
        pool = ZFSPool.objects.filter(pool_guid=guid).first()
        if pool is None:
            result.pools_unmatched.append(guid)
            continue
        current = ZFSPoolHealth.objects.filter(pool=pool).first()
        if current is not None and current.captured_at == p.captured_at:
            result.pools_unchanged.append(pool.name)
            continue
        _write(ZFSPoolHealth, "pool", pool, p.values, p.captured_at)
        result.pools_written.append(pool.name)
        for (serial, number), values in sorted(p.members.items()):
            members = list(ZFSVdevMember.objects.filter(
                vdev__pool=pool, partition__number=number, partition__disk__asset__serial=serial,
            )[:2])
            if len(members) != 1:
                (result.members_ambiguous if members else result.members_unmatched).append((guid, serial, number))
                continue
            _write(ZFSVdevMemberHealth, "member", members[0], values, p.captured_at)
            result.members_written += 1
    return result
