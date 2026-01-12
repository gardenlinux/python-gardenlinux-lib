import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import gardenlinux.features.metadata_main as metadata_main

from .constants import generate_container_amd64_release_metadata


def test_main_output(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test successful "output-release-metadata"
    """
    # Arrange
    argv = [
        "prog",
        "--cname",
        "container-amd64",
        "--version",
        "today",
        "--commit",
        "local",
        "output-release-metadata",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Act
    metadata_main.main()

    # Assert
    expected = generate_container_amd64_release_metadata("today", "local")
    assert expected == capsys.readouterr().out.strip()


def test_main_write(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test successful "write"
    """
    # Arrange
    with TemporaryDirectory() as tmpdir:
        os_release_file = Path(tmpdir, "os_release")
        argv = [
            "prog",
            "--cname",
            "container-amd64",
            "--version",
            "today",
            "--commit",
            "local",
            "--release-file",
            str(os_release_file),
            "write",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        # Act
        metadata_main.main()

        # Assert
        expected = generate_container_amd64_release_metadata("today", "local")
        assert expected == os_release_file.open("r").read()


def test_main_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test validation between release metadata and arguments given
    """
    # Arrange
    with TemporaryDirectory() as tmpdir:
        os_release_file = Path(tmpdir, "os_release")

        with os_release_file.open("w") as fp:
            fp.write(generate_container_amd64_release_metadata("today", "local"))

        argv = [
            "prog",
            "--cname",
            "base-python-amd64",
            "--version",
            "today",
            "--commit",
            "local",
            "--release-file",
            str(os_release_file),
            "output-release-metadata",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        # Act / Assert
        with pytest.raises(RuntimeError):
            metadata_main.main()
