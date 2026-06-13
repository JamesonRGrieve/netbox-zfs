# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

_pools = PluginMenuItem(
    link="plugins:netbox_zfs:zfspool_list",
    link_text="Pools",
    buttons=[PluginMenuButton("plugins:netbox_zfs:zfspool_add", "Add", "mdi mdi-plus-thick")],
)
_vdevs = PluginMenuItem(
    link="plugins:netbox_zfs:zfsvdev_list",
    link_text="Vdevs",
    buttons=[PluginMenuButton("plugins:netbox_zfs:zfsvdev_add", "Add", "mdi mdi-plus-thick")],
)
_members = PluginMenuItem(
    link="plugins:netbox_zfs:zfsvdevmember_list",
    link_text="Vdev Members",
    buttons=[PluginMenuButton("plugins:netbox_zfs:zfsvdevmember_add", "Add", "mdi mdi-plus-thick")],
)
_datasets = PluginMenuItem(
    link="plugins:netbox_zfs:zfsdataset_list",
    link_text="Datasets",
    buttons=[PluginMenuButton("plugins:netbox_zfs:zfsdataset_add", "Add", "mdi mdi-plus-thick")],
)
_volumes = PluginMenuItem(
    link="plugins:netbox_zfs:zfsvolume_list",
    link_text="Volumes (zvols)",
    buttons=[PluginMenuButton("plugins:netbox_zfs:zfsvolume_add", "Add", "mdi mdi-plus-thick")],
)

menu = PluginMenu(
    label="ZFS",
    groups=(
        ("Topology", (_pools, _vdevs, _members)),
        ("Namespace", (_datasets, _volumes)),
    ),
    icon_class="mdi mdi-database",
)
