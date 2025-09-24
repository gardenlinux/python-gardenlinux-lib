import argparse

from .release import upload_to_github_release_page


def main():
    parser = argparse.ArgumentParser(description="GitHub Release Script")
    subparsers = parser.add_subparsers(dest="command")

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--owner", default="gardenlinux")
    upload_parser.add_argument("--repo", default="gardenlinux")
    upload_parser.add_argument("--release_id", required=True)
    upload_parser.add_argument("--file_path", required=True)
    upload_parser.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()

    if args.command == "upload":
        upload_to_github_release_page(
            args.owner, args.repo, args.release_id, args.file_path, args.dry_run
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
