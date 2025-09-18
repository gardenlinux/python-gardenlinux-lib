import os
import shutil
from pathlib import Path

import pytest
import requests
import requests_mock
from git import Repo
from moto import mock_aws

from gardenlinux.apt.debsource import DebsrcFile
from gardenlinux.features import CName
from gardenlinux.github.__main__ import (
    GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME, RELEASE_ID_FILE, _get_package_list,
    download_metadata_file, get_file_extension_for_platform,
    get_platform_display_name, get_platform_release_note_data,
    get_variant_from_flavor, release_notes_changes_section,
    release_notes_compare_package_versions_section,
    upload_to_github_release_page, write_to_release_id_file)
from gardenlinux.s3 import S3Artifacts

import boto3  # isort: skip


GARDENLINUX_RELEASE = "1877.3"
GARDENLINUX_COMMIT = "75df9f401a842914563f312899ec3ce34b24515c"
GARDENLINUX_COMMIT_SHORT = GARDENLINUX_COMMIT[:8]

GLVD_BASE_URL = "https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1"
GL_REPO_BASE_URL = "https://packages.gardenlinux.io/gardenlinux"

TEST_DATA_DIR = Path(os.path.dirname(__file__)) / ".." / ".." / "test-data" / "release_notes"
S3_ARTIFACTS = TEST_DATA_DIR / "s3_bucket_artifacts"
S3_DOWNLOADS_DIR = Path(os.path.dirname(__file__)) / ".." / ".." / "s3_downloads"

TEST_FLAVORS = [("foo_bar_baz", "legacy"),
                ("aws-gardener_prod_trustedboot_tpm2-amd64", "legacy"),
                ("openstack-gardener_prod_tpm2_trustedboot-arm64", "tpm2_trustedboot"),
                ("azure-gardener_prod_usi-amd64", "usi"),
                ("", "legacy")]


class SubmoduleAsRepo(Repo):
    """This will fake a git submodule as a git repository object."""
    def __new__(cls, *args, **kwargs):
        print('In SubmoduleAsRepo.__new__')
        r = super().__new__(Repo)
        r.__init__(*args, **kwargs)
        print(f'{r=}')

        maybe_gl_submodule = [submodule for submodule in r.submodules if submodule.name.endswith("/gardenlinux")]
        if not maybe_gl_submodule:
            return r
        else:
            gl = maybe_gl_submodule[0]
        print(f'{gl=}')

        sr = gl.module()
        print(f'{sr=}')
        sr.remotes.origin.pull("main")
        print('git pull done')
        return sr


@pytest.fixture
def downloads_dir():
    os.makedirs(S3_DOWNLOADS_DIR, exist_ok=True)
    yield
    shutil.rmtree(S3_DOWNLOADS_DIR)


@pytest.fixture
def release_id_file():
    # this will make the file unwritable
    with open(RELEASE_ID_FILE, "w"):
        pass
    os.chmod(RELEASE_ID_FILE, 0)
    yield
    os.remove(RELEASE_ID_FILE)


@pytest.mark.parametrize("flavor", TEST_FLAVORS)
def test_get_variant_from_flavor(flavor):
    assert get_variant_from_flavor(flavor[0]) == flavor[1]


def test_get_package_list():
    gl_packages_gz = TEST_DATA_DIR / "Packages.gz"

    with requests_mock.Mocker(real_http=True) as m:
        with open(gl_packages_gz, 'rb') as pgz:
            m.get(
                f"{GL_REPO_BASE_URL}/dists/{GARDENLINUX_RELEASE}/main/binary-amd64/Packages.gz",
                body=pgz,
                status_code=200
            )
    assert isinstance(_get_package_list(GARDENLINUX_RELEASE), DebsrcFile)


def test_get_platform_release_note_data_invalid_platform():
    assert get_platform_release_note_data("_", "foo") is None


def test_get_file_extension_for_platform_invalid_platform():
    assert get_file_extension_for_platform("foo") == ".raw"


def test_get_platform_display_name_invalid_platform():
    assert get_platform_display_name("foo") == "FOO"


def test_write_to_release_id_file_broken_file_permissions(release_id_file):
    with pytest.raises(SystemExit):
        write_to_release_id_file(GARDENLINUX_RELEASE)


def test_download_metadata_file(downloads_dir):
    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(GARDENLINUX_RELEASE, GARDENLINUX_COMMIT_SHORT))
    download_metadata_file(s3_artifacts,
                           cname.cname,
                           GARDENLINUX_RELEASE,
                           GARDENLINUX_COMMIT_SHORT,
                           S3_DOWNLOADS_DIR)
    assert (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_release(downloads_dir):
    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    release = "0000.0"
    commit = GARDENLINUX_COMMIT_SHORT
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(release, commit))
    with pytest.raises(IndexError):
        download_metadata_file(s3_artifacts,
                               cname.cname,
                               release,
                               commit,
                               S3_DOWNLOADS_DIR)
    assert not (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_commit(downloads_dir):
    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    release = GARDENLINUX_RELEASE
    commit = "deadbeef"
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(release, commit))
    with pytest.raises(IndexError):
        download_metadata_file(s3_artifacts,
                               cname.cname,
                               release,
                               commit,
                               S3_DOWNLOADS_DIR)
    assert not (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_release_and_commit(downloads_dir):
    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    release = "0000.0"
    commit = "deadbeef"
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(release, commit))
    with pytest.raises(IndexError):
        download_metadata_file(s3_artifacts,
                               cname.cname,
                               release,
                               commit,
                               S3_DOWNLOADS_DIR)
    assert not (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_release_notes_changes_section_empty_packagelist():
    with requests_mock.Mocker(real_http=True) as m:
        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{GARDENLINUX_RELEASE}",
            text='{"packageList": []}',
            status_code=200
        )
        assert release_notes_changes_section(GARDENLINUX_RELEASE) == "", \
            "Expected an empty result if GLVD returns an empty package list"


