# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


class ZFSPoolTable(NetBoxTable):
    name = tables.Column(linkify=True)
    host = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfspool_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSPool
        fields = (
            "pk", "id", "name", "pool_guid", "host", "ashift", "autotrim", "autoexpand",
            "comment", "tags", "created", "last_updated",
        )
        default_columns = ("name", "host", "pool_guid", "ashift")


class ZFSVdevTable(NetBoxTable):
    pool = tables.Column(linkify=True)
    vdev_class = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvdev_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVdev
        fields = ("pk", "id", "pool", "vdev_class", "redundancy", "index", "tags", "created", "last_updated")
        default_columns = ("pool", "vdev_class", "redundancy", "index")


class ZFSVdevMemberTable(NetBoxTable):
    vdev = tables.Column(linkify=True)
    partition = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvdevmember_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVdevMember
        fields = ("pk", "id", "vdev", "partition", "device_link_type", "whole_disk", "tags", "created", "last_updated")
        default_columns = ("vdev", "partition", "device_link_type", "whole_disk")


class ZFSDatasetTable(NetBoxTable):
    name = tables.Column(linkify=True)
    pool = tables.Column(linkify=True)
    parent = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsdataset_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSDataset
        fields = (
            "pk", "id", "pool", "parent", "name", "recordsize", "compression", "checksum",
            "copies", "atime", "relatime", "dedup", "sync", "logbias", "redundant_metadata",
            "dnodesize", "primarycache", "secondarycache", "volmode", "exec", "setuid", "devices",
            "readonly", "canmount", "mountpoint", "snapdir", "overlay", "nbmand", "vscan", "zoned",
            "xattr", "acltype", "aclinherit", "aclmode", "casesensitivity", "normalization",
            "utf8only", "version", "quota", "refquota", "reservation", "refreservation",
            "snapshot_limit", "filesystem_limit", "special_small_blocks", "sharenfs", "sharesmb",
            "encryption", "encryptionroot", "keyformat", "keylocation", "pbkdf2iters", "mlslabel",
            "context", "fscontext", "defcontext", "rootcontext", "tags", "created", "last_updated",
        )
        default_columns = ("name", "pool", "compression", "mountpoint", "quota", "sharenfs")


class ZFSVolumeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    pool = tables.Column(linkify=True)
    parent = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvolume_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVolume
        fields = (
            "pk", "id", "pool", "parent", "name", "volsize", "volblocksize", "volmode", "snapdev",
            "compression", "checksum", "copies", "dedup", "sync", "logbias", "redundant_metadata",
            "primarycache", "secondarycache", "readonly", "reservation", "refreservation",
            "encryption", "encryptionroot", "keyformat", "keylocation", "pbkdf2iters", "mlslabel",
            "context", "fscontext", "defcontext", "rootcontext", "tags", "created", "last_updated",
        )
        default_columns = ("name", "pool", "volsize", "volblocksize", "compression")
