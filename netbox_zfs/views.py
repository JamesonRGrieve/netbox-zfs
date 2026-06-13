# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class ZFSPoolView(generic.ObjectView):
    queryset = models.ZFSPool.objects.all()


class ZFSPoolListView(generic.ObjectListView):
    queryset = models.ZFSPool.objects.all()
    table = tables.ZFSPoolTable
    filterset = filtersets.ZFSPoolFilterSet
    filterset_form = forms.ZFSPoolFilterForm


class ZFSPoolEditView(generic.ObjectEditView):
    queryset = models.ZFSPool.objects.all()
    form = forms.ZFSPoolForm


class ZFSPoolDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSPool.objects.all()


class ZFSPoolBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSPool.objects.all()
    table = tables.ZFSPoolTable


class ZFSVdevView(generic.ObjectView):
    queryset = models.ZFSVdev.objects.all()


class ZFSVdevListView(generic.ObjectListView):
    queryset = models.ZFSVdev.objects.all()
    table = tables.ZFSVdevTable
    filterset = filtersets.ZFSVdevFilterSet
    filterset_form = forms.ZFSVdevFilterForm


class ZFSVdevEditView(generic.ObjectEditView):
    queryset = models.ZFSVdev.objects.all()
    form = forms.ZFSVdevForm


class ZFSVdevDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSVdev.objects.all()


class ZFSVdevBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSVdev.objects.all()
    table = tables.ZFSVdevTable


class ZFSVdevMemberView(generic.ObjectView):
    queryset = models.ZFSVdevMember.objects.all()


class ZFSVdevMemberListView(generic.ObjectListView):
    queryset = models.ZFSVdevMember.objects.all()
    table = tables.ZFSVdevMemberTable
    filterset = filtersets.ZFSVdevMemberFilterSet
    filterset_form = forms.ZFSVdevMemberFilterForm


class ZFSVdevMemberEditView(generic.ObjectEditView):
    queryset = models.ZFSVdevMember.objects.all()
    form = forms.ZFSVdevMemberForm


class ZFSVdevMemberDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSVdevMember.objects.all()


class ZFSVdevMemberBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSVdevMember.objects.all()
    table = tables.ZFSVdevMemberTable


class ZFSDatasetView(generic.ObjectView):
    queryset = models.ZFSDataset.objects.all()


class ZFSDatasetListView(generic.ObjectListView):
    queryset = models.ZFSDataset.objects.all()
    table = tables.ZFSDatasetTable
    filterset = filtersets.ZFSDatasetFilterSet
    filterset_form = forms.ZFSDatasetFilterForm


class ZFSDatasetEditView(generic.ObjectEditView):
    queryset = models.ZFSDataset.objects.all()
    form = forms.ZFSDatasetForm


class ZFSDatasetDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSDataset.objects.all()


class ZFSDatasetBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSDataset.objects.all()
    table = tables.ZFSDatasetTable


class ZFSVolumeView(generic.ObjectView):
    queryset = models.ZFSVolume.objects.all()


class ZFSVolumeListView(generic.ObjectListView):
    queryset = models.ZFSVolume.objects.all()
    table = tables.ZFSVolumeTable
    filterset = filtersets.ZFSVolumeFilterSet
    filterset_form = forms.ZFSVolumeFilterForm


class ZFSVolumeEditView(generic.ObjectEditView):
    queryset = models.ZFSVolume.objects.all()
    form = forms.ZFSVolumeForm


class ZFSVolumeDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSVolume.objects.all()


class ZFSVolumeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSVolume.objects.all()
    table = tables.ZFSVolumeTable
