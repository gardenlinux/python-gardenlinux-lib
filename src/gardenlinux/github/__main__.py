import argparse

from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME
from gardenlinux.logger import LoggerSetup

from .release import (
    create_github_release,
    upload_to_github_release_page,
    write_to_release_id_file,
)
from .release_notes import create_github_release_notes

LOGGER = LoggerSetup.get_logger("gardenlinux.github", "INFO")


def main():
    parser = argparse.ArgumentParser(description="GitHub Release Script")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--owner", default="gardenlinux")
    create_parser.add_argument("--repo", default="gardenlinux")
    create_parser.add_argument("--tag", required=True)
    create_parser.add_argument("--commit", required=True)
    create_parser.add_argument("--latest", action="store_true", default=False)
    create_parser.add_argument("--dry-run", action="store_true", default=False)

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--owner", default="gardenlinux")
    upload_parser.add_argument("--repo", default="gardenlinux")
    upload_parser.add_argument("--release_id", required=True)
    upload_parser.add_argument("--file_path", required=True)
    upload_parser.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()

    if args.command == "create":
        body = create_github_release_notes(
            args.tag, args.commit, GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME
        )
        if args.dry_run:
            print("Dry Run ...")
            print("This release would be created:")
            print(body)
        else:
            release_id = create_github_release(
                args.owner, args.repo, args.tag, args.commit, args.latest, body
            )
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
