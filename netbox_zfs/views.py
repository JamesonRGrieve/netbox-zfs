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


# Readings shown on a health page; the full history is the filtered readings list.
HISTORY_ROWS = 25


class ZFSPoolHealthView(generic.ObjectView):
    queryset = models.ZFSPoolHealth.objects.all()

    def get_extra_context(self, request, instance):
        readings = tables.ZFSPoolHealthReadingTable(instance.readings[:HISTORY_ROWS], orderable=False)
        readings.columns.hide("pool")
        return {"readings_table": readings, "readings_count": instance.readings.count()}


class ZFSPoolHealthListView(generic.ObjectListView):
    queryset = models.ZFSPoolHealth.objects.all()
    table = tables.ZFSPoolHealthTable
    filterset = filtersets.ZFSPoolHealthFilterSet
    filterset_form = forms.ZFSPoolHealthFilterForm


class ZFSPoolHealthEditView(generic.ObjectEditView):
    queryset = models.ZFSPoolHealth.objects.all()
    form = forms.ZFSPoolHealthForm


class ZFSPoolHealthDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSPoolHealth.objects.all()


class ZFSPoolHealthBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSPoolHealth.objects.all()
    table = tables.ZFSPoolHealthTable


class ZFSPoolHealthReadingView(generic.ObjectView):
    queryset = models.ZFSPoolHealthReading.objects.all()


class ZFSPoolHealthReadingListView(generic.ObjectListView):
    queryset = models.ZFSPoolHealthReading.objects.all()
    table = tables.ZFSPoolHealthReadingTable
    filterset = filtersets.ZFSPoolHealthReadingFilterSet
    filterset_form = forms.ZFSPoolHealthReadingFilterForm


class ZFSPoolHealthReadingEditView(generic.ObjectEditView):
    queryset = models.ZFSPoolHealthReading.objects.all()
    form = forms.ZFSPoolHealthReadingForm


class ZFSPoolHealthReadingDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSPoolHealthReading.objects.all()


class ZFSPoolHealthReadingBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSPoolHealthReading.objects.all()
    table = tables.ZFSPoolHealthReadingTable


class ZFSVdevMemberHealthView(generic.ObjectView):
    queryset = models.ZFSVdevMemberHealth.objects.all()

    def get_extra_context(self, request, instance):
        readings = tables.ZFSVdevMemberHealthReadingTable(instance.readings[:HISTORY_ROWS], orderable=False)
        readings.columns.hide("member")
        return {"readings_table": readings, "readings_count": instance.readings.count()}


class ZFSVdevMemberHealthListView(generic.ObjectListView):
    queryset = models.ZFSVdevMemberHealth.objects.all()
    table = tables.ZFSVdevMemberHealthTable
    filterset = filtersets.ZFSVdevMemberHealthFilterSet
    filterset_form = forms.ZFSVdevMemberHealthFilterForm


class ZFSVdevMemberHealthEditView(generic.ObjectEditView):
    queryset = models.ZFSVdevMemberHealth.objects.all()
    form = forms.ZFSVdevMemberHealthForm


class ZFSVdevMemberHealthDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSVdevMemberHealth.objects.all()


class ZFSVdevMemberHealthBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSVdevMemberHealth.objects.all()
    table = tables.ZFSVdevMemberHealthTable


class ZFSVdevMemberHealthReadingView(generic.ObjectView):
    queryset = models.ZFSVdevMemberHealthReading.objects.all()


class ZFSVdevMemberHealthReadingListView(generic.ObjectListView):
    queryset = models.ZFSVdevMemberHealthReading.objects.all()
    table = tables.ZFSVdevMemberHealthReadingTable
    filterset = filtersets.ZFSVdevMemberHealthReadingFilterSet
    filterset_form = forms.ZFSVdevMemberHealthReadingFilterForm


class ZFSVdevMemberHealthReadingEditView(generic.ObjectEditView):
    queryset = models.ZFSVdevMemberHealthReading.objects.all()
    form = forms.ZFSVdevMemberHealthReadingForm


class ZFSVdevMemberHealthReadingDeleteView(generic.ObjectDeleteView):
    queryset = models.ZFSVdevMemberHealthReading.objects.all()


class ZFSVdevMemberHealthReadingBulkDeleteView(generic.BulkDeleteView):
    queryset = models.ZFSVdevMemberHealthReading.objects.all()
    table = tables.ZFSVdevMemberHealthReadingTable
