# -*- coding: utf-8 -*-

GL_RELEASE_CVE_PLACEHOLDER = """
The following packages have been upgraded, to address the mentioned CVEs:
**todo release facilitator: fill this in**
""".strip()

GL_RELEASE_CHARACTERS_LIMIT = 125000

GL_RELEASE_MAJOR_TEMPLATE = """# Software Component Versions

```
$components_versions
```

# Published images

| Variant | Platform | Architecture | Flavor | Regions | Download Links |
|---------|----------|--------------|--------|---------|----------------|
$published_images_table

## Kernel Module Build Container (kmodbuild)

```
$kmodbuild_registry_url
```
"""

GL_RELEASE_MINOR_TEMPLATE = """# Changes

$changes

## Software Component Versions

```
$components_versions
```

## Changes in Package Versions compared to $previous_release_version

$compared_package_versions_table

# Published images

| Variant | Platform | Architecture | Flavor | Regions | Download Links |
|---------|----------|--------------|--------|---------|----------------|
$published_images_table

## Kernel Module Build Container (kmodbuild)

```
$kmodbuild_registry_url
```
"""

HIGHLIGHT_PACKAGES = [
    "linux-image-amd64",
    # "linux-image-arm64", @TODO: ReleaseImagesMetadata downloads binary-amd64
    "systemd",
    "containerd",
    "runc",
    "curl",
    "openssl",
    "openssh-server",
    "libc-bin",
]

IMAGE_VARIANTS = {
    "legacy": "Default",
    "usi": "USI (Unified System Image)",
    "trustedboot": "TPM2 Trusted Boot",
}
