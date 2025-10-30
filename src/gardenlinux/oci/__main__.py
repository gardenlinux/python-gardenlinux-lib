#!/usr/bin/env python3

"""
gl-oci main entrypoint
"""

import json

import click

from .container import Container
from .podman import Podman
from .podman_context import PodmanContext


@click.group()
def cli():
    """
    gl-oci click argument entrypoint

    :since: 0.7.0
    """

    pass


@cli.command()
@click.option(
    "--index",
    required=True,
    help="OCI image index name",
)
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=True,
    help="OCI tag of image",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the index with",
)
def add_container_to_index(index, container, tag, additional_tag):
    """
    Adds an image container to an OCI image index.

    :since: 0.11.0
    """

    manifest_container = Container(f"{container}:{tag}")

    manifest = manifest_container.read_manifest()

    index_container = Container(index)

    index = index_container.read_or_generate_index()
    index.append_manifest(manifest_container)

    index_container.push_index(index, additional_tag)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=True,
    help="OCI tag of image",
)
@click.option(
    "--dir",
    "directory",
    required=True,
    type=click.Path(),
    help="Path to the build Containerfile",
)
@click.option(
    "--platform",
    required=False,
    help="OCI platform as os/arch/variant",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the manifest with",
)
@click.option(
    "--build_arg",
    required=False,
    default=[],
    multiple=True,
    help="Additional build args for Containerfile",
)
@click.option(
    "--oci_archive",
    required=False,
    help="Write build result to the OCI archive path and file name",
)
def build_container(
    container, tag, directory, platform, additional_tag, build_arg, oci_archive
):
    """
    Build an OCI container based on the defined `Containerfile`.

    :since: 0.11.0
    """

    podman = Podman()

    with PodmanContext() as podman_context:
        if oci_archive is None:
            image_id = podman.build(
                directory,
                podman=podman_context,
                platform=platform,
                oci_tag=f"{container}:{tag}",
                build_args=Podman.parse_build_args_list(build_arg),
            )
        else:
            build_result_data = podman.build_and_save_oci_archive(
                directory,
                oci_archive,
                podman=podman_context,
                platform=platform,
                oci_tag=f"{container}:{tag}",
                build_args=Podman.parse_build_args_list(build_arg),
            )

            _, image_id = build_result_data.popitem()

        if additional_tag is not None:
            podman.tag_list(
                image_id, Podman.get_container_tag_list(container, additional_tag)
            )

    print(image_id)


@cli.command()
@click.option(
    "--oci_archive",
    required=False,
    help="Write build result to the OCI archive path and file name",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the manifest with",
)
def load_container(oci_archive, additional_tag):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    podman = Podman()

    with PodmanContext() as podman_context:
        image_id = podman.load_oci_archive(oci_archive, podman=podman_context)

        if additional_tag is not None:
            podman.tag_list(image_id, additional_tag, podman=podman_context)

    print(image_id)


@cli.command()
@click.option(
    "--dir",
    "directory",
    required=True,
    type=click.Path(),
    help="path to the build artifacts",
)
def load_containers_from_directory(directory):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    result = Podman().load_oci_archives_from_directory(directory)
    print(json.dumps(result))


