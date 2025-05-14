#!/usr/bin/env python3

from .features import parse_features

from functools import reduce
from os.path import basename, dirname

import argparse
import re


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--version", dest="version")
    parser.add_argument("cname")

    args = parser.parse_args()

    re_match = re.match(
        "([a-zA-Z0-9]+(-[a-zA-Z0-9\\_\\-]*?)?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
        args.cname,
    )

    assert re_match, f"not a valid cname {args.cname}"

    if re_match.lastindex == 1:
        cname_base, arch = re_match[1].split("-", 1)
        commit_id = None
        version = None
    else:
        arch = re_match[4]
        cname_base = re_match[1]
        commit_id = re_match[7]
        version = re_match[6]

    if args.arch is not None:
        arch = args.arch

    if args.version is not None:
        re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", args.cname)
        assert re_match, f"not a valid version {args.version}"

        commit_id = re_match[3]
        version = re_match[1]

    gardenlinux_root = dirname(args.feature_dir)
    feature_dir_name = basename(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    graph = parse_features.get_features_graph(
        cname_base, gardenlinux_root, feature_dir_name
    )

    sorted_features = parse_features.sort_nodes(graph)

    minimal_feature_set = get_minimal_feature_set(graph)

    sorted_minimal_features = parse_features.sort_set(
        minimal_feature_set, sorted_features
    )

    cname_base = get_cname_base(sorted_minimal_features)

    cname = f"{cname_base}-{arch}"
    if commit_id is not None:
        cname += f"-{version}-{commit_id}"

    print(cname)


def get_cname_base(sorted_features):
    return reduce(
        lambda a, b: a + ("-" if not b.startswith("_") else "") + b, sorted_features
    )


def get_minimal_feature_set(graph):
    return set([node for (node, degree) in graph.in_degree() if degree == 0])


def get_flavor_from_cname(cname: str, get_arch: bool = True) -> str:
    """
    Extracts the flavor from a canonical name.

    :param str cname: Canonical name of an image
    :param bool get_arch: Whether to include the architecture in the flavor
    :return: Flavor string
    """

    # cname:
    # azure-gardener_prod_tpm2_trustedboot-amd64-1312.2-80ffcc87
    # transform to flavor:
    # azure-gardener_prod_tpm2_trustedboot-amd64

    platform = cname.split("-")[0]
    features = cname.split("-")[1:-1]
    arch = cname.split("-")[-1]

    if get_arch:
        return f"{platform}-{features}-{arch}"
    else:
        return f"{platform}-{features}"


if __name__ == "__main__":
    main()
