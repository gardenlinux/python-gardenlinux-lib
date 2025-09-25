import requests_mock

from gardenlinux.constants import GLVD_BASE_URL
from gardenlinux.github.release_notes import (
    release_notes_changes_section,
    release_notes_compare_package_versions_section,
)

from ..constants import TEST_GARDENLINUX_RELEASE


def test_release_notes_changes_section_empty_packagelist():
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{TEST_GARDENLINUX_RELEASE}",
            text='{"packageList": []}',
            status_code=200
        )
        assert release_notes_changes_section(TEST_GARDENLINUX_RELEASE) == "", \
            "Expected an empty result if GLVD returns an empty package list"


def test_release_notes_changes_section_broken_glvd_response():
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{TEST_GARDENLINUX_RELEASE}",
            text="<html><body><h1>Personal Home Page</h1></body></html>",
            status_code=200
        )
        assert "fill this in" in release_notes_changes_section(TEST_GARDENLINUX_RELEASE), \
            "Expected a placeholder message to be generated if GVLD response is not valid"


def test_release_notes_compare_package_versions_section_semver_is_not_recognized():
    assert release_notes_compare_package_versions_section("1.2.0", []) == "", "Semver is not supported"


def test_release_notes_compare_package_versions_section_unrecognizable_version():
    assert release_notes_compare_package_versions_section("garden.linux", []) == ""