def test_release_notes_changes_section_broken_glvd_response():
    with requests_mock.Mocker(real_http=True) as m:
        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{GARDENLINUX_RELEASE}",
            text="<html><body><h1>Personal Home Page</h1></body></html>",
            status_code=200
        )
        assert "fill this in" in release_notes_changes_section(GARDENLINUX_RELEASE), \
            "Expected a placeholder message to be generated if GVLD response is not valid"


def test_release_notes_compare_package_versions_section_semver_is_not_recognized():
    assert release_notes_compare_package_versions_section("1.2.0", []) == "", "Semver is not supported"


def test_release_notes_compare_package_versions_section_unrecognizable_version():
    assert release_notes_compare_package_versions_section("garden.linux", []) == ""


@mock_aws
def test_github_release_page(monkeypatch, downloads_dir):
    monkeypatch.setattr("gardenlinux.github.__main__.Repo", SubmoduleAsRepo)
    import gardenlinux.github

    release_fixture_path = TEST_DATA_DIR / f"github_release_notes_{GARDENLINUX_RELEASE}.md"
    glvd_response_fixture_path = TEST_DATA_DIR / f"glvd_{GARDENLINUX_RELEASE}.json"

    with requests_mock.Mocker(real_http=True) as m:
        with mock_aws():
            s3 = boto3.resource("s3", region_name="eu-central-1")
            s3.create_bucket(Bucket=GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME,
                             CreateBucketConfiguration={
                                 'LocationConstraint': 'eu-central-1'})
            bucket = s3.Bucket(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
            for yaml_file in S3_ARTIFACTS.glob("*.yaml"):
                filename = yaml_file.name
                base = filename[:-len(".s3_metadata.yaml")]
                key = f"meta/singles/{base}-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}"
                bucket.upload_file(str(yaml_file), key)

            resp_json = glvd_response_fixture_path.read_text()
            m.get(
                f"{GLVD_BASE_URL}/patchReleaseNotes/{GARDENLINUX_RELEASE}",
                text=resp_json,
                status_code=200
            )
            generated_release_notes = gardenlinux.github.create_github_release_notes(
                GARDENLINUX_RELEASE,
                GARDENLINUX_COMMIT
            )

            release_notes_fixture = release_fixture_path.read_text()
            assert generated_release_notes == release_notes_fixture


def test_upload_to_github_release_page_dryrun(caplog):
    with requests_mock.Mocker():
        assert upload_to_github_release_page(
            "gardenlinux",
            "gardenlinux",
            GARDENLINUX_RELEASE,
            S3_DOWNLOADS_DIR / "artifact.log",
            dry_run=True) is None
        assert any("Dry run: would upload" in record.message for record in caplog.records), "Expected a dry‑run log entry"


def test_upload_to_github_release_page_needs_github_token():
    with requests_mock.Mocker():
        with pytest.raises(ValueError) as exn:
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                S3_DOWNLOADS_DIR / "artifact.log",
                dry_run=False)
            assert str(exn.value) == "GITHUB_TOKEN environment variable not set", \
                "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"


def test_upload_to_github_release_page(downloads_dir, caplog):
    os.environ["GITHUB_TOKEN"] = "foobarbazquux"
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=201
        )

        with open(S3_DOWNLOADS_DIR / "artifact.log", "w") as f:
            f.write("AllThePrettyLittleHorses")
        upload_to_github_release_page(
            "gardenlinux",
            "gardenlinux",
            GARDENLINUX_RELEASE,
            S3_DOWNLOADS_DIR / "artifact.log",
            dry_run=False)
        assert any("Upload successful" in record.message for record in caplog.records), \
            "Expected an upload confirmation log entry"


def test_upload_to_github_release_page_failed(downloads_dir, caplog):
    os.environ["GITHUB_TOKEN"] = "foobarbazquux"
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=503
        )

        with open(S3_DOWNLOADS_DIR / "artifact.log", "w") as f:
            f.write("AllThePrettyLittleHorses")
        with pytest.raises(requests.exceptions.HTTPError):
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                S3_DOWNLOADS_DIR / "artifact.log",
                dry_run=False)
        assert any("Upload failed with status code 503:" in record.message for record in caplog.records), \
            "Expected an error HTTP status code to be logged"
