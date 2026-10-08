#!/usr/bin/env python3

"""
gl-oci main entrypoint
"""

import argparse
import json
from pathlib import Path
from typing import Optional

from .image_manifest import ImageManifest
from .podman import Podman
from .podman_context import PodmanContext
from .repository import Repository


def _add_additional_tag_list_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--additional-tag` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--additional-tag",
        action="append",
        default=[],
        dest="additional_tag",
        help="Additional tag to push the index with",
    )


def _add_arch_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--arch` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--arch",
        required=False,
        dest="arch",
        help="Target Image CPU Architecture",
    )


def _add_build_arg_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--build-arg` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--build-arg",
        action="append",
        default=[],
        dest="build_arg",
        help="Additional build args for Containerfile",
    )


def _add_cname_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--cname` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--cname",
        required=True,
        dest="cname",
        help="Canonical Name of Image",
    )


def _add_commit_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--commit` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--commit",
        required=False,
        dest="commit",
        help="Commit of image",
    )


def _add_cosign_file_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--cosign-file` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--cosign-file",
        type=Path,
        required=False,
        dest="cosign_file",
        help="A file where the pushed manifests digests is written to. The content can be used by an external tool (e.g. cosign) to sign the manifests contents",
    )


def _add_dir_to_parser(
    parser: argparse.ArgumentParser, help_text: str, default_value: Optional[str] = None
) -> None:
    """
    Add `--dir` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--dir",
        type=Path,
        required=(default_value is None),
        default=default_value,
        dest="directory",
        help=help_text,
    )


def _add_manifest_file_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--manifest-file` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--manifest-file",
        type=Path,
        default="manifests/manifest.json",
        dest="manifest_file",
        help="A file where the index entry for the pushed manifest is written to.",
    )


def _add_oci_archive_to_parser(
    parser: argparse.ArgumentParser, required: bool = True
) -> None:
    """
    Add `--oci-archive` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--oci-archive",
        type=Path,
        required=required,
        dest="oci_archive",
        help="Write build result to the OCI archive path and file name",
    )


def _add_oci_destination_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--destination` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--destination",
        required=False,
        dest="destination",
        help="OCI repository destination",
    )


def _add_oci_index_args_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--index and --index-tag` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--index",
        required=True,
        dest="index",
        help="OCI image index",
    )

    parser.add_argument(
        "--index-tag",
        required=True,
        dest="index_tag",
        help="OCI image index tag",
    )


def _add_oci_insecure_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--insecure` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--insecure",
        action=argparse.BooleanOptionalAction,
        dest="insecure",
        default=False,
        help="Use HTTP to communicate with the registry",
    )


def _add_oci_platform_to_parser(
    parser: argparse.ArgumentParser, required: bool = True
) -> None:
    """
    Add `--platform` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--platform",
        required=required,
        dest="platform",
        help="OCI platform as os/arch/variant",
    )


def _add_oci_repository_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--repository` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--repository",
        required=True,
        dest="repository",
        help="Repository Path",
    )


