# Parse features lib
This library helps you to work with the gardenlinux/features folder. It parses all info.yamls and builds a tree.

Features (planned):
* validate CNAMEs
* validate info.yamls
* Deduct dependencies from cname_base

## Quickstart
**Inclusion via poetry**:

`parse_features_lib = { git  = "https://github.com/gardenlinux/parse_features_lib", rev="main" }`
```python
import parse_features_lib

if __name__ == "__main__":
    # Step 1: parse the "features directory" and get the full graph containing all features
    all_features = parse_features_lib.read_feature_files("features")

    # Step 2: supply desired features and get all their dependencies
    dependencies = parse_features_lib.filter_graph(all_features, {"gardener", "_prod", "server", "ociExample"})

    # Step 3: play with the retrieved data.
    for feature, info in dependencies.nodes(data="content"):
        if "oci_artifacts" in info:
            print(feature, info["oci_artifacts"])
```