# netbox-zfs — Agent Operating Guide

Same engineering + test discipline as `../netbox-pf` and `../netbox-fs`.

`netbox-zfs` is an **AGPL-3.0** NetBox 4.6 plugin: the **native source of truth for ZFS pools,
vdevs, datasets, and zvols**. Vdev members reference **`netbox_fs.Partition`** (not whole drives),
so it **depends on `netbox-fs`** (which depends on `netbox-inventory`). Install/migrate order is
`netbox_inventory` → `netbox_fs` → `netbox_zfs`.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter.
- Any source change gets **comprehensive tests WITHOUT MOCKS** under `netbox_zfs/tests/`.
- Write concise code. **SPDX header on every source file**.

### DO NOT, EVER:
- Make assumptions or answer with "is likely" / "probably".
- Skip a failing test instead of fixing the root cause.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Real test
  DB only. The backfill command is tested against real Asset/Disk/Partition fixtures.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date`.
- Imports are package-relative inside `netbox_zfs` (`from .models import ZFSPool`); the cross-plugin
  partition reference is the one deliberate exception (`from netbox_fs.models import Partition`).
- Models inherit `netbox.models.NetBoxModel`.
- Migrations are **hand-authored**; the initial migration `dependencies` on
  `("netbox_fs", "0001_initial")` enforces cross-plugin ordering. Verify with
  `makemigrations netbox_zfs --check --dry-run`.

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_zfs`, `base_url='zfs'` |
| `choices.py` | vdev class & redundancy, device-link type, ZFS property enums |
| `models.py` | `ZFSPool`, `ZFSVdev`, `ZFSVdevMember`, `ZFSDataset`, `ZFSVolume` |
| `migrations/` | hand-authored; cross-plugin FK to `netbox_fs.Partition` |
| `api/`, `filtersets.py`, `tables.py`, `forms.py`, `views.py`, `urls.py`, `navigation.py`, `templates/` | REST API + UI |
| `management/commands/backfill_zfs_from_inventory.py` | idempotent backfill from legacy Asset custom fields |

### Model notes
- `ZFSPool.pool_guid` is `unique`, nullable (blank → NULL via `save()`); it is the stable identity.
  `host` is `SET_NULL`/nullable (pools export/import between hosts).
- `ZFSVdev` splits `vdev_class` from `redundancy` (mirrored SLOG, dRAID). `(pool, class, index)` unique.
- `ZFSVdevMember.partition` is a `ForeignKey` to `netbox_fs.Partition`, `on_delete=PROTECT`, uniqued
  per `(vdev, partition)`. A partition may back members in several vdevs (a hot spare shared across
  pools is the same partition in each pool's spare vdev); it may not appear twice in one vdev.
- `ZFSDataset` is hierarchical (`parent`, CASCADE). `ZFSVolume.volsize` is required; zvols are leaves.

---

## Testing (NO MOCKS — real DB, NetBox test framework)
- `python /opt/netbox/app/netbox/manage.py test netbox_zfs --keepdb -v2`.
- Coverage bar: every model, serializer, filterset, view, plus the cross-plugin FK round-trip, the
  dual-partition (live + spare) drive case, mirrored SLOG, required-`volsize` zvol, and the backfill
  command (idempotency, `--dry-run`, single-partition limitation).

---

## Licensing
- **AGPL-3.0-or-later**. SPDX header in every file.
