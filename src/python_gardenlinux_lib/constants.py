#!/usr/bin/env python3

# It is important that this list is sorted in descending length of the entries
GL_MEDIA_TYPES = [
    "gcpimage.tar.gz.log",
    "firecracker.tar.gz",
    "platform.test.log",
    "platform.test.xml",
    "gcpimage.tar.gz",
    "chroot.test.log",
    "chroot.test.xml",
    "pxe.tar.gz.log",
    "root.squashfs",
    "manifest.log",
    "release.log",
    "pxe.tar.gz",
    "qcow2.log",
    "test-log",
    "boot.efi",
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
    "initrd": "application/io.gardenlinux.initrd",
    "root.squashfs": "application/io.gardenlinux.squashfs",
    "boot.efi": "application/io.gardenlinux.efi",
    "platform.test.log": "application/io.gardenlinux.io.platform.test.log",
    "platform.test.xml": "application/io.gardenlinux.io.platform.test.xml",
    "chroot.test.log": "application/io.gardenlinux.io.chroot.test.log",
    "chroot.test.xml": "application/io.gardenlinux.io.chroot.test.xml",
    "oci.log": "application/io.gardenlinux.log",
}
