# -*- coding: utf-8 -*-

RELEASE_DATA = """
GARDENLINUX_CNAME="container_trustedboot_usi-amd64-1234.1"
GARDENLINUX_VERSION=1234.1
GARDENLINUX_COMMIT_ID="abc123lo"
GARDENLINUX_COMMIT_ID_LONG="abc123long"
GARDENLINUX_PLATFORM="container"
GARDENLINUX_FEATURES="_usi,_trustedboot"
GARDENLINUX_FEATURES_ELEMENTS=
GARDENLINUX_FEATURES_FLAGS="_usi,_trustedboot"
GARDENLINUX_FEATURES_PLATFORMS="container"
"""

S3_METADATA = """
platform: container
architecture: amd64
base_image: null
build_committish: abc123lo
build_timestamp: {build_timestamp}
logs: null
modifiers:
- _ephemeral
- _slim
- base
- container
- _usi
- _trustedboot
require_uefi: true
secureboot: true
published_image_metadata: null
s3_bucket: test-bucket
s3_key: meta/singles/container_trustedboot_usi-amd64-1234.1-abc123lo
test_result: null
version: '1234.1'
paths:
- name: container_trustedboot_usi-amd64-1234.1-abc123lo.release
  s3_bucket_name: test-bucket
  s3_key: objects/container_trustedboot_usi-amd64-1234.1-abc123lo/container_trustedboot_usi-amd64-1234.1-abc123lo.release
  suffix: .release
  md5sum: {md5sum}
  sha256sum: {sha256sum}
gardenlinux_epoch: 1234
""".strip()
