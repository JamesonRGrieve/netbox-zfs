# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from netbox_fs.models import Partition
from utilities.forms.fields import (
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField,
)
from utilities.forms.rendering import FieldSet
from .choices import VdevClassChoices, VdevRedundancyChoices
from .models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


class ZFSPoolForm(NetBoxModelForm):
    host = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)

    fieldsets = (
        FieldSet("name", "pool_guid", "host", "comment", name="Pool"),
        FieldSet("ashift", "autotrim", "autoexpand", name="Properties"),
    )

    class Meta:
        model = ZFSPool
        fields = ["name", "pool_guid", "host", "ashift", "autotrim", "autoexpand", "comment", "tags"]


class ZFSVdevForm(NetBoxModelForm):
    pool = DynamicModelChoiceField(queryset=ZFSPool.objects.all())

    fieldsets = (FieldSet("pool", "vdev_class", "redundancy", "index", "draid_config", name="Vdev"),)

    class Meta:
        model = ZFSVdev
        fields = ["pool", "vdev_class", "redundancy", "index", "draid_config", "tags"]


class ZFSVdevMemberForm(NetBoxModelForm):
    vdev = DynamicModelChoiceField(queryset=ZFSVdev.objects.all())
    partition = DynamicModelChoiceField(queryset=Partition.objects.all())

    fieldsets = (FieldSet("vdev", "partition", "device_link_type", "whole_disk", name="Member"),)

    class Meta:
        model = ZFSVdevMember
        fields = ["vdev", "partition", "device_link_type", "whole_disk", "tags"]


class ZFSDatasetForm(NetBoxModelForm):
    pool = DynamicModelChoiceField(queryset=ZFSPool.objects.all())
    parent = DynamicModelChoiceField(queryset=ZFSDataset.objects.all(), required=False)

    fieldsets = (
        FieldSet("pool", "parent", "name", name="Dataset"),
        FieldSet(
            "recordsize", "compression", "checksum", "copies", "dedup", "sync", "logbias",
            "redundant_metadata", "dnodesize", "primarycache", "secondarycache", "volmode",
            name="Storage",
        ),
        FieldSet(
            "atime", "relatime", "exec", "setuid", "devices", "readonly", "canmount", "mountpoint",
            "snapdir", "overlay", "nbmand", "vscan", "zoned", name="Behaviour",
        ),
        FieldSet("xattr", "acltype", "aclinherit", "aclmode", name="ACL / xattr"),
        FieldSet(
            "casesensitivity", "normalization", "utf8only", "version", name="Create-time (immutable)",
        ),
        FieldSet(
            "quota", "refquota", "reservation", "refreservation", "snapshot_limit",
            "filesystem_limit", "special_small_blocks", name="Space",
        ),
        FieldSet("sharenfs", "sharesmb", name="Sharing"),
        FieldSet(
            "encryption", "encryptionroot", "keyformat", "keylocation", "pbkdf2iters",
            name="Encryption",
        ),
        FieldSet("mlslabel", "context", "fscontext", "defcontext", "rootcontext", name="SELinux"),
        FieldSet("advanced", name="Advanced"),
    )

    class Meta:
        model = ZFSDataset
        fields = [
            "pool", "parent", "name", "recordsize", "compression", "checksum", "copies", "dedup",
            "sync", "logbias", "redundant_metadata", "dnodesize", "primarycache", "secondarycache",
            "volmode", "atime", "relatime", "exec", "setuid", "devices", "readonly", "canmount",
            "mountpoint", "snapdir", "overlay", "nbmand", "vscan", "zoned", "xattr", "acltype",
            "aclinherit", "aclmode", "casesensitivity", "normalization", "utf8only", "version",
            "quota", "refquota", "reservation", "refreservation", "snapshot_limit",
            "filesystem_limit", "special_small_blocks", "sharenfs", "sharesmb", "encryption",
            "encryptionroot", "keyformat", "keylocation", "pbkdf2iters", "mlslabel", "context",
            "fscontext", "defcontext", "rootcontext", "advanced", "tags",
        ]


class ZFSVolumeForm(NetBoxModelForm):
    pool = DynamicModelChoiceField(queryset=ZFSPool.objects.all())
    parent = DynamicModelChoiceField(queryset=ZFSDataset.objects.all(), required=False)

    fieldsets = (
        FieldSet("pool", "parent", "name", "volsize", "volblocksize", "volmode", "snapdev", name="Volume"),
        FieldSet(
            "compression", "checksum", "copies", "dedup", "sync", "logbias", "redundant_metadata",
            "primarycache", "secondarycache", "readonly", name="Storage",
        ),
        FieldSet("reservation", "refreservation", name="Space"),
        FieldSet(
            "encryption", "encryptionroot", "keyformat", "keylocation", "pbkdf2iters",
            name="Encryption",
        ),
        FieldSet("mlslabel", "context", "fscontext", "defcontext", "rootcontext", name="SELinux"),
        FieldSet("advanced", name="Advanced"),
    )

    class Meta:
        model = ZFSVolume
        fields = [
            "pool", "parent", "name", "volsize", "volblocksize", "volmode", "snapdev",
            "compression", "checksum", "copies", "dedup", "sync", "logbias", "redundant_metadata",
            "primarycache", "secondarycache", "readonly", "reservation", "refreservation",
            "encryption", "encryptionroot", "keyformat", "keylocation", "pbkdf2iters", "mlslabel",
            "context", "fscontext", "defcontext", "rootcontext", "advanced", "tags",
        ]


class ZFSPoolFilterForm(NetBoxModelFilterSetForm):
    model = ZFSPool
    host_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Host")
    tag = TagFilterField(ZFSPool)


class ZFSVdevFilterForm(NetBoxModelFilterSetForm):
    model = ZFSVdev
    pool_id = DynamicModelMultipleChoiceField(queryset=ZFSPool.objects.all(), required=False, label="Pool")
    vdev_class = forms.MultipleChoiceField(choices=VdevClassChoices, required=False)
    redundancy = forms.MultipleChoiceField(choices=VdevRedundancyChoices, required=False)
    tag = TagFilterField(ZFSVdev)


class ZFSVdevMemberFilterForm(NetBoxModelFilterSetForm):
    model = ZFSVdevMember
    vdev_id = DynamicModelMultipleChoiceField(queryset=ZFSVdev.objects.all(), required=False, label="Vdev")
    partition_id = DynamicModelMultipleChoiceField(queryset=Partition.objects.all(), required=False, label="Partition")
    tag = TagFilterField(ZFSVdevMember)


class ZFSDatasetFilterForm(NetBoxModelFilterSetForm):
    model = ZFSDataset
    pool_id = DynamicModelMultipleChoiceField(queryset=ZFSPool.objects.all(), required=False, label="Pool")
    parent_id = DynamicModelMultipleChoiceField(queryset=ZFSDataset.objects.all(), required=False, label="Parent")
    tag = TagFilterField(ZFSDataset)


class ZFSVolumeFilterForm(NetBoxModelFilterSetForm):
    model = ZFSVolume
    pool_id = DynamicModelMultipleChoiceField(queryset=ZFSPool.objects.all(), required=False, label="Pool")
    parent_id = DynamicModelMultipleChoiceField(queryset=ZFSDataset.objects.all(), required=False, label="Parent")
    tag = TagFilterField(ZFSVolume)
