import sys
from pathlib import Path

import pytest
import requests_mock

import gardenlinux.github.release.__main__ as gh
from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME

from ..constants import TEST_GARDENLINUX_COMMIT, TEST_GARDENLINUX_RELEASE
from .constants import RELEASE_JSON, REPO_JSON, TEST_GARDENLINUX_RELEASE_ID


def test_script_parse_args_wrong_command(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["gh", "rejoice"])

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "argument command: invalid choice: 'rejoice'" in captured.err, (
        "Expected help message printed"
    )


def test_script_parse_args_create_command_required_args(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gh",
            "create-with-gl-release-notes",
            "--owner",
            "gardenlinux",
            "--repo",
            "gardenlinux",
        ],
    )

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "the following arguments are required: --tag, --commit" in captured.err, (
        "Expected help message on missing arguments for 'create' command"
    )


def test_script_create_dry_run(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gh",
            "create-with-gl-release-notes",
            "--owner",
            "gardenlinux",
            "--repo",
            "gardenlinux",
            "--tag",
            TEST_GARDENLINUX_RELEASE,
            "--commit",
            TEST_GARDENLINUX_COMMIT,
            "--dry-run",
        ],
    )
    monkeypatch.setattr(
        "gardenlinux.github.release.__main__.create_github_release_notes",
        lambda tag, commit, bucket: f"{tag} {commit} {bucket}",
    )

    gh.main()
    captured = capfd.readouterr()

    assert (
        captured.out
        == f"Dry Run ...\nThis release would be created:\n{TEST_GARDENLINUX_RELEASE} {TEST_GARDENLINUX_COMMIT} {GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME}\n"
    ), "Expected dry-run create to return generated release notes text"


def test_script_create(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    with requests_mock.Mocker() as m:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "gh",
                "create-with-gl-release-notes",
                "--owner",
                "gardenlinux",
                "--repo",
                "gardenlinux",
                "--tag",
                TEST_GARDENLINUX_RELEASE,
                "--commit",
                TEST_GARDENLINUX_COMMIT,
            ],
        )
        monkeypatch.setattr(
            "gardenlinux.github.release.__main__.create_github_release_notes",
            lambda tag, commit, bucket: f"{tag} {commit} {bucket}",
        )
        monkeypatch.setenv("GITHUB_TOKEN", "invalid")

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

        gh.main()

        assert any(
            "Release created with ID: 101" in record.message
            for record in caplog.records
        ), "Expected a release creation confirmation log entry"


def test_script_upload_needs_github_token(
    monkeypatch: pytest.MonkeyPatch, artifact_for_upload: Path
) -> None:
    with pytest.raises(ValueError) as exn:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "gh",
                "upload",
                "--owner",
                "gardenlinux",
                "--repo",
                "gardenlinux",
                "--release_id",
                str(TEST_GARDENLINUX_RELEASE_ID),
                "--file_path",
                str(artifact_for_upload),
                "--dry-run",
            ],
        )

        gh.main()

        assert str(exn.value) == "GITHUB_TOKEN environment variable not set", (
            "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"
        )


def test_script_parse_args_upload_command_required_args(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys, "argv", ["gh", "upload", "--owner", "gardenlinux", "--repo", "gardenlinux"]
    )

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert (
        "the following arguments are required: --release_id, --file_path"
        in captured.err
    ), "Expected help message on missing arguments for 'upload' command"


def test_script_upload_dry_run(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    github_token: str,
    artifact_for_upload: Path,
) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "//api.github.com:443/repos/gardenlinux/gardenlinux",
            json=REPO_JSON,
            status_code=200,
        )

        m.get(
            f"//api.github.com:443/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE_ID}",
            json=RELEASE_JSON,
            status_code=200,
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "gh",
                "upload",
                "--owner",
                "gardenlinux",
                "--repo",
                "gardenlinux",
                "--release_id",
                str(TEST_GARDENLINUX_RELEASE_ID),
                "--file_path",
                str(artifact_for_upload),
                "--dry-run",
            ],
        )

        gh.main()

        captured = capfd.readouterr()
        assert "would be uploaded for release" in captured.out, (
            "Expected a dry‑run log entry"
        )


def test_script_upload_inaccessible_file(
    monkeypatch: pytest.MonkeyPatch,
    capfd: pytest.CaptureFixture[str],
    github_token: str,
    artifact_for_upload: Path,
) -> None:
    artifact_for_upload.chmod(0)

    with requests_mock.Mocker() as m:
        m.get(
            "//api.github.com:443/repos/gardenlinux/gardenlinux",
            json=REPO_JSON,
            status_code=200,
        )

        m.get(
            f"//api.github.com:443/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE_ID}",
            json=RELEASE_JSON,
            status_code=200,
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "gh",
                "upload",
                "--owner",
                "gardenlinux",
                "--repo",
                "gardenlinux",
                "--release_id",
                str(TEST_GARDENLINUX_RELEASE_ID),
                "--file_path",
                str(artifact_for_upload),
            ],
        )

        with pytest.raises(PermissionError):
            gh.main()


def test_script_upload(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    github_token: str,
    artifact_for_upload: Path,
) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "//api.github.com:443/repos/gardenlinux/gardenlinux",
            json=REPO_JSON,
            status_code=200,
        )

        m.get(
            f"//api.github.com:443/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE_ID}",
            json=RELEASE_JSON,
            status_code=200,
        )

        m.post(
            f"//uploads.github.com:443/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE_ID}/assets?label=&name=artifact.log",
            json={},
            status_code=201,
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "gh",
                "upload",
                "--owner",
                "gardenlinux",
                "--repo",
                "gardenlinux",
                "--release_id",
                str(TEST_GARDENLINUX_RELEASE_ID),
                "--file_path",
                str(artifact_for_upload),
            ],
        )

        gh.main()

        assert any("Uploaded file" in record.message for record in caplog.records), (
            "Expected a upload file log entry"
        )
