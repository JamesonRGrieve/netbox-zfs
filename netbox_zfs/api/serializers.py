# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from netbox_fs.api.serializers import PartitionSerializer
from rest_framework import serializers
from ..models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


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
            "atime", "dedup", "quota", "refquota", "reservation", "mountpoint", "canmount",
            "encryption", "encryptionroot", "keyformat", "keylocation", "advanced",
            "tags", "custom_fields", "created", "last_updated",
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
            "compression", "dedup", "encryption", "encryptionroot", "advanced",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "volsize"]
