#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-features-parse main entrypoint
"""

import argparse
import os
import re
from os import path
from typing import Any, Set

from .artifact_base_name import ArtifactBaseName
from .parser import Parser

_ARGS_TYPE_ALLOWED = [
    "arch",
    "artifact_base_name",
    "cname",
    "commit_id",
    "container_name",
    "container_tag",
    "elements",
    "features",
    "flags",
    "flavor",
    "graph",
    "platform",
    "platforms",
    "version",
    "version_and_commit_id",
    "versioned_flavor",
]

RE_CAMEL_CASE_SPLITTER = re.compile("([A-Z]+|[a-z0-9])([A-Z])(?!$)")
"""
CamelCase splitter RegExp
"""


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-features-parse.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 0.10.9
    """

    parser = argparse.ArgumentParser(
        prog="gl-features-parse",
        description="Parse and extract information from Garden Linux features.",
    )

    parser.add_argument(
        "--arch",
        dest="arch",
        help="Target architecture (e.g., amd64, arm64). Overrides architecture from CName.",
    )

    parser.add_argument(
        "--artifact-base-name",
        dest="artifact_base_name",
        help="Artifact base name to parse. Must be a valid Garden Linux Artifact Base Name.",
    )

    parser.add_argument(
        "--cname",
        dest="cname",
        help="Canonical Name (CName) to parse.",
    )

    parser.add_argument(
        "--commit",
        dest="commit",
        help="Git commit hash. If not specified, will be read from COMMIT file or release file.",
    )

    parser.add_argument(
        "--feature-dir",
        default="features",
        help="Path to the features directory (default: 'features'). Either --feature-dir or --release-file must be provided.",
    )

    parser.add_argument(
        "--flavor",
        dest="flavor",
        help="Garden Linux flavor name.",
    )

    parser.add_argument(
        "--ignore",
        dest="ignore",
        type=lambda arg: set([f for f in arg.split(",") if f]),
        default=set(),
        help="Comma-separated list of features to ignore when processing (e.g., 'feature1,feature2').",
    )

    parser.add_argument(
        "--release-file",
        dest="release_file",
        help="Path to a release file containing features metadata. Either --feature-dir or --release-file must be provided.",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="Version string. If not specified, will be read from VERSION file or release file.",
    )

    parser.add_argument(
        "--versioned-flavor",
        dest="versioned_flavor",
        help="Garden Linux versioned flavor name.",
    )

    parser.add_argument(
        "type",
        nargs="?",
        choices=_ARGS_TYPE_ALLOWED,
        default="cname",
        help="Type of output to generate. Choices: {}. Default: 'cname'.".format(
            ", ".join(_ARGS_TYPE_ALLOWED)
        ),
    )

    return parser


def main() -> None:
    """
    gl-features-parse main()

    :since: 0.7.0
    """

    parser = get_parser()
    args = parser.parse_args()

    assert args.feature_dir or args.release_file or os.environ.get("GL_ROOT_DIR"), (
        "Please provide either `--feature-dir` or `--release-file` argument"
    )

    arch = args.arch
    commit_id_or_hash = args.commit
    gardenlinux_root = os.environ.get("GL_ROOT_DIR", path.dirname(args.feature_dir))
    version = args.version

    if not gardenlinux_root:
        gardenlinux_root = "."

    if not version or not commit_id_or_hash:
        version, commit_id_or_hash = (
            ArtifactBaseName.get_version_and_commit_id_from_files(gardenlinux_root)
        )

    abn_object = ArtifactBaseName.new_instance(
        args.artifact_base_name,
        cname=args.cname,
        flavor=args.flavor,
        versioned_flavor=args.versioned_flavor,
        arch=arch,
        version=version,
        commit_id_or_hash=commit_id_or_hash,
    )

    if args.release_file is not None:
        abn_object.load_from_release_file(args.release_file)

    arch = abn_object.arch
    cname = abn_object.cname
    commit_id_or_hash = abn_object.commit_id
    version = abn_object.version

    feature_dir_name = path.basename(args.feature_dir)

    if args.type == "arch":
        print(arch)
    elif args.type in (
        "artifact_base_name",
        "cname",
        "container_name",
        "elements",
        "features",
        "flags",
        "flavor",
        "graph",
        "platform",
        "platforms",
        "versioned_flavor",
    ):
        if args.type == "graph" or len(args.ignore) > 0:
            features_parser = Parser(gardenlinux_root, feature_dir_name)

            print_output_from_features_parser(
                args.type, abn_object, features_parser, cname, args.ignore
            )
        else:
            print_output_from_abn_object(args.type, abn_object)
    elif args.type == "commit_id":
        print(commit_id_or_hash[:8])
    elif args.type == "container_tag":
        print(re.sub("\\W+", "-", f"{version}-{commit_id_or_hash[:8]}"))
    elif args.type == "version":
        print(version)
    elif args.type == "version_and_commit_id":
        print(f"{version}-{commit_id_or_hash[:8]}")


