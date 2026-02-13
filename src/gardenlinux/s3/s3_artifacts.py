# -*- coding: utf-8 -*-

"""
S3 GardenLinux artifacts
"""

import logging
import re
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
    def bucket(self) -> Bucket:
        """
        Returns the underlying S3 bucket.

        :return: (boto3.Bucket) S3 bucket
        :since:  0.9.0
        """

        return self._bucket

    def download_to_directory(
        self, cname: str, artifacts_dir: PathLike[str] | str
    ) -> None:
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
            release_object.key, str(artifacts_dir.joinpath(f"{cname}.s3_metadata.yaml"))
        )

        for s3_object in self._bucket.objects.filter(Prefix=f"objects/{cname}").all():
            self._bucket.download_file(
                s3_object.key, str(artifacts_dir.joinpath(basename(s3_object.key)))
            )

    def upload_from_directory(
        self,
        base_name: str,
        artifacts_dir: PathLike[str] | str,
        delete_before_push: bool = False,
        dry_run: bool = False,
    ) -> None:
        """
        Pushes S3 artifacts to the underlying bucket.

        :param base_name:          Base name of the GardenLinux S3 artifacts
        :param artifacts_dir:      Path of the image artifacts
        :param delete_before_push: True to delete objects before upload

        :since: 0.8.0
        """

        artifacts_dir = Path(artifacts_dir)

        if not artifacts_dir.is_dir():
            raise RuntimeError(f"Artifacts directory given is invalid: {artifacts_dir}")

        release_file = artifacts_dir.joinpath(f"{base_name}.release")

        if not release_file.exists():
            raise RuntimeError(f"Release file not found: {release_file}")

        # RegEx for S3 supported characters
        re_object = re.compile("[^a-zA-Z0-9\\s+\\-=.\\_:/@]")

        def _sanitize(value: Optional[str]) -> Optional[str]:
            if value is None:
                return None
            return re_object.sub("+", str(value))

        def _read_kv_file(path: Path) -> ConfigParser:
            cfg = ConfigParser(allow_unnamed_section=True, interpolation=None)
            with path.open("r", encoding="utf-8") as fp:
                cfg.read_file(fp)
            return cfg

        def _get_required(cfg: ConfigParser, key: str, what: Path) -> str:
            if not cfg.has_option(UNNAMED_SECTION, key):
                raise RuntimeError(f"Missing required field {key} in {what}")
            v = cfg.get(UNNAMED_SECTION, key).strip()
            if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
                v = v[1:-1]
            if v == "":
                raise RuntimeError(f"Empty required field {key} in {what}")
            return v

        def _get_optional(cfg: ConfigParser, key: str) -> Optional[str]:
            if not cfg.has_option(UNNAMED_SECTION, key):
                return None
            v = cfg.get(UNNAMED_SECTION, key).strip()
            if len(v) >= 2 and ((v[0] == '"' and v[-1] == '"') or (v[0] == "'" and v[-1] == "'")):
                v = v[1:-1]
            if v == "":
                return None
            return v

        release_config = _read_kv_file(release_file)

        # Backwards compatibility: platform fallback
        cname = _get_optional(release_config, "GARDENLINUX_CNAME")
        platform = _get_optional(release_config, "GARDENLINUX_PLATFORM")
        if platform is None:
            if cname is None:
                cname = base_name
            platform = cname.split("-", 1)[0]

        # Hard guard: frankenstein images must never be published
        if platform == "frankenstein":
            raise RuntimeError("frankenstein images must not be published")

        version = _get_required(release_config, "GARDENLINUX_VERSION", release_file)
        commit_id_long = _get_required(
            release_config, "GARDENLINUX_COMMIT_ID_LONG", release_file
        )

        platform_variant = _get_optional(
            release_config, "GARDENLINUX_PLATFORM_VARIANT"
        )

        features = _get_optional(release_config, "GARDENLINUX_FEATURES")
        feature_set_list: list[str] = []
        if features is not None:
            feature_set_list = [x.strip() for x in features.split(",")]
            feature_set_list = [x for x in feature_set_list if x]

        gardenlinux_epoch = None
        try:
            gardenlinux_epoch = int(version.split(".", 1)[0])
        except Exception:
            gardenlinux_epoch = None

        release_timestamp = stat(release_file).st_mtime
        requirements_file = artifacts_dir.joinpath(f"{base_name}.requirements")
        require_uefi = False
        secureboot = False
        tpm2 = False
        arch = None

        if requirements_file.exists():
            requirements_config = _read_kv_file(requirements_file)

            if requirements_config.has_option(UNNAMED_SECTION, "arch"):
                arch = requirements_config.get(UNNAMED_SECTION, "arch").strip()

            if requirements_config.has_option(UNNAMED_SECTION, "uefi"):
                require_uefi = requirements_config.getboolean(UNNAMED_SECTION, "uefi")

            if requirements_config.has_option(UNNAMED_SECTION, "secureboot"):
                secureboot = requirements_config.getboolean(
                    UNNAMED_SECTION, "secureboot"
                )

            if requirements_config.has_option(UNNAMED_SECTION, "tpm2"):
                tpm2 = requirements_config.getboolean(UNNAMED_SECTION, "tpm2")

        # Backwards compatibility: arch fallback
        if not arch:
            if cname is None:
                cname = base_name
            cname_parts = cname.split("-")
            if len(cname_parts) < 2:
                raise RuntimeError(
                    "Architecture could not be determined from requirements file or cname"
                )
            arch = cname_parts[-2]

        arch = _sanitize(arch)

        metadata = {
            "platform": platform,
            "platform_variant": platform_variant,
            "architecture": arch,
            "version": version,
            "gardenlinux_epoch": gardenlinux_epoch,
            "build_committish": commit_id_long,
            "build_timestamp": datetime.fromtimestamp(release_timestamp),
            "modifiers": feature_set_list,
            "require_uefi": require_uefi,
            "secureboot": secureboot,
            "tpm2": tpm2,
            "paths": [],
            "s3_bucket": self._bucket.name,
            "s3_key": f"meta/singles/{base_name}",
        }

        if metadata["platform_variant"] is None:
            del metadata["platform_variant"]

        if metadata["gardenlinux_epoch"] is None:
            del metadata["gardenlinux_epoch"]

        base_name_length = len(base_name)

        for artifact in artifacts_dir.iterdir():
            if artifact.is_dir():
                continue

            if artifact.name == f"{base_name}.release":
                continue

            if artifact.name == f"{base_name}.requirements":
                continue

            s3_key = f"objects/{base_name}/{artifact.name}"

            with artifact.open("rb") as fp:
                md5sum = file_digest(fp, "md5").hexdigest()
                sha256sum = file_digest(fp, "sha256").hexdigest()

            if artifact.name.startswith(base_name):
                suffix = artifact.name[base_name_length:]
            else:
                suffix = artifact.suffix

            artifact_metadata = {
                "name": artifact.name,
                "s3_bucket_name": self._bucket.name,
                "s3_key": s3_key,
                "suffix": _sanitize(suffix),
                "md5sum": md5sum,
                "sha256sum": sha256sum,
            }

            s3_tags = {
                "architecture": arch,
                "platform": _sanitize(platform),
                "version": _sanitize(version),
                "committish": commit_id_long,
                "md5sum": md5sum,
                "sha256sum": sha256sum,
            }

            if not dry_run:
                if delete_before_push:
                    self._bucket.delete_objects(Delete={"Objects": [{"Key": s3_key}]})

                self._bucket.upload_file(
                    str(artifact),
                    s3_key,
                    ExtraArgs={"Tagging": urlencode(s3_tags)},
                )

            metadata["paths"].append(artifact_metadata)

        if dry_run:
            print(yaml.dump(metadata, sort_keys=False))
        else:
            if delete_before_push:
                self._bucket.delete_objects(
                    Delete={"Objects": [{"Key": f"meta/singles/{base_name}"}]}
                )

            with TemporaryFile(mode="wb+") as fp:
                fp.write(yaml.dump(metadata, sort_keys=False).encode("utf-8"))
                fp.seek(0)

                self._bucket.upload_fileobj(
                    fp,
                    f"meta/singles/{base_name}",
                    ExtraArgs={"ContentType": "text/yaml"},
                )
