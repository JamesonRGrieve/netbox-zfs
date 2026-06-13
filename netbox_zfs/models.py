# SPDX-License-Identifier: AGPL-3.0-or-later
"""ZFS topology model: pools, vdevs, vdev members (which reference netbox-fs partitions), and the
dataset/zvol namespace. Designed *intent* lives here; live pool health is reconciler output."""
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import (
    DeviceLinkTypeChoices, VdevClassChoices, VdevRedundancyChoices, ZFSCanmountChoices,
    ZFSCompressionChoices, ZFSDedupChoices, ZFSEncryptionChoices, ZFSKeyformatChoices,
    ZFSOnOffChoices,
)


class ZFSPool(NetBoxModel):
    """A ZFS storage pool. ``pool_guid`` is the stable identity (it survives rename and export/
    import); ``name`` is only the current display name and can collide across hosts. ``host`` is
    nullable because an exported pool is imported on no host."""

    name = models.CharField(max_length=255, help_text="Current pool name (zpool name).")
    pool_guid = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        unique=True,
        help_text="Stable ZFS pool GUID (`zpool get guid`). Survives rename/export/import.",
    )
    host = models.ForeignKey(
        "dcim.Device",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zfs_pools",
        help_text="The device the pool is currently imported on (blank = exported / not imported).",
    )
    ashift = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Pool sector-size exponent (e.g. 12 = 4 KiB)."
    )
    autotrim = models.CharField(max_length=3, choices=ZFSOnOffChoices, blank=True)
    autoexpand = models.CharField(max_length=3, choices=ZFSOnOffChoices, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    last_seen_state = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional timestamped snapshot of reconciled health (ONLINE/DEGRADED/…). The "
        "designed topology is the source of truth; live state is reconciler output.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "ZFS Pool"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_zfs:zfspool", args=[self.pk])

    def save(self, *args, **kwargs):
        # Empty GUID must be stored as NULL so multiple intent-first pools don't collide on "".
        if not self.pool_guid:
            self.pool_guid = None
        super().save(*args, **kwargs)


class ZFSVdev(NetBoxModel):
    """A vdev within a pool. ``vdev_class`` (its role) is independent of ``redundancy`` (its
    layout), so e.g. a mirrored SLOG is ``class=log, redundancy=mirror``."""

    pool = models.ForeignKey(ZFSPool, on_delete=models.CASCADE, related_name="vdevs")
    vdev_class = models.CharField(
        max_length=8, choices=VdevClassChoices, default=VdevClassChoices.DATA
    )
    redundancy = models.CharField(
        max_length=8, choices=VdevRedundancyChoices, default=VdevRedundancyChoices.STRIPE
    )
    index = models.PositiveSmallIntegerField(
        default=0, help_text="Order of this vdev within its class in the pool."
    )
    draid_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="dRAID parameters (data, children, spares) when redundancy is draid*.",
    )

    class Meta:
        ordering = ["pool", "vdev_class", "index"]
        verbose_name = "ZFS Vdev"
        constraints = [
            models.UniqueConstraint(
                fields=["pool", "vdev_class", "index"],
                name="netbox_zfs_vdev_unique_pool_class_index",
            ),
        ]

    def __str__(self):
        return f"{self.pool}: {self.vdev_class} {self.redundancy} #{self.index}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_zfs:zfsvdev", args=[self.pk])

    def get_vdev_class_color(self):
        return VdevClassChoices.colors.get(self.vdev_class)


