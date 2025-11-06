#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-features-parse main entrypoint
"""

import argparse
import logging
import os
import re
from os import path
from typing import Any, List, Set

from .cname import CName
from .parser import Parser

_ARGS_TYPE_ALLOWED = [
    "cname",
    "cname_base",
    "container_name",
    "container_tag",
    "commit_id",
    "features",
    "platform",
    "flags",
    "flavor",
    "elements",
    "arch",
    "version",
    "version_and_commit_id",
    "graph",
]

RE_CAMEL_CASE_SPLITTER = re.compile("([A-Z]+|[a-z0-9])([A-Z])(?!$)")
"""
CamelCase splitter RegExp
"""


def main() -> None:
    """
    gl-features-parse main()

    :since: 0.7.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--cname", dest="cname", required=True)
    parser.add_argument("--commit", dest="commit")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--release-file", dest="release_file")
    parser.add_argument("--default-arch", dest="default_arch")
    parser.add_argument("--default-version", dest="default_version")
    parser.add_argument("--version", dest="version")

    parser.add_argument(
        "--ignore",
        dest="ignore",
        type=lambda arg: set([f for f in arg.split(",") if f]),
        default=set(),
    )

    parser.add_argument("type", nargs="?", choices=_ARGS_TYPE_ALLOWED, default="cname")

    args = parser.parse_args()

    assert bool(args.feature_dir) or bool(
        args.release_file
    ), "Please provide either `--feature_dir` or `--release_file` argument"

    arch = args.arch
    flavor = None
    commit_id_or_hash = args.commit
    gardenlinux_root = path.dirname(args.feature_dir)
    version = args.version

    if arch is None or arch == "":
        arch = args.default_arch

    if gardenlinux_root == "":
        gardenlinux_root = "."

    if version is None or version == "":
        try:
            version, commit_id_or_hash = get_version_and_commit_id_from_files(
                gardenlinux_root
            )
        except RuntimeError as exc:
            logging.debug(
                "Failed to parse version information for GL root '{0}': {1}".format(
                    gardenlinux_root, exc
                )
            )

            version = args.default_version

    if args.cname:
        cname = CName(
            args.cname, arch=arch, commit_hash=commit_id_or_hash, version=version
        )

        if args.release_file is not None:
            cname.load_from_release_file(args.release_file)

        arch = cname.arch
        flavor = cname.flavor
        commit_id_or_hash = cname.commit_id
        version = cname.version

    if (arch is None or arch == "") and (
        args.type in ("cname", "container_name", "arch")
    ):
        raise RuntimeError(
            "Architecture could not be determined and no default architecture set"
        )

    if (commit_id_or_hash is None or commit_id_or_hash == "") and (
        args.type in ("container_tag", "commit_id", "version_and_commit_id")
    ):
        raise RuntimeError("Commit ID not specified")

    if (version is None or version == "") and (
        args.type
        in (
            "container_tag",
            "commit_id",
            "version",
            "version_and_commit_id",
        )
    ):
        raise RuntimeError("Version not specified and no default version set")

    feature_dir_name = path.basename(args.feature_dir)

    if args.type == "arch":
        print(arch)
    elif args.type in (
        "cname_base",
        "cname",
        "container_name",
        "elements",
        "features",
        "flags",
        "flavor",
        "graph",
        "platform",
    ):
        if args.type == "graph" or len(args.ignore) > 0:
            features_parser = Parser(gardenlinux_root, feature_dir_name)

            print_output_from_features_parser(
                args.type, features_parser, flavor, args.ignore
            )
        else:
            print_output_from_cname(args.type, cname)
    elif args.type == "commit_id":
        print(commit_id_or_hash[:8])
    elif args.type == "container_tag":
        print(re.sub("\\W+", "-", f"{version}-{commit_id_or_hash[:8]}"))
    elif args.type == "version":
        print(version)
    elif args.type == "version_and_commit_id":
        print(f"{version}-{commit_id_or_hash[:8]}")


