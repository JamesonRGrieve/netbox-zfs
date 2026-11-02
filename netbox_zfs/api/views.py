# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import (
    ZFSDataset, ZFSPool, ZFSPoolHealth, ZFSPoolHealthReading, ZFSVdev, ZFSVdevMember,
    ZFSVdevMemberHealth, ZFSVdevMemberHealthReading, ZFSVolume,
)
from .serializers import (
    ZFSPoolHealthReadingSerializer, ZFSPoolHealthSerializer, ZFSVdevMemberHealthReadingSerializer,
    ZFSVdevMemberHealthSerializer,
    ZFSDatasetSerializer, ZFSPoolSerializer, ZFSVdevMemberSerializer, ZFSVdevSerializer,
    ZFSVolumeSerializer,
)


class ZFSPoolViewSet(NetBoxModelViewSet):
    queryset = ZFSPool.objects.prefetch_related("host", "tags")
    serializer_class = ZFSPoolSerializer
    filterset_class = filtersets.ZFSPoolFilterSet


class ZFSVdevViewSet(NetBoxModelViewSet):
    queryset = ZFSVdev.objects.prefetch_related("pool", "tags")
    serializer_class = ZFSVdevSerializer
    filterset_class = filtersets.ZFSVdevFilterSet


class ZFSVdevMemberViewSet(NetBoxModelViewSet):
    queryset = ZFSVdevMember.objects.prefetch_related(
        "vdev", "vdev__pool", "partition", "partition__disk", "tags"
    )
    serializer_class = ZFSVdevMemberSerializer
    filterset_class = filtersets.ZFSVdevMemberFilterSet


class ZFSDatasetViewSet(NetBoxModelViewSet):
    queryset = ZFSDataset.objects.prefetch_related("pool", "parent", "tags")
    serializer_class = ZFSDatasetSerializer
    filterset_class = filtersets.ZFSDatasetFilterSet


class ZFSVolumeViewSet(NetBoxModelViewSet):
    queryset = ZFSVolume.objects.prefetch_related("pool", "parent", "tags")
    serializer_class = ZFSVolumeSerializer
    filterset_class = filtersets.ZFSVolumeFilterSet


class ZFSPoolHealthViewSet(NetBoxModelViewSet):
    queryset = ZFSPoolHealth.objects.prefetch_related("pool", "tags")
    serializer_class = ZFSPoolHealthSerializer
    filterset_class = filtersets.ZFSPoolHealthFilterSet


class ZFSPoolHealthReadingViewSet(NetBoxModelViewSet):
    queryset = ZFSPoolHealthReading.objects.prefetch_related("pool", "tags")
    serializer_class = ZFSPoolHealthReadingSerializer
    filterset_class = filtersets.ZFSPoolHealthReadingFilterSet


class ZFSVdevMemberHealthViewSet(NetBoxModelViewSet):
    queryset = ZFSVdevMemberHealth.objects.prefetch_related("member", "tags")
    serializer_class = ZFSVdevMemberHealthSerializer
    filterset_class = filtersets.ZFSVdevMemberHealthFilterSet


class ZFSVdevMemberHealthReadingViewSet(NetBoxModelViewSet):
    queryset = ZFSVdevMemberHealthReading.objects.prefetch_related("member", "tags")
    serializer_class = ZFSVdevMemberHealthReadingSerializer
    filterset_class = filtersets.ZFSVdevMemberHealthReadingFilterSet
