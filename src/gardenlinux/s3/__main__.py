#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-s3 main entrypoint
"""

import argparse

from .s3_artifacts import S3Artifacts

_ARGS_ACTION_ALLOWED = [
    "download-artifacts-from-bucket",
    "upload-artifacts-to-bucket",
]


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-s3.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 0.10.9
    """
    parser = argparse.ArgumentParser(
        description="Upload and download artifacts from S3 buckets."
    )

    parser.add_argument(
        "--bucket",
        dest="bucket",
        help="S3 bucket name to upload to or download from.",
    )
    parser.add_argument(
        "--cname",
        required=False,
        dest="cname",
        help="Canonical name (cname) used as the S3 key prefix for artifacts.",
    )
    parser.add_argument(
        "--path",
        required=False,
        dest="path",
        help="Local directory path for upload (source) or download (destination).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without actually uploading or downloading files.",
    )

    parser.add_argument(
        "action",
        nargs="?",
        choices=_ARGS_ACTION_ALLOWED,
        help="Action to perform. Choices: {}.".format(", ".join(_ARGS_ACTION_ALLOWED)),
    )
    return parser


# Parser object for documentation generation
parser = get_parser()
parser.prog = "gl-s3"


def main() -> None:
    """
    gl-s3 main()

    :since: 0.8.0
    """

    parser = get_parser()
    args = parser.parse_args()

    if args.action == "download-artifacts-from-bucket":
        S3Artifacts(args.bucket).download_to_directory(args.cname, args.path)
    elif args.action == "upload-artifacts-to-bucket":
        S3Artifacts(args.bucket).upload_from_directory(
            args.cname, args.path, dry_run=args.dry_run
        )
