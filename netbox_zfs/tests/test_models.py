# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): pool GUID NULL semantics, vdev uniqueness, the
cross-plugin partition FK + PROTECT, shared-spare (one partition across vdevs) + per-vdev
uniqueness, the dual-partition (live + spare) drive, mirrored SLOG, dataset hierarchy cascade,
and required-volsize zvols."""
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

    def test_shared_spare_partition_across_vdevs(self):
        """A hot-spare partition shared across pools: the same partition backs members in several
        spare vdevs. Allowed (FK, not OneToOne)."""
        part = self._part(_disk(self.iit, "M-2"), 1, 2048, 4095)
        pool_b = ZFSPool.objects.create(name="tank-b")
        spare_a = ZFSVdev.objects.create(pool=self.pool, vdev_class=VdevClassChoices.SPARE, index=0)
        spare_b = ZFSVdev.objects.create(pool=pool_b, vdev_class=VdevClassChoices.SPARE, index=0)
        m_a = ZFSVdevMember.objects.create(vdev=spare_a, partition=part)
        m_b = ZFSVdevMember.objects.create(vdev=spare_b, partition=part)
        self.assertEqual(m_a.partition, m_b.partition)
        self.assertEqual(part.zfs_members.count(), 2)

    def test_partition_unique_within_vdev(self):
        part = self._part(_disk(self.iit, "M-2b"), 1, 2048, 4095)
        ZFSVdevMember.objects.create(vdev=self.vdev, partition=part)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ZFSVdevMember.objects.create(vdev=self.vdev, partition=part)

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

    def test_full_property_surface_round_trip(self):
        """Every promoted settable property persists as its own column."""
        d = ZFSDataset.objects.create(
            pool=self.pool, name="tank/full", recordsize="1M", compression="zstd",
            checksum="blake3", copies=2, atime="off", relatime="on", exec="off", setuid="off",
            devices="off", readonly="on", nbmand="off", vscan="off", overlay="on", zoned="off",
            xattr="sa", acltype="posix", aclinherit="passthrough", aclmode="passthrough",
            sync="disabled", logbias="throughput", snapdir="visible", primarycache="metadata",
            secondarycache="none", redundant_metadata="most", dnodesize="auto", volmode="dev",
            casesensitivity="insensitive", normalization="formD", utf8only="on", version="5",
            sharenfs="rw=192.168.5.130/31", sharesmb="off", quota="10G", refquota="8G",
            reservation="1G", refreservation="512M", snapshot_limit="100", filesystem_limit="50",
            special_small_blocks="32K", mlslabel="none", context="system_u:object_r:tmp_t",
            fscontext="x", defcontext="y", rootcontext="z", pbkdf2iters=350000,
        )
        d.refresh_from_db()
        self.assertEqual(d.checksum, "blake3")
        self.assertEqual(d.copies, 2)
        self.assertEqual(d.xattr, "sa")
        self.assertEqual(d.sharenfs, "rw=192.168.5.130/31")
        self.assertEqual(d.special_small_blocks, "32K")
        self.assertEqual(d.pbkdf2iters, 350000)

    def test_blank_means_inherited_or_default(self):
        """An unset property is stored blank/NULL, not a guessed value."""
        d = ZFSDataset.objects.create(pool=self.pool, name="tank/bare")
        self.assertEqual(d.compression, "")
        self.assertIsNone(d.copies)


class ZFSDatasetInheritanceTest(TestCase):
    """`effective()` resolves the runtime value from the dataset hierarchy."""

    @classmethod
    def setUpTestData(cls):
        cls.pool = ZFSPool.objects.create(name="tank")
        cls.root = ZFSDataset.objects.create(
            pool=cls.pool, name="tank", compression="zstd", atime="off", quota="100G"
        )
        cls.mid = ZFSDataset.objects.create(pool=cls.pool, name="tank/db", parent=cls.root)
        cls.leaf = ZFSDataset.objects.create(
            pool=cls.pool, name="tank/db/pg", parent=cls.mid, compression="lz4"
        )

    def test_local_value_wins(self):
        self.assertEqual(self.leaf.effective("compression"), "lz4")

    def test_inherited_from_nearest_ancestor(self):
        # mid sets nothing; both mid and leaf inherit atime=off from root.
        self.assertEqual(self.mid.effective("atime"), "off")
        self.assertEqual(self.leaf.effective("atime"), "off")

    def test_unset_chain_returns_none_for_default(self):
        self.assertIsNone(self.leaf.effective("checksum"))

    def test_non_inheritable_is_local_only(self):
        # quota does not inherit: set on root, but a child must not borrow it.
        self.assertEqual(self.root.effective("quota"), "100G")
        self.assertIsNone(self.mid.effective("quota"))


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

    def test_full_property_surface_round_trip(self):
        v = ZFSVolume.objects.create(
            pool=self.pool, name="tank/vm/disk1", volsize="20G", volblocksize="16K",
            volmode="dev", snapdev="visible", compression="zstd", checksum="sha256", copies=3,
            dedup="off", readonly="on", sync="always", logbias="latency", primarycache="all",
            secondarycache="metadata", redundant_metadata="some", reservation="1G",
            refreservation="20G", encryption="aes-256-gcm", keyformat="passphrase",
            keylocation="prompt", pbkdf2iters=500000, mlslabel="none", context="c",
            fscontext="f", defcontext="d", rootcontext="r",
        )
        v.refresh_from_db()
        self.assertEqual(v.volmode, "dev")
        self.assertEqual(v.snapdev, "visible")
        self.assertEqual(v.checksum, "sha256")
        self.assertEqual(v.copies, 3)
        self.assertEqual(v.refreservation, "20G")
        self.assertEqual(v.pbkdf2iters, 500000)
