# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored: observed pool and vdev-member health (latest snapshot + history).
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

_BASE = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
    ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
    ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
    ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
]


def _pool_metrics():
    return [
        ("health", models.CharField(blank=True, max_length=16)),
        ("size_bytes", models.BigIntegerField(blank=True, null=True)),
        ("allocated_bytes", models.BigIntegerField(blank=True, null=True)),
        ("free_bytes", models.BigIntegerField(blank=True, null=True)),
        ("fragmentation_percent", models.PositiveSmallIntegerField(blank=True, null=True)),
        ("capacity_percent", models.PositiveSmallIntegerField(blank=True, null=True)),
        ("data_errors", models.BigIntegerField(blank=True, null=True)),
        ("scrub_state", models.CharField(blank=True, max_length=16)),
        ("scrub_end", models.DateTimeField(blank=True, null=True)),
        ("scrub_errors", models.BigIntegerField(blank=True, null=True)),
    ]


def _member_metrics():
    return [
        ("state", models.CharField(blank=True, max_length=16)),
        ("read_errors", models.BigIntegerField(blank=True, null=True)),
        ("write_errors", models.BigIntegerField(blank=True, null=True)),
        ("checksum_errors", models.BigIntegerField(blank=True, null=True)),
        ("slow_ios", models.BigIntegerField(blank=True, null=True)),
    ]


def _tags():
    return ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"))


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0001_initial"),
        ("netbox_zfs", "0003_vdevmember_shared_partition"),
    ]
    operations = [
        migrations.CreateModel(
            name="ZFSPoolHealth",
            fields=_BASE + _pool_metrics() + [
                ("captured_at", models.DateTimeField(blank=True, null=True)),
                ("pool", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="health", to="netbox_zfs.zfspool")),
                _tags(),
            ],
            options={"verbose_name": "ZFS Pool Health", "verbose_name_plural": "ZFS Pool Health", "ordering": ["pool"]},
        ),
        migrations.CreateModel(
            name="ZFSPoolHealthReading",
            fields=_BASE + _pool_metrics() + [
                ("captured_at", models.DateTimeField()),
                ("pool", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="health_readings", to="netbox_zfs.zfspool")),
                _tags(),
            ],
            options={"verbose_name": "ZFS Pool Health Reading", "ordering": ["pool", "-captured_at"]},
        ),
        migrations.AddConstraint(
            model_name="zfspoolhealthreading",
            constraint=models.UniqueConstraint(fields=("pool", "captured_at"), name="netbox_zfs_poolhealthreading_unique"),
        ),
        migrations.CreateModel(
            name="ZFSVdevMemberHealth",
            fields=_BASE + _member_metrics() + [
                ("captured_at", models.DateTimeField(blank=True, null=True)),
                ("member", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="health", to="netbox_zfs.zfsvdevmember")),
                _tags(),
            ],
            options={"verbose_name": "ZFS Vdev Member Health", "verbose_name_plural": "ZFS Vdev Member Health", "ordering": ["member"]},
        ),
        migrations.CreateModel(
            name="ZFSVdevMemberHealthReading",
            fields=_BASE + _member_metrics() + [
                ("captured_at", models.DateTimeField()),
                ("member", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="health_readings", to="netbox_zfs.zfsvdevmember")),
                _tags(),
            ],
            options={"verbose_name": "ZFS Vdev Member Health Reading", "ordering": ["member", "-captured_at"]},
        ),
        migrations.AddConstraint(
            model_name="zfsvdevmemberhealthreading",
            constraint=models.UniqueConstraint(fields=("member", "captured_at"), name="netbox_zfs_memberhealthreading_unique"),
        ),
    ]
