import logging
import sys

from ...constants import RELEASE_ID_FILE
from ...logger import LoggerSetup
from .release import Release

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release", logging.INFO)


def create_github_release(
    owner: str, repo: str, tag: str, commitish: str, latest: bool, body: str
) -> int | None:
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
        "make_latest": "true" if latest else "false",
    }

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        data=json.dumps(data),
        timeout=REQUESTS_TIMEOUTS,
    )

    if response.status_code == 201:
        LOGGER.info("Release created successfully")
        response_json = response.json()
        return int(response_json.get("id"))  # Will raise KeyError if missing
    else:
        LOGGER.error("Failed to create release")
        LOGGER.debug(response.json())
        response.raise_for_status()

    return None  # Simply to make mypy happy. should not be reached.


def write_to_release_id_file(release_id: str | int) -> None:
    try:
        with open(RELEASE_ID_FILE, "w") as file:
            file.write(str(release_id))
        LOGGER.info(f"Created {RELEASE_ID_FILE} successfully.")
    except IOError as e:
        LOGGER.error(f"Could not create {RELEASE_ID_FILE} file: {e}")
        sys.exit(1)


__all__ = ["Release", "write_to_release_id_file"]
