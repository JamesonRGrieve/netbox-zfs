# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_zfs --check --dry-run   (on a dev/ephemeral NetBox)
#
# Promotes the full settable ZFS property surface to first-class optional fields on
# ZFSDataset and ZFSVolume. Blank/NULL means "inherited or default" (resolved at runtime
# via the dataset hierarchy); a value is the locally-set property. ChoiceSet-backed fields
# carry no `choices=` here because NetBox ChoiceSets are not serialized into migrations
# (matching 0001). The data migration moves any existing ``advanced["sharenfs"]`` into the
# new first-class ``sharenfs`` field.
from django.db import migrations, models

# (name, max_length) for the blank CharField columns added to each model.
DATASET_CHARS = [
    ("relatime", 3), ("exec", 3), ("setuid", 3), ("devices", 3), ("readonly", 3),
    ("nbmand", 3), ("vscan", 3), ("overlay", 3), ("zoned", 3), ("utf8only", 3),
    ("checksum", 10), ("xattr", 3), ("acltype", 6), ("aclinherit", 14), ("aclmode", 11),
    ("sync", 8), ("logbias", 10), ("snapdir", 7), ("primarycache", 8), ("secondarycache", 8),
    ("redundant_metadata", 4), ("dnodesize", 6), ("volmode", 7),
    ("casesensitivity", 11), ("normalization", 6), ("version", 8),
    ("sharenfs", 512), ("sharesmb", 512), ("refreservation", 32), ("snapshot_limit", 16),
    ("filesystem_limit", 16), ("special_small_blocks", 16),
    ("mlslabel", 255), ("context", 255), ("fscontext", 255), ("defcontext", 255),
    ("rootcontext", 255),
]
VOLUME_CHARS = [
    ("volmode", 7), ("snapdev", 7), ("checksum", 10), ("readonly", 3), ("sync", 8),
    ("logbias", 10), ("primarycache", 8), ("secondarycache", 8), ("redundant_metadata", 4),
    ("reservation", 32), ("refreservation", 32), ("keyformat", 16), ("keylocation", 255),
    ("mlslabel", 255), ("context", 255), ("fscontext", 255), ("defcontext", 255),
    ("rootcontext", 255),
]
COPIES_CHOICES = [(1, "1"), (2, "2"), (3, "3")]


def _char(model, name, max_length):
    return migrations.AddField(
        model_name=model, name=name,
        field=models.CharField(blank=True, default="", max_length=max_length),
        preserve_default=False,
    )


def move_sharenfs_forward(apps, schema_editor):
    ZFSDataset = apps.get_model("netbox_zfs", "ZFSDataset")
    for ds in ZFSDataset.objects.all():
        adv = ds.advanced or {}
        if "sharenfs" in adv:
            ds.sharenfs = adv.pop("sharenfs") or ""
            ds.advanced = adv
            ds.save(update_fields=["sharenfs", "advanced"])


def move_sharenfs_backward(apps, schema_editor):
    ZFSDataset = apps.get_model("netbox_zfs", "ZFSDataset")
    for ds in ZFSDataset.objects.exclude(sharenfs=""):
        adv = ds.advanced or {}
        adv["sharenfs"] = ds.sharenfs
        ds.advanced = adv
        ds.sharenfs = ""
        ds.save(update_fields=["sharenfs", "advanced"])


class Migration(migrations.Migration):
    dependencies = [("netbox_zfs", "0001_initial")]

    operations = (
        [_char("zfsdataset", n, ml) for n, ml in DATASET_CHARS]
        + [
            migrations.AddField(
                model_name="zfsdataset", name="copies",
                field=models.PositiveSmallIntegerField(blank=True, choices=COPIES_CHOICES, null=True),
            ),
            migrations.AddField(
                model_name="zfsdataset", name="pbkdf2iters",
                field=models.PositiveIntegerField(blank=True, null=True),
            ),
        ]
        + [_char("zfsvolume", n, ml) for n, ml in VOLUME_CHARS]
        + [
            migrations.AddField(
                model_name="zfsvolume", name="copies",
                field=models.PositiveSmallIntegerField(blank=True, choices=COPIES_CHOICES, null=True),
            ),
            migrations.AddField(
                model_name="zfsvolume", name="pbkdf2iters",
                field=models.PositiveIntegerField(blank=True, null=True),
            ),
        ]
        + [migrations.RunPython(move_sharenfs_forward, move_sharenfs_backward)]
    )
