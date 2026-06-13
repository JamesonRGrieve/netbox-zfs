# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_zfs"

router = NetBoxRouter()
router.register("pools", views.ZFSPoolViewSet)
router.register("vdevs", views.ZFSVdevViewSet)
router.register("vdev-members", views.ZFSVdevMemberViewSet)
router.register("datasets", views.ZFSDatasetViewSet)
router.register("volumes", views.ZFSVolumeViewSet)

urlpatterns = router.urls
