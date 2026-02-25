#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-cname main entrypoint
"""

import argparse
import logging
import re
from os.path import basename, dirname

from .__main__ import (
    get_minimal_feature_set,
    get_version_and_commit_id_from_files,
)
from .cname import CName
from .parser import Parser


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-cname.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 1.0.0
    """

    parser = argparse.ArgumentParser(
        prog="gl-cname",
        description="Generate a canonical name (cname) from feature sets.",
    )

    parser.add_argument(
        "--arch",
        dest="arch",
        help="Target architecture (e.g., amd64, arm64). If not specified, will be determined from the cname or feature set.",
    )

    parser.add_argument(
        "--commit",
        dest="commit",
        help="Git commit hash. If not specified, will be read from COMMIT file in the GardenLinux root directory.",
    )

    parser.add_argument(
        "--feature-dir",
        default="features",
        help="Path to the features directory (default: 'features').",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="Version string. If not specified, will be read from VERSION file in the GardenLinux root directory.",
    )

    parser.add_argument(
        "cname",
        help="Canonical name (cname) to process. Must be a valid GardenLinux canonical name format.",
    )

    return parser


def main() -> None:
    """
    gl-cname main()

    :since: 0.7.0
    """

    parser = get_parser()
    args = parser.parse_args()

    re_match = re.match(
        "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
        args.cname,
    )

    assert re_match, f"Not a valid Garden Linux canonical name {args.cname}"

    arch = args.arch
    commit_id_or_hash = args.commit
    gardenlinux_root = dirname(args.feature_dir)
    version = args.version

    if gardenlinux_root == "":
        gardenlinux_root = "."

    if not version:
        try:
            version, commit_id_or_hash = get_version_and_commit_id_from_files(
                gardenlinux_root
            )
        except RuntimeError as exc:
            logging.warning(
                "Failed to parse version information for GL root '{0}': {1}".format(
                    gardenlinux_root, exc
                )
            )

    cname = CName(args.cname, arch=arch, commit_hash=commit_id_or_hash, version=version)

    assert cname.arch, "Architecture could not be determined"

    feature_dir_name = basename(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    graph = Parser(gardenlinux_root, feature_dir_name).filter(cname.flavor)

    sorted_features = Parser.sort_graph_nodes(graph)
    minimal_feature_set = get_minimal_feature_set(graph)

    sorted_minimal_features = Parser.subset(minimal_feature_set, sorted_features)

    generated_cname = Parser.get_flavor_from_feature_set(sorted_minimal_features)

    generated_cname += f"-{cname.arch}"

    if cname.version_and_commit_id is not None:
        generated_cname += f"-{cname.version_and_commit_id}"

    print(generated_cname)


if __name__ == "__main__":
    main()
