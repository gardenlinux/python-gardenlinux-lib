# -*- coding: utf-8 -*-

"""
GitHub release container
"""

from logging import Logger
from typing import Optional

from ...logger import LoggerSetup
from ..client import Client


class Release(object):
    """
    GitHub release instance to provide methods for interaction.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        repo: str,
        owner: str = "gardenlinux",
        token: Optional[str] = None,
        logger: Optional[Logger] = None,
    ):
        """
        Constructor __init__(Release)

        :param repo: GitHub repository containing releases
        :param owner: GitHub owner for release data
        :param token: GitHub access token
        :param logger: Logger instance

        :since: 1.0.0
        """

        self._owner = owner
        self._repo = repo
        self._name: Optional[str] = None
        self._tag: Optional[str] = None
        self._commitish: Optional[str] = None
        self._latest = True
        self._pre_release = False
        self._release_body: Optional[str] = None

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.github")

        self._logger = logger

        self._client = Client(token, self._logger)

    @property
    def body(self) -> str:
        """
        Returns the Git release body set.

        :return: (str) Git release body
        :since:  1.0.0
        """

        if self._release_body is None:
            raise ValueError("GitHub release body not set")

        return self._release_body

    @body.setter
    def body(self, value: str) -> None:
        """
        Sets the Git release body.

        :param value: Git release body

        :since: 1.0.0
        """

        self._release_body = value

    @property
    def commitish(self) -> Optional[str]:
        """
        Returns the Git release related commit hash.

        :return: (str) Git release commit hash
        :since:  1.0.0
        """

        return self._commitish

    @commitish.setter
    def commitish(self, value: str) -> None:
        """
        Sets the Git release related commit hash.

        :param value: Git release commit hash

        :since: 1.0.0
        """

        self._commitish = value

    @property
    def is_latest(self) -> bool:
        """
        Returns true if the Git release is marked as "latest".

        :return: (str) Git release latest status
        :since:  1.0.0
        """

        return self._latest

    @is_latest.setter
    def is_latest(self, value: bool) -> None:
        """
        If set to true the Git release created will be marked as "latest".

        :param value: Git release latest status

        :since: 1.0.0
        """

        self._latest = bool(value)

    @property
    def is_pre_release(self) -> bool:
        """
        Returns true if the Git release is marked as pre-release.

        :return: (str) Git release pre-release status
        :since:  1.0.0
        """

        return self._pre_release

    @is_pre_release.setter
    def is_pre_release(self, value: bool) -> None:
        """
        If set to true the Git release created will be marked as pre-release.

        :param value: Git release pre-release status

        :since: 1.0.0
        """

        self._pre_release = bool(value)

    @property
    def name(self) -> str:
        """
        Returns the Git release name set.

        :return: (str) Git release name
        :since:  1.0.0
        """

        if self._name is None:
            return self.tag

        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the Git release name.

        :param value: Git release name

        :since: 1.0.0
        """

        self._name = value

    @property
    def tag(self) -> str:
        """
        Returns the Git release tag set.

        :return: (str) Git release tag
        :since:  1.0.0
        """

        if self._tag is None:
            raise ValueError("GitHub release tag not set")

        return self._tag

    @tag.setter
    def tag(self, value: str) -> None:
        """
        Sets the Git release tag.

        :param value: Git release tag

        :since: 1.0.0
        """

        self._tag = value

    def create(self) -> int:
        """
        Creates an GitHub release.

        :return: (str) GitHub release ID created
        :since:  1.0.0
        """

        kwargs = {
            "name": self.name,
            "message": self.body,
            "draft": False,
            "prerelease": self.is_pre_release,
            "make_latest": "true" if self.is_latest else "false",
        }

        if self.commitish is not None:
            kwargs["target_commitish"] = self._commitish

        release = self._client.get_repo(
            f"{self._owner}/{self._repo}"
        ).create_git_release(self.tag, **kwargs)

        return release.id  # type: ignore[no-any-return]
