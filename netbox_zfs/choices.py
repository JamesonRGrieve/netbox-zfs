# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the ZFS model. Values match `zpool`/`zfs` property tokens verbatim."""
from utilities.choices import ChoiceSet


class VdevClassChoices(ChoiceSet):
    """The allocation class / role a vdev plays in its pool. Kept separate from redundancy so a
    mirrored SLOG is ``class=log, redundancy=mirror``."""

    DATA = "data"
    LOG = "log"
    CACHE = "cache"
    SPARE = "spare"
    SPECIAL = "special"
    DEDUP = "dedup"
    CHOICES = [
        (DATA, "Data", "blue"),
        (LOG, "Log (SLOG)", "cyan"),
        (CACHE, "Cache (L2ARC)", "teal"),
        (SPARE, "Spare", "yellow"),
        (SPECIAL, "Special", "purple"),
        (DEDUP, "Dedup", "orange"),
    ]


class VdevRedundancyChoices(ChoiceSet):
    """The redundancy layout of a vdev's members."""

    STRIPE = "stripe"
    MIRROR = "mirror"
    RAIDZ1 = "raidz1"
    RAIDZ2 = "raidz2"
    RAIDZ3 = "raidz3"
    DRAID1 = "draid1"
    DRAID2 = "draid2"
    DRAID3 = "draid3"
    CHOICES = [
        (STRIPE, "Stripe (single / no redundancy)"),
        (MIRROR, "Mirror"),
        (RAIDZ1, "RAIDZ1"),
        (RAIDZ2, "RAIDZ2"),
        (RAIDZ3, "RAIDZ3"),
        (DRAID1, "dRAID1"),
        (DRAID2, "dRAID2"),
        (DRAID3, "dRAID3"),
    ]


class DeviceLinkTypeChoices(ChoiceSet):
    """How `zpool status` names a member device (the /dev path style ZFS recorded)."""

    BY_ID = "by-id"
    BY_PARTUUID = "by-partuuid"
    BY_PATH = "by-path"
    BY_VDEV = "by-vdev"
    DEV = "dev"
    CHOICES = [
        (BY_ID, "/dev/disk/by-id"),
        (BY_PARTUUID, "/dev/disk/by-partuuid"),
        (BY_PATH, "/dev/disk/by-path"),
        (BY_VDEV, "/dev/disk/by-vdev"),
        (DEV, "/dev (kernel name)"),
    ]


class ZFSOnOffChoices(ChoiceSet):
    """A simple on/off property; blank means inherited/default."""

    ON = "on"
    OFF = "off"
    CHOICES = [(ON, "On"), (OFF, "Off")]


class ZFSCompressionChoices(ChoiceSet):
    OFF = "off"
    ON = "on"
    LZ4 = "lz4"
    ZSTD = "zstd"
    GZIP = "gzip"
    ZLE = "zle"
    LZJB = "lzjb"
    CHOICES = [
        (OFF, "off"),
        (ON, "on"),
        (LZ4, "lz4"),
        (ZSTD, "zstd"),
        (GZIP, "gzip"),
        (ZLE, "zle"),
        (LZJB, "lzjb"),
    ]


class ZFSDedupChoices(ChoiceSet):
    OFF = "off"
    ON = "on"
    VERIFY = "verify"
    CHOICES = [(OFF, "off"), (ON, "on"), (VERIFY, "verify")]


class ZFSCanmountChoices(ChoiceSet):
    ON = "on"
    OFF = "off"
    NOAUTO = "noauto"
    CHOICES = [(ON, "on"), (OFF, "off"), (NOAUTO, "noauto")]


