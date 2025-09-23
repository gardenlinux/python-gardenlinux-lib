#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-features-parse main entrypoint
"""

import argparse
import logging
import os
import re
import sys
from functools import reduce
from os import path
from typing import Any, List, Set

from .cname import CName
from .parser import Parser

_ARGS_TYPE_ALLOWED = [
    "cname",
    "cname_base",
    "commit_id",
    "features",
    "platforms",
    "flags",
    "elements",
    "arch",
    "version",
    "version_and_commit_id",
    "graph",
]


def main() -> None:
    """
    gl-features-parse main()

    :since: 0.7.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--cname", dest="cname")
    parser.add_argument("--commit", dest="commit")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--default-arch", dest="default_arch")
    parser.add_argument("--default-version", dest="default_version")
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

    arch = args.arch
    flavor = None
    commit_id = args.commit
    gardenlinux_root = path.dirname(args.feature_dir)
    version = args.version

    if arch is None or arch == "":
        arch = args.default_arch

    if gardenlinux_root == "":
        gardenlinux_root = "."

    if version is None or version == "":
        try:
            version, commit_id = get_version_and_commit_id_from_files(gardenlinux_root)
        except RuntimeError as exc:
            logging.debug(
                "Failed to parse version information for GL root '{0}': {1}".format(
                    gardenlinux_root, exc
                )
            )

            version = args.default_version

    if args.cname:
        cname = CName(args.cname, arch=arch, commit_id=commit_id, version=version)

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

    if (
        version is None
        or version == ""
        and (args.type in ("cname", "commit_id", "version", "version_and_commit_id"))
    ):
        raise RuntimeError("Version not specified and no default version set")

    feature_dir_name = path.basename(args.feature_dir)

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
    elif args.type == "commit_id":
        print(commit_id)
    elif args.type == "version":
        print(version)
    elif args.type == "version_and_commit_id":
        print(f"{version}-{commit_id}")


def get_cname_base(sorted_features: Set[str]):
    """
    Get the base cname for the feature set given.

    :param sorted_features: Sorted feature set

    :return: (str) Base cname
    :since: 0.7.0
    """

    return reduce(
        lambda a, b: a + ("-" if not b.startswith("_") else "") + b, sorted_features
    )


def get_version_and_commit_id_from_files(gardenlinux_root: str) -> tuple[str, str]:
    """
    Returns the version and commit ID based on files in the GardenLinux root directory.

    :param gardenlinux_root: GardenLinux root directory

    :return: (tuple) Version and commit ID if readable
    :since:  0.7.0
    """

    commit_id = None
    version = None

    if os.access(path.join(gardenlinux_root, "COMMIT"), os.R_OK):
        with open(path.join(gardenlinux_root, "COMMIT"), "r") as fp:
            commit_id = fp.read().strip()[:8]

    if os.access(path.join(gardenlinux_root, "VERSION"), os.R_OK):
        with open(path.join(gardenlinux_root, "VERSION"), "r") as fp:
            version = fp.read().strip()

    if commit_id is None or version is None:
        raise RuntimeError("Failed to read version or commit ID from files")

    return (version, commit_id)


def get_minimal_feature_set(graph: Any) -> Set[str]:
    """
    Returns the minimal set of features described by the given graph.

    :param graph: networkx.Digraph

    :return: (set) Minimal set of features
    :since:  0.7.0
    """

    return set([node for (node, degree) in graph.in_degree() if degree == 0])


def graph_as_mermaid_markup(flavor: str, graph: Any) -> str:
    """
    Generates a mermaid.js representation of the graph.
    This is helpful to identify dependencies between features.

    Syntax docs:
    https://mermaid.js.org/syntax/flowchart.html?id=flowcharts-basic-syntax

    :param flavor: Flavor name
    :param graph:  networkx.Digraph

    :return: (str) mermaid.js representation
    :since:  0.7.0
    """

    markup = f"---\ntitle: Dependency Graph for Feature {flavor}\n---\ngraph TD;\n"

    for u, v in graph.edges:
        markup += f"    {u}-->{v};\n"

    return markup


def sort_subset(input_set: Set[str], order_list: List[str]) -> List[str]:
    """
    Returns items from `order_list` if given in `input_set`.

    :param input_set:  Set of values
    :param order_list: networkx.Digraph

    :return: (str) mermaid.js representation
    :since:  0.7.0
    """

    return [item for item in order_list if item in input_set]


if __name__ == "__main__":
    main()
