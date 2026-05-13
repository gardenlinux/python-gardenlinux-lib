import pytest
import requests_mock
from github import GithubException

from gardenlinux.github.release import Release

from ..constants import (
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_RELEASE_MINOR,
)
from .constants import REPO_JSON


def test_release(caplog: pytest.LogCaptureFixture, github_token: str) -> None:
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE_MINOR
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


def test_release_create_needs_github_token() -> None:
    with (
        requests_mock.Mocker(),
        pytest.raises(ValueError, match="GITHUB_TOKEN environment variable not set"),
    ):
        _ = Release("gardenlinux", "gardenlinux")


def test_release_raise_on_failure(
    caplog: pytest.LogCaptureFixture, github_token: str
) -> None:
    with requests_mock.Mocker() as m:
        release = Release("gardenlinux", "gardenlinux", token="test")

        release.tag = TEST_GARDENLINUX_RELEASE_MINOR
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


def test_release_id_raises_value_error_if_not_set(github_token: str) -> None:
    release = Release("gardenlinux", "gardenlinux", token="test")

    release.tag = TEST_GARDENLINUX_RELEASE_MINOR
    release.commitish = TEST_GARDENLINUX_COMMIT
    release.is_latest = False
    release.body = ""

    with pytest.raises(ValueError):
        release.id


def test_release_set_name(github_token: str) -> None:
    release = Release("gardenlinux", "gardenlinux", token="test")

    with pytest.raises(ValueError):
        release.name

    release.name = "name"
    assert release.name == "name", "Set name to name"


def test_release_set_pre_release(github_token: str) -> None:
    release = Release("gardenlinux", "gardenlinux", token="test")
    assert not release.is_pre_release, "Default value for is_pre_release is False"

    release.is_pre_release = True
    assert release.is_pre_release, "Set is_pre_release to True"
