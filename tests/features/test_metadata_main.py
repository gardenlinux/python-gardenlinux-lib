import logging
import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import gardenlinux.features.metadata_main as metadata_main
from gardenlinux.constants import (
    GL_BUG_REPORT_URL,
    GL_COMMIT_SPECIAL_VALUES,
    GL_DISTRIBUTION_NAME,
    GL_HOME_URL,
    GL_RELEASE_ID,
    GL_SUPPORT_URL,
)
from gardenlinux.features import CName


def get_container_amd64_release_metadata(version, commit_hash):
    return f"""
ID={GL_RELEASE_ID}
NAME="{GL_DISTRIBUTION_NAME}"
PRETTY_NAME="{GL_DISTRIBUTION_NAME} today"
IMAGE_VERSION=today
VARIANT_ID="container-amd64"
HOME_URL="{GL_HOME_URL}"
SUPPORT_URL="{GL_SUPPORT_URL}"
BUG_REPORT_URL="{GL_BUG_REPORT_URL}"
GARDENLINUX_CNAME="container-amd64-today-local"
GARDENLINUX_FEATURES="_slim,base,container"
GARDENLINUX_FEATURES_PLATFORMS="container"
GARDENLINUX_FEATURES_ELEMENTS="base"
GARDENLINUX_FEATURES_FLAGS="_slim"
GARDENLINUX_VERSION="today"
GARDENLINUX_COMMIT_ID="local"
GARDENLINUX_COMMIT_ID_LONG="local"
""".strip()

def test_main_output(monkeypatch, capsys):
    """
    Test successful "output-release-metadata"
    """
    # Arrange
    argv = ["prog", "--cname", "container-amd64", "--version", "today", "--commit", "local", "output-release-metadata"]
    monkeypatch.setattr(sys, "argv", argv)

    # Act
    metadata_main.main()

    # Assert
    expected = get_container_amd64_release_metadata("today", "local")
    assert expected == capsys.readouterr().out.strip()

def test_main_write(monkeypatch, capsys):
    """
    Test successful "write"
    """
    # Arrange
    with TemporaryDirectory() as tmpdir:
        os_release_file = Path(tmpdir, "os_release")
        argv = ["prog", "--cname", "container-amd64", "--version", "today", "--commit", "local", "--release-file", str(os_release_file), "write"]
        monkeypatch.setattr(sys, "argv", argv)

        # Act
        metadata_main.main()

        # Assert
        expected = get_container_amd64_release_metadata("today", "local")
        assert expected == os_release_file.open("r").read()

def test_main_validation(monkeypatch):
    """
    Test validation between release metadata and arguments given
    """
    # Arrange
    with TemporaryDirectory() as tmpdir:
        os_release_file = Path(tmpdir, "os_release")

        with os_release_file.open("w") as fp:
            fp.write(get_container_amd64_release_metadata("today", "local"))

        argv = ["prog", "--cname", "base-python-amd64", "--version", "today", "--commit", "local", "--release-file", str(os_release_file), "output-release-metadata"]
        monkeypatch.setattr(sys, "argv", argv)

        # Act / Assert
        with pytest.raises(AssertionError):
            metadata_main.main()
