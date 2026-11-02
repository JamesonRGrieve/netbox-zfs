# SPDX-License-Identifier: AGPL-3.0-or-later
"""Observed ZFS health: models, history, the OpenObserve sync, API and views, against a real DB (no
mocks). The end-to-end case talks to a real OpenObserve: set NETBOX_ZFS_TEST_OPENOBSERVE_URL,
_USERNAME and _PASSWORD to a throwaway instance (the suite ingests its own series there)."""
import json
import os
import time
import unittest
from base64 import b64encode
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from core.choices import JobStatusChoices
from core.models import Job
from dcim.models import Manufacturer
from django.test import TestCase
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset, InventoryItemType
from utilities.testing import ViewTestCases
from netbox_zfs import sync
from netbox_zfs.jobs import ZFSHealthSyncJob
from netbox_zfs.tests.test_api import _CRUD
from netbox_zfs.models import (
    ZFSPool, ZFSPoolHealth, ZFSPoolHealthReading, ZFSVdev, ZFSVdevMember, ZFSVdevMemberHealth,
    ZFSVdevMemberHealthReading,
)

T1 = datetime(2026, 11, 1, 20, 30, tzinfo=timezone.utc)
T2 = datetime(2026, 11, 2, 20, 30, tzinfo=timezone.utc)
GUID = "17957810016130979044"


def topology(serials=("SER-1", "SER-2"), guid=GUID, name="pool_3tb"):
    """A pool with one raidz vdev whose members are partition 1 of one drive per serial."""
    mfr = Manufacturer.objects.get_or_create(name="ACME", slug="acme")[0]
    iit = InventoryItemType.objects.get_or_create(manufacturer=mfr, model="DM1", slug="dm1")[0]
    pool = ZFSPool.objects.create(name=name, pool_guid=guid)
    vdev = ZFSVdev.objects.create(pool=pool, vdev_class="data", index=0, redundancy="raidz3")
    members = []
    for serial in serials:
        disk = Disk.objects.create(
            asset=Asset.objects.create(inventoryitem_type=iit, serial=serial, status="used"), total_sectors=10_000_000
        )
        part = Partition.objects.create(disk=disk, number=1, start_sector=2048, end_sector=9_000_000, usage="zfs_member")
        members.append(ZFSVdevMember.objects.create(vdev=vdev, partition=part))
    return pool, members


def sample(name, value, **labels):
    return {"metric": {"__name__": name, "host": "backup", **labels}, "value": [time.time(), str(value)]}


def results(captured_at, guid=GUID, pool=None, members=None):
    pool = pool or {}
    members = members or {}
    return {
        "zfs_pool_metric": [sample("zfs_pool_metric", v, pool_guid=guid, pool="p", field=f) for f, v in pool.items()],
        "zfs_member_metric": [
            sample("zfs_member_metric", v, pool_guid=guid, serial=s, partition=str(n), field=f)
            for (s, n), fields in members.items() for f, v in fields.items()
        ],
        "zfs_captured_at_seconds": [sample("zfs_captured_at_seconds", int(captured_at.timestamp()), pool_guid=guid)],
    }


class HistoryTest(TestCase):
    def test_pool_and_member_saves_record_history(self):
        pool, (member, _) = topology()
        h = ZFSPoolHealth.objects.create(pool=pool, health="ONLINE", capacity_percent=93, captured_at=T1)
        h.capacity_percent, h.captured_at = 94, T2
        h.save()
        self.assertEqual(list(h.readings.values_list("capacity_percent", flat=True)), [94, 93])
        m = ZFSVdevMemberHealth.objects.create(member=member, state="ONLINE", checksum_errors=0, captured_at=T1)
        m.checksum_errors = 3
        m.save()  # same capture: overwritten, not added
        self.assertEqual(list(m.readings.values_list("checksum_errors", flat=True)), [3])
        self.assertEqual(str(h), "Health: pool_3tb")
        self.assertEqual(h.get_health_color(), "green")
        self.assertIn("/plugins/zfs/pool-health/", h.get_absolute_url())
        self.assertIn("/plugins/zfs/member-health-readings/", m.readings.get().get_absolute_url())

    def test_no_capture_time_records_nothing_and_cascade(self):
        pool, (member, _) = topology()
        ZFSPoolHealth.objects.create(pool=pool, health="ONLINE")
        self.assertFalse(ZFSPoolHealthReading.objects.exists())
        ZFSVdevMemberHealth.objects.create(member=member, state="ONLINE", captured_at=T1)
        pool.delete()
        self.assertFalse(ZFSVdevMemberHealthReading.objects.exists())


