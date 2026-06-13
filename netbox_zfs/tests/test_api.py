# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks). Members exercise the
cross-plugin FK to netbox_fs.Partition."""
from dcim.models import Manufacturer
from netbox_fs.models import Disk, Partition
from netbox_inventory.models import Asset, InventoryItemType
from utilities.testing import APIViewTestCases
from netbox_zfs.models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    pass


class ZFSPoolAPITest(_CRUD):
    model = ZFSPool
    brief_fields = ["display", "id", "name", "pool_guid", "url"]
    bulk_update_data = {"comment": "bulk"}

    @classmethod
    def setUpTestData(cls):
        ZFSPool.objects.bulk_create([ZFSPool(name="p1"), ZFSPool(name="p2"), ZFSPool(name="p3")])
        cls.create_data = [
            {"name": "new1"},
            {"name": "new2", "ashift": 12},
            {"name": "new3", "autotrim": "on"},
        ]


class ZFSVdevAPITest(_CRUD):
    model = ZFSVdev
    brief_fields = ["display", "id", "pool", "redundancy", "url", "vdev_class"]
    bulk_update_data = {"redundancy": "mirror"}

    @classmethod
    def setUpTestData(cls):
        pool = ZFSPool.objects.create(name="tank")
        ZFSVdev.objects.bulk_create([
            ZFSVdev(pool=pool, vdev_class="data", index=0, redundancy="raidz2"),
            ZFSVdev(pool=pool, vdev_class="data", index=1, redundancy="raidz2"),
            ZFSVdev(pool=pool, vdev_class="data", index=2, redundancy="raidz2"),
        ])
        cls.create_data = [
            {"pool": pool.pk, "vdev_class": "log", "redundancy": "mirror", "index": 0},
            {"pool": pool.pk, "vdev_class": "cache", "redundancy": "stripe", "index": 0},
            {"pool": pool.pk, "vdev_class": "spare", "redundancy": "stripe", "index": 0},
        ]


class ZFSVdevMemberAPITest(_CRUD):
    model = ZFSVdevMember
    brief_fields = ["display", "id", "partition", "url", "vdev"]
    bulk_update_data = {"whole_disk": True}

    @classmethod
    def setUpTestData(cls):
        mfr = Manufacturer.objects.create(name="ACME", slug="acme")
        iit = InventoryItemType.objects.create(manufacturer=mfr, model="DM1", slug="dm1")
        asset = Asset.objects.create(inventoryitem_type=iit, serial="VM", status="stored")
        disk = Disk.objects.create(asset=asset, total_sectors=10_000_000)
        parts = [
            Partition.objects.create(
                disk=disk, number=i + 1, start_sector=2048 + i * 100_000,
                end_sector=2048 + i * 100_000 + 50_000, usage="zfs_member",
            )
            for i in range(6)
        ]
        pool = ZFSPool.objects.create(name="tank")
        vdev = ZFSVdev.objects.create(pool=pool, vdev_class="data", index=0, redundancy="raidz2")
        ZFSVdevMember.objects.bulk_create([
            ZFSVdevMember(vdev=vdev, partition=parts[0]),
            ZFSVdevMember(vdev=vdev, partition=parts[1]),
            ZFSVdevMember(vdev=vdev, partition=parts[2]),
        ])
        cls.create_data = [
            {"vdev": vdev.pk, "partition": parts[3].pk},
            {"vdev": vdev.pk, "partition": parts[4].pk, "whole_disk": True},
            {"vdev": vdev.pk, "partition": parts[5].pk, "device_link_type": "by-id"},
        ]


class ZFSDatasetAPITest(_CRUD):
    model = ZFSDataset
    brief_fields = ["display", "id", "name", "url"]
    bulk_update_data = {"compression": "lz4"}

    @classmethod
    def setUpTestData(cls):
        pool = ZFSPool.objects.create(name="tank")
        ZFSDataset.objects.bulk_create([
            ZFSDataset(pool=pool, name="tank/a"),
            ZFSDataset(pool=pool, name="tank/b"),
            ZFSDataset(pool=pool, name="tank/c"),
        ])
        cls.create_data = [
            {"pool": pool.pk, "name": "tank/d"},
            {"pool": pool.pk, "name": "tank/e", "compression": "zstd", "recordsize": "16K"},
            {"pool": pool.pk, "name": "tank/f", "mountpoint": "/tank/f"},
        ]


class ZFSVolumeAPITest(_CRUD):
    model = ZFSVolume
    brief_fields = ["display", "id", "name", "url", "volsize"]
    bulk_update_data = {"compression": "zstd"}

    @classmethod
    def setUpTestData(cls):
        pool = ZFSPool.objects.create(name="tank")
        ZFSVolume.objects.bulk_create([
            ZFSVolume(pool=pool, name="tank/v1", volsize="10G"),
            ZFSVolume(pool=pool, name="tank/v2", volsize="20G"),
            ZFSVolume(pool=pool, name="tank/v3", volsize="30G"),
        ])
        cls.create_data = [
            {"pool": pool.pk, "name": "tank/v4", "volsize": "5G"},
            {"pool": pool.pk, "name": "tank/v5", "volsize": "6G", "volblocksize": "16K"},
            {"pool": pool.pk, "name": "tank/v6", "volsize": "7G", "compression": "lz4"},
        ]
