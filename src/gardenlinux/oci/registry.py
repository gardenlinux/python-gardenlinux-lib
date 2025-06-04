# -*- coding: utf-8 -*-

import base64
import configparser
import copy
import hashlib
import json
import logging
import os
import shutil
import sys
import tarfile
import tempfile
import uuid
from enum import Enum, auto
from platform import architecture
from typing import Optional, Tuple

import jsonschema
import oras.auth
import oras.client
import oras.defaults
import oras.oci
import oras.provider
import oras.utils
import requests
from oras.container import Container as OrasContainer
from oras.decorator import ensure_container
from oras.provider import Registry
from oras.schemas import manifest as oras_manifest_schema

from ..constants import OCI_ANNOTATION_SIGNATURE_KEY, OCI_ANNOTATION_SIGNED_STRING_KEY
from ..features import CName
from .checksum import (
    calculate_sha256,
    verify_sha256,
)
from .wrapper import retry_on_error
from python_gardenlinux_lib.features.parse_features import get_oci_metadata_from_fileset
from .schemas import (
    EmptyIndex,
    EmptyManifestMetadata,
    EmptyPlatform,
)
from .schemas import index as indexSchema


class ManifestState(Enum):
    Incomplete = auto()
    Complete = auto()
    Final = auto()


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def get_image_state(manifest: dict) -> str:
    if "annotations" not in manifest:
        logger.warning("No annotations set for manifest.")
        return "UNDEFINED"
    if "image_state" not in manifest["annotations"]:
        logger.warning("No image_state set for manifest.")
        return "UNDEFINED"
    return manifest["annotations"]["image_state"]


def NewPlatform(architecture: str, version: str) -> dict:
    platform = copy.deepcopy(EmptyPlatform)
    platform["architecture"] = architecture
    platform["os.version"] = version
    return platform


def NewManifestMetadata(
    digest: str, size: int, annotations: dict, platform_data: dict
) -> dict:
    manifest_meta_data = copy.deepcopy(EmptyManifestMetadata)
    manifest_meta_data["mediaType"] = "application/vnd.oci.image.manifest.v1+json"
    manifest_meta_data["digest"] = digest
    manifest_meta_data["size"] = size
    manifest_meta_data["annotations"] = annotations
    manifest_meta_data["platform"] = platform_data
    return manifest_meta_data


def NewIndex() -> dict:
    index = copy.deepcopy(EmptyIndex)
    index["mediaType"] = "application/vnd.oci.image.index.v1+json"
    return index


def create_config_from_dict(conf: dict, annotations: dict) -> Tuple[dict, str]:
    """
    Write a new OCI configuration to file, and generate oci metadata for it
    For reference see https://github.com/opencontainers/image-spec/blob/main/config.md
    annotations, mediatype, size, digest are not part of digest and size calculation,
    and therefore must be attached to the output dict and not written to the file.

    :param conf: dict with custom configuration (the payload of the configuration)
    :param annotations: dict with custom annotations to be attached to metadata part of config

    """
    config_path = os.path.join(os.path.curdir, str(uuid.uuid4()))
    with open(config_path, "w") as fp:
        json.dump(conf, fp)
    conf["annotations"] = annotations
    conf["mediaType"] = oras.defaults.unknown_config_media_type
    conf["size"] = oras.utils.get_size(config_path)
    conf["digest"] = f"sha256:{oras.utils.get_file_hash(config_path)}"
    return conf, config_path


def construct_manifest_entry_signed_data_string(
    cname: str, version: str, new_manifest_metadata: dict, architecture: str
) -> str:
    data_to_sign = (
        f"version:{version}  cname:{cname}  architecture:{architecture}  manifest-size"
        f":{new_manifest_metadata['size']}  manifest-digest:{new_manifest_metadata['digest']}"
    )
    return data_to_sign