def _add_oci_tag_to_parser(
    parser: argparse.ArgumentParser,
    required: bool = True,
    multiple: bool = False,
) -> None:
    """
    Add `--tag` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    kwargs = {
        "required": required,
        "dest": "tag",
        "help": "OCI tag of image",
    }

    if multiple:
        kwargs["action"] = "append"
        kwargs["default"] = []

    parser.add_argument("--tag", **kwargs)  # type: ignore[arg-type]


def _add_version_to_parser(parser: argparse.ArgumentParser) -> None:
    """
    Add `--version` to the given argument parser.

    :param parser: ArgumentParser instance

    :since: 1.0.0
    """

    parser.add_argument(
        "--version",
        required=False,
        dest="version",
        help="Version of image",
    )


def get_parser() -> argparse.ArgumentParser:
    """
    Get the argument parser for gl-oci.
    Used for documentation generation.

    :return: ArgumentParser instance
    :since: 1.0.0
    """

    parser = argparse.ArgumentParser(
        prog="gl-oci",
        description="gl-oci provides functionality to handle OCI images.",
    )

    subparsers = parser.add_subparsers(dest="action", help="Action to perform.")

    add_image_to_index_parser = subparsers.add_parser("add-image-to-index")

    _add_oci_index_args_to_parser(add_image_to_index_parser)
    _add_oci_repository_to_parser(add_image_to_index_parser)
    _add_oci_tag_to_parser(add_image_to_index_parser)
    _add_oci_insecure_to_parser(add_image_to_index_parser)
    _add_additional_tag_list_to_parser(add_image_to_index_parser)

    build_image_parser = subparsers.add_parser("build-image")

    _add_oci_repository_to_parser(build_image_parser)
    _add_oci_tag_to_parser(build_image_parser)
    _add_dir_to_parser(build_image_parser, "Path to the build Containerfile")
    _add_oci_platform_to_parser(build_image_parser, False)
    _add_additional_tag_list_to_parser(build_image_parser)
    _add_build_arg_to_parser(build_image_parser)
    _add_oci_archive_to_parser(build_image_parser, False)

    load_image_parser = subparsers.add_parser("load-image")

    _add_oci_archive_to_parser(load_image_parser, False)
    _add_additional_tag_list_to_parser(load_image_parser)

    load_images_from_directory_parser = subparsers.add_parser(
        "load-images-from-directory"
    )

    _add_dir_to_parser(
        load_images_from_directory_parser, "Directory of the build artifacts"
    )

    new_index_parser = subparsers.add_parser("new-index")

    _add_oci_index_args_to_parser(new_index_parser)
    _add_oci_insecure_to_parser(new_index_parser)
    _add_additional_tag_list_to_parser(new_index_parser)

    pull_image_parser = subparsers.add_parser("pull-image")

    _add_oci_repository_to_parser(pull_image_parser)
    _add_oci_tag_to_parser(pull_image_parser, False)
    _add_oci_platform_to_parser(pull_image_parser, False)
    _add_oci_insecure_to_parser(pull_image_parser)

    push_image_parser = subparsers.add_parser("push-image")

    _add_oci_repository_to_parser(push_image_parser)
    _add_oci_tag_to_parser(push_image_parser, False)
    _add_oci_destination_to_parser(push_image_parser)
    _add_oci_insecure_to_parser(push_image_parser)

    push_index_from_directory_parser = subparsers.add_parser(
        "push-index-from-directory"
    )

    _add_oci_index_args_to_parser(push_index_from_directory_parser)

    _add_dir_to_parser(
        push_index_from_directory_parser,
        default_value="manifests",
        help_text="Directory to read index entry files from.",
    )

    _add_oci_insecure_to_parser(push_index_from_directory_parser)
    _add_additional_tag_list_to_parser(push_index_from_directory_parser)

    push_index_tags_parser = subparsers.add_parser("push-index-tags")

    _add_oci_index_args_to_parser(push_index_tags_parser)
    _add_oci_insecure_to_parser(push_index_tags_parser)
    _add_oci_tag_to_parser(push_index_tags_parser, multiple=True)

    push_manifest_parser = subparsers.add_parser("push-manifest")

    _add_oci_repository_to_parser(push_manifest_parser)
    _add_cname_to_parser(push_manifest_parser)
    _add_arch_to_parser(push_manifest_parser)
    _add_version_to_parser(push_manifest_parser)
    _add_commit_to_parser(push_manifest_parser)
    _add_dir_to_parser(push_manifest_parser, "Directory of the build artifacts")
    _add_manifest_file_to_parser(push_manifest_parser)
    _add_cosign_file_to_parser(push_manifest_parser)
    _add_oci_insecure_to_parser(push_manifest_parser)
    _add_additional_tag_list_to_parser(push_manifest_parser)

    push_manifest_tags_parser = subparsers.add_parser("push-manifest-tags")

    _add_oci_repository_to_parser(push_manifest_tags_parser)
    _add_cname_to_parser(push_manifest_tags_parser)
    _add_arch_to_parser(push_manifest_tags_parser)
    _add_version_to_parser(push_manifest_tags_parser)
    _add_commit_to_parser(push_manifest_tags_parser)
    _add_oci_insecure_to_parser(push_manifest_tags_parser)
    _add_oci_tag_to_parser(push_manifest_tags_parser, multiple=True)

    save_image_parser = subparsers.add_parser("save-image")

    _add_oci_repository_to_parser(save_image_parser)
    _add_oci_tag_to_parser(save_image_parser, False)
    _add_oci_archive_to_parser(save_image_parser, False)

    tag_image_parser = subparsers.add_parser("tag-image")

    _add_oci_repository_to_parser(tag_image_parser)
    _add_oci_tag_to_parser(tag_image_parser, False)
    _add_additional_tag_list_to_parser(tag_image_parser)

    return parser


def main() -> None:
    """
    gl-oci provides functionality to handle OCI images. It can pull and push
    images from remote repositories as well as handle GardenLinux artifacts, OCI
    image indices and manifests.

    :since: 0.7.0
    """

    parser = get_parser()
    args = parser.parse_args()

    match args.action:
        case "add-image-to-index":
            manifest_repository = Repository(
                f"{args.repository}:{args.tag}", insecure=args.insecure
            )

            manifest = manifest_repository.read_manifest()

            index_resource = Repository(
                f"{args.index}:{args.index_tag}", insecure=args.insecure
            )

            image_index = index_resource.read_or_generate_index()
            image_index.append_manifest(manifest)

            index_resource.push_index(image_index)
            index_resource.push_index_for_tags(image_index, args.additional_tag)
        case "build-image":
            podman = Podman()

            with PodmanContext() as podman_context:
                if args.oci_archive is None:
                    image_id = podman.build(
                        args.directory,
                        podman=podman_context,
                        platform=args.platform,
                        oci_tag=f"{args.repository}:{args.tag}",
                        build_args=Podman.parse_build_args_list(args.build_arg),
                    )
                else:
                    build_result_data = podman.build_and_save_oci_archive(
                        args.directory,
                        args.oci_archive,
                        podman=podman_context,
                        platform=args.platform,
                        oci_tag=f"{args.repository}:{args.tag}",
                        build_args=Podman.parse_build_args_list(args.build_arg),
                    )

                    _, image_id = build_result_data.popitem()

                if args.additional_tag is not None:
                    podman.tag_list(
                        image_id,
                        Podman.get_image_tag_list(args.repository, args.additional_tag),
                    )

            print(image_id)
        case "load-image":
            podman = Podman()

            with PodmanContext() as podman_context:
                image_id = podman.load_oci_archive(
                    args.oci_archive, podman=podman_context
                )

                if args.additional_tag is not None:
                    podman.tag_list(
                        image_id, args.additional_tag, podman=podman_context
                    )

            print(image_id)
        case "load-images-from-directory":
            result = Podman().load_oci_archives_from_directory(args.directory)
            print(json.dumps(result))
        case "new-index":
            index_resource = Repository(
                f"{args.index}:{args.index_tag}", insecure=args.insecure
            )

            image_index = index_resource.generate_index()
            index_resource.push_index(image_index)
            index_resource.push_index_for_tags(image_index, args.additional_tag)
        case "pull-image":
            image_id = Podman(insecure=args.insecure).pull(
                args.repository, oci_tag=args.tag, platform=args.platform
            )
            print(image_id)
        case "push-image":
            Podman(insecure=args.insecure).push(
                args.repository, oci_tag=args.tag, destination=args.destination
            )
        case "push-index-from-directory":
            index_resource = Repository(
                f"{args.index}:{args.index_tag}", insecure=args.insecure
            )
            index_resource.push_index_from_directory(
                args.directory, args.additional_tag
            )
        case "push-index-tags":
            index_resource = Repository(
                f"{args.index}:{args.index_tag}", insecure=args.insecure
            )

            image_index = index_resource.read_or_generate_index()
            index_resource.push_index_for_tags(image_index, args.tag)
        case "push-manifest":
            repository = Repository(
                f"{args.repository}:{args.version}", insecure=args.insecure
            )

            manifest = repository.read_or_generate_manifest(
                args.cname, args.arch, args.version, args.commit
            )

            if not isinstance(manifest, ImageManifest):
                raise RuntimeError("Data given for OCI image manifest is incomplete")

            repository.push_manifest_and_artifacts_from_directory(
                manifest, args.directory, args.manifest_file, args.additional_tag
            )

            if args.cosign_file:
                print(manifest.digest, file=open(args.cosign_file, "w"))
        case "push-manifest-tags":
            repository = Repository(
                f"{args.repository}:{args.version}", insecure=args.insecure
            )

            manifest = repository.read_or_generate_manifest(
                args.cname, args.arch, args.version, args.commit
            )

            repository.push_manifest_for_tags(manifest, args.tag)
        case "save-image":
            podman = Podman()

            image_id = podman.get_image_id(args.repository, oci_tag=args.tag)
            podman.save_oci_archive(image_id, args.oci_archive, oci_tag=args.tag)
        case "tag-image":
            podman = Podman()

            with PodmanContext() as podman_context:
                image_id = podman.get_image_id(
                    args.repository, podman=podman_context, oci_tag=args.tag
                )

                if args.additional_tag is not None:
                    podman.tag_list(
                        image_id,
                        Podman.get_image_tag_list(args.repository, args.additional_tag),
                        podman=podman_context,
                    )


if __name__ == "__main__":
    main()
