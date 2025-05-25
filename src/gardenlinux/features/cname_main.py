#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from os.path import basename, dirname
import argparse
import re

from .__main__ import (
    get_cname_base,
    get_minimal_feature_set,
    get_version_and_commit_id_from_files,
    sort_subset,
)
from .cname import CName
from .parser import Parser


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--version", dest="version")
    parser.add_argument("cname")

    args = parser.parse_args()

    re_match = re.match(
        "([a-zA-Z0-9]+([\\_\\-][a-zA-Z0-9]+)*?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
        args.cname,
    )

    assert re_match, f"Not a valid GardenLinux canonical name {args.cname}"

    arch = None
    gardenlinux_root = dirname(args.feature_dir)
    version = args.version

    if args.arch is not None:
        arch = args.arch

    if args.version is not None:
        version = args.version

    if not version:
        version_data = get_version_and_commit_id_from_files(gardenlinux_root)
        version = f"{version_data[0]}-{version_data[1]}"

    cname = CName(args.cname, arch=arch, version=version)

    assert cname.arch, "Architecture could not be determined"

    feature_dir_name = basename(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    graph = Parser(gardenlinux_root, feature_dir_name).filter(cname.flavor)

    sorted_features = Parser.sort_graph_nodes(graph)
    minimal_feature_set = get_minimal_feature_set(graph)

    sorted_minimal_features = sort_subset(minimal_feature_set, sorted_features)

    generated_cname = get_cname_base(sorted_minimal_features)

    if cname.arch is not None:
        generated_cname += f"-{cname.arch}"

    if cname.version_and_commit_id is not None:
        generated_cname += f"-{cname.version_and_commit_id}"

    print(generated_cname)


if __name__ == "__main__":
    main()
