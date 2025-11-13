#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-python-exportlibs main entrypoint
"""

from argparse import ArgumentParser

from .exporter import _get_default_package_dir, export

_ARGS_TYPE_ALLOWED = [
    "copy",
]


def parse_args():
    """
    Parses arguments used for main()

    :return: (object) Parsed argparse.ArgumentParser namespace
    :since:  TODO
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
    gl-python-exportlibs main()

    :since: TODO
    """

    args = parse_args()

    export(output_dir=args.output_dir, package_dir=args.package_dir)


if __name__ == "__main__":
    # Create a null logger as default
    main()
