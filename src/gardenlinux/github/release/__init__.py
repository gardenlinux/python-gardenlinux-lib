import os

import requests

from gardenlinux.logger import LoggerSetup

LOGGER = LoggerSetup.get_logger("gardenlinux.github", "INFO")

REQUESTS_TIMEOUTS = (5, 30)  # connect, read


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