def graph_as_mermaid_markup(cname: str | None, graph: Any) -> str:
    """
    Generates a mermaid.js representation of the graph.
    This is helpful to identify dependencies between features.

    Syntax docs:
    https://mermaid.js.org/syntax/flowchart.html?id=flowcharts-basic-syntax

    :param cname: Garden Linux canonical name
    :param graph: networkx.Digraph

    :return: (str) mermaid.js representation
    :since:  0.7.0
    """

    if cname is None:
        raise RuntimeError("Error while generating graph: CName is None!")

    markup = f"---\ntitle: Dependency Graph for Feature {cname}\n---\ngraph TD;\n"

    for u, v in graph.edges:
        markup += f"    {u}-->{v};\n"

    return markup


def print_output_from_features_parser(
    output_type: str,
    abn_object: ArtifactBaseName,
    parser: Parser,
    cname: str,
    ignores_list: Set[str],
) -> None:
    """
    Prints output to stdout based on the given features parser and parameters.

    :param output_type: Output type
    :param parser: Features parser
    :param cname: Garden Linux canonical name
    :param ignores_list: Features to ignore

    :since: 1.0.0
    """

    def additional_filter_func(node: str) -> bool:
        return node not in ignores_list

    if output_type == "features":
        print(
            parser.filter_as_string(
                cname, additional_filter_func=additional_filter_func
            )
        )
    elif output_type in ("platform", "platforms", "elements", "flags"):
        features_by_type = parser.filter_as_dict(
            cname, additional_filter_func=additional_filter_func
        )

        if output_type == "platform":
            print(features_by_type["platform"][0])
        if output_type == "platforms":
            print(",".join(features_by_type["platform"]))
        elif output_type == "elements":
            print(",".join(features_by_type["element"]))
        elif output_type == "flags":
            print(",".join(features_by_type["flag"]))
    else:
        graph = parser.filter(cname, additional_filter_func=additional_filter_func)

        sorted_features = Parser.sort_graph_nodes(graph)
        minimal_feature_set = Parser.get_minimal_feature_set(graph)

        sorted_minimal_features = Parser.subset(minimal_feature_set, sorted_features)

        cname = Parser.get_cname_from_feature_set(sorted_minimal_features)

        match output_type:
            case "artifact_base_name":
                print(f"{cname}-{abn_object.arch}-{abn_object.version_and_commit_id}")
            case "cname":
                print(cname)
            case "container_name":
                print(RE_CAMEL_CASE_SPLITTER.sub("\\1_\\2", cname).lower())
            case "flavor":
                print(f"{cname}-{abn_object.arch}")
            case "graph":
                print(graph_as_mermaid_markup(cname, graph))
            case "versioned_flavor":
                print(f"{cname}-{abn_object.arch}-{abn_object.version}")


def print_output_from_abn_object(
    output_type: str, abn_object: ArtifactBaseName
) -> None:
    """
    Prints output to stdout based on the given CName instance.

    :param output_type: Output type
    :param cname_instance: CName instance

    :since: 1.0.0
    """

    if output_type in ("artifact_base_name", "cname", "flavor", "versioned_flavor"):
        sorted_features = Parser.get_cname_as_feature_set(abn_object.cname)
        cname = Parser.get_cname_from_feature_set(sorted_features)

        match output_type:
            case "artifact_base_name":
                print(f"{cname}-{abn_object.arch}-{abn_object.version_and_commit_id}")
            case "cname":
                print(cname)
            case "flavor":
                print(f"{cname}-{abn_object.arch}")
            case "versioned_flavor":
                print(f"{cname}-{abn_object.arch}-{abn_object.version}")
    elif output_type == "container_name":
        print(RE_CAMEL_CASE_SPLITTER.sub("\\1-\\2", abn_object.cname).lower())
    elif output_type == "platform":
        print(abn_object.platform)
    elif output_type == "platforms":
        print(abn_object.feature_set_platform)
    elif output_type == "elements":
        print(abn_object.feature_set_element)
    elif output_type == "features":
        print(abn_object.feature_set)
    elif output_type == "flags":
        print(abn_object.feature_set_flag)


if __name__ == "__main__":
    main()
