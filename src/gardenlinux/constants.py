# -*- coding: utf-8 -*-

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
    "gcpimage.tar.gz.log",
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
    "pxe.tar.gz.log",
    "root.squashfs",
    "manifest.log",
    "squashfs.log",
    "release.log",
    "vmlinuz.log",
    "initrd.log",
    "pxe.tar.gz",
    "qcow2.log",
    "test-log",
    "squashfs",
    "manifest",
    "vmdk.log",
    "tar.log",
    "uki.log",
    "vmlinuz",
    "release",
    "vhd.log",
    "ova.log",
    "raw.log",
    "oci.log",
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
]

GL_MEDIA_TYPE_LOOKUP = {
    "tar": "application/io.gardenlinux.image.archive.format.tar",
    "tar.gz": "application/io.gardenlinux.image.archive.format.tar.gz",
    "pxe.tar.gz": "application/io.gardenlinux.image.archive.format.pxe.tar.gz",
    "iso": "application/io.gardenlinux.image.archive.format.iso",
    "oci": "application/io.gardenlinux.image.archive.format.oci",
    "firecracker.tar.gz": "application/io.gardenlinux.image.archive.format.firecracker.tar.gz",
    "qcow2": "application/io.gardenlinux.image.format.qcow2",
    "vhd": "application/io.gardenlinux.image.format.vhd",
    "gcpimage.tar.gz": "application/io.gardenlinux.image.format.gcpimage.tar.gz",
    "vmdk": "application/io.gardenlinux.image.format.vmdk",
    "ova": "application/io.gardenlinux.image.format.ova",
    "efi": "application/io.gardenlinux.efi",
    "uki": "application/io.gardenlinux.uki",
    "uki.log": "application/io.gardenlinux.log",
    "raw": "application/io.gardenlinux.image.archive.format.raw",
    "manifest.log": "application/io.gardenlinux.log",
    "release.log": "application/io.gardenlinux.log",
    "test-log": "application/io.gardenlinux.test-log",
    "manifest": "application/io.gardenlinux.manifest",
    "tar.log": "application/io.gardenlinux.log",
    "release": "application/io.gardenlinux.release",
    "raw.log": "application/io.gardenlinux.log",
    "qcow2.log": "application/io.gardenlinux.log",
    "pxe.tar.gz.log": "application/io.gardenlinux.log",
    "gcpimage.tar.gz.log": "application/io.gardenlinux.log",
    "vmdk.log": "application/io.gardenlinux.log",
    "vhd.log": "application/io.gardenlinux.log",
    "ova.log": "application/io.gardenlinux.log",
    "vmlinuz": "application/io.gardenlinux.kernel",
    "vmlinuz.log": "application/io.gardenlinux.log",
    "initrd": "application/io.gardenlinux.initrd",
    "initrd.log": "application/io.gardenlinux.log",
    "initrd.unified": "application/io.gardenlinux.initrd",
    "root.squashfs": "application/io.gardenlinux.squashfs",
    "squashfs": "application/io.gardenlinux.squashfs",
    "squashfs.log": "application/io.gardenlinux.log",
    "platform.test.log": "application/io.gardenlinux.io.platform.test.log",
    "platform.test.xml": "application/io.gardenlinux.io.platform.test.xml",
    "chroot.test.log": "application/io.gardenlinux.io.chroot.test.log",
    "chroot.test.xml": "application/io.gardenlinux.io.chroot.test.xml",
    "oci.log": "application/io.gardenlinux.log",
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

OCI_ANNOTATION_SIGNATURE_KEY = "io.gardenlinux.oci.signature"
OCI_ANNOTATION_SIGNED_STRING_KEY = "io.gardenlinux.oci.signed-string"
OCI_IMAGE_INDEX_MEDIA_TYPE = "application/vnd.oci.image.index.v1+json"