class ParseTest(TestCase):
    def test_codes_times_and_members(self):
        pools = sync.parse(results(
            T1, pool={"health": 1, "capacity_percent": 93, "scrub_state": 2, "scrub_end_seconds": int(T1.timestamp()), "data_errors": 0},
            members={("SER-1", 1): {"state": 0, "checksum_errors": 7}, ("SER  2 ", 1): {"state": 7}},
        ))
        p = pools[GUID]
        self.assertEqual(p.values, {"health": "DEGRADED", "capacity_percent": 93, "scrub_state": "FINISHED", "scrub_end": T1, "data_errors": 0})
        self.assertEqual(p.members, {("SER-1", 1): {"state": "ONLINE", "checksum_errors": 7}, ("SER 2", 1): {"state": "AVAIL"}})

    def test_unknown_code_never_scrubbed_and_undated(self):
        r = results(T1, pool={"health": -1, "scrub_end_seconds": 0, "bogus": 5})
        r["zfs_pool_metric"].append(sample("zfs_pool_metric", 1, pool_guid="UNDATED", field="health"))
        pools = sync.parse(r)
        self.assertEqual(set(pools), {GUID})
        self.assertEqual(pools[GUID].values, {"health": "", "scrub_end": None})


class ApplyTest(TestCase):
    def test_writes_pool_and_members_and_reports_gaps(self):
        pool, (m1, m2) = topology()
        r = sync.apply(sync.parse(merged(
            results(T1, pool={"health": 0, "capacity_percent": 93}, members={
                ("SER-1", 1): {"state": 0, "read_errors": 0, "checksum_errors": 2},
                ("SER-2", 1): {"state": 0},
                ("SER-2", 2): {"state": 7},          # a spare partition NetBox doesn't model
                ("NO-ASSET", 1): {"state": 0},
            }),
            results(T1, guid="999"),                # a pool NetBox doesn't have
        )))
        self.assertEqual((r.pools_written, r.pools_unmatched, r.members_written), (["pool_3tb"], ["999"], 2))
        self.assertEqual(sorted(r.members_unmatched), [(GUID, "NO-ASSET", 1), (GUID, "SER-2", 2)])
        self.assertEqual(ZFSPoolHealth.objects.get(pool=pool).capacity_percent, 93)
        self.assertEqual(ZFSVdevMemberHealth.objects.get(member=m1).checksum_errors, 2)
        r = sync.apply(sync.parse(results(T1, pool={"capacity_percent": 99})))
        self.assertEqual(r.pools_unchanged, ["pool_3tb"])
        r = sync.apply(sync.parse(results(T2, pool={"capacity_percent": 94}, members={("SER-1", 1): {"checksum_errors": 5}})))
        self.assertEqual(list(ZFSPoolHealth.objects.get(pool=pool).readings.values_list("capacity_percent", flat=True)), [94, 93])
        self.assertEqual(list(ZFSVdevMemberHealth.objects.get(member=m1).readings.values_list("checksum_errors", flat=True)), [5, 2])

    def test_ambiguous_member(self):
        pool, (m1, _) = topology()
        spare = ZFSVdev.objects.create(pool=pool, vdev_class="spare", index=0, redundancy="stripe")
        ZFSVdevMember.objects.create(vdev=spare, partition=m1.partition)
        r = sync.apply(sync.parse(results(T1, members={("SER-1", 1): {"state": 0}})))
        self.assertEqual(r.members_ambiguous, [(GUID, "SER-1", 1)])


def merged(*parts):
    out = {q: [] for q in sync.QUERIES}
    for part in parts:
        for q, samples in part.items():
            out[q] += samples
    return out


class ConfigTest(TestCase):
    def test_env(self):
        self.assertIsNone(sync.OpenObserveConfig.from_env({}))
        env = {f"NETBOX_ZFS_OPENOBSERVE_{k}": v for k, v in (("URL", "http://o2"), ("USERNAME", "u"), ("PASSWORD", "p"))}
        self.assertEqual(sync.OpenObserveConfig.from_env(env), sync.OpenObserveConfig("http://o2", "default", "u", "p"))


class PoolHealthReadingAPITest(*_CRUD):
    model = ZFSPoolHealthReading
    brief_fields = ["captured_at", "display", "health", "id", "pool", "url"]
    bulk_update_data = {"health": "DEGRADED"}

    @classmethod
    def setUpTestData(cls):
        pool, _ = topology()
        ZFSPoolHealthReading.objects.bulk_create([
            ZFSPoolHealthReading(pool=pool, captured_at=datetime(2026, m, 1, tzinfo=timezone.utc), health="ONLINE") for m in (1, 2, 3)
        ])
        cls.create_data = [
            {"pool": pool.pk, "captured_at": T1, "health": "ONLINE", "capacity_percent": 93},
            {"pool": pool.pk, "captured_at": T2, "health": "DEGRADED", "data_errors": 1},
            {"pool": pool.pk, "captured_at": datetime(2026, 12, 1, tzinfo=timezone.utc), "scrub_state": "FINISHED", "scrub_end": T1},
        ]


class MemberHealthAPITest(*_CRUD):
    model = ZFSVdevMemberHealth
    brief_fields = ["captured_at", "display", "id", "member", "state", "url"]
    bulk_update_data = {"state": "FAULTED"}

    @classmethod
    def setUpTestData(cls):
        _, members = topology(serials=[f"S{i}" for i in range(6)])
        ZFSVdevMemberHealth.objects.bulk_create([ZFSVdevMemberHealth(member=m, state="ONLINE") for m in members[:3]])
        cls.create_data = [
            {"member": members[3].pk, "state": "ONLINE", "read_errors": 0},
            {"member": members[4].pk, "state": "DEGRADED", "checksum_errors": 12},
            {"member": members[5].pk, "state": "AVAIL", "captured_at": T1},
        ]


