# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_zfs --check --dry-run   (on a dev/ephemeral NetBox)
#
# Lets one partition back members in several vdevs: a hot-spare disk shared across multiple
# pools is the same partition listed in each pool's spare vdev. Demotes the OneToOneField to a
# ForeignKey (related_name pluralised zfs_member -> zfs_members) and adds a (vdev, partition)
# unique constraint so a partition can't be listed twice within one vdev.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_fs", "0001_initial"),
        ("netbox_zfs", "0002_dataset_volume_properties"),
    ]

    operations = [
        migrations.AlterField(
            model_name="zfsvdevmember",
            name="partition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="zfs_members",
                to="netbox_fs.partition",
            ),
        ),
        migrations.AddConstraint(
            model_name="zfsvdevmember",
            constraint=models.UniqueConstraint(
                fields=("vdev", "partition"), name="netbox_zfs_vdevmember_unique"
            ),
        ),
    ]