class ZFSVdevMember(NetBoxModel):
    """A member of a vdev: a 1:1 reference to a netbox-fs partition. A drive's live partition and
    its hot-spare partition are two separate members in two different (class) vdevs."""

    vdev = models.ForeignKey(ZFSVdev, on_delete=models.CASCADE, related_name="members")
    partition = models.OneToOneField(
        "netbox_fs.Partition",
        on_delete=models.PROTECT,
        related_name="zfs_member",
        help_text="The partition backing this member (PROTECTed — can't be deleted while in use).",
    )
    device_link_type = models.CharField(
        max_length=16, choices=DeviceLinkTypeChoices, default=DeviceLinkTypeChoices.BY_PARTUUID
    )
    whole_disk = models.BooleanField(
        default=False, help_text="ZFS was given the whole disk and created the partition itself."
    )

    class Meta:
        ordering = ["vdev", "partition"]
        verbose_name = "ZFS Vdev Member"

    def __str__(self):
        return f"{self.vdev} ← {self.partition}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_zfs:zfsvdevmember", args=[self.pk])


class ZFSDataset(NetBoxModel):
    """A ZFS filesystem dataset. Hierarchical via ``parent`` (ZFS ``destroy -r`` cascades)."""

    pool = models.ForeignKey(ZFSPool, on_delete=models.CASCADE, related_name="datasets")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    name = models.CharField(max_length=255, help_text="Full dataset path, e.g. tank/db/postgres.")
    recordsize = models.CharField(max_length=16, blank=True, help_text="e.g. 128K, 16K.")
    compression = models.CharField(max_length=16, choices=ZFSCompressionChoices, blank=True)
    atime = models.CharField(max_length=3, choices=ZFSOnOffChoices, blank=True)
    dedup = models.CharField(max_length=8, choices=ZFSDedupChoices, blank=True)
    quota = models.CharField(max_length=32, blank=True, help_text="e.g. 10G, none.")
    refquota = models.CharField(max_length=32, blank=True)
    reservation = models.CharField(max_length=32, blank=True)
    mountpoint = models.CharField(max_length=255, blank=True)
    canmount = models.CharField(max_length=8, choices=ZFSCanmountChoices, blank=True)
    encryption = models.CharField(max_length=16, choices=ZFSEncryptionChoices, blank=True)
    encryptionroot = models.CharField(max_length=255, blank=True)
    keyformat = models.CharField(max_length=16, choices=ZFSKeyformatChoices, blank=True)
    keylocation = models.CharField(max_length=255, blank=True)
    advanced = models.JSONField(
        default=dict, blank=True, help_text="Lossless catch-all for other ZFS properties."
    )

    class Meta:
        ordering = ["pool", "name"]
        verbose_name = "ZFS Dataset"
        constraints = [
            models.UniqueConstraint(
                fields=["pool", "name"], name="netbox_zfs_dataset_unique_pool_name"
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_zfs:zfsdataset", args=[self.pk])


class ZFSVolume(NetBoxModel):
    """A ZFS volume (zvol) — a block device. ``volsize`` is required (it defines the device);
    ``volblocksize`` is fixed at creation. Zvols are leaves; ``parent`` only places them in the
    namespace."""

    pool = models.ForeignKey(ZFSPool, on_delete=models.CASCADE, related_name="volumes")
    parent = models.ForeignKey(
        ZFSDataset,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="volumes",
        help_text="Parent dataset for namespace placement (optional).",
    )
    name = models.CharField(max_length=255, help_text="Full zvol path, e.g. tank/vm/disk-0.")
    volsize = models.CharField(
        max_length=32, help_text="Volume size, e.g. 10G — defines the block device size."
    )
    volblocksize = models.CharField(
        max_length=16, blank=True, help_text="Block size set at creation, e.g. 8K, 16K."
    )
    compression = models.CharField(max_length=16, choices=ZFSCompressionChoices, blank=True)
    dedup = models.CharField(max_length=8, choices=ZFSDedupChoices, blank=True)
    encryption = models.CharField(max_length=16, choices=ZFSEncryptionChoices, blank=True)
    encryptionroot = models.CharField(max_length=255, blank=True)
    advanced = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["pool", "name"]
        verbose_name = "ZFS Volume (zvol)"
        constraints = [
            models.UniqueConstraint(
                fields=["pool", "name"], name="netbox_zfs_volume_unique_pool_name"
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_zfs:zfsvolume", args=[self.pk])
