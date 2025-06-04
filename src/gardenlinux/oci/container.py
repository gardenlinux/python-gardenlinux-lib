# -*- coding: utf-8 -*-

import json
import jsonschema
import logging
from base64 import b64encode
from configparser import ConfigParser, UNNAMED_SECTION
from collections.abc import Sequence
from hashlib import sha256
from oras.container import Container as OrasContainer
from oras.defaults import unknown_config_media_type as UNKNOWN_CONFIG_MEDIA_TYPE
from oras.provider import Registry
from oras.utils import make_targz, extract_targz
from os import fdopen, getenv, PathLike
from pathlib import Path
from requests import Response
from tempfile import mkstemp
from typing import Optional
from urllib.parse import urlsplit

from ..constants import GL_MEDIA_TYPE_LOOKUP, OCI_IMAGE_INDEX_MEDIA_TYPE
from ..features.cname import CName
from ..logger import LoggerSetup

from .index import Index
from .layer import Layer
from .manifest import Manifest
from .schemas import index as IndexSchema


class Container(Registry):
    def __init__(
        self,
        container_url: str,
        insecure: bool = False,
        token: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
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

        Registry.__init__(
            self,
            hostname=container_url_data.netloc,
            auth_backend="token",
            insecure=insecure,
        )

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._container_name = container_url_data.path[1:]
        self._logger = logger

        if token is None:
            token = getenv("GL_CLI_REGISTRY_TOKEN")

        if token is not None:
            self._token = b64encode(token.encode("utf-8")).decode("utf-8")
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

    def generate_index(self):
        """
        Generates an image index
        """

        return Index()

    def generate_manifest(
        self,
        cname: str,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
        commit: Optional[str] = None,
        feature_set: Optional[str] = None,
    ):
        """
        Generates an image manifest

        :param str cname: Canonical name of the manifest
        :param str architecture: Target architecture of the manifest
        :param str version: Artifacts version of the manifest
        :param str commit: The commit hash of the manifest
        :param str feature_set: The expanded list of the included features of this manifest
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

        manifest = Manifest()

        manifest["annotations"] = {}
        manifest["annotations"]["version"] = version
        manifest["annotations"]["cname"] = cname
        manifest["annotations"]["architecture"] = architecture
        manifest["annotations"]["feature_set"] = feature_set
        manifest["annotations"]["flavor"] = f"{cname_object.flavor}-{architecture}"
        manifest["annotations"]["commit"] = commit

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

    def _get_index_without_response_parsing(self):
        manifest_url = self.get_container(
            f"{self._container_name}:{self._container_version}"
        ).manifest_url()

        return self.do_request(
            f"{self.prefix}://{manifest_url}",
            headers={"Accept": OCI_IMAGE_INDEX_MEDIA_TYPE},
        )

    def _get_manifest_without_response_parsing(self, reference):
        return self.do_request(
            f"{self.prefix}://{self.hostname}/v2/{self._container_name}/manifests/{reference}",
            headers={"Accept": "application/vnd.oci.image.manifest.v1+json"},
        )

    def push_index_from_directory(
        self, manifests_dir: PathLike | str, additional_tags: list = None
    ):
        """
        Replaces an old manifest entries with new ones

        :param str manifest_folder: the folder where the manifest entries are read from
        :param list additional_tags: the additional tags to push the index with
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
        Push tags for an given index.

        :param manifest: Image manifest
        :param tags: List of tags to push the manifest for
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
        Pushes an image manifest and its artifacts.

        :param manifest: Image manifest
        :param artifacts_with_metadata: A list of file names and their artifacts metadata
        :param str artifacts_dir: Path of the image artifacts
        :param str feature_set: The expanded list of the included features of this manifest
        :param str manifest_file: The file name where the modified manifest is written to
        :param list additional_tags: Additional tags to push the manifest with
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
        Pushes an image manifest and its artifacts.

        :param manifest: Image manifest
        :param artifacts_with_metadata: A list of file names and their artifacts metadata
        :param str artifacts_dir: Path of the image artifacts
        :param str feature_set: The expanded list of the included features of this manifest
        :param str manifest_file: The file name where the modified manifest is written to
        :param list additional_tags: Additional tags to push the manifest with
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
                layer_dict = layer.to_dict()

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
        if not isinstance(artifacts_dir, PathLike):
            artifacts_dir = Path(artifacts_dir)

        if not isinstance(manifest, Manifest):
            raise RuntimeError("Artifacts image manifest given is invalid")

        files = [
            file_name for file_name in artifacts_dir.iterdir() if file_name.is_file()
        ]

        # Scan and extract nested artifacts
        for file_path_name in files:
            if file_path_name.match("*.pxe.tar.gz"):
                self._logger.info(f"Found nested artifact {file_path_name}")
                extract_targz(file_path_name, artifacts_dir)

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
        Push tags for an given manifest.

        :param manifest: Image manifest
        :param tags: List of tags to push the manifest for
        """

        # For each additional tag, push the manifest using Registry.upload_manifest
        for tag in tags:
            manifest_container = OrasContainer(f"{self._container_url}:{tag}")

            self._check_200_response(self.upload_manifest(manifest, manifest_container))

    def read_or_generate_index(self):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
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
        cname: str,
        architecture: Optional[str] = None,
        version: Optional[str] = None,
        commit: Optional[str] = None,
        feature_set: Optional[str] = None,
    ) -> Manifest:
        """
        Reads an image manifest from registry or generates it if not found.

        :param str cname: canonical name of the manifest
        :param str architecture: target architecture of the manifest
        :param str version: artifacts version of the manifest
        :param str commit: the commit hash of the manifest
        :param str feature_set: The expanded list of the included features of this manifest
        """

        if architecture is None:
            architecture = CName(cname, architecture, version).arch

        response = self._get_manifest_without_response_parsing(
            f"{self._container_version}-{cname}-{architecture}"
        )

        if response.ok:
            manifest = Manifest(**response.json())
        elif response.status_code == 404:
            manifest = self.generate_manifest(
                cname, architecture, version, commit, feature_set
            )
        else:
            response.raise_for_status()

        return manifest

    def _upload_index(self, index: dict, reference: Optional[str] = None) -> Response:
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
        :param str arch: arch of the target image
        :param set files: a list of filenames (not paths) to set oci_metadata for
        :return: list of dicts, where each dict represents a layer
        """

        artifacts_with_metadata = []

        for file_name in files:
            artifacts_with_metadata.append(
                Layer.generate_metadata_from_file_name(file_name, arch)
            )

        return artifacts_with_metadata
