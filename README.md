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

You can find our full documentation for this python library on our
[Documentation Hub](https://gardenlinux-docs.netlify.app/reference/supporting_tools/python-gardenlinux-lib.html).

For a detailed API documentation, check
[gardenlinux.github.io/python-gardenlinux-lib/api.html](https://gardenlinux.github.io/python-gardenlinux-lib/)

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

<p align="center">
  <img alt="Bundesministerium für Wirtschaft und Energie (BMWE)-EU funding logo" src="https://apeirora.eu/assets/img/BMWK-EU.png" width="400"/>
</p>
