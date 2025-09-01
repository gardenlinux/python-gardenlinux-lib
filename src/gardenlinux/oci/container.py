# -*- coding: utf-8 -*-

"""
OCI container
"""

import json
import logging
from base64 import b64encode
from collections.abc import Sequence
from configparser import UNNAMED_SECTION, ConfigParser
from hashlib import sha256
from os import PathLike, fdopen, getenv
from pathlib import Path
from tempfile import mkstemp
from typing import Optional
from urllib.parse import urlsplit

import jsonschema
from oras.container import Container as OrasContainer
from oras.defaults import unknown_config_media_type as UNKNOWN_CONFIG_MEDIA_TYPE
from oras.provider import Registry
from oras.utils import extract_targz, make_targz
from requests import Response

from ..constants import GL_MEDIA_TYPE_LOOKUP, OCI_IMAGE_INDEX_MEDIA_TYPE
from ..features.cname import CName
from ..logger import LoggerSetup
from .index import Index
from .layer import Layer
from .image_manifest import ImageManifest
from .manifest import Manifest
from .schemas import index as IndexSchema


class Container(Registry):
    """
    OCI container instance to provide methods for interaction.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        container_url: str,
        insecure: bool = False,
        token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(Container)

        :param container_url: OCI container URL
        :param insecure: True if access is provided via HTTP without encryption
        :param token: OCI access token
        :param logger: Logger instance

        :since: 0.7.0
        """

        if "://" in container_url:
            container_data = container_url.rsplit(":", 2)

            if len(container_data) < 3:
                raise RuntimeError("Container name given is invalid")

            self._container_url = f"{container_data[0]}:{container_data[1]}"
            self._container_version = container_data[2]
        else:
            container_data = container_url.rsplit(":", 1)

            if len(container_data) < 2:
                raise RuntimeError("Container name given is invalid")

            scheme = "http" if insecure else "https"

            self._container_url = f"{scheme}://{container_data[0]}"
            self._container_version = container_data[1]

        container_url_data = urlsplit(self._container_url)
        self._token = None

        if token is None:
            token = getenv("GL_CLI_REGISTRY_TOKEN")

        if token is not None:
            auth_backend = "token"
            self._token = b64encode(token.encode("utf-8")).decode("utf-8")
        else:
            auth_backend = "basic"

        Registry.__init__(
            self,
            hostname=container_url_data.netloc,
            auth_backend=auth_backend,
            insecure=insecure,
        )

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._container_name = container_url_data.path[1:]
        self._logger = logger

        if self._token is not None:
            self.auth.set_token_auth(self._token)
        else:
            # Authentication credentials from environment
            username = getenv("GL_CLI_REGISTRY_USERNAME")
            password = getenv("GL_CLI_REGISTRY_PASSWORD")

            # Login to registry if credentials are provided
            if username and password:
                self._logger.debug(f"Logging in with username/password")

                try:
                    self.login(username, password)
                except Exception as login_error:
                    self._logger.error(f"Login error: {str(login_error)}")

    def generate_image_manifest(
        self,
        cname: str,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
        commit: Optional[str] = None,
        feature_set: Optional[str] = None,
    ):
        """
        Generates an OCI image manifest

        :param cname: Canonical name of the manifest
        :param architecture: Target architecture of the manifest
        :param version: Artifacts version of the manifest
        :param commit: The commit hash of the manifest
        :param feature_set: The expanded list of the included features of this manifest

        :return: (object) OCI image manifest
        :since:  0.10.0
        """

        cname_object = CName(cname, architecture, version)

        if architecture is None:
            architecture = cname_object.arch
        if version is None:
            version = cname_object.version
        if commit is None:
            commit = cname_object.commit_id
        if feature_set is None:
            feature_set = cname_object.feature_set

        if commit is None:
            commit = ""

        manifest = ImageManifest()

        manifest.version = version
        manifest.cname = cname
        manifest.arch = architecture
        manifest.feature_set = feature_set
        manifest.commit = commit

        description = (
            f"Image: {cname} "
            f"Flavor: {cname_object.flavor} "
            f"Architecture: {architecture} "
            f"Features: {feature_set} "
            f"Commit: {commit} "
        )

        manifest["annotations"]["org.opencontainers.image.description"] = description

        manifest.config_from_dict(
            {},
            {"cname": cname, "architecture": architecture},
        )

        return manifest

    def generate_index(self):
        """
        Generates an OCI image index

        :return: (object) OCI image index
        :since:  0.7.0
        """

        return Index()

    def generate_manifest(
        self,
        version: Optional[str] = None,
        commit: Optional[str] = None,
    ):
        """
        Generates an OCI manifest

        :param cname: Canonical name of the manifest
        :param architecture: Target architecture of the manifest
        :param version: Artifacts version of the manifest
        :param commit: The commit hash of the manifest
        :param feature_set: The expanded list of the included features of this manifest

        :return: (object) OCI manifest
        :since:  0.9.2
        """

        manifest = Manifest()

        manifest.version = version
        manifest.commit = commit

        manifest.config_from_dict({}, {})

        return manifest

    def _get_index_without_response_parsing(self):
        """
        Return the response of an OCI image index request.

        :return: (object) OCI image index request response
        :since:  0.7.0
        """

        manifest_url = self.get_container(
            f"{self._container_name}:{self._container_version}"
        ).manifest_url()

        return self.do_request(
            f"{self.prefix}://{manifest_url}",
            headers={"Accept": OCI_IMAGE_INDEX_MEDIA_TYPE},
        )

    def _get_manifest_without_response_parsing(self, reference):
        """
        Return the response of an OCI image manifest request.

        :return: (object) OCI image manifest request response
        :since:  0.7.0
        """

        return self.do_request(
            f"{self.prefix}://{self.hostname}/v2/{self._container_name}/manifests/{reference}",
            headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
        )

    def push_index_from_directory(
        self, manifests_dir: PathLike | str, additional_tags: list = None
    ):
        """
        Replaces an old manifest entries with new ones

        :param manifests_dir:   Directory where the manifest entries are read from
        :param additional_tags: Additional tags to push the index with

        :since: 0.7.0
        """

        if not isinstance(manifests_dir, PathLike):
            manifests_dir = Path(manifests_dir)

        index = self.read_or_generate_index()

        # Ensure mediaType is set for existing indices
        if "mediaType" not in index:
            index["mediaType"] = OCI_IMAGE_INDEX_MEDIA_TYPE

        new_entries = 0

        for file_path_name in manifests_dir.iterdir():
            with open(file_path_name, "r") as fp:
                manifest = json.loads(fp.read())

            if manifest["annotations"]["cname"] in index.manifests_as_dict:
                existing_manifest = index.manifests_as_dict[
                    manifest["annotations"]["cname"]
                ]

                if manifest["digest"] == existing_manifest["digest"]:
                    self._logger.debug(
                        f"Skipping manifest with digest {manifest["digest"]} - already exists"
                    )

                    continue

            index.append_manifest(manifest)

            self._logger.info(
                f"Index appended locally {manifest["annotations"]["cname"]}"
            )

            new_entries += 1

        self._check_200_response(self._upload_index(index))
        self._logger.info(f"Index pushed with {new_entries} new entries")

        if isinstance(additional_tags, Sequence) and len(additional_tags) > 0:
            self._logger.info(f"Processing {len(additional_tags)} additional tags")

            self.push_index_for_tags(
                index,
                additional_tags,
            )

    def push_index_for_tags(self, index, tags):
        """
        Push tags for an given OCI image index.

        :param index: OCI image index
        :param tags:  List of tags to push the index for

        :since: 0.7.0
        """

        # For each additional tag, push the manifest using Registry.upload_manifest
        for tag in tags:
            self._check_200_response(self._upload_index(index, tag))

    def push_manifest(
        self,
        manifest: Manifest,
        manifest_file: Optional[str] = None,
        additional_tags: Optional[list] = None,
    ) -> Manifest:
        """
        Pushes an OCI image manifest.

        :param manifest:                OCI image manifest
        :param artifacts_with_metadata: A list of file names and their artifacts metadata
        :param manifest_file:           File name where the modified manifest is written to
        :param additional_tags:         Additional tags to push the manifest with

        :return: (object) OCI image manifest
        :since:  0.7.0
        """

        if not isinstance(manifest, Manifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        container_name = f"{self._container_name}:{self._container_version}"

        fd, config_file = mkstemp()

        try:
            with fdopen(fd, mode="wb") as fp:
                fp.write(manifest.config_json)

            self._check_200_response(
                self.upload_blob(config_file, container_name, manifest["config"])
            )

            self._logger.debug(f"Successfully pushed config for {container_name}")
        finally:
            Path(config_file).unlink()

        manifest_container = OrasContainer(
            f"{self._container_url}:{self._container_version}-{manifest.cname}-{manifest.arch}"
        )

        self._check_200_response(self.upload_manifest(manifest, manifest_container))

        self._logger.info(
            f"Successfully pushed {manifest_container} ({manifest.digest})"
        )

        if isinstance(additional_tags, Sequence) and len(additional_tags) > 0:
            self._logger.info(f"Processing {len(additional_tags)} additional tags")

            self.push_manifest_for_tags(
                manifest,
                additional_tags,
            )

        if manifest_file is not None:
            manifest.write_metadata_file(manifest_file)
            self._logger.info(f"Index entry written to {manifest_file}")

        return manifest

    def push_manifest_and_artifacts(
        self,
        manifest: Manifest,
        artifacts_with_metadata: list[dict],
        artifacts_dir: Optional[PathLike | str] = ".build",
        manifest_file: Optional[str] = None,
        additional_tags: Optional[list] = None,
    ) -> Manifest:
        """
        Pushes an OCI image manifest and its artifacts.

        :param manifest:                OCI image manifest
        :param artifacts_with_metadata: A list of file names and their artifacts metadata
        :param artifacts_dir:           Path of the image artifacts
        :param manifest_file:           File name where the modified manifest is written to
        :param additional_tags:         Additional tags to push the manifest with

        :return: (object) OCI image manifest
        :since:  0.7.0
        """

        if not isinstance(manifest, Manifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        if not isinstance(artifacts_dir, PathLike):
            artifacts_dir = Path(artifacts_dir)

        container_name = f"{self._container_name}:{self._container_version}"

        # For each file, create sign, attach and push a layer
        for artifact in artifacts_with_metadata:
            file_path_name = artifacts_dir.joinpath(artifact["file_name"])

            layer = Layer(file_path_name, artifact["media_type"])

            if artifact["annotations"]:
                layer["annotations"].update(artifact["annotations"])

            if not file_path_name.exists():
                raise ValueError(f"{file_path_name} does not exist.")

            cleanup_blob = False

            try:
                if file_path_name.is_dir():
                    file_path_name = Path(make_targz(file_path_name))
                    cleanup_blob = True

                manifest.append_layer(layer)
                layer_dict = layer.dict

                self._logger.debug(f"Layer: {layer_dict}")

                self._check_200_response(
                    self.upload_blob(file_path_name, container_name, layer_dict)
                )

                self._logger.info(
                    f"Pushed {artifact["file_name"]}: {layer_dict["digest"]}"
                )
            finally:
                if cleanup_blob and file_path_name.exists():
                    file_path_name.unlink()

        self.push_manifest(manifest, manifest_file, additional_tags)

        return manifest

    def push_manifest_and_artifacts_from_directory(
        self,
        manifest: Manifest,
        artifacts_dir: Optional[PathLike | str] = ".build",
        manifest_file: Optional[str] = None,
        additional_tags: Optional[list] = None,
    ) -> Manifest:
        """
        Pushes an OCI image manifest and its artifacts from the given directory.

        :param manifest:        OCI image manifest
        :param artifacts_dir:   Path of the image artifacts
        :param manifest_file:   File name where the modified manifest is written to
        :param additional_tags: Additional tags to push the manifest with

        :return: (object) OCI image manifest
        :since:  0.7.0
        """

        if not isinstance(artifacts_dir, PathLike):
            artifacts_dir = Path(artifacts_dir)

        if not isinstance(manifest, Manifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        # Scan and extract nested artifacts
        for file_path_name in artifacts_dir.glob("*.pxe.tar.gz"):
            self._logger.info(f"Found nested artifact {file_path_name}")
            extract_targz(file_path_name, artifacts_dir)

        files = [
            file_name for file_name in artifacts_dir.iterdir() if file_name.is_file()
        ]

        artifacts_with_metadata = Container.get_artifacts_metadata_from_files(
            files, manifest.arch
        )

        for artifact in artifacts_with_metadata:
            if artifact["media_type"] == "application/io.gardenlinux.release":
                artifact_config = ConfigParser(allow_unnamed_section=True)
                artifact_config.read(artifacts_dir.joinpath(artifact["file_name"]))

                if artifact_config.has_option(UNNAMED_SECTION, "GARDENLINUX_FEATURES"):
                    manifest.feature_set = artifact_config.get(
                        UNNAMED_SECTION, "GARDENLINUX_FEATURES"
                    )

                if manifest.commit == "" and artifact_config.has_option(
                    UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID"
                ):
                    manifest.commit = artifact_config.get(
                        UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID"
                    )

        return self.push_manifest_and_artifacts(
            manifest,
            artifacts_with_metadata,
            artifacts_dir,
            manifest_file,
            additional_tags,
        )

    def push_manifest_for_tags(self, manifest, tags):
        """
        Push tags for an given OCI image manifest.

        :param manifest: OCI image manifest
        :param tags:     List of tags to push the index for

        :since: 0.7.0
        """

        # For each additional tag, push the manifest using Registry.upload_manifest
        for tag in tags:
            manifest_container = OrasContainer(f"{self._container_url}:{tag}")

            self._check_200_response(self.upload_manifest(manifest, manifest_container))

    def read_or_generate_index(self):
        """
        Reads from registry or generates the OCI image index.

        :return: OCI image manifest
        :since:  0.7.0
        """

        response = self._get_index_without_response_parsing()

        if response.ok:
            index = Index(**response.json())
        elif response.status_code == 404:
            index = self.generate_index()
        else:
            response.raise_for_status()

        return index

    def read_or_generate_manifest(
        self,
        cname: Optional[str] = None,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
        commit: Optional[str] = None,
        feature_set: Optional[str] = None,
    ) -> Manifest:
        """
        Reads from registry or generates the OCI manifest.

        :param cname: Canonical name of the manifest
        :param architecture: Target architecture of the manifest
        :param version: Artifacts version of the manifest
        :param commit: The Git commit ID of the manifest
        :param feature_set: The expanded list of the included features of this manifest

        :return: OCI image manifest
        :since:  0.7.0
        """

        if cname is None:
            manifest_type = Manifest

            response = self._get_manifest_without_response_parsing(
                self._container_version
            )
        else:
            manifest_type = ImageManifest

            if architecture is None:
                architecture = CName(cname, architecture, version).arch

            response = self._get_manifest_without_response_parsing(
                f"{self._container_version}-{cname}-{architecture}"
            )

        if response.ok:
            manifest = manifest_type(**response.json())
        elif response.status_code == 404:
            if cname is None:
                manifest = self.generate_manifest(version, commit)
            else:
                manifest = self.generate_image_manifest(
                    cname, architecture, version, commit, feature_set
                )
        else:
            response.raise_for_status()

        return manifest

    def _upload_index(self, index: dict, reference: Optional[str] = None) -> Response:
        """
        Uploads the given OCI image index and returns the response.

        :param index:     OCI image index
        :param reference: OCI container reference (tag) to push to

        :return: (object) OCI image index put response
        :since:  0.7.0
        """

        jsonschema.validate(index, schema=IndexSchema)

        if reference is None:
            reference = self._container_version

        return self.do_request(
            f"{self.prefix}://{self.hostname}/v2/{self._container_name}/manifests/{reference}",
            "PUT",
            headers={"Content-Type": OCI_IMAGE_INDEX_MEDIA_TYPE},
            data=index.json,
        )

    @staticmethod
    def get_artifacts_metadata_from_files(files: list, arch: str) -> list:
        """
        Returns OCI layer metadata for the given list of files.

        :param files: a list of filenames (not paths) to set oci_metadata for
        :param arch: arch of the target image

        :return: (list) List of dicts, where each dict represents a layer
        :since:  0.7.0
        """

        artifacts_with_metadata = []

        for file_name in files:
            artifacts_with_metadata.append(
                Layer.generate_metadata_from_file_name(file_name, arch)
            )

        return artifacts_with_metadata
