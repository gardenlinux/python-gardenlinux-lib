# -*- coding: utf-8 -*-

"""
S3 object index with flavors filtering
"""

import base64
import json
import logging
import os
import subprocess
import time
import yaml
from typing import Any, Optional

from ..flavors.parser import Parser
from ..logger import LoggerSetup
from .bucket import Bucket


class S3ObjectIndex(object):
    """
    S3 object index class with flavors filtering capabilities

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: s3
    :since:      0.9.0
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
        Constructor __init__(S3ObjectIndex)

        :param bucket_name: S3 bucket name
        :param endpoint_url: S3 endpoint URL
        :param s3_resource_config: Additional boto3 S3 config values
        :param logger: Logger instance

        :since: 0.9.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.s3")

        self._bucket = Bucket(bucket_name, endpoint_url, s3_resource_config)
        self._logger = logger

    def get_index(
        self,
        prefix: str,
        cache_file: Optional[str] = None,
        cache_ttl: int = 3600,
    ) -> dict[str, Any]:
        """
        Get and cache S3 objects with an indexed list of objects.

        :param prefix:     Prefix for S3 objects
        :param cache_file: Path to cache file (optional, enables caching when provided)
        :param cache_ttl:  Cache time-to-live in seconds

        :returns: Dictionary containing 'index' and 'artifacts' keys

        :since: 0.9.0
        """

        self._logger.debug(f"Getting object index for prefix: {prefix}")

        # Fetch directly if no caching
        if cache_file is None:
            artifacts = [
                s3_object.key
                for s3_object in self._bucket.objects.filter(Prefix=prefix).all()
            ]
            self._logger.debug(f"Fetched {len(artifacts)} artifacts without caching")
            return {"index": self._build_index(artifacts), "artifacts": artifacts}

        # Check cache
        index_file = cache_file + ".index.json"
        if (
            os.path.exists(cache_file)
            and os.path.exists(index_file)
            and time.time() - os.path.getmtime(cache_file) < cache_ttl
        ):
            try:
                with open(cache_file, "r") as f:
                    artifacts = json.load(f)
                with open(index_file, "r") as f:
                    index = json.load(f)
                self._logger.debug("Using cached object index")
                return {"index": index, "artifacts": artifacts}
            except (json.JSONDecodeError, IOError):
                self._logger.warning("Cache files corrupted, fetching fresh data")

        # Fetch from S3 and cache
        artifacts = [
            s3_object.key
            for s3_object in self._bucket.objects.filter(Prefix=prefix).all()
        ]
        index = self._build_index(artifacts)

        self._logger.info(f"Fetched {len(artifacts)} artifacts from S3")

        # Save cache
        try:
            with open(cache_file, "w") as f:
                json.dump(artifacts, f)
            with open(index_file, "w") as f:
                json.dump(index, f)
            self._logger.debug("Saved object index to cache")
        except IOError:
            self._logger.warning("Failed to save cache files")

        return {"index": index, "artifacts": artifacts}

    def _build_index(self, objects: list[str]) -> dict[str, list[str]]:
        """
        Build an index of objects for faster searching.

        :param objects: List of object keys
        :returns: Dictionary index with simple objects list
        :since: 0.9.0
        """

        cnames = {
            obj.split("/")[1]
            for obj in objects
            if obj.startswith("objects/") and len(obj.split("/")) >= 3
        }
        self._logger.debug(f"Built index with {len(cnames)} unique objects")
        return {"objects": sorted(cnames)}
