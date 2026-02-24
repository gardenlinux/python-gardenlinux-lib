import logging
import sys

from ...constants import RELEASE_ID_FILE
from ...logger import LoggerSetup
from .release import Release

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release", logging.INFO)


def write_to_release_id_file(release_id: str | int) -> None:
    try:
        with open(RELEASE_ID_FILE, "w") as file:
            file.write(str(release_id))
        LOGGER.info(f"Created {RELEASE_ID_FILE} successfully.")
    except IOError as e:
        LOGGER.error(f"Could not create {RELEASE_ID_FILE} file: {e}")
        sys.exit(1)


__all__ = ["Release", "write_to_release_id_file"]
