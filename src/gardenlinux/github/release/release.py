# -*- coding: utf-8 -*-

"""
GitHub release container
"""

from logging import Logger
from os import PathLike
from pathlib import Path
from typing import Optional, Self

from github import GithubException
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

from ...logger import LoggerSetup
from ..client import Client


class Release(object):
    """
    GitHub release instance to provide methods for interaction.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      0.10.19
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

        :since: 0.10.19
        """

        self._owner = owner
        self._repo = repo
        self._release_id: Optional[int] = None
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
        Returns the GitHub release body set.

        :return: (str) GitHub release body
        :since:  0.10.19
        """

        if self._release_body is None:
            raise ValueError("GitHub release body not set")

        return self._release_body

    @body.setter
    def body(self, value: str) -> None:
        """
        Sets the GitHub release body.

        :param value: GitHub release body

        :since: 0.10.19
        """

        self._release_body = value

    @property
    def commitish(self) -> Optional[str]:
        """
        Returns the Git release related commit hash.

        :return: (str) Git release commit hash
        :since:  0.10.19
        """

        return self._commitish

    @commitish.setter
    def commitish(self, value: str) -> None:
        """
        Sets the Git release related commit hash.

        :param value: Git release commit hash

        :since: 0.10.19
        """

        self._commitish = value

    @property
    def id(self) -> int:
        """
        Returns the GitHub release ID set.

        :return: (int) GitHub release ID
        :since:  0.10.19
        """

        if self._release_id is None:
            raise ValueError("GitHub release ID not set")

        return self._release_id

    @property
    def is_latest(self) -> bool:
        """
        Returns true if the Git release is marked as "latest".

        :return: (str) Git release latest status
        :since:  0.10.19
        """

        return self._latest

    @is_latest.setter
    def is_latest(self, value: bool) -> None:
        """
        If set to true the Git release created will be marked as "latest".

        :param value: Git release latest status

        :since: 0.10.19
        """

        self._latest = bool(value)

    @property
    def is_pre_release(self) -> bool:
        """
        Returns true if the Git release is marked as pre-release.

        :return: (str) Git release pre-release status
        :since:  0.10.19
        """

        return self._pre_release

    @is_pre_release.setter
    def is_pre_release(self, value: bool) -> None:
        """
        If set to true the Git release created will be marked as pre-release.

        :param value: Git release pre-release status

        :since: 0.10.19
        """

        self._pre_release = bool(value)

    @property
    def name(self) -> str:
        """
        Returns the Git release name set.

        :return: (str) Git release name
        :since:  0.10.19
        """

        if self._name is None:
            return self.tag

        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """
        Sets the Git release name.

        :param value: Git release name

        :since: 0.10.19
        """

        self._name = value

    @property
    def tag(self) -> str:
        """
        Returns the Git release tag set.

        :return: (str) Git release tag
        :since:  0.10.19
        """

        if self._tag is None:
            raise ValueError("GitHub release tag not set")

        return self._tag

    @tag.setter
    def tag(self, value: str) -> None:
        """
        Sets the Git release tag.

        :param value: Git release tag

        :since: 0.10.19
        """

        self._tag = value

    def _copy_from_release_object(self, release_object: GitRelease | Self) -> None:
        """
        Creates an GitHub release.

        :return: (str) GitHub release ID created
        :since:  0.10.19
        """

        self._name = release_object.name

        if isinstance(release_object, GitRelease):
            self._release_id = release_object.id
            self._tag = release_object.tag_name
            self._commitish = release_object.target_commitish
            self._pre_release = release_object.prerelease
            self._release_body = release_object.body_text
        else:
            self._tag = release_object.tag
            self._commitish = release_object.commitish
            self._pre_release = release_object.is_pre_release
            self._release_body = release_object.body

    def create(self) -> int:
        """
        Creates an GitHub release.

        :return: (str) GitHub release ID created
        :since:  0.10.19
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

        self._release_id = release.id

        return self._release_id

    def get_asset_by_name(self, asset_name: str) -> GitReleaseAsset:
        """
        Returns an GitHub release asset by the given name.

        :param asset_name: Asset name

        :return: (object) GitHub release asset
        :since:  0.10.19
        """

        github_release = self._client.get_repo(
            f"{self._owner}/{self._repo}"
        ).get_release(self.id)

        for asset in github_release.assets:
            if asset_name == asset.name:
                return asset

        raise RuntimeError(f"No asset found with name: {asset_name}")

    def upload_asset(
        self, asset_file_path_name: PathLike[str] | str, overwrite: bool = False
    ) -> None:
        """
        Uploads an GitHub release asset.

        :param asset_file_path_name: File path and name to be uploaded

        :since: 0.10.19
        """

        if not isinstance(asset_file_path_name, PathLike):
            asset_file_path_name = Path(asset_file_path_name)

        if asset_file_path_name.stat().st_size < 1:  # type: ignore[attr-defined]
            self._logger.info(f"{asset_file_path_name} is empty and will be ignored")
            return

        github_release = self._client.get_repo(
            f"{self._owner}/{self._repo}"
        ).get_release(self.id)

        asset_file_name = asset_file_path_name.name  # type: ignore[attr-defined]

        try:
            github_release.upload_asset(str(asset_file_path_name), name=asset_file_name)
        except GithubException as exc:
            is_asset_upload_retried = False

            if overwrite and exc.status == 422:
                asset = self.get_asset_by_name(asset_file_name)

                asset.delete_asset()
                self.upload_asset(asset_file_path_name)

                is_asset_upload_retried = True

            if not is_asset_upload_retried:
                raise

        self._logger.info(f"Uploaded file '{asset_file_name}'")

    @staticmethod
    def get(
        release_id: int,
        repo: str,
        owner: str = "gardenlinux",
        token: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> "Release":
        """
        Creates an GitHub release.

        :return: (str) GitHub release ID created
        :since:  0.10.19
        """

        github_release = (
            Client(token, logger).get_repo(f"{owner}/{repo}").get_release(release_id)
        )

        release = Release(repo, owner, token, logger)
        release._copy_from_release_object(github_release)

        return release
