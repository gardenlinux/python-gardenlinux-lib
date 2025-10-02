import sys

import pytest
import requests
import requests_mock

import gardenlinux.github.release.__main__ as gh
from gardenlinux.github.release import upload_to_github_release_page

from ..constants import TEST_GARDENLINUX_RELEASE


def test_upload_to_github_release_page_dryrun(caplog, artifact_for_upload):
    with requests_mock.Mocker():
        assert (
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                artifact_for_upload,
                dry_run=True,
            )
            is None
        )
        assert any(
            "Dry run: would upload" in record.message for record in caplog.records
        ), "Expected a dry‑run log entry"


def test_upload_to_github_release_page_needs_github_token(
    downloads_dir, artifact_for_upload
):
    with requests_mock.Mocker():
        with pytest.raises(ValueError) as exn:
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                artifact_for_upload,
                dry_run=False,
            )
            assert (
                str(exn.value) == "GITHUB_TOKEN environment variable not set"
            ), "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"


def test_upload_to_github_release_page(
    downloads_dir, caplog, github_token, artifact_for_upload
):
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=201,
        )

        upload_to_github_release_page(
            "gardenlinux",
            "gardenlinux",
            TEST_GARDENLINUX_RELEASE,
            artifact_for_upload,
            dry_run=False,
        )
        assert any(
            "Upload successful" in record.message for record in caplog.records
        ), "Expected an upload confirmation log entry"


def test_upload_to_github_release_page_unreadable_artifact(
    downloads_dir, caplog, github_token, artifact_for_upload
):
    artifact_for_upload.chmod(0)

    upload_to_github_release_page(
        "gardenlinux",
        "gardenlinux",
        TEST_GARDENLINUX_RELEASE,
        artifact_for_upload,
        dry_run=False,
    )
    assert any(
        "Error reading file" in record.message for record in caplog.records
    ), "Expected an error message log entry"


def test_upload_to_github_release_page_failed(
    downloads_dir, caplog, github_token, artifact_for_upload
):
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{TEST_GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=503,
        )

        with pytest.raises(requests.exceptions.HTTPError):
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                TEST_GARDENLINUX_RELEASE,
                artifact_for_upload,
                dry_run=False,
            )
        assert any(
            "Upload failed with status code 503:" in record.message
            for record in caplog.records
        ), "Expected an error HTTP status code to be logged"


def test_script_parse_args_wrong_command(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["gh", "rejoice"])

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert (
        "argument command: invalid choice: 'rejoice'" in captured.err
    ), "Expected help message printed"


def test_script_parse_args_upload_command_required_args(monkeypatch, capfd):
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


def test_script_upload_dry_run(monkeypatch, capfd):
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
            TEST_GARDENLINUX_RELEASE,
            "--file_path",
            "foo",
            "--dry-run",
        ],
    )
    monkeypatch.setattr(
        "gardenlinux.github.release.__main__.upload_to_github_release_page",
        lambda a1, a2, a3, a4, dry_run: print(f"dry-run: {dry_run}"),
    )

    gh.main()
    captured = capfd.readouterr()

    assert captured.out == "dry-run: True\n"
