# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import ZFSDataset, ZFSPool, ZFSVdev, ZFSVdevMember, ZFSVolume
from .serializers import (
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
