from pathlib import Path
import subprocess
import sys

from ..logger import LoggerSetup


class Git:
    """Git operations handler."""

    def __init__(self, logger=None):
        """Initialize Git handler.

        Args:
            logger: Optional logger instance
        """
        self.log = logger or LoggerSetup.get_logger("gardenlinux.git")

    def get_root(self):
        """Get the root directory of the current Git repository."""
        try:
            root_dir = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], text=True
            ).strip()
            self.log.debug(f"Git root directory: {root_dir}")
            return Path(root_dir)
        except subprocess.CalledProcessError as e:
            self.log.error(
                "Not a git repository or unable to determine root directory."
            )
            self.log.debug(f"Git command failed with: {e}")
            sys.exit(1)
