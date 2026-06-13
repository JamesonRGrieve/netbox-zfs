<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-zfs

A NetBox 4.6 plugin: a **native source of truth for ZFS pools, vdevs, datasets, and zvols**.

It sits on top of **`netbox-fs`** (disks/partitions/filesystems), which in turn sits on
**`netbox-inventory`** (the physical `Asset`). The dependency stack:

```
netbox-inventory   Asset      (physical drive)
   ▲
netbox-fs          Disk → Partition → Filesystem
   ▲
netbox-zfs         ZFSPool → ZFSVdev → ZFSVdevMember(→ Partition)
                   ZFSPool → ZFSDataset (hierarchical) / ZFSVolume (zvol)
```

## Why partitions, not drives

ZFS vdev members are **partitions**, and not every partition on a drive is ZFS. Modeling members
as `netbox_fs.Partition` references means a drive that holds **both** a live vdev-member partition
**and** a hot-spare partition is represented exactly: the two partitions join two different vdevs
(e.g. a `raidz`-class data vdev and a `spare`-class vdev) on the same pool.

## Model

- **ZFSPool** — `name` (display) + `pool_guid` (the stable identity that survives rename/export/
  import) + `host` (`dcim.Device`, nullable: an exported pool has no host) + properties (`ashift`,
  `autotrim`, `autoexpand`, `comment`). `last_seen_state` holds an optional reconciled-health
  snapshot — NetBox stores the *designed* topology; live ONLINE/DEGRADED state is reconciler output.
- **ZFSVdev** — belongs to a pool; `vdev_class` (data/log/cache/spare/special/dedup) is kept
  **separate** from `redundancy` (stripe/mirror/raidz1-3/draid1-3) so a *mirrored SLOG*
  (`class=log, redundancy=mirror`) and dRAID (`draid_config`) are expressible.
- **ZFSVdevMember** — a vdev's member: a 1:1 reference to a `netbox_fs.Partition` (PROTECTed so a
  live member can't be deleted out from under the pool), plus `device_link_type`
  (by-id/by-partuuid/by-path/…) and a `whole_disk` flag.
- **ZFSDataset** — a filesystem dataset; hierarchical (`parent`) with the usual properties
  (recordsize, compression, atime, dedup, quota/refquota/reservation, mountpoint, canmount,
  encryption).
- **ZFSVolume** — a zvol; `volsize` is **required** (it defines the block device), `volblocksize` is
  set at creation. Zvols are leaves (no children); an optional `parent` dataset places them in the
  namespace.

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Migrating from the legacy custom fields

The prod-lab previously stored ZFS membership in `netbox_inventory.Asset` custom fields
(`zpool`, `vdev`, `vdev_role`). A management command backfills first-class objects from those:

```bash
python manage.py backfill_zfs_from_inventory --dry-run   # report only, writes nothing
python manage.py backfill_zfs_from_inventory             # create Disk/Partition/Pool/Vdev/Member
python manage.py backfill_zfs_from_inventory --deprecate-fields   # then delete the 3 CustomFields
```

The old fields are whole-drive granular, so the backfill synthesizes **one full-disk partition per
asset** and **cannot** reconstruct a live+spare split — split such drives manually afterward. SMART
and hardware custom fields are untouched.

## Install

`netbox-fs` (and `netbox-inventory`) must be installed first, and listed **before** `netbox_zfs`
in `PLUGINS`.

```bash
uv pip install --python /opt/netbox/venv/bin/python -e .   # or: pip install netbox-zfs
# PLUGINS = [..., "netbox_inventory", "netbox_fs", "netbox_zfs"]
python manage.py migrate netbox_zfs
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks); they build inventory/fs fixtures.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_zfs --keepdb -v2
python /opt/netbox/app/netbox/manage.py makemigrations netbox_zfs --check --dry-run
```

## License

AGPL-3.0-or-later.
