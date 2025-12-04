# -*- coding: utf-8 -*-

"""
GitHub client
"""

from logging import Logger
from os import environ
from typing import Any, Optional

from github import Auth, Github

from ..logger import LoggerSetup


class Client(object):
    """
    GitHub client instance to provide methods for interaction with GitHub API.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, token: Optional[str] = None, logger: Optional[Logger] = None):
        """
        Constructor __init__(Client)

        :param token: GitHub access token
        :param logger: Logger instance

        :since: 1.0.0
        """

        self._client = None
        self._token = token

        if self._token is None or self._token.strip() == "":
            self._token = environ.get("GITHUB_TOKEN")

        if self._token is None:
            raise ValueError("GITHUB_TOKEN environment variable not set")

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.github")

        self._logger = logger

    @property
    def instance(self) -> Github:
        if self._client is None:
            self._client = Github(auth=Auth.Token(self._token))

        return self._client

    def __getattr__(self, name: str) -> Any:
        """
        python.org: Called when an attribute lookup has not found the attribute in
        the usual places (i.e. it is not an instance attribute nor is it found in the
        class tree for self).

        :param name: Attribute name

        :return: (mixed) Attribute
        :since:  0.8.0
        """

        self._logger.debug(f"gardenlinux.github.Client.{name} accessed")
        return getattr(self.instance, name)
