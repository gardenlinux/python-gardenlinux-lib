#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-build main entrypoint
"""

import pathlib
from argparse import ArgumentParser

from .exporter import _get_default_package_dir, export

_ARGS_TYPE_ALLOWED = [
    "export-python-libs",
]


def parse_args():
    """
    Parses arguments used for main()

    :return: (object) Parsed argparse.ArgumentParser namespace
    :since:  1.0.0
    """

    parser = ArgumentParser(
        description="Export shared libraries required by installed pip packages to a portable directory"
    )

    parser.add_argument("type", choices=_ARGS_TYPE_ALLOWED, default=None)
    parser.add_argument(
        "--output-dir",
        default="/required_libs",
        help="Directory containing the shared libraries.",
    )
    parser.add_argument(
        "--package-dir",
        default=_get_default_package_dir(),
        help="Path of the generated output",
    )

    return parser.parse_args()


def main():
    """
    gl-gl-build main()

    :since: 1.0.0
    """

    args = parse_args()

    match args.type:
        case "export-python-libs":
            export(output_dir=pathlib.Path(args.output_dir), package_dir=pathlib.Path(args.package_dir))
        case _:
            raise NotImplementedError


if __name__ == "__main__":
    # Create a null logger as default
    main()
