# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): explicit `<fk>_id` filters scope correctly."""
from dcim.models import Manufacturer
from django.test import TestCase
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset, InventoryItemType
from utilities.testing import create_test_device
from netbox_zfs.choices import VdevClassChoices, VdevRedundancyChoices
from netbox_zfs.filtersets import (
    ZFSDatasetFilterSet, ZFSPoolFilterSet, ZFSVdevFilterSet, ZFSVdevMemberFilterSet,
    ZFSVolumeFilterSet,
)
from netbox_zfs.models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


def _inv_type():
    mfr = Manufacturer.objects.create(name="ACME", slug="acme")
    return InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")


class ZFSPoolFilterSetTest(TestCase):
    queryset = ZFSPool.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.host = create_test_device("h1")
        ZFSPool.objects.create(name="tank", host=cls.host, comment="primary")
        ZFSPool.objects.create(name="backup")

    def test_host_id(self):
        self.assertEqual(ZFSPoolFilterSet({"host_id": [self.host.pk]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(ZFSPoolFilterSet({"q": "tank"}, self.queryset).qs.count(), 1)
        self.assertEqual(ZFSPoolFilterSet({"q": "primary"}, self.queryset).qs.count(), 1)


class ZFSVdevFilterSetTest(TestCase):
    queryset = ZFSVdev.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")
        cls.pool2 = ZFSPool.objects.create(name="backup")
        ZFSVdev.objects.create(pool=cls.pool, vdev_class=VdevClassChoices.DATA, index=0, redundancy=VdevRedundancyChoices.RAIDZ2)
        ZFSVdev.objects.create(pool=cls.pool, vdev_class=VdevClassChoices.LOG, index=0, redundancy=VdevRedundancyChoices.MIRROR)
        ZFSVdev.objects.create(pool=cls.pool2, vdev_class=VdevClassChoices.DATA, index=0)

    def test_pool_id(self):
        self.assertEqual(ZFSVdevFilterSet({"pool_id": [self.pool.pk]}, self.queryset).qs.count(), 2)

    def test_vdev_class(self):
        self.assertEqual(ZFSVdevFilterSet({"vdev_class": [VdevClassChoices.LOG]}, self.queryset).qs.count(), 1)

    def test_redundancy(self):
        self.assertEqual(ZFSVdevFilterSet({"redundancy": [VdevRedundancyChoices.MIRROR]}, self.queryset).qs.count(), 1)


class ZFSVdevMemberFilterSetTest(TestCase):
    queryset = ZFSVdevMember.objects.all()

    @classmethod
    def setUpTestData(cls):
        iit = _inv_type()
        asset = Asset.objects.create(inventoryitem_type=iit, serial="MF", status="stored")
        disk = Disk.objects.create(asset=asset, total_sectors=10_000_000)
        cls.parts = [
            Partition.objects.create(disk=disk, number=i + 1, start_sector=2048 + i * 100_000,
                                     end_sector=2048 + i * 100_000 + 50_000, usage="zfs_member")
            for i in range(3)
        ]
        pool = ZFSPool.objects.create(name="tank")
        cls.vdev = ZFSVdev.objects.create(pool=pool, vdev_class="data", index=0)
        cls.vdev2 = ZFSVdev.objects.create(pool=pool, vdev_class="spare", index=0)
        ZFSVdevMember.objects.create(vdev=cls.vdev, partition=cls.parts[0])
        ZFSVdevMember.objects.create(vdev=cls.vdev, partition=cls.parts[1])
        ZFSVdevMember.objects.create(vdev=cls.vdev2, partition=cls.parts[2])

    def test_vdev_id(self):
        self.assertEqual(ZFSVdevMemberFilterSet({"vdev_id": [self.vdev.pk]}, self.queryset).qs.count(), 2)

    def test_partition_id(self):
        self.assertEqual(
            ZFSVdevMemberFilterSet({"partition_id": [self.parts[2].pk]}, self.queryset).qs.count(), 1
        )


class ZFSDatasetFilterSetTest(TestCase):
    queryset = ZFSDataset.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")
        pool2 = ZFSPool.objects.create(name="backup")
        ZFSDataset.objects.create(pool=cls.pool, name="tank/db", mountpoint="/db")
        ZFSDataset.objects.create(pool=cls.pool, name="tank/vm")
        ZFSDataset.objects.create(pool=pool2, name="backup/snap")

    def test_pool_id(self):
        self.assertEqual(ZFSDatasetFilterSet({"pool_id": [self.pool.pk]}, self.queryset).qs.count(), 2)

    def test_search(self):
        self.assertEqual(ZFSDatasetFilterSet({"q": "tank/db"}, self.queryset).qs.count(), 1)
        self.assertEqual(ZFSDatasetFilterSet({"q": "/db"}, self.queryset).qs.count(), 1)


class ZFSVolumeFilterSetTest(TestCase):
    queryset = ZFSVolume.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")
        pool2 = ZFSPool.objects.create(name="backup")
        ZFSVolume.objects.create(pool=cls.pool, name="tank/vm/disk0", volsize="10G")
        ZFSVolume.objects.create(pool=pool2, name="backup/vm/disk0", volsize="10G")

    def test_pool_id(self):
        self.assertEqual(ZFSVolumeFilterSet({"pool_id": [self.pool.pk]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(ZFSVolumeFilterSet({"q": "tank/vm"}, self.queryset).qs.count(), 1)
