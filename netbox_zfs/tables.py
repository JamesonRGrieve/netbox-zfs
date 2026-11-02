# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    ZFSDataset, ZFSPool, ZFSPoolHealth, ZFSPoolHealthReading, ZFSVdev, ZFSVdevMember,
    ZFSVdevMemberHealth, ZFSVdevMemberHealthReading, ZFSVolume,
)


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


class ZFSPoolHealthTable(NetBoxTable):
    pool = tables.Column(linkify=True)
    captured_at = tables.DateTimeColumn(linkify=True)
    health = columns.ChoiceFieldColumn()
    scrub_state = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfspoolhealth_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSPoolHealth
        fields = ("pk", "id", "pool", "captured_at", "health", "size_bytes", "allocated_bytes", "free_bytes", "fragmentation_percent", "capacity_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors", "tags", "created", "last_updated")
        default_columns = ("pool", "captured_at", "health", "capacity_percent", "fragmentation_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors")


class ZFSPoolHealthReadingTable(NetBoxTable):
    pool = tables.Column(linkify=True)
    captured_at = tables.DateTimeColumn(linkify=True)
    health = columns.ChoiceFieldColumn()
    scrub_state = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfspoolhealthreading_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSPoolHealthReading
        fields = ("pk", "id", "pool", "captured_at", "health", "size_bytes", "allocated_bytes", "free_bytes", "fragmentation_percent", "capacity_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors", "tags", "created", "last_updated")
        default_columns = ("pool", "captured_at", "health", "capacity_percent", "fragmentation_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors")


class ZFSVdevMemberHealthTable(NetBoxTable):
    member = tables.Column(linkify=True)
    captured_at = tables.DateTimeColumn(linkify=True)
    state = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvdevmemberhealth_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVdevMemberHealth
        fields = ("pk", "id", "member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors", "slow_ios", "tags", "created", "last_updated")
        default_columns = ("member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors")


class ZFSVdevMemberHealthReadingTable(NetBoxTable):
    member = tables.Column(linkify=True)
    captured_at = tables.DateTimeColumn(linkify=True)
    state = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvdevmemberhealthreading_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVdevMemberHealthReading
        fields = ("pk", "id", "member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors", "slow_ios", "tags", "created", "last_updated")
        default_columns = ("member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors")
