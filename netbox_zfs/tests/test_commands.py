# SPDX-License-Identifier: AGPL-3.0-or-later
"""Backfill management-command tests against a real DB (no mocks): cross-plugin synthesis of
Disk/Partition (netbox-fs) + Pool/Vdev/Member (netbox-zfs) from legacy Asset custom fields."""
from io import StringIO
from dcim.models import Manufacturer
from django.core.management import call_command
from django.test import TestCase
from extras.models import CustomField
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset, InventoryItemType
from netbox_zfs.models import ZFSPool, ZFSVdev, ZFSVdevMember


class BackfillZFSCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        mfr = Manufacturer.objects.create(name="ACME", slug="acme")
        iit = InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")
        cls.a1 = Asset.objects.create(
            inventoryitem_type=iit, serial="Z-1", status="stored",
            custom_field_data={"zpool": "tank", "vdev": "raidz2-0", "vdev_role": "data", "drive_capacity_gb": 1000},
        )
        cls.a2 = Asset.objects.create(
            inventoryitem_type=iit, serial="Z-2", status="stored",
            custom_field_data={"zpool": "tank", "vdev": "raidz2-0", "vdev_role": "data", "drive_capacity_gb": 1000},
        )
        cls.a_spare = Asset.objects.create(
            inventoryitem_type=iit, serial="Z-S", status="stored",
            custom_field_data={"zpool": "tank", "vdev": "", "vdev_role": "spare", "drive_capacity_gb": 1000},
        )
        cls.a_none = Asset.objects.create(
            inventoryitem_type=iit, serial="Z-N", status="stored", custom_field_data={"drive_model": "x"}
        )

    def _run(self, *args):
        out = StringIO()
        call_command("backfill_zfs_from_inventory", *args, stdout=out, stderr=StringIO())
        return out.getvalue()

    def test_dry_run_writes_nothing(self):
        self._run("--dry-run")
        self.assertEqual(ZFSPool.objects.count(), 0)
        self.assertEqual(Disk.objects.count(), 0)

    def test_backfill_creates_topology(self):
        self._run()
        self.assertEqual(ZFSPool.objects.filter(name="tank").count(), 1)
        self.assertEqual(ZFSVdev.objects.count(), 2)  # one data vdev (raidz2-0) + one spare vdev
        self.assertEqual(Disk.objects.count(), 3)
        self.assertEqual(Partition.objects.filter(usage="zfs_member").count(), 3)
        self.assertEqual(ZFSVdevMember.objects.count(), 3)
        self.assertEqual(ZFSVdev.objects.get(vdev_class="data").redundancy, "raidz2")
        self.assertEqual(Disk.objects.get(asset=self.a1).total_sectors, 1000 * 1_000_000_000 // 512)

    def test_skips_assets_without_zpool(self):
        self._run()
        self.assertFalse(Disk.objects.filter(asset=self.a_none).exists())

    def test_idempotent(self):
        self._run()
        self._run()
        self.assertEqual(ZFSPool.objects.count(), 1)
        self.assertEqual(ZFSVdev.objects.count(), 2)
        self.assertEqual(ZFSVdevMember.objects.count(), 3)
        self.assertEqual(Partition.objects.count(), 3)

    def test_deprecate_fields(self):
        CustomField.objects.create(name="zpool", type="text")
        CustomField.objects.create(name="vdev", type="text")
        CustomField.objects.create(name="vdev_role", type="text")
        self._run("--deprecate-fields")
        self.assertEqual(CustomField.objects.filter(name__in=["zpool", "vdev", "vdev_role"]).count(), 0)
