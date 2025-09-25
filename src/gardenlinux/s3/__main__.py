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


def main() -> None:
    """
    gl-s3 main()

    :since: 0.8.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--bucket", dest="bucket")
    parser.add_argument("--cname", required=False, dest="cname")
    parser.add_argument("--path", required=False, dest="path")

    parser.add_argument("action", nargs="?", choices=_ARGS_ACTION_ALLOWED)

    args = parser.parse_args()

    if args.action == "download-artifacts-from-bucket":
        S3Artifacts(args.bucket).download_to_directory(args.cname, args.path)
    elif args.action == "upload-artifacts-to-bucket":
        S3Artifacts(args.bucket).upload_from_directory(args.cname, args.path)
