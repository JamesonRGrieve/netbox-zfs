# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-zfs: a native NetBox source of truth for ZFS pools, vdevs, datasets, and zvols.

A pool is composed of vdevs; each vdev's members are **partitions** (from ``netbox-fs``), not whole
drives — so a single physical drive carrying a live vdev-member partition *and* a hot-spare
partition is modeled faithfully (each partition joins a different vdev). Depends on ``netbox-fs``
(which depends on ``netbox-inventory``): ZFS topology → partitions → disks → physical assets.

Observed health (pool state, capacity, scrub results, per-member error counters) is kept beside the
designed topology as a latest snapshot plus daily history, filled by a daily OpenObserve sync job.
"""
from netbox.plugins import PluginConfig

__version__ = "0.1.0"


class NetBoxZFSConfig(PluginConfig):
    name = "netbox_zfs"
    verbose_name = "ZFS"
    description = "Native SoT for ZFS pools, vdevs, datasets, and zvols"
    version = __version__
    author = "Jameson"
    base_url = "zfs"
    min_version = "4.6.0"
    max_version = "4.6.99"

    def ready(self):
        super().ready()
        from . import jobs  # noqa: F401  registers the daily OpenObserve health sync as a system job


config = NetBoxZFSConfig