class PoolHealthViewTest(ViewTestCases.GetObjectViewTestCase, ViewTestCases.ListObjectsViewTestCase):
    model = ZFSPoolHealth

    def _get_base_url(self):
        return "plugins:netbox_zfs:zfspoolhealth_{}"

    @classmethod
    def setUpTestData(cls):
        for i, guid in enumerate(("1", "2", "3")):
            pool, _ = topology(serials=[f"V{i}"], guid=guid, name=f"p{i}")
            ZFSPoolHealth.objects.create(pool=pool, health="ONLINE", capacity_percent=90, captured_at=T1)
        cls.health = ZFSPoolHealth.objects.get(pool__pool_guid="1")
        cls.health.capacity_percent, cls.health.captured_at = 91, T2
        cls.health.save()

    def test_history_panel_and_pool_page(self):
        self.add_permissions("netbox_zfs.view_zfspoolhealth", "netbox_zfs.view_zfspool")
        r = self.client.get(self.health.get_absolute_url())
        self.assertHttpStatus(r, 200)
        self.assertContains(r, "All 2 readings")
        self.assertEqual([row.record.capacity_percent for row in r.context["readings_table"].rows], [91, 90])
        r = self.client.get(self.health.pool.get_absolute_url())
        self.assertHttpStatus(r, 200)
        self.assertContains(r, "Data errors")


class MemberHealthReadingViewTest(ViewTestCases.GetObjectViewTestCase, ViewTestCases.ListObjectsViewTestCase):
    model = ZFSVdevMemberHealthReading

    def _get_base_url(self):
        return "plugins:netbox_zfs:zfsvdevmemberhealthreading_{}"

    @classmethod
    def setUpTestData(cls):
        _, (m, _) = topology()
        for day in (1, 2, 3):
            ZFSVdevMemberHealthReading.objects.create(member=m, captured_at=datetime(2026, 11, day, tzinfo=timezone.utc), state="ONLINE")


ENV = {k: os.environ.get(f"NETBOX_ZFS_TEST_OPENOBSERVE_{k}", "") for k in ("URL", "USERNAME", "PASSWORD")}


@unittest.skipUnless(all(ENV.values()), "needs a throwaway OpenObserve (NETBOX_ZFS_TEST_OPENOBSERVE_*)")
class OpenObserveEndToEndTest(TestCase):
    """Ingest ZFS series into a real OpenObserve, then run the job: the health lands in NetBox."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        now_ms = int(time.time() * 1000)
        base = {"__type__": "gauge", "host": "backup", "pool_guid": "424242", "_timestamp": now_ms}
        rows = [
            {**base, "__name__": "zfs_pool_metric", "pool": "e2e", "field": "health", "value": 1},
            {**base, "__name__": "zfs_pool_metric", "pool": "e2e", "field": "data_errors", "value": 4},
            {**base, "__name__": "zfs_member_metric", "serial": "E2E-1", "partition": "1", "field": "checksum_errors", "value": 9},
            {**base, "__name__": "zfs_member_metric", "serial": "E2E-1", "partition": "1", "field": "state", "value": 2},
            {**base, "__name__": "zfs_captured_at_seconds", "pool": "e2e", "value": int(T1.timestamp())},
        ]
        token = b64encode(f"{ENV['USERNAME']}:{ENV['PASSWORD']}".encode()).decode()
        req = Request(
            f"{ENV['URL'].rstrip('/')}/api/default/ingest/metrics/_json", data=json.dumps(rows).encode(),
            headers={"Authorization": f"Basic {token}", "Content-Type": "application/json"}, method="POST",
        )
        with urlopen(req, timeout=30) as resp:
            assert resp.status == 200, resp.status
        time.sleep(5)  # OpenObserve makes ingested rows queryable after its in-memory flush

    def test_job_syncs_from_openobserve(self):
        pool, (member,) = topology(serials=["E2E-1"], guid="424242", name="e2e")
        env = {f"NETBOX_ZFS_OPENOBSERVE_{k}": v for k, v in ENV.items()}
        old = {k: os.environ.get(k) for k in env}
        os.environ.update(env)
        try:
            job = ZFSHealthSyncJob.enqueue(immediate=True)
        finally:
            for k, v in old.items():
                os.environ.pop(k) if v is None else os.environ.__setitem__(k, v)
        job = Job.objects.get(pk=job.pk)
        self.assertEqual(job.status, JobStatusChoices.STATUS_COMPLETED, job.log_entries)
        h = ZFSPoolHealth.objects.get(pool=pool)
        self.assertEqual((h.health, h.data_errors, h.captured_at), ("DEGRADED", 4, T1))
        m = ZFSVdevMemberHealth.objects.get(member=member)
        self.assertEqual((m.state, m.checksum_errors), ("FAULTED", 9))
