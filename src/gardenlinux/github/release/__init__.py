import json
import logging
import os
import sys

import requests

from ...constants import RELEASE_ID_FILE, REQUESTS_TIMEOUTS
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


def upload_to_github_release_page(
    github_owner: str,
    github_repo: str,
    gardenlinux_release_id: str | int,
    file_to_upload: str,
    dry_run: bool,
) -> None:
    if dry_run:
        LOGGER.info(
            f"Dry run: would upload {file_to_upload} to release {gardenlinux_release_id} in repo {github_owner}/{github_repo}"
        )
        return

    if os.path.getsize(file_to_upload) < 1:
        LOGGER.info(f"{file_to_upload} is empty and will be ignored")
        return

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/octet-stream",
    }

    upload_url = f"https://uploads.github.com/repos/{github_owner}/{github_repo}/releases/{gardenlinux_release_id}/assets?name={os.path.basename(file_to_upload)}"

    try:
        with open(file_to_upload, "rb") as f:
            file_contents = f.read()
    except IOError as e:
        LOGGER.error(f"Error reading file {file_to_upload}: {e}")
        return

    response = requests.post(
        upload_url, headers=headers, data=file_contents, timeout=REQUESTS_TIMEOUTS
    )
    if response.status_code == 201:
        LOGGER.info("Upload successful")
    else:
        LOGGER.error(
            f"Upload failed with status code {response.status_code}: {response.text}"
        )
        response.raise_for_status()


__all__ = ["Release", "write_to_release_id_file", "upload_to_github_release_page"]
