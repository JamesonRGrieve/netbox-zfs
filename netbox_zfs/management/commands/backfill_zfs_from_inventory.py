# SPDX-License-Identifier: AGPL-3.0-or-later
"""Backfill first-class ZFS objects from the legacy netbox_inventory.Asset custom fields
(zpool / vdev / vdev_role). For each asset carrying a zpool, synthesize: a netbox-fs Disk + a single
full-disk Partition (usage=zfs_member), and a netbox-zfs Pool / Vdev / VdevMember.

FIDELITY LIMIT: the legacy fields are whole-DRIVE granular (one vdev_role per asset), so this can
only ever produce ONE partition / membership per drive. It CANNOT reconstruct a drive that holds
both a live member partition and a hot-spare partition — split those manually afterward.

Idempotent (get_or_create throughout). ``--dry-run`` writes nothing; ``--deprecate-fields`` then
deletes the three legacy CustomField definitions. SMART and hardware-identity custom fields are
untouched (SMART is migrated separately by netbox-smart's backfill command)."""
from django.core.management.base import BaseCommand
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset
from netbox_zfs.choices import VdevClassChoices, VdevRedundancyChoices
from netbox_zfs.models import ZFSPool, ZFSVdev, ZFSVdevMember

LEGACY_FIELDS = ["zpool", "vdev", "vdev_role"]
_REDUNDANCY_PREFIXES = [
    ("draid3", VdevRedundancyChoices.DRAID3),
    ("draid2", VdevRedundancyChoices.DRAID2),
    ("draid1", VdevRedundancyChoices.DRAID1),
    ("draid", VdevRedundancyChoices.DRAID1),
    ("raidz3", VdevRedundancyChoices.RAIDZ3),
    ("raidz2", VdevRedundancyChoices.RAIDZ2),
    ("raidz1", VdevRedundancyChoices.RAIDZ1),
    ("raidz", VdevRedundancyChoices.RAIDZ1),
    ("mirror", VdevRedundancyChoices.MIRROR),
]


def _vdev_class(vdev_role):
    role = (vdev_role or "").strip().lower()
    valid = {c[0] for c in VdevClassChoices.CHOICES}
    return role if role in valid else VdevClassChoices.DATA


def _redundancy(vdev_name):
    name = (vdev_name or "").strip().lower()
    for prefix, value in _REDUNDANCY_PREFIXES:
        if name.startswith(prefix):
            return value
    return VdevRedundancyChoices.STRIPE


def _vdev_index(vdev_name):
    name = (vdev_name or "").strip()
    if "-" in name and name.rsplit("-", 1)[-1].isdigit():
        return int(name.rsplit("-", 1)[-1])
    return 0


def _total_sectors(custom_field_data):
    gb = custom_field_data.get("drive_capacity_gb")
    if gb:
        return max(1, int(gb) * 1_000_000_000 // 512)
    return 1  # placeholder geometry — operator corrects later


class Command(BaseCommand):
    help = "Backfill ZFS pools/vdevs/members from legacy Asset zpool/vdev/vdev_role custom fields."

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="Report only; write nothing.")
        parser.add_argument(
            "--deprecate-fields",
            action="store_true",
            help="After backfill, delete the legacy zpool/vdev/vdev_role CustomField definitions.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        pools = vdevs = members = skipped = warned = 0
        for asset in Asset.objects.all():
            cf = asset.custom_field_data or {}
            zpool = (cf.get("zpool") or "").strip()
            if not zpool:
                skipped += 1
                continue
            vdev_name = (cf.get("vdev") or "").strip()
            vdev_role = cf.get("vdev_role")
            host = getattr(asset, "installed_device", None)
            if dry_run:
                self.stdout.write(
                    f"[dry-run] {asset}: pool={zpool} host={host} vdev={vdev_name or '(none)'} "
                    f"class={_vdev_class(vdev_role)} redundancy={_redundancy(vdev_name)}"
                )
                members += 1
                continue

            disk, _ = Disk.objects.get_or_create(
                asset=asset, defaults={"total_sectors": _total_sectors(cf)}
            )
            partition = disk.partitions.filter(usage="zfs_member").first()
            if partition is None:
                if disk.partitions.exists():
                    self.stderr.write(
                        f"WARN {asset}: disk already partitioned; skipping member synthesis."
                    )
                    warned += 1
                    continue
                partition = Partition.objects.create(
                    disk=disk, number=1, start_sector=0,
                    end_sector=max(0, disk.total_sectors - 1), usage="zfs_member",
                )

            pool, pool_created = ZFSPool.objects.get_or_create(name=zpool, host=host)
            pools += 1 if pool_created else 0
            vdev, vdev_created = ZFSVdev.objects.get_or_create(
                pool=pool,
                vdev_class=_vdev_class(vdev_role),
                index=_vdev_index(vdev_name),
                defaults={"redundancy": _redundancy(vdev_name)},
            )
            vdevs += 1 if vdev_created else 0
            _, member_created = ZFSVdevMember.objects.get_or_create(
                partition=partition, defaults={"vdev": vdev}
            )
            members += 1 if member_created else 0

        self.stdout.write(
            self.style.SUCCESS(
                f"ZFS backfill: {pools} pools, {vdevs} vdevs, {members} members created; "
                f"{skipped} assets skipped (no zpool); {warned} warned."
            )
        )
        if not dry_run:
            self.stdout.write(
                "Note: legacy fields are whole-drive granular — drives with both a live and a "
                "spare partition need manual splitting."
            )
        if options["deprecate_fields"]:
            self._deprecate(dry_run)

    def _deprecate(self, dry_run):
        from extras.models import CustomField

        qs = CustomField.objects.filter(name__in=LEGACY_FIELDS)
        count = qs.count()
        if dry_run:
            self.stdout.write(f"[dry-run] would delete {count} legacy ZFS CustomField definitions.")
            return
        qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {count} legacy ZFS CustomField definitions."))
