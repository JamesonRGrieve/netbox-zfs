# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): pool GUID NULL semantics, vdev uniqueness, the
cross-plugin partition OneToOne + PROTECT, the dual-partition (live + spare) drive, mirrored SLOG,
dataset hierarchy cascade, and required-volsize zvols."""
from dcim.models import Manufacturer
from django.db import transaction
from django.db.models import ProtectedError
from django.db.utils import IntegrityError
from django.test import TestCase
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset, InventoryItemType
from netbox_zfs.choices import VdevClassChoices, VdevRedundancyChoices
from netbox_zfs.models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


def _inv_type():
    mfr = Manufacturer.objects.create(name="ACME", slug="acme")
    return InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")


def _disk(iit, serial, sectors=1_000_000):
    asset = Asset.objects.create(inventoryitem_type=iit, serial=serial, status="stored")
    return Disk.objects.create(asset=asset, total_sectors=sectors)


class ZFSPoolModelTest(TestCase):
    def test_create_str_url(self):
        p = ZFSPool.objects.create(name="tank")
        self.assertEqual(str(p), "tank")
        self.assertIn("/plugins/zfs/pools/", p.get_absolute_url())

    def test_blank_guid_becomes_null_and_does_not_collide(self):
        a = ZFSPool.objects.create(name="a", pool_guid="")
        b = ZFSPool.objects.create(name="b", pool_guid="")
        a.refresh_from_db()
        b.refresh_from_db()
        self.assertIsNone(a.pool_guid)
        self.assertIsNone(b.pool_guid)

    def test_guid_unique_when_set(self):
        ZFSPool.objects.create(name="a", pool_guid="GUID-1")
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSPool.objects.create(name="b", pool_guid="GUID-1")


class ZFSVdevModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")

    def test_create_str_url_color(self):
        v = ZFSVdev.objects.create(
            pool=self.pool, vdev_class=VdevClassChoices.DATA, redundancy=VdevRedundancyChoices.RAIDZ2
        )
        self.assertIn("/plugins/zfs/vdevs/", v.get_absolute_url())
        self.assertEqual(v.get_vdev_class_color(), "blue")

    def test_unique_pool_class_index(self):
        ZFSVdev.objects.create(pool=self.pool, vdev_class=VdevClassChoices.DATA, index=0)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSVdev.objects.create(pool=self.pool, vdev_class=VdevClassChoices.DATA, index=0)

    def test_mirrored_slog(self):
        """A SLOG can itself be a mirror — expressible because class and redundancy are separate."""
        v = ZFSVdev.objects.create(
            pool=self.pool, vdev_class=VdevClassChoices.LOG, redundancy=VdevRedundancyChoices.MIRROR
        )
        self.assertEqual(v.vdev_class, "log")
        self.assertEqual(v.redundancy, "mirror")


class ZFSVdevMemberModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.iit = _inv_type()
        cls.pool = ZFSPool.objects.create(name="tank")
        cls.vdev = ZFSVdev.objects.create(pool=cls.pool, vdev_class=VdevClassChoices.DATA, index=0)

    def _part(self, disk, number, start, end):
        return Partition.objects.create(
            disk=disk, number=number, start_sector=start, end_sector=end, usage="zfs_member"
        )

    def test_member_links_partition(self):
        part = self._part(_disk(self.iit, "M-1"), 1, 2048, 4095)
        m = ZFSVdevMember.objects.create(vdev=self.vdev, partition=part)
        self.assertIn("/plugins/zfs/vdev-members/", m.get_absolute_url())
        self.assertEqual(m.partition, part)

    def test_partition_one_to_one(self):
        part = self._part(_disk(self.iit, "M-2"), 1, 2048, 4095)
        ZFSVdevMember.objects.create(vdev=self.vdev, partition=part)
        other = ZFSVdev.objects.create(pool=self.pool, vdev_class=VdevClassChoices.DATA, index=1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSVdevMember.objects.create(vdev=other, partition=part)

    def test_partition_protect(self):
        part = self._part(_disk(self.iit, "M-3"), 1, 2048, 4095)
        ZFSVdevMember.objects.create(vdev=self.vdev, partition=part)
        with self.assertRaises(ProtectedError), transaction.atomic():
            part.delete()

    def test_dual_partition_drive(self):
        """One physical drive: a live member partition in a data vdev AND a hot-spare partition in
        the pool's spare vdev."""
        disk = _disk(self.iit, "M-DUAL")
        live = self._part(disk, 1, 2048, 500_000)
        spare = self._part(disk, 2, 500_001, 999_999)
        spare_vdev = ZFSVdev.objects.create(
            pool=self.pool, vdev_class=VdevClassChoices.SPARE, index=0
        )
        m_live = ZFSVdevMember.objects.create(vdev=self.vdev, partition=live)
        m_spare = ZFSVdevMember.objects.create(vdev=spare_vdev, partition=spare)
        self.assertEqual(m_live.partition.disk, m_spare.partition.disk)
        self.assertEqual(m_live.vdev.vdev_class, "data")
        self.assertEqual(m_spare.vdev.vdev_class, "spare")


class ZFSDatasetModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")

    def test_create_str_url(self):
        d = ZFSDataset.objects.create(pool=self.pool, name="tank/db")
        self.assertEqual(str(d), "tank/db")
        self.assertIn("/plugins/zfs/datasets/", d.get_absolute_url())

    def test_unique_pool_name(self):
        ZFSDataset.objects.create(pool=self.pool, name="tank/db")
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSDataset.objects.create(pool=self.pool, name="tank/db")

    def test_parent_cascade(self):
        parent = ZFSDataset.objects.create(pool=self.pool, name="tank/db")
        child = ZFSDataset.objects.create(pool=self.pool, name="tank/db/pg", parent=parent)
        child_pk = child.pk
        parent.delete()
        self.assertFalse(ZFSDataset.objects.filter(pk=child_pk).exists())


class ZFSVolumeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")

    def test_create_with_volsize(self):
        v = ZFSVolume.objects.create(pool=self.pool, name="tank/vm/disk0", volsize="10G", volblocksize="16K")
        self.assertEqual(str(v), "tank/vm/disk0")
        self.assertIn("/plugins/zfs/volumes/", v.get_absolute_url())
        self.assertEqual(v.volsize, "10G")

    def test_unique_pool_name(self):
        ZFSVolume.objects.create(pool=self.pool, name="tank/vm/disk0", volsize="10G")
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSVolume.objects.create(pool=self.pool, name="tank/vm/disk0", volsize="20G")
