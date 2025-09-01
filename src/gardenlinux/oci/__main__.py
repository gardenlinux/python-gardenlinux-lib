#!/usr/bin/env python3

"""
gl-oci main entrypoint
"""

import os
import click

from pygments.lexer import default

from .container import Container


@click.group()
def cli():
    """
    gl-oci click argument entrypoint

    :since: 0.7.0
    """

    pass


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
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--cname",
    required=False,
    type=click.Path(),
    default=None,
    help="Canonical Name of Image"
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
    container,
    cname,
    arch,
    version,
    commit,
    insecure,
    tag,
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
    container.push_manifest_for_tags(manifest, tag)


@cli.command()
@click.option(
    "--container",
    "container",
    required=True,
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--version",
    "version",
    required=True,
    type=click.Path(),
    help="Version of image",
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
