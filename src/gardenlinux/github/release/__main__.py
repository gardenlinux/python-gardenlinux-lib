import argparse
import logging

from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME
from gardenlinux.logger import LoggerSetup

from ..release_notes import create_github_release_notes
from . import (
    upload_to_github_release_page,
    write_to_release_id_file,
)
from .release import Release

LOGGER = LoggerSetup.get_logger("gardenlinux.github", logging.INFO)


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-gh-release.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 1.0.0
    """

    parser = argparse.ArgumentParser(
        prog="gl-gh-release", description="Create and manage GitHub releases."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    create_parser = subparsers.add_parser("create", help="Create a new GitHub release.")

    create_parser.add_argument(
        "--owner",
        default="gardenlinux",
        help="GitHub repository owner (default: 'gardenlinux').",
    )

    create_parser.add_argument(
        "--repo",
        default="gardenlinux",
        help="GitHub repository name (default: 'gardenlinux').",
    )

    create_parser.add_argument(
        "--tag", required=True, help="Git tag name for the release (required)."
    )

    create_parser.add_argument(
        "--name", help="Release name/title. If not specified, the tag will be used."
    )

    create_parser.add_argument(
        "--body", required=True, help="Release notes/description body (required)."
    )

    create_parser.add_argument(
        "--commit",
        help="Git commit hash. If not specified, the tag will be used to find the commit.",
    )

    create_parser.add_argument(
        "--pre-release",
        action="store_true",
        default=True,
        help="Mark the release as a pre-release (default: True).",
    )

    create_parser.add_argument(
        "--latest",
        action="store_true",
        default=False,
        help="Mark this release as the latest release (default: False).",
    )

    create_parser_gl = subparsers.add_parser(
        "create-with-gl-release-notes",
        help="Create a GitHub release with auto-generated GardenLinux release notes.",
    )

    create_parser_gl.add_argument(
        "--owner",
        default="gardenlinux",
        help="GitHub repository owner (default: 'gardenlinux').",
    )

    create_parser_gl.add_argument(
        "--repo",
        default="gardenlinux",
        help="GitHub repository name (default: 'gardenlinux').",
    )

    create_parser_gl.add_argument(
        "--tag", required=True, help="Git tag name for the release (required)."
    )

    create_parser_gl.add_argument(
        "--commit",
        required=True,
        help="Git commit hash used to generate release notes (required).",
    )

    create_parser_gl.add_argument(
        "--latest",
        action="store_true",
        default=False,
        help="Mark this release as the latest release (default: False).",
    )

    create_parser_gl.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Perform a dry run without actually creating the release.",
    )

    upload_parser = subparsers.add_parser(
        "upload", help="Upload a file to an existing GitHub release."
    )

    upload_parser.add_argument(
        "--owner",
        default="gardenlinux",
        help="GitHub repository owner (default: 'gardenlinux').",
    )

    upload_parser.add_argument(
        "--repo",
        default="gardenlinux",
        help="GitHub repository name (default: 'gardenlinux').",
    )

    upload_parser.add_argument(
        "--release_id",
        required=True,
        help="GitHub release ID to upload the file to (required).",
    )

    upload_parser.add_argument(
        "--file_path",
        required=True,
        help="Path to the file to upload (required).",
    )

    upload_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Perform a dry run without actually uploading the file.",
    )

    return parser


def main() -> None:
    parser = get_parser()
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
        upload_to_github_release_page(
            args.owner, args.repo, args.release_id, args.file_path, args.dry_run
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
