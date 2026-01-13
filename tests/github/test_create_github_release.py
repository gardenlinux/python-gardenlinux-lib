from pathlib import Path

import pytest
import requests
import requests_mock

from gardenlinux.github.release import create_github_release, write_to_release_id_file

from ..constants import TEST_GARDENLINUX_COMMIT, TEST_GARDENLINUX_RELEASE


def test_create_github_release_needs_github_token() -> None:
    with requests_mock.Mocker():
        with pytest.raises(ValueError) as exn:
            create_github_release(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                TEST_GARDENLINUX_COMMIT,
                False,
                "",
            )
            assert str(exn.value) == "GITHUB_TOKEN environment variable not set", (
                "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"
            )


def test_create_github_release_raise_on_failure(
    caplog: pytest.LogCaptureFixture, github_token: None
) -> None:
    with requests_mock.Mocker() as m:
        with pytest.raises(requests.exceptions.HTTPError):
            m.post(
                "https://api.github.com/repos/gardenlinux/gardenlinux/releases",
                text="{}",
                status_code=503,
            )
            create_github_release(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                TEST_GARDENLINUX_COMMIT,
                False,
                "",
            )
        assert any(
            "Failed to create release" in record.message for record in caplog.records
        ), "Expected a failure log record"


def test_create_github_release(
    caplog: pytest.LogCaptureFixture, github_token: None
) -> None:
    with requests_mock.Mocker() as m:
        m.post(
            "https://api.github.com/repos/gardenlinux/gardenlinux/releases",
            text='{"id": 101}',
            status_code=201,
        )
        assert (
            create_github_release(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                TEST_GARDENLINUX_COMMIT,
                False,
                "",
            )
            == 101
        )
        assert any(
            "Release created successfully" in record.message
            for record in caplog.records
        ), "Expected a success log record"


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
