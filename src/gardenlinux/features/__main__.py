#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .cname import CName
from .parser import Parser

from functools import reduce
from os import path
import argparse
import os
import re
import sys


_ARGS_TYPE_ALLOWED = [
    "cname",
    "cname_base",
    "features",
    "platforms",
    "flags",
    "elements",
    "arch",
    "version",
    "graph",
]


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--cname")
    parser.add_argument("--default-arch")
    parser.add_argument("--default-version")
    parser.add_argument("--version", dest="version")

    parser.add_argument(
        "--features", type=lambda arg: set([f for f in arg.split(",") if f])
    )

    parser.add_argument(
        "--ignore",
        dest="ignore",
        type=lambda arg: set([f for f in arg.split(",") if f]),
        default=set(),
    )

    parser.add_argument("type", nargs="?", choices=_ARGS_TYPE_ALLOWED, default="cname")

    args = parser.parse_args()

    assert bool(args.features) or bool(
        args.cname
    ), "Please provide either `--features` or `--cname` argument"

    arch = None
    flavor = None
    commit_id = None
    gardenlinux_root = path.dirname(args.feature_dir)
    version = None

    if args.arch is not None:
        arch = args.arch

    if args.version is not None:
        version = args.version

    if arch is None or arch == "":
        arch = args.default_arch

    if version is None or version == "":
        version_data = get_version_and_commit_id_from_files(gardenlinux_root)
        version = f"{version_data[0]}-{version_data[1]}"

    if args.cname:
        cname = CName(args.cname, arch=arch, version=version)

        arch = cname.arch
        flavor = cname.flavor
        commit_id = cname.commit_id
        version = cname.version

        input_features = Parser.get_cname_as_feature_set(flavor)
    else:
        input_features = args.features

    if arch is None or arch == "" and (args.type in ("cname", "arch")):
        raise RuntimeError(
            "Architecture could not be determined and no default architecture set"
        )

    if version is None or version == "" and (args.type in ("cname", "version")):
        raise RuntimeError("Version not specified and no default version set")

    feature_dir_name = path.basename(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    if gardenlinux_root == "":
        gardenlinux_root = "."

    additional_filter_func = lambda node: node not in args.ignore

    if args.type == "arch":
        print(arch)
    elif args.type in ("cname_base", "cname", "graph"):
        graph = Parser(gardenlinux_root, feature_dir_name).filter(
            flavor, additional_filter_func=additional_filter_func
        )

        sorted_features = Parser.sort_graph_nodes(graph)
        minimal_feature_set = get_minimal_feature_set(graph)

        sorted_minimal_features = sort_subset(minimal_feature_set, sorted_features)

        cname_base = get_cname_base(sorted_minimal_features)

        if args.type == "cname_base":
            print(cname_base)
        elif args.type == "cname":
            cname = flavor

            if arch is not None:
                cname += f"-{arch}"

            if commit_id is not None:
                cname += f"-{version}-{commit_id}"

            print(cname)
        elif args.type == "graph":
            print(graph_as_mermaid_markup(flavor, graph))
    elif args.type == "features":
        print(
            Parser(gardenlinux_root, feature_dir_name).filter_as_string(
                flavor, additional_filter_func=additional_filter_func
            )
        )
    elif args.type in ("flags", "elements", "platforms"):
        features_by_type = Parser(gardenlinux_root, feature_dir_name).filter_as_dict(
            flavor, additional_filter_func=additional_filter_func
        )

        if args.type == "platforms":
            print(",".join(features_by_type["platform"]))
        elif args.type == "elements":
            print(",".join(features_by_type["element"]))
        elif args.type == "flags":
            print(",".join(features_by_type["flag"]))
    elif args.type == "version":
        print(f"{version}-{commit_id}")


def get_cname_base(sorted_features):
    return reduce(
        lambda a, b: a + ("-" if not b.startswith("_") else "") + b, sorted_features
    )


def get_version_and_commit_id_from_files(gardenlinux_root):
    commit_id = None
    version = None

    if os.access(path.join(gardenlinux_root, "COMMIT"), os.R_OK):
        with open(path.join(gardenlinux_root, "COMMIT"), "r") as fp:
            commit_id = fp.read().strip()[:8]

    if os.access(path.join(gardenlinux_root, "VERSION"), os.R_OK):
        with open(path.join(gardenlinux_root, "VERSION"), "r") as fp:
            version = fp.read().strip()

    return (version, commit_id)


def get_minimal_feature_set(graph):
    return set([node for (node, degree) in graph.in_degree() if degree == 0])


def graph_as_mermaid_markup(flavor, graph):
    """
    Generates a mermaid.js representation of the graph.
    This is helpful to identify dependencies between features.

    Syntax docs:
    https://mermaid.js.org/syntax/flowchart.html?id=flowcharts-basic-syntax
    """
    markup = f"---\ntitle: Dependency Graph for Feature {flavor}\n---\ngraph TD;\n"
    for u, v in graph.edges:
        markup += f"    {u}-->{v};\n"
    return markup


def sort_subset(input_set, order_list):
    return [item for item in order_list if item in input_set]


if __name__ == "__main__":
    main()
