#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-metadata main entrypoint
"""

import argparse

from .cname import CName

_ARGS_ACTION_ALLOWED = [
    "output-release-metadata",
    "write",
]


def main() -> None:
    """
    gl-metadata main()

    :since: 0.7.0
    """

    parser = argparse.ArgumentParser()

    parser.add_argument("--arch", dest="arch")
    parser.add_argument("--cname", required=True, dest="cname")
    parser.add_argument("--commit-hash", dest="commit_hash")
    parser.add_argument("--release-file", dest="release_file")
    parser.add_argument("--overwrite-file", type=bool, dest="overwrite_file")
    parser.add_argument("--version", dest="version")

    parser.add_argument(
        "action",
        nargs="?",
        choices=_ARGS_ACTION_ALLOWED,
        default="output-release-metadata",
    )

    args = parser.parse_args()

    cname = CName(
        args.cname, arch=args.arch, commit_hash=args.commit_hash, version=args.version
    )

    if args.commit_hash is not None:
        cname.commit_hash = args.commit_hash

    if args.action == "write":
        cname.save_to_release_file(args.release_file, args.overwrite_file)
    else:
        if args.release_file is not None:
            cname.load_from_release_file(args.release_file)

        print(cname.release_metadata_string)


if __name__ == "__main__":
    main()
