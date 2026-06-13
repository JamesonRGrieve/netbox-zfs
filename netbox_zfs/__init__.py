# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-zfs: a native NetBox source of truth for ZFS pools, vdevs, datasets, and zvols.

A pool is composed of vdevs; each vdev's members are **partitions** (from ``netbox-fs``), not whole
drives — so a single physical drive carrying a live vdev-member partition *and* a hot-spare
partition is modeled faithfully (each partition joins a different vdev). Depends on ``netbox-fs``
(which depends on ``netbox-inventory``): ZFS topology → partitions → disks → physical assets.
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxZFSConfig(PluginConfig):
    name = "netbox_zfs"
    verbose_name = "ZFS"
    description = "Native SoT for ZFS pools, vdevs, datasets, and zvols"
    version = __version__
    author = "Jameson"
    base_url = "zfs"
    min_version = "4.6.0"
    max_version = "4.6.99"


config = NetBoxZFSConfig
