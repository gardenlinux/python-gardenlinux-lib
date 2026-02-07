from pathlib import Path

import pytest
import requests_mock
from github import GithubException

from gardenlinux.github.release import Release, write_to_release_id_file

from ..constants import (
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_RELEASE,
)
from .constants import REPO_JSON


def test_Release_create_needs_github_token() -> None:
    with (
        requests_mock.Mocker(),
        pytest.raises(ValueError, match="GITHUB_TOKEN environment variable not set"),
    ):
        _ = Release("gardenlinux", "gardenlinux")


def test_Release_raise_on_failure(
    caplog: pytest.LogCaptureFixture, github_token: str
) -> None:
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE
        release.commitish = TEST_GARDENLINUX_COMMIT
        release.is_latest = False
        release.body = ""

        with pytest.raises(GithubException):
            m.get(
                "//api.github.com:443/repos/gardenlinux/gardenlinux",
                json=REPO_JSON,
                status_code=200,
            )

            m.post(
                "//api.github.com:443/repos/gardenlinux/gardenlinux/releases",
                json={},
                status_code=503,
            )

            release.create()


def test_Release(caplog: pytest.LogCaptureFixture, github_token: str) -> None:
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE
        release.commitish = TEST_GARDENLINUX_COMMIT
        release.is_latest = False
        release.body = ""

        m.get(
            "//api.github.com:443/repos/gardenlinux/gardenlinux",
            json=REPO_JSON,
            status_code=200,
        )

        m.post(
            "//api.github.com:443/repos/gardenlinux/gardenlinux/releases",
            json={"id": 101},
            status_code=201,
        )

        assert release.create() == 101


def test_write_to_release_id_file(release_id_file: Path) -> None:
    write_to_release_id_file(TEST_GARDENLINUX_RELEASE)
    assert release_id_file.read_text() == TEST_GARDENLINUX_RELEASE


def test_write_to_release_id_file_broken_file_permissions(
    release_id_file: Path, caplog: pytest.LogCaptureFixture
) -> None:
    release_id_file.touch(0)  # this will make the file unwritable

    with pytest.raises(SystemExit):
        write_to_release_id_file(TEST_GARDENLINUX_RELEASE)
    assert any("Could not create" in record.message for record in caplog.records), (
        "Expected a failure log record"
    )
