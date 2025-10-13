import pytest
import requests_mock
from git import Repo
from moto import mock_aws

from gardenlinux.constants import GLVD_BASE_URL
from gardenlinux.github.release_notes import (
    release_notes_changes_section,
    release_notes_compare_package_versions_section,
)
from gardenlinux.github.release_notes.deployment_platform import DeploymentPlatform
from gardenlinux.github.release_notes.helpers import get_variant_from_flavor

from ..constants import (
    RELEASE_NOTES_S3_ARTIFACTS_DIR,
    RELEASE_NOTES_TEST_DATA_DIR,
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_RELEASE,
)

TEST_FLAVORS = [("foo_bar_baz", "legacy"),
                ("aws-gardener_prod_trustedboot_tpm2-amd64", "legacy"),
                ("openstack-gardener_prod_tpm2_trustedboot-arm64", "tpm2_trustedboot"),
                ("azure-gardener_prod_usi-amd64", "usi"),
                ("", "legacy")]


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


def test_release_notes_compare_package_versions_section_legacy_versioning_is_recognized():
    assert "Full List of Packages in Garden Linux version 1.0" in \
        release_notes_compare_package_versions_section("1.0", {}), "Legacy versioning is supported"


def test_release_notes_compare_package_versions_section_legacy_versioning_patch_release_is_recognized(monkeypatch):
    def mock_compare_apt_repo_versions(previous_version, current_version):
        output = f"| Package | {previous_version} | {current_version} |\n"
        output += "|---------|--------------------|-------------------|\n"
        output += "|containerd|1.0|1.1|\n"
        return output

    monkeypatch.setattr("gardenlinux.github.release_notes.sections.compare_apt_repo_versions",
                        mock_compare_apt_repo_versions)

    assert "|containerd|1.0|1.1|" in \
        release_notes_compare_package_versions_section("1.1", {}), "Legacy versioning patch releases are supported"


def test_release_notes_compare_package_versions_section_semver_is_recognized():
    assert "Full List of Packages in Garden Linux version 1.20.0" in \
        release_notes_compare_package_versions_section("1.20.0", {}), "Semver is supported"


def test_release_notes_compare_package_versions_section_semver_patch_release_is_recognized(monkeypatch):
    def mock_compare_apt_repo_versions(previous_version, current_version):
        output = f"| Package | {previous_version} | {current_version} |\n"
        output += "|---------|--------------------|-------------------|\n"
        output += "|containerd|1.0|1.1|\n"
        return output

    monkeypatch.setattr("gardenlinux.github.release_notes.sections.compare_apt_repo_versions",
                        mock_compare_apt_repo_versions)

    assert "|containerd|1.0|1.1|" in \
        release_notes_compare_package_versions_section("1.20.1", {}), "Semver patch releases are supported"


def test_release_notes_compare_package_versions_section_unrecognizable_version(caplog):
    assert release_notes_compare_package_versions_section("garden.linux", {}) is None
    assert any("Unexpected version number format garden.linux" in
               record.message for record in caplog.records), "Expected an error log message"


@pytest.mark.parametrize("flavor", TEST_FLAVORS)
def test_get_variant_from_flavor(flavor):
    assert get_variant_from_flavor(flavor[0]) == flavor[1]


def test_default_get_file_extension_for_deployment_platform():
    assert DeploymentPlatform().image_extension() == "raw"


@mock_aws
def test_github_release_page(monkeypatch, downloads_dir, release_s3_bucket):

    class SubmoduleAsRepo(Repo):
        """This will fake a git submodule as a git repository object."""
        def __new__(cls, *args, **kwargs):
            r = super().__new__(Repo)
            r.__init__(*args, **kwargs)

            maybe_gl_submodule = [submodule for submodule in r.submodules if submodule.name.endswith("/gardenlinux")]
            if not maybe_gl_submodule:
                return r
            else:
                gl = maybe_gl_submodule[0]

            sr = gl.module()
            sr.remotes.origin.pull("main")
            return sr

    monkeypatch.setattr("gardenlinux.github.release_notes.helpers.Repo", SubmoduleAsRepo)
    import gardenlinux.github

    release_fixture_path = RELEASE_NOTES_TEST_DATA_DIR / f"github_release_notes_{TEST_GARDENLINUX_RELEASE}.md"
    glvd_response_fixture_path = RELEASE_NOTES_TEST_DATA_DIR / f"glvd_{TEST_GARDENLINUX_RELEASE}.json"

    with requests_mock.Mocker(real_http=True) as m:
        for yaml_file in RELEASE_NOTES_S3_ARTIFACTS_DIR.glob("*.yaml"):
            filename = yaml_file.name
            base = filename[:-len(".s3_metadata.yaml")]
            key = f"meta/singles/{base}-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT}"
            release_s3_bucket.upload_file(str(yaml_file), key)

        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{TEST_GARDENLINUX_RELEASE}",
            text=glvd_response_fixture_path.read_text(),
            status_code=200
        )
        generated_release_notes = gardenlinux.github.release_notes.create_github_release_notes(
            TEST_GARDENLINUX_RELEASE,
            TEST_GARDENLINUX_COMMIT,
            release_s3_bucket.name
        )

        assert generated_release_notes == release_fixture_path.read_text()
