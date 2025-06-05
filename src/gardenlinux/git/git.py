# -*- coding: utf-8 -*-

import sys
from git import Repo
from git import Git as _Git
from os import PathLike
from pathlib import Path

from ..logger import LoggerSetup


class Git(object):
    """
    Git operations handler based on the given Git directory.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: git
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, git_directory=".", logger=None):
        """
        Constructor __init__(Git)

        :param git_directory: Git directory
        :param logger: Logger instance

        :since: 0.7.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.git")

        if not isinstance(git_directory, PathLike):
            git_directory = Path(git_directory)

        if not git_directory.is_dir():
            raise RuntimeError(f"Git directory given is invalid: {git_directory}")

        self._git_directory = git_directory
        self._logger = logger

    @property
    def commit_id(self):
        """
        Returns the commit ID for Git `HEAD`.

        :return: (str) Git commit ID
        :since:  0.7.0
        """

        return str(self.root_repo.head.commit)

    @property
    def root(self):
        """
        Returns the root directory of the current Git repository.

        :return: (object) Git root directory
        :since:  0.7.0
        """

        root_dir = _Git(self._git_directory).rev_parse(
            "--show-superproject-working-tree"
        )

        self._logger.debug(f"Git root directory: {root_dir}")
        return Path(root_dir)

    @property
    def root_repo(self):
        """
        Returns the root Git `Repo` instance.

        :return: (object) Git root Git `Repo` instance
        :since:  0.7.0
        """

        return Repo(self.root)
