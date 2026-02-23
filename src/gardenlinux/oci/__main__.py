#!/usr/bin/env python3

"""
gl-oci main entrypoint
"""

from typing import List

import click

from .container import Container
from .image_manifest import ImageManifest


@click.group()
def cli() -> None:
    """
    gl-oci click argument entrypoint

    :since: 0.7.0
    """

    pass


@cli.command()
@click.option(
    "--index",
    required=True,
    help="OCI image index",
)
@click.option(
    "--index-tag",
    required=True,
    help="OCI image index tag",
)
@click.option(
    "--manifest_folder",
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
def push_index_from_directory(
    index: str,
    index_tag: str,
    manifest_folder: str,
    insecure: bool,
    additional_tag: List[str],
) -> None:
    """
    Push a list of files from the `manifest_folder` to an index.

    :since: 0.10.9
    """

    index = Container(f"{index}:{index_tag}", insecure=insecure)
    index.push_index_from_directory(manifest_folder, additional_tag)


@cli.command()
@click.option(
    "--index",
    required=True,
    help="OCI image index",
)
@click.option(
    "--index-tag",
    required=True,
    help="OCI image index tag",
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
    help="Tag to push the OCI image index with",
)
def push_index_tags(index: str, index_tag: str, insecure: bool, tag: List[str]) -> None:
    """
    Push OCI image index tags to a registry.

    :since: 0.10.9
    """

    index = Container(f"{index}:{index_tag}", insecure=insecure)

    image_index = index.read_or_generate_index()
    index.push_index_for_tags(image_index, tag)


@cli.command()
@click.option(
    "--container",
    required=True,
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--cname", required=True, type=click.Path(), help="Canonical Name of Image"
)
@click.option(
    "--arch",
    required=False,
    type=click.Path(),
    default=None,
    help="Target Image CPU Architecture",
)
@click.option(
    "--version",
    required=False,
    type=click.Path(),
    default=None,
    help="Version of image",
)
@click.option(
    "--commit",
    required=False,
    type=click.Path(),
    default=None,
    help="Commit of image",
)
@click.option("--dir", "directory", required=True, help="path to the build artifacts")
@click.option(
    "--cosign_file",
    required=False,
    help="A file where the pushed manifests digests is written to. The content can be used by an external tool (e.g. cosign) to sign the manifests contents",
)
@click.option(
    "--manifest_file",
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
    container: str,
    cname: str,
    arch: str,
    version: str,
    commit: str,
    directory: str,
    cosign_file: str,
    manifest_file: str,
    insecure: bool,
    additional_tag: List[str],
) -> None:
    """
    Push artifacts and the manifest from a directory to a registry.

    :since: 0.7.0
    """

    container = Container(f"{container}:{version}", insecure=insecure)

    manifest = container.read_or_generate_manifest(cname, arch, version, commit)

    if not isinstance(manifest, ImageManifest):
        raise RuntimeError("Data given for OCI image manifest is incomplete")

    container.push_manifest_and_artifacts_from_directory(
        manifest, directory, manifest_file, additional_tag
    )

    if cosign_file:
        print(manifest.digest, file=open(cosign_file, "w"))


@cli.command()
@click.option(
    "--container",
    required=True,
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--cname",
    required=False,
    type=click.Path(),
    default=None,
    help="Canonical Name of Image",
)
@click.option(
    "--arch",
    required=False,
    type=click.Path(),
    default=None,
    help="Target Image CPU Architecture",
)
@click.option(
    "--version",
    required=False,
    type=click.Path(),
    default=None,
    help="Version of image",
)
@click.option(
    "--commit",
    required=False,
    type=click.Path(),
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
def push_manifest_tags(
    container: str,
    cname: str,
    arch: str,
    version: str,
    commit: str,
    insecure: bool,
    tag: List[str],
) -> None:
    """
    Push artifacts and the manifest from a directory to a registry.

    :since: 0.10.0
    """

    container = Container(f"{container}:{version}", insecure=insecure)

    manifest = container.read_or_generate_manifest(cname, arch, version, commit)
    container.push_manifest_for_tags(manifest, tag)


def main() -> None:
    """
    gl-oci main()

    :since: 0.7.0
    """

    cli()


if __name__ == "__main__":
    cli()