def get_version_and_commit_id_from_files(gardenlinux_root: str) -> tuple[str, str]:
    """
    Returns the version and commit ID based on files in the GardenLinux root directory.

    :param gardenlinux_root: GardenLinux root directory

    :return: (tuple) Version and commit ID if readable
    :since:  0.7.0
    """

    commit_hash = None
    version = None

    if os.access(path.join(gardenlinux_root, "COMMIT"), os.R_OK):
        with open(path.join(gardenlinux_root, "COMMIT"), "r") as fp:
            commit_hash = fp.read().strip()[:8]

    if os.access(path.join(gardenlinux_root, "VERSION"), os.R_OK):
        with open(path.join(gardenlinux_root, "VERSION"), "r") as fp:
            version = fp.read().strip()

    if commit_hash is None or version is None:
        raise RuntimeError("Failed to read version or commit ID from files")

    return (version, commit_hash)


def get_minimal_feature_set(graph: Any) -> Set[str]:
    """
    Returns the minimal set of features described by the given graph.

    :param graph: networkx.Digraph

    :return: (set) Minimal set of features
    :since:  0.7.0
    """

    return set([node for (node, degree) in graph.in_degree() if degree == 0])


def graph_as_mermaid_markup(flavor: str | None, graph: Any) -> str:
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

    if flavor is None:
        raise RuntimeError("Error while generating graph: Flavor is None!")

    markup = f"---\ntitle: Dependency Graph for Feature {flavor}\n---\ngraph TD;\n"

    for u, v in graph.edges:
        markup += f"    {u}-->{v};\n"

    return markup


def print_output_from_features_parser(
    output_type: str, parser: Parser, flavor: str, ignores_list: set
) -> None:
    """
    Prints output to stdout based on the given features parser and parameters.

    :param output_type: Output type
    :param parser: Features parser
    :param flavor: Flavor
    :param ignores_list: Features to ignore

    :since: 1.0.0
    """

    additional_filter_func = lambda node: node not in ignores_list

    if output_type == "features":
        print(
            parser.filter_as_string(
                flavor, additional_filter_func=additional_filter_func
            )
        )
    elif (output_type in "platform", "elements", "flags"):
        features_by_type = parser.filter_as_dict(
            flavor, additional_filter_func=additional_filter_func
        )

        if output_type == "platform":
            print(features_by_type["platform"][0])
        elif output_type == "elements":
            print(",".join(features_by_type["element"]))
        elif output_type == "flags":
            print(",".join(features_by_type["flag"]))
    else:
        graph = parser.filter(flavor, additional_filter_func=additional_filter_func)

        sorted_features = Parser.sort_graph_nodes(graph)
        minimal_feature_set = get_minimal_feature_set(graph)

        sorted_minimal_features = Parser.subset(minimal_feature_set, sorted_features)

        cname_base = Parser.get_flavor_from_feature_set(sorted_minimal_features)

        if output_type == "cname_base":
            print(cname_base)
        elif output_type == "cname":
            cname = flavor

            if arch is not None:
                cname += f"-{arch}"

            if commit_id_or_hash is not None:
                cname += f"-{version}-{commit_id_or_hash[:8]}"

            print(cname)
        elif output_type == "container_name":
            print(RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", cname_base).lower())
        elif output_type == "platform":
            print(features_by_type["platform"][0])
        elif output_type == "elements":
            print(",".join(features_by_type["element"]))
        elif output_type == "flags":
            print(",".join(features_by_type["flag"]))
        elif output_type == "graph":
            print(graph_as_mermaid_markup(flavor, graph))


def print_output_from_cname(output_type: str, cname_instance: CName) -> None:
    """
    Prints output to stdout based on the given CName instance.

    :param output_type: Output type
    :param cname_instance: CName instance

    :since: 1.0.0
    """

    if output_type in ("cname_base", "cname", "flavor"):
        sorted_features = Parser.get_flavor_as_feature_set(cname_instance.flavor)
        flavor = Parser.get_flavor_from_feature_set(sorted_features)

        if output_type in ("cname_base", "flavor"):
            print(flavor)
        else:
            if cname_instance.version_and_commit_id is None:
                raise RuntimeError(
                    "Version and commit ID can't be provided without appropriate input."
                )

            print(
                f"{flavor}-{cname_instance.arch}-{cname_instance.version_and_commit_id}"
            )
    elif output_type == "container_name":
        print(RE_CAMEL_CASE_SPLITTER.sub("\\1-\\2", cname_instance.flavor).lower())
    elif output_type == "platform":
        print(cname_instance.feature_set_platform)
    elif output_type == "elements":
        print(cname_instance.feature_set_element)
    elif output_type == "features":
        print(cname_instance.feature_set)
    elif output_type == "flags":
        print(cname_instance.feature_set_flag)


if __name__ == "__main__":
    main()
