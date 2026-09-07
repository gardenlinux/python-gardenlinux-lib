#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-metadata main entrypoint
"""

import argparse
from os import environ

from .artifact_base_name import ArtifactBaseName

_ARGS_ACTION_ALLOWED = [
    "output-release-metadata",
    "write",
]


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-metadata.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 1.0.0
    """

    parser = argparse.ArgumentParser(
        prog="gl-metadata",
        description="Handle GardenLinux metadata reading and writing.",
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
        "--flavor",
        dest="flavor",
        help="GardenLinux flavor name.",
    )

    parser.add_argument(
        "--release-file",
        dest="release_file",
        help="Path to a release file containing features metadata.",
    )

    parser.add_argument(
        "--overwrite-file",
        type=bool,
        dest="overwrite_file",
        help="Accept overwriting existing files.",
    )

    parser.add_argument(
        "--version",
        dest="version",
        help="Version string. If not specified, will be read from VERSION file or release file.",
    )

    parser.add_argument(
        "--versioned-flavor",
        dest="versioned_flavor",
        help="GardenLinux versioned flavor name.",
    )

    parser.add_argument(
        "action",
        nargs="?",
        choices=_ARGS_ACTION_ALLOWED,
        default="output-release-metadata",
    )

    return parser


def main() -> None:
    """
    gl-metadata main()

    :since: 0.7.0
    """

    parser = get_parser()
    args = parser.parse_args()

    commit_id_or_hash = args.commit
    gardenlinux_root = environ.get("GL_ROOT_DIR")
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
        arch=args.arch,
        version=args.version,
        commit_id_or_hash=args.commit,
    )

    if args.action == "write":
        abn_object.save_to_release_file(args.release_file, args.overwrite_file)
    else:
        if args.release_file is not None:
            abn_object.load_from_release_file(args.release_file)

        print(abn_object.release_metadata_string)


if __name__ == "__main__":
    main()
