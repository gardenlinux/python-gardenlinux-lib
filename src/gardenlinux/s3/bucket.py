# -*- coding: utf-8 -*-

"""
S3 bucket
"""

import boto3
import logging
from typing import Any, Optional

from ..logger import LoggerSetup


class Bucket(object):
    """
    S3 bucket class

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
        Constructor __init__(Bucket)

        :param bucket_name: S3 bucket name
        :param endpoint_url: S3 endpoint URL
        :param s3_resource_config: Additional boto3 S3 config values
        :param logger: Logger instance

        :since: 0.8.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.s3")

        if s3_resource_config is None:
            s3_resource_config = {}

        if endpoint_url is not None:
            s3_resource_config["endpoint_url"] = endpoint_url

        self._s3_resource = boto3.resource("s3", **s3_resource_config)

        self._bucket = self._s3_resource.Bucket(bucket_name)
        self._logger = logger

    @property
    def objects(self):
        """
        Returns a list of all objects in a bucket.

        :return: (list) S3 bucket objects
        :since:  0.8.0
        """

        self._logger.debug(f"Returning all S3 bucket objects for {self._bucket.name}")

        return self._bucket.objects.all()

    def __getattr__(self, name):
        """
        python.org: Called when an attribute lookup has not found the attribute in
        the usual places (i.e. it is not an instance attribute nor is it found in the
        class tree for self).

        :param name: Attribute name

        :return: (mixed) Attribute
        :since:  0.8.0
        """

        return getattr(self._bucket, name)

    def download_file(self, key, file_name, *args, **kwargs):
        """
        boto3: Download an S3 object to a file.

        :param key:       The name of the key to download from.
        :param file_name: The path to the file to download to.

        :since: 0.8.0
        """

        self._bucket.download_file(key, file_name, *args, **kwargs)

        self._logger.info(f"Downloaded {key} from S3 to {file_name}")

    def download_fileobj(self, key, fp, *args, **kwargs):
        """
        boto3: Download an object from this bucket to a file-like-object.

        :param key: The name of the key to download from.
        :param fp:  A file-like object to download into.

        :since: 0.8.0
        """

        self._bucket.download_fileobj(key, fp, *args, **kwargs)

        self._logger.info(f"Downloaded {key} from S3 as binary data")

    def upload_file(self, file_name, key, *args, **kwargs):
        """
        boto3: Upload a file to an S3 object.

        :param file_name: The path to the file to upload.
        :param key:       The name of the key to upload to.

        :since: 0.8.0
        """

        self._bucket.upload_file(file_name, key, *args, **kwargs)

        self._logger.info(f"Uploaded {key} to S3 for {file_name}")

    def upload_fileobj(self, fp, key, *args, **kwargs):
        """
        boto3: Upload a file-like object to this bucket.

        :param fp:  A file-like object to upload.
        :param key: The name of the key to upload to.

        :since: 0.8.0
        """

        self._bucket.upload_fileobj(fp, key, *args, **kwargs)

        self._logger.info(f"Uploaded {key} to S3 as binary data")
