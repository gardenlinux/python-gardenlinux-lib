#!/usr/bin/env python3

import click
import os

from pygments.lexer import default

from python_gardenlinux_lib.oci.registry import GlociRegistry


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--container",
    required=True,
    type=click.Path(),
    help="Container Name",
)
@click.option(
    "--version",
    required=True,
    type=click.Path(),
    help="Version of image",
)
@click.option(
    "--arch",
    required=True,
    type=click.Path(),
    help="Target Image CPU Architecture",
)
@click.option(
    "--cname", required=True, type=click.Path(), help="Canonical Name of Image"
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
def push_manifest(
    container, version, arch, cname, directory, cosign_file, manifest_file, insecure
):
    """push artifacts from a dir to a registry, get the index-entry for the manifest in return"""
    container_name = f"{container}:{version}"
    registry = GlociRegistry(
        container_name=container_name,
        token=os.getenv("GLOCI_REGISTRY_TOKEN"),
        insecure=insecure,
    )
    digest = registry.push_from_dir(arch, version, cname, directory, manifest_file)
    if cosign_file:
        print(digest, file=open(cosign_file, "w"))


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
def update_index(container, version, manifest_folder, insecure):
    """push a index entry from a list of files to an index"""
    container_name = f"{container}:{version}"
    registry = GlociRegistry(
        container_name=container_name,
        token=os.getenv("GLOCI_REGISTRY_TOKEN"),
        insecure=insecure,
    )
    registry.update_index(manifest_folder)


def main():
    """Entry point for the gl-oci command."""
    cli()


if __name__ == "__main__":
    cli()
