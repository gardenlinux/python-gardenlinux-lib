#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-diff main entrypoint
"""

import argparse
import json
import pathlib
from os.path import basename, dirname

from .difference_formatter import Formatter


def main():
    """
    gl-diff main()

    :since: 1.0.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--feature-dir", default="features")
    parser.add_argument("--diff-dir", default="diffs")
    parser.add_argument("--nightly-stats", default="nightly_stats")
    parser.add_argument("--output", default="Result.md")
    parser.add_argument("flavors_matrix")
    parser.add_argument("bare_flavors_matrix")

    args = parser.parse_args()

    gardenlinux_root = dirname(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    feature_dir_name = basename(args.feature_dir)

    formatter = Formatter(
        json.loads(args.flavors_matrix),
        json.loads(args.bare_flavors_matrix),
        pathlib.Path(args.diff_dir),
        pathlib.Path(args.nightly_stats),
        gardenlinux_root,
        feature_dir_name,
    )

    with open(args.output, "w") as f:
        f.write(str(formatter))


if __name__ == "__main__":
    main()