def construct_layer_signed_data_string(
    cname: str, version: str, architecture: str, media_type: str, checksum_sha256: str
) -> str:
    data_to_sign = f"version:{version}  cname:{cname} architecture:{architecture}  media_type:{media_type}  digest:{checksum_sha256}"
    return data_to_sign


class GlociRegistry(Registry):
    def __init__(
        self,
        container_name: str,
        insecure: bool = False,
        token: Optional[str] = None,
        config_path: Optional[str] = None,
    ):
        super().__init__(auth_backend="token", insecure=insecure)
        self.container = OrasContainer(container_name)
        self.container_name = container_name
        self.registry_url = self.container.registry
        self.config_path = config_path
        if not token:
            logger.info("No Token provided.")
        else:
            self.token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
            self.auth.set_token_auth(self.token)

    @ensure_container
    def get_manifest_json(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        if not allowed_media_type:
            default_image_index_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_index_media_type]
        # self.load_configs(container)
        headers = {"Accept": ";".join(allowed_media_type)}
        headers.update(self.headers)
        get_manifest = f"{self.prefix}://{container.manifest_url()}"
        response = self.do_request(get_manifest, "GET", headers=headers)
        self._check_200_response(response)
        return response

    @ensure_container
    def get_manifest_size(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return 0
        return len(response.content)

    @ensure_container
    def get_digest(
        self, container: OrasContainer, allowed_media_type: Optional[list[str]] = None
    ):
        response = self.get_manifest_json(container, allowed_media_type)
        if response is None:
            return ""
        return f"sha256:{hashlib.sha256(response.content).hexdigest()}"

    def get_index(self, allowed_media_type: Optional[list[str]] = None):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found

        TODO: refactor: use get_manifest_json and call it with index mediatype.
        """
        if not allowed_media_type:
            default_image_index_media_type = "application/vnd.oci.image.index.v1+json"
            allowed_media_type = [default_image_index_media_type]

        headers = {"Accept": ";".join(allowed_media_type)}
        manifest_url = f"{self.prefix}://{self.container.manifest_url()}"
        response = self.do_request(manifest_url, "GET", headers=headers)
        try:
            self._check_200_response(response)
            index = response.json()
            return index

        except ValueError:
            logger.info("Index not found, creating new Index!")
            return NewIndex()

    @ensure_container
    def get_manifest_meta_data_by_cname(
        self,
        container: OrasContainer,
        cname: str,
        version: str,
        arch: str,
        allowed_media_type: Optional[list[str]] = None,
    ):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
        """
        index = self.get_index(allowed_media_type=allowed_media_type)

        if "manifests" not in index:
            logger.debug("Index is empty")
            return None

        for manifest_meta in index["manifests"]:
            # Annotations are optional:
            # https://github.com/opencontainers/image-spec/blob/v1.0.1/descriptor.md#properties

            if "annotations" in manifest_meta:
                if (
                    "cname" in manifest_meta["annotations"]
                    and "architecture" in manifest_meta["annotations"]
                    and "os.version" in manifest_meta["platform"]
                    and manifest_meta["annotations"]["cname"] == cname
                    and manifest_meta["annotations"]["architecture"] == arch
                    and manifest_meta["platform"]["os.version"] == version
                ):
                    return manifest_meta

        return None

    @ensure_container
    def get_manifest_by_digest(
        self,
        container: OrasContainer,
        digest: str,
        allowed_media_type: Optional[list[str]] = None,
    ):
        if not allowed_media_type:
            default_image_manifest_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_manifest_media_type]

        manifest_url = f"{self.prefix}://{container.get_blob_url(digest)}".replace(
            "/blobs/", "/manifests/"
        )
        headers = {"Accept": ";".join(allowed_media_type)}
        response = self.do_request(manifest_url, "GET", headers=headers, stream=False)
        self._check_200_response(response)
        manifest = response.json()
        verify_sha256(digest, response.content)
        jsonschema.validate(manifest, schema=oras_manifest_schema)
        return manifest

    @ensure_container
    def get_manifest_by_cname(
        self,
        container: OrasContainer,
        cname: str,
        version: str,
        arch: str,
        allowed_media_type: Optional[list[str]] = None,
    ):
        """
        Returns the manifest for a cname+arch combination of a container
        Will return None if no result was found
        """
        if not allowed_media_type:
            default_image_manifest_media_type = (
                "application/vnd.oci.image.manifest.v1+json"
            )
            allowed_media_type = [default_image_manifest_media_type]
        manifest_meta = self.get_manifest_meta_data_by_cname(
            container, cname, version, arch
        )
        if manifest_meta is None:
            logger.error(f"No manifest found for {cname}-{arch}")
            return None
        if "digest" not in manifest_meta:
            logger.error("No digest found in metadata!")
        manifest_digest = manifest_meta["digest"]
        return self.get_manifest_by_digest(
            container, manifest_digest, allowed_media_type=allowed_media_type
        )

    def change_state(self, cname: str, version: str, architecture: str, new_state: str):
        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )
        manifest = self.get_manifest_by_cname(
            manifest_container, cname, version, architecture
        )

        if "annotations" not in manifest:
            logger.warning("No annotations found in manifest, init annotations now.")
            manifest["annotations"] = {}

    def attach_layer(
        self,
        cname: str,
        version: str,
        architecture: str,
        file_path: str,
        media_type: str,
    ):
        if not os.path.exists(file_path):
            exit(f"{file_path} does not exist.")

        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )

        manifest = self.get_manifest_by_cname(
            self.container, cname, version, architecture
        )

        layer = self.create_layer(file_path, cname, version, architecture, media_type)
        self._check_200_response(self.upload_blob(file_path, self.container, layer))

        manifest["layers"].append(layer)

        old_manifest_digest = self.get_digest(manifest_container)
        self._check_200_response(self.upload_manifest(manifest, manifest_container))

        new_manifest_metadata = self.get_manifest_meta_data_by_cname(
            self.container, cname, version, architecture
        )
        new_manifest_metadata["digest"] = self.get_digest(manifest_container)
        new_manifest_metadata["size"] = self.get_manifest_size(manifest_container)
        new_manifest_metadata["platform"] = NewPlatform(architecture, version)

        new_index = self.update_index(old_manifest_digest, new_manifest_metadata)
        self._check_200_response(self.upload_index(new_index))

        print(f"Successfully attached {file_path} to {manifest_container}")

    def sign_manifest_entry(
        self, new_manifest_metadata: dict, version: str, architecture: str, cname: str
    ):
        data_to_sign = construct_manifest_entry_signed_data_string(
            cname, version, new_manifest_metadata, architecture
        )
        signature = self.signer.sign_data(data_to_sign)
        new_manifest_metadata["annotations"].update(
            {
                OCI_ANNOTATION_SIGNATURE_KEY: signature,
                OCI_ANNOTATION_SIGNED_STRING_KEY: data_to_sign,
            }
        )

    def sign_layer(
        self,
        layer: dict,
        cname: str,
        version: str,
        architecture: str,
        checksum_sha256: str,
        media_type: str,
    ):
        data_to_sign = construct_layer_signed_data_string(
            cname, version, architecture, media_type, checksum_sha256
        )
        signature = self.signer.sign_data(data_to_sign)
        layer["annotations"].update(
            {
                OCI_ANNOTATION_SIGNATURE_KEY: signature,
                OCI_ANNOTATION_SIGNED_STRING_KEY: data_to_sign,
            }
        )

    def verify_manifest_meta_signature(self, manifest_meta: dict):
        if "annotations" not in manifest_meta:
            raise ValueError("manifest does not contain annotations")
        if OCI_ANNOTATION_SIGNATURE_KEY not in manifest_meta["annotations"]:
            raise ValueError("manifest is not signed")
        if OCI_ANNOTATION_SIGNED_STRING_KEY not in manifest_meta["annotations"]:
            raise ValueError("manifest is not signed")
        signature = manifest_meta["annotations"][OCI_ANNOTATION_SIGNATURE_KEY]
        signed_data = manifest_meta["annotations"][OCI_ANNOTATION_SIGNED_STRING_KEY]
        cname = manifest_meta["annotations"]["cname"]
        version = manifest_meta["platform"]["os.version"]
        architecture = manifest_meta["annotations"]["architecture"]
        signed_data_expected = construct_manifest_entry_signed_data_string(
            cname, version, manifest_meta, architecture
        )
        if signed_data_expected != signed_data:
            raise ValueError(
                f"Signed data does not match expected signed data.\n{signed_data} != {signed_data_expected}"
            )
        self.signer.verify_signature(signed_data, signature)

    def verify_manifest_signature(self, manifest: dict):
        if "layers" not in manifest:
            raise ValueError("manifest does not contain layers")
        if "annotations" not in manifest:
            raise ValueError("manifest does not contain annotations")

        cname = manifest["annotations"]["cname"]
        version = manifest["annotations"]["version"]
        architecture = manifest["annotations"]["architecture"]
        for layer in manifest["layers"]:
            if "annotations" not in layer:
                raise ValueError(f"layer does not contain annotations. layer: {layer}")
            if OCI_ANNOTATION_SIGNATURE_KEY not in layer["annotations"]:
                raise ValueError(f"layer is not signed. layer: {layer}")
            if OCI_ANNOTATION_SIGNED_STRING_KEY not in layer["annotations"]:
                raise ValueError(f"layer is not signed. layer: {layer}")
            media_type = layer["mediaType"]
            checksum_sha256 = layer["digest"].removeprefix("sha256:")
            signature = layer["annotations"][OCI_ANNOTATION_SIGNATURE_KEY]
            signed_data = layer["annotations"][OCI_ANNOTATION_SIGNED_STRING_KEY]
            signed_data_expected = construct_layer_signed_data_string(
                cname, version, architecture, media_type, checksum_sha256
            )
            if signed_data_expected != signed_data:
                raise ValueError(
                    f"Signed data does not match expected signed data. {signed_data} != {signed_data_expected}"
                )
            self.signer.verify_signature(signed_data, signature)

    @ensure_container
    def remove_container(self, container: OrasContainer):
        self.delete_tag(container.manifest_url())

    def status_all(self):
        """
        Validate if container is valid
        - all manifests require a info.yaml in the layers
        - info.yaml needs to be signed (TODO)
        - all layers listed in info.yaml must exist
        - all mediatypes of layers listed in info.yaml must be set correctly
        """
        index = self.get_index()

        if "manifests" not in index:
            logger.info("No manifests in index")
            return
        for manifest_meta in index["manifests"]:
            manifest_digest = manifest_meta["digest"]
            manifest = self.get_manifest_by_digest(self.container, manifest_digest)
            image_state = get_image_state(manifest)
            print(f"{manifest_digest}:\t{image_state}")

    def upload_index(self, index: dict) -> requests.Response:
        jsonschema.validate(index, schema=indexSchema)
        headers = {
            "Content-Type": "application/vnd.oci.image.index.v1+json",
            "Content-Length": str(len(index)),
        }
        tag = self.container.digest or self.container.tag

        index_url = (
            f"{self.container.registry}/v2/{self.container.api_prefix}/manifests/{tag}"
        )
        response = self.do_request(
            f"{self.prefix}://{index_url}",  # noqa
            "PUT",
            headers=headers,
            json=index,
        )
        return response

    def push_image_manifest(
        self,
        architecture: str,
        cname: str,
        version: str,
        build_artifacts_dir: str,
        oci_metadata: list,
        feature_set: str,
        manifest_file: str,
        commit: Optional[str] = None,
    ):
        """
        creates and pushes an image manifest

        :param oci_metadata: a list of filenames and their OCI metadata, can be constructed with
        parse_features.get_oci_metadata or parse_features.get_oci_metadata_from_fileset
        :param str architecture: target architecture of the image
        :param str cname: canonical name of the target image
        :param str build_artifacts_dir: directory where the build artifacts are located
        :param str feature_set: the expanded list of the included features of this manifest. It will be set in the
        manifest itself and in the index entry for this manifest
        :param str commit: the commit hash of the image
        :param str manifest_file: the file where the manifest is written to
        :returns the digest of the pushed manifest
        """

        # Handle null commit value
        if commit is None:
            commit = ""

        # TODO: construct oci_artifacts default data

        manifest_image = oras.oci.NewManifest()
        total_size = 0

        # For each file, create sign, attach and push a layer
        for artifact in oci_metadata:
            annotations_input = artifact["annotations"]
            media_type = artifact["media_type"]
            file_path = os.path.join(build_artifacts_dir, artifact["file_name"])

            if not os.path.exists(file_path):
                raise ValueError(f"{file_path} does not exist.")

            cleanup_blob = False
            if os.path.isdir(file_path):
                file_path = oras.utils.make_targz(file_path)
                cleanup_blob = True

            # Create and sign layer information
            layer = self.create_layer(
                file_path, cname, version, architecture, media_type
            )
            total_size += int(layer["size"])

            if annotations_input:
                layer["annotations"].update(annotations_input)
            # Attach this layer to the manifest that is currently created (and pushed later)
            manifest_image["layers"].append(layer)
            logger.debug(f"Layer: {layer}")
            # Push
            response = self.upload_blob(file_path, self.container, layer)
            self._check_200_response(response)
            logger.info(f"Pushed {artifact["file_name"]} {layer["digest"]}")
            if cleanup_blob and os.path.exists(file_path):
                os.remove(file_path)
        # This ends up in the manifest
        parsed_cname = CName(cname, arch=architecture)
        architecture = parsed_cname.arch
        flavor = parsed_cname.flavor
        manifest_image["annotations"] = {}
        manifest_image["annotations"]["version"] = version
        manifest_image["annotations"]["cname"] = cname
        manifest_image["annotations"]["architecture"] = architecture
        manifest_image["annotations"]["feature_set"] = feature_set
        manifest_image["annotations"]["flavor"] = f"${flavor}-${architecture}"
        manifest_image["annotations"]["commit"] = commit
        description = (
            f"Image: {cname} "
            f"Flavor: {flavor} "
            f"Architecture: {architecture} "
            f"Features: {feature_set} "
            f"Commit: {commit} "
        )
        manifest_image["annotations"][
            "org.opencontainers.image.description"
        ] = description

        config_annotations = {"cname": cname, "architecture": architecture}
        conf, config_file = create_config_from_dict(dict(), config_annotations)

        response = self.upload_blob(config_file, self.container, conf)

        os.remove(config_file)
        self._check_200_response(response)

        manifest_image["config"] = conf

        manifest_container = OrasContainer(
            f"{self.container_name}-{cname}-{architecture}"
        )

        local_digest = f"sha256:{hashlib.sha256(json.dumps(manifest_image).encode('utf-8')).hexdigest()}"

        self._check_200_response(
            self.upload_manifest(manifest_image, manifest_container)
        )
        logger.info(f"Successfully pushed {self.container} {local_digest}")

        # This ends up in the index-entry for the manifest
        metadata_annotations = {"cname": cname, "architecture": architecture}
        metadata_annotations["feature_set"] = feature_set
        manifest_digest = self.get_digest(manifest_container)
        if manifest_digest != local_digest:
            raise ValueError("local and remotely calculated digests do not match")
        manifest_index_metadata = NewManifestMetadata(
            manifest_digest,
            self.get_manifest_size(manifest_container),
            metadata_annotations,
            NewPlatform(architecture, version),
        )

        print(json.dumps(manifest_index_metadata), file=open(manifest_file, "w"))
        logger.info(f"Index entry written to {manifest_file}")

        return local_digest

    def update_index(self, manifest_folder, additional_tags: list = None):
        """
        replaces an old manifest entry with a new manifest entry

        :param str manifest_folder: the folder where the manifest entries are read from
        :param list additional_tags: the additional tags to push the index with
        """
        index = self.get_index()
        # Ensure mediaType is set for existing indices
        if "mediaType" not in index:
            index["mediaType"] = "application/vnd.oci.image.index.v1+json"

        new_entries = 0

        for file in os.listdir(manifest_folder):
            manifest_metadata = json.loads(
                open(manifest_folder + "/" + file, "r").read()
            )
            # Skip if manifest with same digest already exists
            found = False
            for entry in index["manifests"]:
                if entry["digest"] == manifest_metadata["digest"]:
                    found = True
                    break
            if found:
                logger.info(
                    f"Skipping manifest with digest {manifest_metadata["digest"]} - already exists"
                )
                continue
            index["manifests"].append(manifest_metadata)
            logger.info(
                f"Index appended locally {manifest_metadata["annotations"]["cname"]}"
            )
            new_entries += 1

        self._check_200_response(self.upload_index(index))
        logger.info(f"Index pushed with {new_entries} new entries")

        for tag in additional_tags:
            self.container.digest = None
            self.container.tag = tag
            self.upload_index(index)
            logger.info(f"Index pushed with additional tag {tag}")

    def create_layer(
        self,
        file_path: str,
        cname: str,
        version: str,
        architecture: str,
        media_type: str,
    ):
        checksum_sha256 = calculate_sha256(file_path)
        layer = oras.oci.NewLayer(file_path, media_type, is_dir=False)
        layer["annotations"] = {
            oras.defaults.annotation_title: os.path.basename(file_path),
        }
        return layer

    @retry_on_error(max_retries=3, initial_delay=2, backoff_factor=2)
    def upload_blob(self, file_path, container, metadata=None):
        """
        Upload a blob to the registry with retry logic for network errors.

        Args:
            file_path: Path to the file to upload
            container: Container object
            metadata: Optional metadata for the blob

        Returns:
            Response from the upload
        """
        # Call the parent class's upload_blob method
        return super().upload_blob(file_path, container, metadata)

    def push_from_dir(
        self,
        architecture: str,
        version: str,
        cname: str,
        directory: str,
        manifest_file: str,
        additional_tags: list = None,
    ):
        """
        Push artifacts from a directory to a registry

        Args:
            architecture: Target architecture of the image
            version: Version tag for the image
            cname: Canonical name of the image
            directory: Directory containing the artifacts
            manifest_file: File to write the manifest index entry to
            additional_tags: Additional tags to push the manifest with

        Returns:
            The digest of the pushed manifest
        """
        if additional_tags is None:
            additional_tags = []

        try:
            # scan and extract nested artifacts
            for file in os.listdir(directory):
                try:
                    if file.endswith(".pxe.tar.gz"):
                        logger.info(f"Found nested artifact {file}")
                        nested_tar_obj = tarfile.open(f"{directory}/{file}")
                        nested_tar_obj.extractall(filter="data", path=directory)
                        nested_tar_obj.close()
                except (OSError, tarfile.FilterError, tarfile.TarError) as e:
                    print(f"Failed to extract nested artifact {file}", e)
                    exit(1)

            # Get metadata from files
            oci_metadata = get_oci_metadata_from_fileset(
                os.listdir(directory), architecture
            )

            features = ""
            commit = ""
            for artifact in oci_metadata:
                if artifact["media_type"] == "application/io.gardenlinux.release":
                    try:
                        file_path = f"{directory}/{artifact['file_name']}"

                        config = configparser.ConfigParser(allow_unnamed_section=True)
                        config.read(file_path)

                        if config.has_option(
                            configparser.UNNAMED_SECTION, "GARDENLINUX_FEATURES"
                        ):
                            features = config.get(
                                configparser.UNNAMED_SECTION, "GARDENLINUX_FEATURES"
                            )
                        if config.has_option(
                            configparser.UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID"
                        ):
                            commit = config.get(
                                configparser.UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID"
                            )

                    except (configparser.Error, IOError) as e:
                        logger.error(
                            f"Error reading config file {artifact['file_name']}: {e}"
                        )
                    break

            # Push the image manifest
            digest = self.push_image_manifest(
                architecture,
                cname,
                version,
                directory,
                oci_metadata,
                features,
                manifest_file,
                commit=commit,
            )

            # Process additional tags if provided
            if additional_tags and len(additional_tags) > 0:
                print(f"DEBUG: Processing {len(additional_tags)} additional tags")
                logger.info(f"Processing {len(additional_tags)} additional tags")

                self.push_additional_tags_manifest(
                    architecture,
                    cname,
                    version,
                    additional_tags,
                    container=self.container,
                )

            return digest
        except Exception as e:
            print("Error: ", e)
            exit(1)

    def push_additional_tags_manifest(
        self, architecture, cname, version, additional_tags, container
    ):
        """
        Push additional tags for an existing manifest using ORAS Registry methods

        Args:
            architecture: Target architecture of the image
            cname: Canonical name of the image
            version: Version tag for the image
            additional_tags: List of additional tags to push
            container: Container object
        """
        try:
            # Source tag is the tag containing the version-cname-architecture combination
            source_tag = f"{version}-{cname}-{architecture}"
            source_container = copy.deepcopy(container)
            source_container.tag = source_tag

            # Authentication credentials from environment
            token = os.getenv("GL_CLI_REGISTRY_TOKEN")
            username = os.getenv("GL_CLI_REGISTRY_USERNAME")
            password = os.getenv("GL_CLI_REGISTRY_PASSWORD")

            # Login to registry if credentials are provided
            if username and password:
                logger.debug(f"Logging in with username/password")
                try:
                    self.login(username, password)
                except Exception as login_error:
                    logger.error(f"Login error: {str(login_error)}")
            elif token:
                # If token is provided, set it directly on the Registry instance
                logger.debug(f"Using token authentication")
                self.token = base64.b64encode(token.encode("utf-8")).decode("utf-8")
                self.auth.set_token_auth(self.token)

            # Get the manifest from the source container
            try:
                logger.debug(f"Getting manifest from {source_container}")
                manifest = self.get_manifest(source_container)
                if not manifest:
                    logger.error(f"Failed to get manifest for {source_container}")
                    return
                logger.info(
                    f"Successfully retrieved manifest: {manifest['mediaType'] if 'mediaType' in manifest else 'unknown'}"
                )
            except Exception as get_error:
                logger.error(f"Error getting manifest: {str(get_error)}")
                return

            # For each additional tag, push the manifest using Registry.upload_manifest
            for tag in additional_tags:
                try:
                    logger.debug(f"Pushing additional tag: {tag}")

                    # Create a new container for this tag
                    tag_container = copy.deepcopy(container)
                    tag_container.tag = tag

                    logger.debug(f"Pushing to container: {tag_container}")

                    # Upload the manifest to the new tag
                    response = self.upload_manifest(manifest, tag_container)

                    if response and response.status_code in [200, 201]:
                        logger.info(f"Successfully pushed tag {tag} for manifest")
                    else:
                        status_code = getattr(response, "status_code", "unknown")
                        response_text = getattr(response, "text", "No response text")
                        logger.error(
                            f"Failed to push tag {tag} for manifest: {status_code}"
                        )

                except Exception as tag_error:
                    logger.error(
                        f"Error pushing tag {tag} for manifest: {str(tag_error)}"
                    )

        except Exception as e:
            logger.error(f"Error in push_additional_tags_manifest: {str(e)}")
