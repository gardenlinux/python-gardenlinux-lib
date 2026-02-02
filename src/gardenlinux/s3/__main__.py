#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-s3 main entrypoint
"""

import argparse

from .s3_artifacts import S3Artifacts


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-s3.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 0.10.9
    """

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bucket", dest="bucket", help="S3 bucket name to upload to or download from."
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

    subparsers = parser.add_subparsers(dest="action", help="Action to perform.")

    download_parser = subparsers.add_parser("download-artifacts-from-bucket")

    download_parser.add_argument(
        "--cname",
        required=False,
        dest="cname",
        help="Canonical name (cname) used as the S3 key prefix for artifacts.",
    )

    upload_parser = subparsers.add_parser("upload-artifacts-to-bucket")

    upload_parser.add_argument(
        "--artifact-name", dest="artifact_name", help="S3 artifact base name."
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

    args = parser.parse_args()

    if args.action == "download-artifacts-from-bucket":
        S3Artifacts(args.bucket).download_to_directory(args.cname, args.path)
    elif args.action == "upload-artifacts-to-bucket":
        S3Artifacts(args.bucket).upload_from_directory(
            args.artifact_name, args.path, dry_run=args.dry_run
        )
