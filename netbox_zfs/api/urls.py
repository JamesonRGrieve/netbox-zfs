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
router.register("pool-health", views.ZFSPoolHealthViewSet)
router.register("pool-health-readings", views.ZFSPoolHealthReadingViewSet)
router.register("member-health", views.ZFSVdevMemberHealthViewSet)
router.register("member-health-readings", views.ZFSVdevMemberHealthReadingViewSet)

urlpatterns = router.urls
