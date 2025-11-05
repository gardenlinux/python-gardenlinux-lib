import os
from pathlib import Path

ARCHS = ["amd64", "arm64"]

# GardenLinux "bare" feature
BARE_FLAVOR_FEATURE_CONTENT = {"description": "Bare flavor", "type": "platform"}

BARE_FLAVOR_LIBC_FEATURE_CONTENT = {
    "description": "Bare libc feature",
    "type": "element",
}

# GardenLinux flavors schema for validation
GL_FLAVORS_SCHEMA = {
    "type": "object",
    "version": {"type": "integer"},
    "properties": {
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "flavors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "features": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "arch": {"type": "string"},
                                "build": {"type": "boolean"},
                                "test": {"type": "boolean"},
                                "test-platform": {"type": "boolean"},
                                "publish": {"type": "boolean"},
                            },
                            "required": [
                                "features",
                                "arch",
                                "build",
                                "test",
                                "test-platform",
                                "publish",
                            ],
                        },
                    },
                },
                "required": ["name", "category", "flavors"],
            },
        },
    },
    "required": ["targets"],
}

# It is important that this list is sorted in descending length of the entries
GL_MEDIA_TYPES = [
    "secureboot.aws-efivars",
    "secureboot.kek.auth",
    "secureboot.pk.auth",
    "secureboot.kek.crt",
    "secureboot.kek.der",
    "secureboot.db.auth",
    "firecracker.tar.gz",
    "secureboot.pk.crt",
    "secureboot.pk.der",
    "secureboot.db.crt",
    "secureboot.db.der",
    "secureboot.db.arn",
    "platform.test.log",
    "platform.test.xml",
    "gcpimage.tar.gz",
    "chroot.test.log",
    "chroot.test.xml",
    "initrd.unified",
    "root.squashfs",
    "requirements",
    "pxe.tar.gz",
    "test-log",
    "squashfs",
    "manifest",
    "vmlinuz",
    "cmdline",
    "release",
    "initrd",
    "tar.gz",
    "qcow2",
    "tar",
    "iso",
    "oci",
    "vhd",
    "vmdk",
    "ova",
    "efi",
    "uki",
    "raw",
    "log",
]

GL_MEDIA_TYPE_LOOKUP = {
    "tar": "application/io.gardenlinux.image.archive.format.tar",
    "tar.gz": "application/io.gardenlinux.image.archive.format.tar.gz",
    "log": "application/io.gardenlinux.log",
    "pxe.tar.gz": "application/io.gardenlinux.image.archive.format.pxe.tar.gz",
    "iso": "application/io.gardenlinux.image.archive.format.iso",
    "oci": "application/io.gardenlinux.image.archive.format.oci",
    "firecracker.tar.gz": "application/io.gardenlinux.image.archive.format.firecracker.tar.gz",
    "qcow2": "application/io.gardenlinux.image.format.qcow2",
    "vhd": "application/io.gardenlinux.image.format.vhd",
    "gcpimage.tar.gz": "application/io.gardenlinux.image.format.gcpimage.tar.gz",
    "vmdk": "application/io.gardenlinux.image.format.vmdk",
    "ova": "application/io.gardenlinux.image.format.ova",
    "requirements": "application/io.gardenlinux.image.requirements",
    "efi": "application/io.gardenlinux.efi",
    "uki": "application/io.gardenlinux.uki",
    "raw": "application/io.gardenlinux.image.archive.format.raw",
    "test-log": "application/io.gardenlinux.test-log",
    "manifest": "application/io.gardenlinux.manifest",
    "release": "application/io.gardenlinux.release",
    "vmlinuz": "application/io.gardenlinux.kernel",
    "initrd": "application/io.gardenlinux.initrd",
    "cmdline": "application/io.gardenlinux.cmdline",
    "initrd.unified": "application/io.gardenlinux.initrd",
    "root.squashfs": "application/io.gardenlinux.squashfs",
    "squashfs": "application/io.gardenlinux.squashfs",
    "platform.test.log": "application/io.gardenlinux.io.platform.test.log",
    "platform.test.xml": "application/io.gardenlinux.io.platform.test.xml",
    "chroot.test.log": "application/io.gardenlinux.io.chroot.test.log",
    "chroot.test.xml": "application/io.gardenlinux.io.chroot.test.xml",
    "secureboot.pk.crt": "application/io.gardenlinux.cert.secureboot.pk.crt",
    "secureboot.pk.der": "application/io.gardenlinux.cert.secureboot.pk.der",
    "secureboot.pk.auth": "application/io.gardenlinux.cert.secureboot.pk.auth",
    "secureboot.kek.crt": "application/io.gardenlinux.cert.secureboot.kek.crt",
    "secureboot.kek.der": "application/io.gardenlinux.cert.secureboot.kek.der",
    "secureboot.kek.auth": "application/io.gardenlinux.cert.secureboot.kek.auth",
    "secureboot.db.crt": "application/io.gardenlinux.cert.secureboot.db.crt",
    "secureboot.db.der": "application/io.gardenlinux.cert.secureboot.db.der",
    "secureboot.db.auth": "application/io.gardenlinux.cert.secureboot.db.auth",
    "secureboot.db.arn": "application/io.gardenlinux.cert.secureboot.db.arn",
    "secureboot.aws-efivars": "application/io.gardenlinux.cert.secureboot.aws-efivars",
}

GL_BUG_REPORT_URL = "https://github.com/gardenlinux/gardenlinux/issues"
GL_COMMIT_SPECIAL_VALUES = ("local",)
GL_DISTRIBUTION_NAME = "Garden Linux"
GL_HOME_URL = "https://gardenlinux.io"
GL_RELEASE_ID = "gardenlinux"
GL_REPOSITORY_URL = "https://github.com/gardenlinux/gardenlinux"
GL_SUPPORT_URL = "https://github.com/gardenlinux/gardenlinux"

OCI_ANNOTATION_SIGNATURE_KEY = "io.gardenlinux.oci.signature"
OCI_ANNOTATION_SIGNED_STRING_KEY = "io.gardenlinux.oci.signed-string"
OCI_IMAGE_INDEX_MEDIA_TYPE = "application/vnd.oci.image.index.v1+json"

RELEASE_ID_FILE = ".github_release_id"

REQUESTS_TIMEOUTS = (5, 30)  # connect, read

S3_DOWNLOADS_DIR = Path(os.path.dirname(__file__)) / ".." / "s3_downloads"

GLVD_BASE_URL = (
    "https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1"
)
GL_DEB_REPO_BASE_URL = "https://packages.gardenlinux.io/gardenlinux"

GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME = "gardenlinux-github-releases"

# https://github.com/gardenlinux/gardenlinux/issues/3044
# Empty string is the 'legacy' variant with traditional root fs and still needed/supported
IMAGE_VARIANTS = ["", "_usi", "_tpm2_trustedboot"]
