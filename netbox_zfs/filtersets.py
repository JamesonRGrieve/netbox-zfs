# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from dcim.models import Device
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from netbox_fs.models import Partition
from .choices import VdevClassChoices, VdevRedundancyChoices
from .models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume


class ZFSPoolFilterSet(NetBoxModelFilterSet):
    # Explicit FK filter: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields.
    host_id = django_filters.ModelMultipleChoiceFilter(
        field_name="host", queryset=Device.objects.all(), label="Host (ID)"
    )

    class Meta:
        model = ZFSPool
        fields = ["id", "name", "pool_guid", "ashift", "autotrim", "autoexpand"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(pool_guid__icontains=value) | Q(comment__icontains=value)
        )


class ZFSVdevFilterSet(NetBoxModelFilterSet):
    pool_id = django_filters.ModelMultipleChoiceFilter(
        field_name="pool", queryset=ZFSPool.objects.all(), label="Pool (ID)"
    )
    vdev_class = django_filters.MultipleChoiceFilter(choices=VdevClassChoices)
    redundancy = django_filters.MultipleChoiceFilter(choices=VdevRedundancyChoices)

    class Meta:
        model = ZFSVdev
        fields = ["id", "index"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(pool__name__icontains=value))


class ZFSVdevMemberFilterSet(NetBoxModelFilterSet):
    vdev_id = django_filters.ModelMultipleChoiceFilter(
        field_name="vdev", queryset=ZFSVdev.objects.all(), label="Vdev (ID)"
    )
    partition_id = django_filters.ModelMultipleChoiceFilter(
        field_name="partition", queryset=Partition.objects.all(), label="Partition (ID)"
    )

    class Meta:
        model = ZFSVdevMember
        fields = ["id", "device_link_type", "whole_disk"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(vdev__pool__name__icontains=value) | Q(partition__name__icontains=value)
        )


class ZFSDatasetFilterSet(NetBoxModelFilterSet):
    pool_id = django_filters.ModelMultipleChoiceFilter(
        field_name="pool", queryset=ZFSPool.objects.all(), label="Pool (ID)"
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name="parent", queryset=ZFSDataset.objects.all(), label="Parent (ID)"
    )

    class Meta:
        model = ZFSDataset
        fields = [
            "id", "name", "recordsize", "compression", "checksum", "copies", "atime", "relatime",
            "dedup", "sync", "logbias", "redundant_metadata", "dnodesize", "volmode", "readonly",
            "canmount", "mountpoint", "snapdir", "xattr", "acltype", "casesensitivity",
            "encryption",
        ]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(mountpoint__icontains=value) | Q(sharenfs__icontains=value)
        )


class ZFSVolumeFilterSet(NetBoxModelFilterSet):
    pool_id = django_filters.ModelMultipleChoiceFilter(
        field_name="pool", queryset=ZFSPool.objects.all(), label="Pool (ID)"
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        field_name="parent", queryset=ZFSDataset.objects.all(), label="Parent (ID)"
    )

    class Meta:
        model = ZFSVolume
        fields = [
            "id", "name", "volsize", "volblocksize", "volmode", "snapdev", "compression",
            "checksum", "copies", "dedup", "sync", "logbias", "redundant_metadata", "readonly",
            "encryption",
        ]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))
