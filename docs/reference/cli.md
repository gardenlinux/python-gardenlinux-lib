---
title: Command-Line Interface - Python Library
description: Command-Line Interface of the Garden Linux Python Library
related_topics:
  - /reference/supporting_tools/python-gardenlinux-lib.md
  - /reference/python-gardenlinux-lib-cli.md
  - /how-to/python-gardenlinux-lib-release.md
migration_status: "new"
migration_source: ""
migration_issue: ""
migration_stakeholder: "@tmangold, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: python-gardenlinux-lib
github_source_path: docs/reference/cli.md
github_target_path: docs/reference/python-gardenlinux-lib-cli.md
---

# Documentation

_python-gardenlinux-lib_ strictly follows the syntax and intention of
[Semantic Versioning](https://www.semver.org). Each release reflects the
intention and expected impact therefore.

A new release is done by tagging a commit with a valid version. This will create
a GitHub pre-release for proof-reading. Once done a new release can be published
using GitHub CLI or UI.

Newly added docstrings should contain the first version supporting the new API /
command line.

## Step by Step Guide

1. **Set version files:**

   _python-gardenlinux-lib_ versioning needs to be set in:
   - `pyproject.toml`
   - `.github/actions/setup/action.yml`

   Additionally at the moment (removal pending):
   - `.github/actions/features_parse/action.yml`
   - `.github/actions/flavors_parse/action.yml`

2. **Create git tag:**

   ```bash
   git tag <tag>
   ```

3. **Review and publish:**

   Review the generated pre-release changelog by visiting the GitHub project
   release page and publish it if applicable.

4. **Consume the library:**

   Projects consuming the _python-gardenlinux-lib_ may use the following git URL
   for dependency definition:

   ```bash
   pip install git+https://github.com/gardenlinux/python-gardenlinux-lib.git@1.0.0
   ```

   Or in `requirements.txt`:

   ```
   gardenlinux @ git+https://github.com/gardenlinux/python-gardenlinux-lib.git@1.0.0
   ```

## Related Topics

<RelatedTopics />
