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
