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
        FieldSet("recordsize", "compression", "atime", "dedup", "canmount", "mountpoint", name="Properties"),
        FieldSet("quota", "refquota", "reservation", name="Space"),
        FieldSet("encryption", "encryptionroot", "keyformat", "keylocation", name="Encryption"),
        FieldSet("advanced", name="Advanced"),
    )

    class Meta:
        model = ZFSDataset
        fields = [
            "pool", "parent", "name", "recordsize", "compression", "atime", "dedup", "quota",
            "refquota", "reservation", "mountpoint", "canmount", "encryption", "encryptionroot",
            "keyformat", "keylocation", "advanced", "tags",
        ]


class ZFSVolumeForm(NetBoxModelForm):
    pool = DynamicModelChoiceField(queryset=ZFSPool.objects.all())
    parent = DynamicModelChoiceField(queryset=ZFSDataset.objects.all(), required=False)

    fieldsets = (
        FieldSet("pool", "parent", "name", "volsize", "volblocksize", name="Volume"),
        FieldSet("compression", "dedup", "encryption", "encryptionroot", "advanced", name="Properties"),
    )

    class Meta:
        model = ZFSVolume
        fields = [
            "pool", "parent", "name", "volsize", "volblocksize", "compression", "dedup",
            "encryption", "encryptionroot", "advanced", "tags",
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
