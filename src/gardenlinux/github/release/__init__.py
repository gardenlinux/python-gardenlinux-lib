import json
import os
import sys

import requests

from gardenlinux.constants import RELEASE_ID_FILE, REQUESTS_TIMEOUTS
from gardenlinux.logger import LoggerSetup

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release", "INFO")


def create_github_release(owner, repo, tag, commitish, latest, body):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {
        "tag_name": tag,
        "target_commitish": commitish,
        "name": tag,
        "body": body,
        "draft": False,
        "prerelease": False,
        "make_latest": "true" if latest else "false"
    }

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        data=json.dumps(data),
        timeout=REQUESTS_TIMEOUTS
    )

    if response.status_code == 201:
        LOGGER.info("Release created successfully")
        response_json = response.json()
        return response_json.get("id")
    else:
        LOGGER.error("Failed to create release")
        LOGGER.debug(response.json())
        response.raise_for_status()


def write_to_release_id_file(release_id):
    try:
        with open(RELEASE_ID_FILE, "w") as file:
            file.write(release_id)
        LOGGER.info(f"Created {RELEASE_ID_FILE} successfully.")
    except IOError as e:
        LOGGER.error(f"Could not create {RELEASE_ID_FILE} file: {e}")
        sys.exit(1)


def upload_to_github_release_page(
    github_owner, github_repo, gardenlinux_release_id, file_to_upload, dry_run
):
    if dry_run:
        LOGGER.info(
            f"Dry run: would upload {file_to_upload} to release {gardenlinux_release_id} in repo {github_owner}/{github_repo}"
        )
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

    response = requests.post(upload_url, headers=headers, data=file_contents, timeout=REQUESTS_TIMEOUTS)
    if response.status_code == 201:
        LOGGER.info("Upload successful")
    else:
        LOGGER.error(
            f"Upload failed with status code {response.status_code}: {response.text}"
        )
        response.raise_for_status()
