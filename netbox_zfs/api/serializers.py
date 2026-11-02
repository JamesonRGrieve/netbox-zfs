# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from netbox_fs.api.serializers import PartitionSerializer
from rest_framework import serializers
from ..models import (
    ZFSDataset, ZFSPool, ZFSPoolHealth, ZFSPoolHealthReading, ZFSVdev, ZFSVdevMember,
    ZFSVdevMemberHealth, ZFSVdevMemberHealthReading, ZFSVolume,
)


class ZFSPoolSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfspool-detail")
    host = DeviceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ZFSPool
        fields = [
            "id", "url", "display", "name", "pool_guid", "host", "ashift", "autotrim",
            "autoexpand", "comment", "last_seen_state",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "pool_guid"]


class ZFSVdevSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsvdev-detail")
    pool = ZFSPoolSerializer(nested=True)

    class Meta:
        model = ZFSVdev
        fields = [
            "id", "url", "display", "pool", "vdev_class", "redundancy", "index", "draid_config",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "pool", "vdev_class", "redundancy"]


class ZFSVdevMemberSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsvdevmember-detail")
    vdev = ZFSVdevSerializer(nested=True)
    partition = PartitionSerializer(nested=True)

    class Meta:
        model = ZFSVdevMember
        fields = [
            "id", "url", "display", "vdev", "partition", "device_link_type", "whole_disk",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "vdev", "partition"]


class ZFSDatasetSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsdataset-detail")
    pool = ZFSPoolSerializer(nested=True)
    # `parent` is left as the default PK field to avoid recursive self-nesting.

    class Meta:
        model = ZFSDataset
        fields = [
            "id", "url", "display", "pool", "parent", "name", "recordsize", "compression",
            "atime", "relatime", "dedup", "quota", "refquota", "reservation", "refreservation",
            "mountpoint", "canmount", "exec", "setuid", "devices", "readonly", "nbmand", "vscan",
            "overlay", "zoned", "checksum", "xattr", "acltype", "aclinherit", "aclmode", "sync",
            "logbias", "snapdir", "primarycache", "secondarycache", "redundant_metadata",
            "dnodesize", "volmode", "copies", "casesensitivity", "normalization", "utf8only",
            "version", "sharenfs", "sharesmb", "snapshot_limit", "filesystem_limit",
            "special_small_blocks", "encryption", "encryptionroot", "keyformat", "keylocation",
            "pbkdf2iters", "mlslabel", "context", "fscontext", "defcontext", "rootcontext",
            "advanced", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name"]


class ZFSVolumeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsvolume-detail")
    pool = ZFSPoolSerializer(nested=True)
    parent = ZFSDatasetSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = ZFSVolume
        fields = [
            "id", "url", "display", "pool", "parent", "name", "volsize", "volblocksize",
            "volmode", "snapdev", "compression", "dedup", "checksum", "copies", "readonly",
            "sync", "logbias", "primarycache", "secondarycache", "redundant_metadata",
            "reservation", "refreservation", "encryption", "encryptionroot", "keyformat",
            "keylocation", "pbkdf2iters", "mlslabel", "context", "fscontext", "defcontext",
            "rootcontext", "advanced", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "volsize"]


class ZFSPoolHealthSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfspoolhealth-detail")
    pool = ZFSPoolSerializer(nested=True)

    class Meta:
        model = ZFSPoolHealth
        fields = [
            "id", "url", "display", "pool", "captured_at", "health", "size_bytes", "allocated_bytes", "free_bytes", "fragmentation_percent", "capacity_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "pool", "captured_at", "health"]


class ZFSPoolHealthReadingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfspoolhealthreading-detail")
    pool = ZFSPoolSerializer(nested=True)

    class Meta:
        model = ZFSPoolHealthReading
        fields = [
            "id", "url", "display", "pool", "captured_at", "health", "size_bytes", "allocated_bytes", "free_bytes", "fragmentation_percent", "capacity_percent", "data_errors", "scrub_state", "scrub_end", "scrub_errors",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "pool", "captured_at", "health"]


class ZFSVdevMemberHealthSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsvdevmemberhealth-detail")
    member = ZFSVdevMemberSerializer(nested=True)

    class Meta:
        model = ZFSVdevMemberHealth
        fields = [
            "id", "url", "display", "member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors", "slow_ios",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "member", "captured_at", "state"]


class ZFSVdevMemberHealthReadingSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_zfs-api:zfsvdevmemberhealthreading-detail")
    member = ZFSVdevMemberSerializer(nested=True)

    class Meta:
        model = ZFSVdevMemberHealthReading
        fields = [
            "id", "url", "display", "member", "captured_at", "state", "read_errors", "write_errors", "checksum_errors", "slow_ios",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "member", "captured_at", "state"]
