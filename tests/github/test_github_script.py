import sys

import pytest

import gardenlinux.github.release.__main__ as gh
from gardenlinux.constants import GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME

from ..constants import TEST_GARDENLINUX_COMMIT, TEST_GARDENLINUX_RELEASE


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
        sys, "argv", ["gh", "create", "--owner", "gardenlinux", "--repo", "gardenlinux"]
    )

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "the following arguments are required: --tag, --commit" in captured.err, (
        "Expected help message on missing arguments for 'create' command"
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


def test_script_create_dry_run(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gh",
            "create",
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
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "gh",
            "create",
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
    monkeypatch.setattr(
        "gardenlinux.github.release.__main__.create_github_release",
        lambda a1, a2, a3, a4, a5, a6: TEST_GARDENLINUX_RELEASE,
    )

    gh.main()

    assert any(
        f"Release created with ID: {TEST_GARDENLINUX_RELEASE}" in record.message
        for record in caplog.records
    ), "Expected a release creation confirmation log entry"


def test_script_upload_dry_run(
    monkeypatch: pytest.MonkeyPatch, capfd: pytest.CaptureFixture[str]
) -> None:
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
