#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functools import reduce
from os.path import basename, dirname
import argparse
import re

from .__main__ import get_cname_base, get_minimal_feature_set, get_version_and_commit_id_from_files, sort_subset
from .parser import Parser


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--version", dest="version")
    parser.add_argument("cname")

    args = parser.parse_args()

    re_match = re.match(
        "([a-zA-Z0-9]+(-[a-zA-Z0-9\\_\\-]*?)?)(-([a-z0-9]+)(-([a-z0-9.]+)-([a-z0-9]+))*)?$",
        args.cname
    )

    assert re_match, f"Not a valid GardenLinux canonical name {args.cname}"

    arch = None
    commit_id = None
    gardenlinux_root = dirname(args.feature_dir)
    version = None

    if re_match.lastindex == 1:
        data_splitted = re_match[1].split("-", 1)

        if len(data_splitted) > 1:
            arch = data_splitted[1]

        cname_base = data_splitted[0]
    else:
        arch = re_match[4]
        cname_base = re_match[1]
        commit_id = re_match[7]
        version = re_match[6]

    if args.arch is not None:
        arch = args.arch

    assert arch is not None and arch != "", "Architecture could not be determined"

    if not commit_id or not version:
        version, commit_id = get_version_and_commit_id_from_files(gardenlinux_root)

    if args.version is not None:
        re_match = re.match("([a-z0-9.]+)(-([a-z0-9]+))?$", args.version)
        assert re_match, f"Not a valid version {args.version}"

        commit_id = re_match[3]
        version = re_match[1]

    feature_dir_name = basename(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    graph = Parser(gardenlinux_root, feature_dir_name).filter(cname_base)

    sorted_features = Parser.sort_reversed_graph_nodes(graph)

    minimal_feature_set = get_minimal_feature_set(graph)

    sorted_minimal_features = sort_subset(
        minimal_feature_set, sorted_features
    )

    cname = get_cname_base(sorted_minimal_features)

    if arch is not None:
        cname += f"-{arch}"

    if commit_id is not None:
        cname += f"-{version}-{commit_id}"

    print(cname)


if __name__ == "__main__":
    main()
