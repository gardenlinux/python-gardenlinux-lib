# -*- coding: utf-8 -*-

"""
S3 GardenLinux artifacts
"""

import logging
from configparser import UNNAMED_SECTION, ConfigParser
from datetime import datetime
from hashlib import file_digest
from os import PathLike, stat
from os.path import basename
from pathlib import Path
from tempfile import TemporaryFile
from typing import Any, Optional
from urllib.parse import urlencode

import yaml

from ..features.cname import CName
from .bucket import Bucket


class S3Artifacts(object):
    """
    S3Artifacts support access to GardenLinux S3 resources.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: s3
    :since:      0.8.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        bucket_name: str,
        endpoint_url: Optional[str] = None,
        s3_resource_config: Optional[dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(S3Artifacts)

        :param bucket_name: S3 bucket name
        :param endpoint_url: S3 endpoint URL
        :param s3_resource_config: Additional boto3 S3 config values
        :param logger: Logger instance

        :since: 0.8.0
        """

        self._bucket = Bucket(bucket_name, endpoint_url, s3_resource_config, logger)

    @property
    def bucket(self):
        """
        Returns the underlying S3 bucket.

        :return: (boto3.Bucket) S3 bucket
        :since:  0.9.0
        """

        return self._bucket

    def download_to_directory(
        self,
        cname: str,
        artifacts_dir: str | PathLike[str],
    ):
        """
        Download S3 artifacts to a given directory.

        :param cname:         Canonical name of the GardenLinux S3 artifacts
        :param artifacts_dir: Path for the image artifacts

        :since: 0.8.0
        """

        artifacts_dir = Path(artifacts_dir)

        if not artifacts_dir.is_dir():
            raise RuntimeError(f"Artifacts directory given is invalid: {artifacts_dir}")

        release_object = list(
            self._bucket.objects.filter(Prefix=f"meta/singles/{cname}")
        )[0]

        self._bucket.download_file(
            release_object.key, artifacts_dir.joinpath(f"{cname}.s3_metadata.yaml")
        )

        for s3_object in self._bucket.objects.filter(Prefix=f"objects/{cname}").all():
            self._bucket.download_file(
                s3_object.key, artifacts_dir.joinpath(basename(s3_object.key))
            )

    def upload_from_directory(
        self,
        cname: str,
        artifacts_dir: str | PathLike[str],
        delete_before_push=False,
    ):
        """
        Pushes S3 artifacts to the underlying bucket.

        :param cname:              Canonical name of the GardenLinux S3 artifacts
        :param artifacts_dir:      Path of the image artifacts
        :param delete_before_push: True to delete objects before upload

        :since: 0.8.0
        """

        artifacts_dir = Path(artifacts_dir)

        cname_object = CName(cname)

        if cname_object.arch is None:
            raise RuntimeError("Architecture could not be determined from cname")

        if not artifacts_dir.is_dir():
            raise RuntimeError(f"Artifacts directory given is invalid: {artifacts_dir}")

        release_file = artifacts_dir.joinpath(f"{cname}.release")
        release_timestamp = stat(release_file).st_ctime

        release_config = ConfigParser(allow_unnamed_section=True)
        release_config.read(release_file)

        if cname_object.version != release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_VERSION"
        ):
            raise RuntimeError(
                f"Release file data and given cname conflict detected: Version {cname_object.version}"
            )

        if cname_object.commit_id != release_config.get(
            UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID"
        ):
            raise RuntimeError(
                f"Release file data and given cname conflict detected: Commit ID {cname_object.commit_id}"
            )

        if cname_object.version is None:
            raise RuntimeError("CName version could not be determined!")

        commit_hash = release_config.get(UNNAMED_SECTION, "GARDENLINUX_COMMIT_ID_LONG")

        feature_set = release_config.get(UNNAMED_SECTION, "GARDENLINUX_FEATURES")
        feature_list = feature_set.split(",")

        requirements_file = artifacts_dir.joinpath(f"{cname}.requirements")
        require_uefi = None
        secureboot = None

        if requirements_file.exists():
            requirements_config = ConfigParser(allow_unnamed_section=True)
            requirements_config.read(requirements_file)

            if requirements_config.has_option(UNNAMED_SECTION, "uefi"):
                require_uefi = requirements_config.getboolean(UNNAMED_SECTION, "uefi")

            if requirements_config.has_option(UNNAMED_SECTION, "secureboot"):
                secureboot = requirements_config.getboolean(
                    UNNAMED_SECTION, "secureboot"
                )

        if require_uefi is None:
            require_uefi = "_usi" in feature_list

        if secureboot is None:
            secureboot = "_trustedboot" in feature_list

        metadata = {
            "platform": cname_object.platform,
            "architecture": cname_object.arch,
            "base_image": None,
            "build_committish": commit_hash,
            "build_timestamp": datetime.fromtimestamp(release_timestamp).isoformat(),
            "gardenlinux_epoch": int(cname_object.version.split(".", 1)[0]),
            "logs": None,
            "modifiers": feature_list,
            "require_uefi": require_uefi,
            "secureboot": secureboot,
            "published_image_metadata": None,
            "s3_bucket": self._bucket.name,
            "s3_key": f"meta/singles/{cname}",
            "test_result": None,
            "version": cname_object.version,
            "paths": [],
        }

        for artifact in artifacts_dir.iterdir():
            if not artifact.match(f"{cname}*"):
                continue

            if not artifact.name.startswith(cname):
                raise RuntimeError(
                    f"Artifact name '{artifact.name}' does not start with cname '{cname}'"
                )

            s3_key = f"objects/{cname}/{artifact.name}"

            with artifact.open("rb") as fp:
                md5sum = file_digest(fp, "md5").hexdigest()
                sha256sum = file_digest(fp, "sha256").hexdigest()

            suffix = artifact.name[len(cname) :]

            artifact_metadata = {
                "name": artifact.name,
                "s3_bucket_name": self._bucket.name,
                "s3_key": s3_key,
                "suffix": suffix,
                "md5sum": md5sum,
                "sha256sum": sha256sum,
            }

            s3_tags = {
                "architecture": cname_object.arch,
                "platform": cname_object.platform,
                "version": cname_object.version,
                "committish": commit_hash,
                "md5sum": md5sum,
                "sha256sum": sha256sum,
            }

            if delete_before_push:
                self._bucket.delete_objects(Delete={"Objects": [{"Key": s3_key}]})

            self._bucket.upload_file(
                artifact,
                s3_key,
                ExtraArgs={"Tagging": urlencode(s3_tags)},
            )

            metadata["paths"].append(artifact_metadata)

        if delete_before_push:
            self._bucket.delete_objects(
                Delete={"Objects": [{"Key": f"meta/singles/{cname}"}]}
            )

        with TemporaryFile(mode="wb+") as fp:
            fp.write(yaml.dump(metadata).encode("utf-8"))
            fp.seek(0)

            self._bucket.upload_fileobj(
                fp, f"meta/singles/{cname}", ExtraArgs={"ContentType": "text/yaml"}
            )
