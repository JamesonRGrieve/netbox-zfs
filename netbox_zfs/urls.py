# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views

urlpatterns = [
    # Pools
    path("pools/", views.ZFSPoolListView.as_view(), name="zfspool_list"),
    path("pools/add/", views.ZFSPoolEditView.as_view(), name="zfspool_add"),
    path("pools/delete/", views.ZFSPoolBulkDeleteView.as_view(), name="zfspool_bulk_delete"),
    path("pools/<int:pk>/", views.ZFSPoolView.as_view(), name="zfspool"),
    path("pools/<int:pk>/edit/", views.ZFSPoolEditView.as_view(), name="zfspool_edit"),
    path("pools/<int:pk>/delete/", views.ZFSPoolDeleteView.as_view(), name="zfspool_delete"),
    path("pools/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="zfspool_changelog", kwargs={"model": models.ZFSPool}),
    path("pools/<int:pk>/journal/", ObjectJournalView.as_view(), name="zfspool_journal", kwargs={"model": models.ZFSPool}),
    # Vdevs
    path("vdevs/", views.ZFSVdevListView.as_view(), name="zfsvdev_list"),
    path("vdevs/add/", views.ZFSVdevEditView.as_view(), name="zfsvdev_add"),
    path("vdevs/delete/", views.ZFSVdevBulkDeleteView.as_view(), name="zfsvdev_bulk_delete"),
    path("vdevs/<int:pk>/", views.ZFSVdevView.as_view(), name="zfsvdev"),
    path("vdevs/<int:pk>/edit/", views.ZFSVdevEditView.as_view(), name="zfsvdev_edit"),
    path("vdevs/<int:pk>/delete/", views.ZFSVdevDeleteView.as_view(), name="zfsvdev_delete"),
    path("vdevs/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="zfsvdev_changelog", kwargs={"model": models.ZFSVdev}),
    path("vdevs/<int:pk>/journal/", ObjectJournalView.as_view(), name="zfsvdev_journal", kwargs={"model": models.ZFSVdev}),
    # Vdev members
    path("vdev-members/", views.ZFSVdevMemberListView.as_view(), name="zfsvdevmember_list"),
    path("vdev-members/add/", views.ZFSVdevMemberEditView.as_view(), name="zfsvdevmember_add"),
    path("vdev-members/delete/", views.ZFSVdevMemberBulkDeleteView.as_view(), name="zfsvdevmember_bulk_delete"),
    path("vdev-members/<int:pk>/", views.ZFSVdevMemberView.as_view(), name="zfsvdevmember"),
    path("vdev-members/<int:pk>/edit/", views.ZFSVdevMemberEditView.as_view(), name="zfsvdevmember_edit"),
    path("vdev-members/<int:pk>/delete/", views.ZFSVdevMemberDeleteView.as_view(), name="zfsvdevmember_delete"),
    path("vdev-members/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="zfsvdevmember_changelog", kwargs={"model": models.ZFSVdevMember}),
    path("vdev-members/<int:pk>/journal/", ObjectJournalView.as_view(), name="zfsvdevmember_journal", kwargs={"model": models.ZFSVdevMember}),
    # Datasets
    path("datasets/", views.ZFSDatasetListView.as_view(), name="zfsdataset_list"),
    path("datasets/add/", views.ZFSDatasetEditView.as_view(), name="zfsdataset_add"),
    path("datasets/delete/", views.ZFSDatasetBulkDeleteView.as_view(), name="zfsdataset_bulk_delete"),
    path("datasets/<int:pk>/", views.ZFSDatasetView.as_view(), name="zfsdataset"),
    path("datasets/<int:pk>/edit/", views.ZFSDatasetEditView.as_view(), name="zfsdataset_edit"),
    path("datasets/<int:pk>/delete/", views.ZFSDatasetDeleteView.as_view(), name="zfsdataset_delete"),
    path("datasets/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="zfsdataset_changelog", kwargs={"model": models.ZFSDataset}),
    path("datasets/<int:pk>/journal/", ObjectJournalView.as_view(), name="zfsdataset_journal", kwargs={"model": models.ZFSDataset}),
    # Volumes (zvols)
    path("volumes/", views.ZFSVolumeListView.as_view(), name="zfsvolume_list"),
    path("volumes/add/", views.ZFSVolumeEditView.as_view(), name="zfsvolume_add"),
    path("volumes/delete/", views.ZFSVolumeBulkDeleteView.as_view(), name="zfsvolume_bulk_delete"),
    path("volumes/<int:pk>/", views.ZFSVolumeView.as_view(), name="zfsvolume"),
    path("volumes/<int:pk>/edit/", views.ZFSVolumeEditView.as_view(), name="zfsvolume_edit"),
    path("volumes/<int:pk>/delete/", views.ZFSVolumeDeleteView.as_view(), name="zfsvolume_delete"),
    path("volumes/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name="zfsvolume_changelog", kwargs={"model": models.ZFSVolume}),
    path("volumes/<int:pk>/journal/", ObjectJournalView.as_view(), name="zfsvolume_journal", kwargs={"model": models.ZFSVolume}),
]
