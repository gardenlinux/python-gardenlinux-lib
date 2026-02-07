# -*- coding: utf-8 -*-

"""
OCI container
"""

import json
import logging
from base64 import b64encode
from collections.abc import Sequence
from configparser import UNNAMED_SECTION, ConfigParser
from os import PathLike, fdopen, getenv
from pathlib import Path
from tempfile import mkstemp
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

import jsonschema
from oras.container import Container as OrasContainer
from oras.provider import Registry
from oras.utils import extract_targz, make_targz
from requests import HTTPError, Response

from ..constants import OCI_IMAGE_INDEX_MEDIA_TYPE
from ..features.cname import CName
from ..logger import LoggerSetup
from .image_manifest import ImageManifest
from .index import Index
from .layer import Layer
from .manifest import Manifest
from .schemas import index as IndexSchema


class Container(Registry):  # type: ignore[misc]
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

        container_data = container_url.rsplit(":", 1)

        if len(container_data) < 2:
            raise RuntimeError("Container name given is invalid")

        self._container_version = container_data[1]

        if "://" in container_data[0]:
            scheme = container_data[0].split(":", 1)[0].lower()
            insecure = scheme != "https"

            self._container_url = container_data[0]
        else:
            scheme = "http" if insecure else "https"

            self._container_url = f"{scheme}://{container_data[0]}"

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
                self._logger.debug("Logging in with username/password")

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
    ) -> ImageManifest:
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

        manifest.version = version  # type: ignore[assignment]
        manifest.cname = cname
        manifest.arch = architecture  # type: ignore[assignment]
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

    def generate_index(self) -> Index:
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
    ) -> Manifest:
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

        manifest.version = version  # type: ignore[assignment]
        manifest.commit = commit  # type: ignore[assignment]

        manifest.config_from_dict({}, {})

        return manifest

    def _get_index_without_response_parsing(self) -> Response:
        """
        Return the response of an OCI image index request.

        :return: (object) OCI image index request response
        :since:  0.7.0
        """

        manifest_url = self.get_container(
            f"{self._container_name}:{self._container_version}"
        ).manifest_url()

        return self.do_request(  # type: ignore[no-any-return]
            f"{self.prefix}://{manifest_url}",
            headers={"Accept": OCI_IMAGE_INDEX_MEDIA_TYPE},
        )

    def _get_manifest_without_response_parsing(self, reference: str) -> Response:
        """
        Return the response of an OCI image manifest request.

        :return: (object) OCI image manifest request response
        :since:  0.7.0
        """

        return self.do_request(  # type: ignore[no-any-return]
            f"{self.prefix}://{self.hostname}/v2/{self._container_name}/manifests/{reference}",
            headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
        )

    def push_index(self, index: Index, tag: Optional[str] = None) -> None:
        """
        Replaces an old manifest entries with new ones

        :param manifests_dir:   Directory where the manifest entries are read from
        :param additional_tags: Additional tags to push the index with

        :since: 1.0.0
        """

        index_kwargs = {}

        if tag is not None:
            index_kwargs["reference"] = tag

        self._check_200_response(self._upload_index(index, **index_kwargs))

    def push_index_from_directory(
        self,
        manifests_dir: PathLike[str] | str,
        additional_tags: Optional[List[str]] = None,
    ) -> None:
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

        for file_path_name in manifests_dir.iterdir():  # type: ignore[attr-defined]
            with open(file_path_name, "r") as fp:
                manifest = json.loads(fp.read())

            if manifest["annotations"]["cname"] in index.manifests_as_dict:
                existing_manifest = index.manifests_as_dict[
                    manifest["annotations"]["cname"]
                ]

                if manifest["digest"] == existing_manifest["digest"]:
                    self._logger.debug(
                        f"Skipping manifest with digest {manifest['digest']} - already exists"
                    )

                    continue

            index.append_manifest(manifest)

            self._logger.info(
                f"Index appended locally {manifest['annotations']['cname']}"
            )

            new_entries += 1

        self.push_index(index)
        self._logger.info(f"Index pushed with {new_entries} new entries")

        if isinstance(additional_tags, Sequence) and len(additional_tags) > 0:
            self._logger.info(f"Processing {len(additional_tags)} additional tags")

            self.push_index_for_tags(
                index,
                additional_tags,
            )

    def push_index_for_tags(self, index: Index, tags: List[str]) -> None:
        """
        Push tags for an given OCI image index.

        :param index: OCI image index
        :param tags:  List of tags to push the index for

        :since: 0.7.0
        """

        # For each additional tag, push the manifest using Registry.upload_manifest
        for tag in tags:
            self.push_index(index, tag)

    def push_manifest(
        self,
        manifest: Manifest,
        manifest_file: Optional[str] = None,
        additional_tags: Optional[List[str]] = None,
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

        manifest_url = f"{self._container_url}:{self._container_version}"

        if isinstance(manifest, ImageManifest):
            manifest_url += f"-{manifest.cname}-{manifest.arch}"

        manifest_container = OrasContainer(manifest_url)

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

        if manifest_file is not None and isinstance(manifest, ImageManifest):
            manifest.write_metadata_file(manifest_file)
            self._logger.info(f"Index entry written to {manifest_file}")

        return manifest

    def push_manifest_and_artifacts(
        self,
        manifest: ImageManifest,
        artifacts_with_metadata: list[Dict[str, Any]],
        artifacts_dir: PathLike[str] | str = ".build",
        manifest_file: Optional[str] = None,
        additional_tags: Optional[List[str]] = None,
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

        if not isinstance(manifest, ImageManifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        if not isinstance(artifacts_dir, PathLike):
            artifacts_dir = Path(artifacts_dir)

        container_name = f"{self._container_name}:{self._container_version}"

        # For each file, create sign, attach and push a layer
        for artifact in artifacts_with_metadata:
            file_path_name = artifacts_dir.joinpath(artifact["file_name"])  # type: ignore[attr-defined]

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
                    f"Pushed {artifact['file_name']}: {layer_dict['digest']}"
                )
            finally:
                if cleanup_blob and file_path_name.exists():
                    file_path_name.unlink()

        self.push_manifest(manifest, manifest_file, additional_tags)

        return manifest

    def push_manifest_and_artifacts_from_directory(
        self,
        manifest: ImageManifest,
        artifacts_dir: PathLike[str] | str = ".build",
        manifest_file: Optional[str] = None,
        additional_tags: Optional[List[str]] = None,
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

        if not isinstance(manifest, ImageManifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        # Scan and extract nested artifacts
        for file_path_name in artifacts_dir.glob("*.pxe.tar.gz"):  # type: ignore[attr-defined]
            self._logger.info(f"Found nested artifact {file_path_name}")
            extract_targz(file_path_name, artifacts_dir)

        files = [
            file_name
            for file_name in artifacts_dir.iterdir()  # type: ignore[attr-defined]
            if file_name.is_file()
        ]

        artifacts_with_metadata = Container.get_artifacts_metadata_from_files(
            files, manifest.arch
        )

        for artifact in artifacts_with_metadata:
            if artifact["media_type"] == "application/io.gardenlinux.release":
                artifact_config = ConfigParser(allow_unnamed_section=True)
                artifact_config.read(artifacts_dir.joinpath(artifact["file_name"]))  # type: ignore[attr-defined]

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

    def push_manifest_for_tags(self, manifest: Manifest, tags: List[str]) -> None:
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

    def read_index(self) -> Index:
        """
        Reads the OCI image index from registry.

        :return: OCI image manifest
        :since:  1.0.0
        """

        response = self._get_index_without_response_parsing()

        if response.ok:
            index = Index(**response.json())
        else:
            response.raise_for_status()

        return index

    def read_manifest(
        self,
        cname: Optional[str] = None,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
    ) -> Manifest:
        """
        Reads the OCI manifest from registry.

        :param cname: Canonical name of the manifest
        :param architecture: Target architecture of the manifest
        :param version: Artifacts version of the manifest

        :return: OCI image manifest
        :since:  1.0.0
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
        else:
            response.raise_for_status()

        return manifest

    def read_or_generate_index(self) -> Index:
        """
        Reads from registry or generates the OCI image index.

        :return: OCI image index
        :since:  0.7.0
        """

        try:
            index = self.read_index()
        except HTTPError as exc:
            if exc.response.status_code != 404:
                raise

            index = self.generate_index()

        return index

    def read_or_generate_manifest(
        self,
        cname: Optional[str] = None,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
        commit: Optional[str] = None,
        feature_set: Optional[str] = None,
    ) -> Manifest | ImageManifest:
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

        try:
            manifest = self.read_manifest(cname, architecture, version)
        except HTTPError as exc:
            if exc.response.status_code != 404:
                raise

            if cname is None:
                manifest = self.generate_manifest(version, commit)
            else:
                manifest = self.generate_image_manifest(
                    cname, architecture, version, commit, feature_set
                )

        return manifest

    def _upload_index(self, index: Index, reference: Optional[str] = None) -> Response:
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

        return self.do_request(  # type: ignore[no-any-return]
            f"{self.prefix}://{self.hostname}/v2/{self._container_name}/manifests/{reference}",
            "PUT",
            headers={"Content-Type": OCI_IMAGE_INDEX_MEDIA_TYPE},
            data=index.json,
        )

    @staticmethod
    def get_artifacts_metadata_from_files(
        files: List[str], arch: str
    ) -> List[Dict[str, Any]]:
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