class ZFSEncryptionChoices(ChoiceSet):
    OFF = "off"
    ON = "on"
    AES_256_GCM = "aes-256-gcm"
    AES_192_GCM = "aes-192-gcm"
    AES_128_GCM = "aes-128-gcm"
    AES_256_CCM = "aes-256-ccm"
    AES_192_CCM = "aes-192-ccm"
    AES_128_CCM = "aes-128-ccm"
    CHOICES = [
        (OFF, "off"),
        (ON, "on (default)"),
        (AES_256_GCM, "aes-256-gcm"),
        (AES_192_GCM, "aes-192-gcm"),
        (AES_128_GCM, "aes-128-gcm"),
        (AES_256_CCM, "aes-256-ccm"),
        (AES_192_CCM, "aes-192-ccm"),
        (AES_128_CCM, "aes-128-ccm"),
    ]


class ZFSKeyformatChoices(ChoiceSet):
    PASSPHRASE = "passphrase"
    RAW = "raw"
    HEX = "hex"
    CHOICES = [(PASSPHRASE, "passphrase"), (RAW, "raw"), (HEX, "hex")]


class ZFSChecksumChoices(ChoiceSet):
    CHOICES = [
        ("on", "on"), ("off", "off"), ("fletcher2", "fletcher2"), ("fletcher4", "fletcher4"),
        ("sha256", "sha256"), ("noparity", "noparity"), ("sha512", "sha512"), ("skein", "skein"),
        ("edonr", "edonr"), ("blake3", "blake3"),
    ]


class ZFSXattrChoices(ChoiceSet):
    """`xattr` storage style. `sa` = system-attribute (preferred on Linux); `dir` = `on`."""

    CHOICES = [("on", "on"), ("off", "off"), ("sa", "sa"), ("dir", "dir")]


class ZFSAclTypeChoices(ChoiceSet):
    CHOICES = [("off", "off"), ("nfsv4", "nfsv4"), ("posix", "posix")]


class ZFSAclInheritChoices(ChoiceSet):
    CHOICES = [
        ("discard", "discard"), ("noallow", "noallow"), ("restricted", "restricted"),
        ("passthrough", "passthrough"), ("passthrough-x", "passthrough-x"),
    ]


class ZFSAclModeChoices(ChoiceSet):
    CHOICES = [
        ("discard", "discard"), ("groupmask", "groupmask"), ("passthrough", "passthrough"),
        ("restricted", "restricted"),
    ]


class ZFSSyncChoices(ChoiceSet):
    CHOICES = [("standard", "standard"), ("always", "always"), ("disabled", "disabled")]


class ZFSLogbiasChoices(ChoiceSet):
    CHOICES = [("latency", "latency"), ("throughput", "throughput")]


class ZFSSnapdirChoices(ChoiceSet):
    """`snapdir` (filesystem) and `snapdev` (volume) share the hidden/visible tokens."""

    CHOICES = [("hidden", "hidden"), ("visible", "visible")]


class ZFSCacheChoices(ChoiceSet):
    """`primarycache` / `secondarycache` (ARC / L2ARC) caching policy."""

    CHOICES = [("all", "all"), ("none", "none"), ("metadata", "metadata")]


class ZFSRedundantMetadataChoices(ChoiceSet):
    CHOICES = [("all", "all"), ("most", "most"), ("some", "some"), ("none", "none")]


class ZFSDnodeSizeChoices(ChoiceSet):
    CHOICES = [
        ("legacy", "legacy"), ("auto", "auto"), ("1k", "1k"), ("2k", "2k"),
        ("4k", "4k"), ("8k", "8k"), ("16k", "16k"),
    ]


class ZFSCasesensitivityChoices(ChoiceSet):
    """Create-time only; immutable afterwards."""

    CHOICES = [("sensitive", "sensitive"), ("insensitive", "insensitive"), ("mixed", "mixed")]


class ZFSNormalizationChoices(ChoiceSet):
    """Create-time only; immutable afterwards."""

    CHOICES = [
        ("none", "none"), ("formC", "formC"), ("formD", "formD"),
        ("formKC", "formKC"), ("formKD", "formKD"),
    ]


class ZFSVolModeChoices(ChoiceSet):
    CHOICES = [
        ("default", "default"), ("full", "full"), ("geom", "geom"),
        ("dev", "dev"), ("none", "none"),
    ]