@cli.command()
@click.option(
    "--index",
    required=True,
    help="OCI image index name",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the index with",
)
def new_index(index, additional_tag):
    """
    Push a list of files from the `manifest_folder` to an index.

    :since: 0.7.0
    """

    index = index_container.generate_index()
    index_container.push_index(index, additional_tag)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=False,
    help="OCI tag of image",
)
@click.option(
    "--platform",
    required=False,
    help="OCI platform as os/arch/variant",
)
def pull_container(container, tag, platform):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    image_id = Podman().pull(container, oci_tag=tag, platform=platform)
    print(image_id)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=False,
    help="OCI tag of image",
)
@click.option(
    "--destination",
    required=False,
    help="OCI container destination",
)
def push_container(container, tag, destination):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    Podman().push(container, oci_tag=tag, destination=destination)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option("--cname", required=True, help="Canonical Name of Image")
@click.option(
    "--arch",
    required=False,
    default=None,
    help="Target Image CPU Architecture",
)
@click.option(
    "--version",
    required=False,
    default=None,
    help="Version of image",
)
@click.option(
    "--commit",
    required=False,
    default=None,
    help="Commit of image",
)
@click.option(
    "--dir",
    "directory",
    required=True,
    type=click.Path(),
    help="path to the build artifacts",
)
@click.option(
    "--cosign_file",
    required=False,
    help="A file where the pushed manifests digests is written to. The content can be used by an external tool (e.g. cosign) to sign the manifests contents",
)
@click.option(
    "--manifest_file",
    type=click.Path(),
    default="manifests/manifest.json",
    help="A file where the index entry for the pushed manifest is written to.",
)
@click.option(
    "--insecure",
    default=False,
    help="Use HTTP to communicate with the registry",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the manifest with",
)
def push_manifest(
    container,
    cname,
    arch,
    version,
    commit,
    directory,
    cosign_file,
    manifest_file,
    insecure,
    additional_tag,
):
    """
    Push artifacts and the manifest from a directory to a registry.

    :since: 0.7.0
    """

    container = Container(
        f"{container}:{version}",
        insecure=insecure,
    )

    manifest = container.read_or_generate_manifest(cname, arch, version, commit)

    container.push_manifest_and_artifacts_from_directory(
        manifest, directory, manifest_file, additional_tag
    )

    if cosign_file:
        print(manifest.digest, file=open(cosign_file, "w"))


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--cname",
    required=False,
    default=None,
    help="Canonical Name of Image",
)
@click.option(
    "--arch",
    required=False,
    default=None,
    help="Target Image CPU Architecture",
)
@click.option(
    "--version",
    required=False,
    default=None,
    help="Version of image",
)
@click.option(
    "--commit",
    required=False,
    default=None,
    help="Commit of image",
)
@click.option(
    "--insecure",
    default=False,
    help="Use HTTP to communicate with the registry",
)
@click.option(
    "--tag",
    required=True,
    multiple=True,
    help="Tag to push the manifest with",
)
def push_manifest_tags(container, cname, arch, version, commit, insecure, tag):
    """
    Push artifacts and the manifest from a directory to a registry.

    :since: 0.10.0
    """

    container = Container(
        f"{container}:{version}",
        insecure=insecure,
    )

    manifest = container.read_or_generate_manifest(cname, arch, version, commit)
    container.push_manifest_for_tags(manifest, tag)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=False,
    help="OCI tag of image",
)
@click.option(
    "--oci_archive",
    required=False,
    help="Write build result to the OCI archive path and file name",
)
def save_container(container, tag, oci_archive):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    podman = Podman()

    image_id = podman.get_image_id(container, oci_tag=tag)
    podman.save_oci_archive(image_id, oci_archive, oci_tag=tag)


@cli.command()
@click.option(
    "--container",
    required=True,
    help="Container Name",
)
@click.option(
    "--tag",
    required=False,
    help="OCI tag of image",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the manifest with",
)
def tag_container(container, tag, additional_tag):
    """
    Push to an OCI registry.

    :since: 0.11.0
    """

    podman = Podman()

    image_id = podman.get_image_id(container, oci_tag=tag)

    if additional_tag is not None:
        podman.tag_list(
            image_id, Podman.get_container_tag_list(container, additional_tag, podman=podman_context)
        )


@cli.command()
@click.option(
    "--container",
    "container",
    required=True,
    help="Container Name",
)
@click.option(
    "--version",
    "version",
    required=True,
    help="Version of image",
)
@click.option(
    "--manifest_folder",
    type=click.Path(),
    default="manifests",
    help="A folder where the index entries are read from.",
)
@click.option(
    "--insecure",
    default=False,
    help="Use HTTP to communicate with the registry",
)
@click.option(
    "--additional_tag",
    required=False,
    multiple=True,
    help="Additional tag to push the index with",
)
def update_index(container, version, manifest_folder, insecure, additional_tag):
    """
    Push a list of files from the `manifest_folder` to an index.

    :since: 0.7.0
    """

    container = Container(
        f"{container}:{version}",
        insecure=insecure,
    )

    container.push_index_from_directory(manifest_folder, additional_tag)


def main():
    """
    gl-oci main()

    :since: 0.7.0
    """

    cli()


if __name__ == "__main__":
    cli()
