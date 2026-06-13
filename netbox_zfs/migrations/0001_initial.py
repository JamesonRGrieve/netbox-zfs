# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_zfs --check --dry-run   (on a dev/ephemeral NetBox)
#
# The dependency on ("netbox_fs", "0001_initial") is load-bearing: ZFSVdevMember has a cross-plugin
# FK to netbox_fs.Partition, so the fs tables must exist first. Install order is therefore
# netbox_inventory -> netbox_fs -> netbox_zfs.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("netbox_fs", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="ZFSPool",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("name", models.CharField(max_length=255)),
                ("pool_guid", models.CharField(blank=True, max_length=32, null=True, unique=True)),
                ("ashift", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("autotrim", models.CharField(blank=True, max_length=3)),
                ("autoexpand", models.CharField(blank=True, max_length=3)),
                ("comment", models.CharField(blank=True, max_length=255)),
                ("last_seen_state", models.JSONField(blank=True, default=dict)),
                ("host", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="zfs_pools", to="dcim.device")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "ZFS Pool", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="ZFSDataset",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("name", models.CharField(max_length=255)),
                ("recordsize", models.CharField(blank=True, max_length=16)),
                ("compression", models.CharField(blank=True, max_length=16)),
                ("atime", models.CharField(blank=True, max_length=3)),
                ("dedup", models.CharField(blank=True, max_length=8)),
                ("quota", models.CharField(blank=True, max_length=32)),
                ("refquota", models.CharField(blank=True, max_length=32)),
                ("reservation", models.CharField(blank=True, max_length=32)),
                ("mountpoint", models.CharField(blank=True, max_length=255)),
                ("canmount", models.CharField(blank=True, max_length=8)),
                ("encryption", models.CharField(blank=True, max_length=16)),
                ("encryptionroot", models.CharField(blank=True, max_length=255)),
                ("keyformat", models.CharField(blank=True, max_length=16)),
                ("keylocation", models.CharField(blank=True, max_length=255)),
                ("advanced", models.JSONField(blank=True, default=dict)),
                ("pool", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="datasets", to="netbox_zfs.zfspool")),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="children", to="netbox_zfs.zfsdataset")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "ZFS Dataset",
                "ordering": ["pool", "name"],
                "constraints": [models.UniqueConstraint(fields=("pool", "name"), name="netbox_zfs_dataset_unique_pool_name")],
            },
        ),
        migrations.CreateModel(
            name="ZFSVolume",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("name", models.CharField(max_length=255)),
                ("volsize", models.CharField(max_length=32)),
                ("volblocksize", models.CharField(blank=True, max_length=16)),
                ("compression", models.CharField(blank=True, max_length=16)),
                ("dedup", models.CharField(blank=True, max_length=8)),
                ("encryption", models.CharField(blank=True, max_length=16)),
                ("encryptionroot", models.CharField(blank=True, max_length=255)),
                ("advanced", models.JSONField(blank=True, default=dict)),
                ("pool", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="volumes", to="netbox_zfs.zfspool")),
                ("parent", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="volumes", to="netbox_zfs.zfsdataset")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "ZFS Volume (zvol)",
                "ordering": ["pool", "name"],
                "constraints": [models.UniqueConstraint(fields=("pool", "name"), name="netbox_zfs_volume_unique_pool_name")],
            },
        ),
        migrations.CreateModel(
            name="ZFSVdev",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("vdev_class", models.CharField(default="data", max_length=8)),
                ("redundancy", models.CharField(default="stripe", max_length=8)),
                ("index", models.PositiveSmallIntegerField(default=0)),
                ("draid_config", models.JSONField(blank=True, default=dict)),
                ("pool", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="vdevs", to="netbox_zfs.zfspool")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "verbose_name": "ZFS Vdev",
                "ordering": ["pool", "vdev_class", "index"],
                "constraints": [models.UniqueConstraint(fields=("pool", "vdev_class", "index"), name="netbox_zfs_vdev_unique_pool_class_index")],
            },
        ),
        migrations.CreateModel(
            name="ZFSVdevMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
                ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ("device_link_type", models.CharField(default="by-partuuid", max_length=16)),
                ("whole_disk", models.BooleanField(default=False)),
                ("vdev", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="members", to="netbox_zfs.zfsvdev")),
                ("partition", models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name="zfs_member", to="netbox_fs.partition")),
                ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={"verbose_name": "ZFS Vdev Member", "ordering": ["vdev", "partition"]},
        ),
    ]
