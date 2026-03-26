# Command-Line Interface

This page documents all available command-line tools provided by
python-gardenlinux-lib. Run `command --help` for detailed usage information.

## Features Commands

### gl-cname

Generate a canonical name (cname) from feature sets.

```bash
gl-cname [options]
```

### gl-features-parse

Parse and extract information from GardenLinux features.

```bash
gl-features-parse [options]
```

## Flavors Commands

### gl-flavors-parse

Parse flavors.yaml and generate combinations.

```bash
gl-flavors-parse [options]
```

## OCI Commands

### gl-oci

Push OCI artifacts to a registry and manage manifests.

```bash
gl-oci [command] [options]
```

Commands:

- `push` - Push OCI artifacts to a registry
- `manifest` - Manage OCI manifests

## S3 Commands

### gl-s3

Upload and download artifacts from S3 buckets.

```bash
gl-s3 [command] [options]
```

Commands:

- `upload` - Upload artifacts to S3
- `download` - Download artifacts from S3

## GitHub Commands

### gl-gh-release

Create and manage GitHub releases.

```bash
gl-gh-release [command] [options]
```

Commands:

- `create` - Create a new release
- `update` - Update an existing release
- `list` - List all releases
