# -*- coding: utf-8 -*-

from git import Git as _Git
from pathlib import Path
import sys

from ..logger import LoggerSetup


class Git:
    """Git operations handler."""

    def __init__(self, logger=None):
        """Initialize Git handler.

        Args:
            logger: Optional logger instance
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.git")

        self._logger = logger

    def get_root(self):
        """Get the root directory of the current Git repository."""
        root_dir = Git(".").rev_parse("--show-superproject-working-tree")
        self.log.debug(f"Git root directory: {root_dir}")

        return Path(root_dir)
