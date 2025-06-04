# -*- coding: utf-8 -*-

import sys
from git import Repo
from git import Git as _Git
from os import PathLike
from pathlib import Path

from ..logger import LoggerSetup


class Git(object):
    """Git operations handler."""

    def __init__(self, git_directory=".", logger=None):
        """Initialize Git handler.

        Args:
            logger: Optional logger instance
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
        """Get the commit ID for Git `HEAD`."""
        return str(self.root_repo.head.commit)

    @property
    def root(self):
        """Get the root directory of the current Git repository."""
        root_dir = _Git(self._git_directory).rev_parse(
            "--show-superproject-working-tree"
        )

        self._logger.debug(f"Git root directory: {root_dir}")
        return Path(root_dir)

    @property
    def root_repo(self):
        """Get the root Git `Repo` instance."""
        return Repo(self.root)
