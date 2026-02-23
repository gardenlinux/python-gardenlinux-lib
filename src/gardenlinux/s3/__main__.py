#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-s3 main entrypoint
"""

import argparse

from .s3_artifacts import S3Artifacts


def main() -> None:
    """
    gl-s3 main()

    :since: 0.8.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--bucket", dest="bucket")
    parser.add_argument("--path", required=False, dest="path")
    parser.add_argument("--dry-run", action="store_true")

    subparsers = parser.add_subparsers(dest="action")

    download_parser = subparsers.add_parser("download-artifacts-from-bucket")
    download_parser.add_argument("--cname", required=False, dest="cname")

    upload_parser = subparsers.add_parser("upload-artifacts-to-bucket")
    upload_parser.add_argument("--artifact-name", required=False, dest="artifact_name")

    args = parser.parse_args()

    if args.action == "download-artifacts-from-bucket":
        S3Artifacts(args.bucket).download_to_directory(args.cname, args.path)
    elif args.action == "upload-artifacts-to-bucket":
        S3Artifacts(args.bucket).upload_from_directory(
            args.artifact_name, args.path, dry_run=args.dry_run
        )
