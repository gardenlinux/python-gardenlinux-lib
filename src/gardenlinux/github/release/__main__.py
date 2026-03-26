import argparse
import logging

from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME
from gardenlinux.logger import LoggerSetup

from ..release_notes import create_github_release_notes
from . import (
    write_to_release_id_file,
)
from .release import Release

LOGGER = LoggerSetup.get_logger("gardenlinux.github", logging.INFO)


def main() -> None:
    parser = argparse.ArgumentParser(description="GitHub Release Script")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--owner", default="gardenlinux")
    create_parser.add_argument("--repo", default="gardenlinux")
    create_parser.add_argument("--tag", required=True)
    create_parser.add_argument("--name")
    create_parser.add_argument("--body", required=True)
    create_parser.add_argument("--commit")
    create_parser.add_argument("--pre-release", action="store_true", default=True)
    create_parser.add_argument("--latest", action="store_true", default=False)

    create_parser_gl = subparsers.add_parser("create-with-gl-release-notes")
    create_parser_gl.add_argument("--owner", default="gardenlinux")
    create_parser_gl.add_argument("--repo", default="gardenlinux")
    create_parser_gl.add_argument("--tag", required=True)
    create_parser_gl.add_argument("--commit", required=True)
    create_parser_gl.add_argument("--latest", action="store_true", default=False)
    create_parser_gl.add_argument("--dry-run", action="store_true", default=False)

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--owner", default="gardenlinux")
    upload_parser.add_argument("--repo", default="gardenlinux")
    upload_parser.add_argument("--release_id", type=int, required=True)
    upload_parser.add_argument("--file_path", required=True)
    upload_parser.add_argument("--dry-run", action="store_true", default=False)

    upload_parser.add_argument(
        "--overwrite-same-name", action="store_true", default=False
    )

    args = parser.parse_args()

    if args.command == "create":
        release = Release(args.repo, args.owner)
        release.tag = args.tag
        release.name = args.name
        release.body = args.body
        release.commitish = args.commit
        release.is_pre_release = args.pre_release
        release.is_latest = args.latest
        release.create()
    elif args.command == "create-with-gl-release-notes":
        body = create_github_release_notes(
            args.tag, args.commit, GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME
        )

        if args.dry_run:
            print("Dry Run ...")
            print("This release would be created:")
            print(body)
        else:
            release = Release(args.repo, args.owner)
            release.tag = args.tag
            release.body = body
            release.commitish = args.commit
            release.is_latest = args.latest

            release_id = release.create()
            write_to_release_id_file(f"{release_id}")
            LOGGER.info(f"Release created with ID: {release_id}")
    elif args.command == "upload":
        release = Release.get(args.release_id, repo=args.repo, owner=args.owner)

        if args.dry_run:
            print("Dry Run ...")

            print(
                f"The file {args.file_path} would be uploaded for release: {release.name}"
            )
        else:
            release.upload_asset(args.file_path, args.overwrite_same_name)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
