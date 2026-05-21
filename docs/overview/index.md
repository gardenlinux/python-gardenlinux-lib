---
title: "Python Library"
description: An overview of the Garden Linux Python Library
related_topics:
  - /reference/supporting_tools/python-gardenlinux-lib
  - /reference/python-gardenlinux-lib-cli
  - /how-to/python-gardenlinux-lib-release
migration_status: "done"
migration_stakeholder: "@tmangold, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: python-gardenlinux-lib
github_source_path: docs/overview/index.md
github_target_path: "docs/reference/supporting_tools/python-gardenlinux-lib.md"
---

# Garden Linux Python Library Documentation

Welcome to the Garden Linux Python Library documentation. This library provides
Python tools and utilities for working with Garden Linux features, flavors, OCI
artifacts, S3 buckets, and GitHub releases.

## Overview

The Garden Linux Python Library is a comprehensive toolkit for managing and
interacting with Garden Linux components. It includes:

- **Feature Management**: Parse and work with Garden Linux features and generate
  canonical names
- **Flavor Processing**: Parse flavors.yaml and generate combinations
- **OCI Operations**: Push OCI artifacts to registries and manage manifests
- **S3 Integration**: Upload and download artifacts from S3 buckets
- **GitHub Integration**: Create and manage GitHub releases with release notes

## Installation

### Using `poetry` (from Git)

Add the library as a dependency in your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
gardenlinux = { git = "https://github.com/gardenlinux/python-gardenlinux-lib", rev = "0.10.5" }
```

Then install:

```bash
poetry install
```

### Local development setup

```bash
git clone https://github.com/gardenlinux/python-gardenlinux-lib.git
cd python-gardenlinux-lib
python -m venv venv
source venv/bin/activate
poetry install
```

## Quickstart

### Example: list features for a given `cname`

```python
from gardenlinux.features import Parser

cname = "aws-gardener_prod"
feature_list = Parser().filter_as_list(cname)

print(f"features of {cname}:")
for feature in feature_list:
    print(feature)
```

For more examples and for all CLI tools, see the **Command-Line Interface** and
**API Reference** sections in the docs:
[https://gardenlinux.github.io/python-gardenlinux-lib/](https://gardenlinux.github.io/python-gardenlinux-lib/)

## Quick Start

### Command-Line Interface

The library provides several command-line tools for common operations. See the
[Command-Line Interface documentation](/reference/python-gardenlinux-lib-cli.md)
for detailed information about all available commands.

### Release Management

For information about versioning and release procedures, see the
[Release documentation](/how-to/python-gardenlinux-lib-release.md).

### API Reference

For detailed Python API documentation, including all modules, classes, and
functions, see the
[API Reference on ReadTheDocs](https://gardenlinux.github.io/python-gardenlinux-lib/api.html).

## Related Topics

<RelatedTopics />
