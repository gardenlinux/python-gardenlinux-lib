#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-diff main entrypoint
"""

import argparse
import json
import pathlib
from os.path import basename, dirname

from .comparator import Comparator
from .markdown_formatter import MarkdownFormatter


def generate(args: argparse.Namespace) -> None:
    """
    Call Comparator

    :param args:            Parsed args

    :since: 1.0.0
    """

    comparator = Comparator(nightly=args.nightly)

    files, whitelist = comparator.generate(args.a, args.b)

    result = json.dumps(files)

    if files == {} and whitelist:
        result = "whitelist"

    if args.out:
        with open(args.out, "w") as f:
            f.write(result + "\n")
    else:
        print(result)

    if files != {}:
        exit(64)


def format(args: argparse.Namespace) -> None:
    """
    Call MarkdownFormatter

    :param args:            Parsed args

    :since: 1.0.0
    """

    gardenlinux_root = dirname(args.feature_dir)

    if gardenlinux_root == "":
        gardenlinux_root = "."

    feature_dir_name = basename(args.feature_dir)

    formatter = MarkdownFormatter(
        json.loads(args.flavors_matrix),
        json.loads(args.bare_flavors_matrix),
        pathlib.Path(args.diff_dir),
        pathlib.Path(args.nightly_stats),
        gardenlinux_root,
        feature_dir_name,
    )

    print(str(formatter), end="")


def main() -> None:
    """
    gl-diff main()

    :since: 1.0.0
    """

    parser = argparse.ArgumentParser()

    subparser = parser.add_subparsers(
        title="Options",
        description="You can eiter generate the comparison result or format the result to markdown.",
        required=True,
    )

    generate_parser = subparser.add_parser("generate")
    generate_parser.add_argument("--nightly", action="store_true")
    generate_parser.add_argument("--out")
    generate_parser.add_argument("a")
    generate_parser.add_argument("b")
    generate_parser.set_defaults(func=generate)

    format_parser = subparser.add_parser("format")
    format_parser.add_argument("--feature-dir", default="features")
    format_parser.add_argument("--diff-dir", default="diffs")
    format_parser.add_argument("--nightly-stats", default="nightly_stats.csv")
    format_parser.add_argument("flavors_matrix")
    format_parser.add_argument("bare_flavors_matrix")
    format_parser.set_defaults(func=format)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
