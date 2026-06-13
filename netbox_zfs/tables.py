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
            "pk", "id", "pool", "parent", "name", "recordsize", "compression", "atime", "dedup",
            "quota", "mountpoint", "canmount", "encryption", "tags", "created", "last_updated",
        )
        default_columns = ("name", "pool", "compression", "mountpoint", "quota")


class ZFSVolumeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    pool = tables.Column(linkify=True)
    parent = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_zfs:zfsvolume_list")

    class Meta(NetBoxTable.Meta):
        model = ZFSVolume
        fields = (
            "pk", "id", "pool", "parent", "name", "volsize", "volblocksize", "compression",
            "dedup", "encryption", "tags", "created", "last_updated",
        )
        default_columns = ("name", "pool", "volsize", "volblocksize", "compression")
