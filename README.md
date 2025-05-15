![poetry build](https://github.com/gardenlinux/parse_features_lib/actions/workflows/build.yml/badge.svg)
![Black Lint](https://github.com/gardenlinux/parse_features_lib/actions/workflows/black.yml/badge.svg)
![Test](https://github.com/gardenlinux/parse_features_lib/actions/workflows/pytests.yml/badge.svg)
![security check](https://github.com/gardenlinux/parse_features_lib/actions/workflows/bandit.yml/badge.svg)

# Parse features lib

This library includes tooling to build and distribute [Garden Linux](https://github.com/gardenlinux/gardenlinux).

Features:

-   compare APT repositories
-   parse features
-   parse flavors
-   push OCI artifacts to a registry

## Quickstart

### Example: parse features

**Inclusion via poetry**:

`python_gardenlinux_lib = { git  = "https://github.com/gardenlinux/python_gardenlinux_lib", rev="0.6.0" }`

```python
from python_gardenlinux_lib.parse_features import read_feature_files, filter_graph

if __name__ == "__main__":
    # Step 1: parse the "features directory" and get the full graph containing all features
    all_features = parse_features.read_feature_files("features")

    # Step 2: supply desired features and get all their dependencies
    dependencies = parse_features.filter_graph(all_features, {"gardener", "_prod", "server", "ociExample"})

    # Step 3: play with the retrieved data.
    for feature, info in dependencies.nodes(data="content"):
        if "oci_artifacts" in info:
            print(feature, info["oci_artifacts"])
```

## Developer Documentation

The library is documented with docstrings, which are used to generate the developer documentation available [here](https://gardenlinux.github.io/python-gardenlinux-lib/).

## Push OCI artifacts to a registry

this tool helps you to push oci artifacts.

### Installation

```bash
git clone https://github.com/gardenlinux/python-gardenlinux-lib.git
mkdir venv
python -m venv venv
source venv/bin/activate.sh
poetry install
gl-oci --help
```

### Usage

The process to push a Gardenlinux build-output folder to an OCI registry is split into two steps: In the first step all files are pushed to the registry and a manifest that includes all those pushed files (layers) is created and pushed as well. An index entry that links to this manifest is created offline and written to a local file but not pushed to any index. This push to an index can be done in the second step where the local file containing the index entry is read and pushed to an index. The seperation into two steps was done because pushing of manifests takes long and writes to dedicated resources (possible to run in parallel). Updating the index on the other hand is quick but writes to a share resource (not possible to run in parallel). By splitting the process up into two steps it is possible to run the slow part in parallel and the quick part sequentially.

#### 1. Push layers + manifest

To push layers you have to supply the directory with the build outputs `--dir`. Also you have to supply cname (`--cname`), architecture `--arch` and version `--version` of the build. This information will be included in the manifest. You have to supply an endpoint where the artifacts shall be pushed to `--container`, for example `ghcr.io/gardenlinux/gardenlinux`. You can disable enforced HTTPS connections to your registry with `--insecure True`. You can supply `--cosign_file <filename>` if you want to have the hash saved in `<filename>`. This can be handy to read the hash later to sign the manifest with cosign. With `--manifest_file <filename>` you tell the program in which file to store the manifests index entry. This is the file that can be used in the next step to update the index. You can use the environment variable GL_CLI_REGISTRY_TOKEN to authenticate against the registry. Below is an example of a full program call of `push-manifest`

```bash
GL_CLI_REGISTRY_TOKEN=asdf123 gl-oci push-manifest --dir build-metal-gardener_prod --container ghcr.io/gardenlinux/gl-oci --arch amd64 --version 1592.1 --cname metal-gardener_prod --cosign_file digest --manifest_file oci_manifest_entry_metal.json
```

#### 2. Update index with manifest entry

Parameters that are the same as for `push-manifest`:

-   env-var `GL_CLI_REGISTRY_TOKEN`
-   `--version`
-   `--container`
-   `--manifest-file` this time this parameter adjusts the manifest entry file to be read from instead of being written to

A full example looks like this:

```bash
GL_CLI_REGISTRY_TOKEN=asdf123 gl-oci update-index --container ghcr.io/gardenlinux/gl-oci --version 1592.1 --manifest_file oci_manifest_entry_metal.json
```
