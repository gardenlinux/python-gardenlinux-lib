import subprocess
from pathlib import Path
import sys

from ..logging import Logger

def get_git_root(logger=None):
    """Get the root directory of the current Git repository.
    
    Args:
        logger: Optional logger instance. If not provided, will use module's logger.
    """
    log = logger or Logger.get_logger("gardenlinux.git")
    
    try:
        root_dir = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        log.debug(f"Git root directory: {root_dir}")
        return Path(root_dir)
    except subprocess.CalledProcessError as e:
        log.error("Not a git repository or unable to determine root directory.")
        log.debug(f"Git command failed with: {e}")
        sys.exit(1)