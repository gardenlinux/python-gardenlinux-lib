## Garden Linux Python Library

![poetry build](https://github.com/gardenlinux/parse_features_lib/actions/workflows/build.yml/badge.svg)
![Black Lint](https://github.com/gardenlinux/parse_features_lib/actions/workflows/black.yml/badge.svg)
![Test](https://github.com/gardenlinux/parse_features_lib/actions/workflows/pytests.yml/badge.svg)
![security check](https://github.com/gardenlinux/parse_features_lib/actions/workflows/bandit.yml/badge.svg)

Python tooling to work with
[Garden Linux](https://github.com/gardenlinux/gardenlinux) features, flavors,
OCI artifacts, repositories, and releases. It is primarily targeted at Garden
Linux developers and CI pipelines rather than end users.

The library follows the intent of [Semantic Versioning](https://semver.org) for
its public APIs.

### Features

- **Feature management**: parse, filter, and work with Garden Linux feature sets
- **Flavor processing**: parse `flavors.yaml` and generate flavor combinations
- **Repository utilities**: compare APT repositories and query package versions
- **OCI operations**: push OCI artifacts and manifests to container registries
- **S3 integration**: upload/download artifacts from S3 buckets
- **GitHub integration**: create and manage GitHub releases

## Documentation

You can find a full documentation about how to
[install this python library](https://gardenlinux-docs.netlify.app/reference/supporting_tools/python-gardenlinux-lib.html#installation)
and
[use its CLI interface](https://gardenlinux-docs.netlify.app/reference/python-gardenlinux-lib-cli.html)
this on our [documentation hub](https://gardenlinux-docs.netlify.app/).

For a detailed API documentation, check
[gardenlinux.github.io/python-gardenlinux-lib/api.html](https://gardenlinux.github.io/python-gardenlinux-lib/)

# Community

To stay up-to-date with recent news about Gardenlinux, subscribe to our mailing
list:

https://lists.neonephos.org/g/gardenlinux-discussion

For updates and statements regarding security issues, we have a security mailing
list for you:

https://lists.neonephos.org/g/gardenlinux-security

For embargoed security related topics, this list is for you:

https://lists.neonephos.org/g/gardenlinux-security-embargo

# Contributing

We welcome your contributions to Gardenlinux or any supporting projects.

To find our more, visit our
[Contributor Documentation](https://gardenlinux-docs.netlify.app/contributing).

## Licensing

Copyright 2025 SAP SE or an SAP affiliate company and GardenLinux contributors.
Please see our [LICENSE](LICENSE.md) for copyright and license information.
Detailed information including third-party components and their
licensing/copyright information is available
[via the REUSE tool](https://reuse.software).

<p align="center">
  <img alt="Bundesministerium für Wirtschaft und Energie (BMWE)-EU funding logo" src="https://apeirora.eu/assets/img/BMWK-EU.png" width="400"/>
</p>
