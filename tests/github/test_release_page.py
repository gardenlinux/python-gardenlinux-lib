import os
import shutil
import sys
from pathlib import Path

import pytest
import requests
import requests_mock
from git import Repo
from moto import mock_aws

import gardenlinux
import gardenlinux.github.__main__ as gh
from gardenlinux.apt.debsource import DebsrcFile
from gardenlinux.features import CName
from gardenlinux.github.__main__ import (
    GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME, RELEASE_ID_FILE, _get_package_list,
    create_github_release, download_metadata_file,
    get_file_extension_for_platform, get_platform_display_name,
    get_platform_release_note_data, get_variant_from_flavor,
    release_notes_changes_section,
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
    f = Path(RELEASE_ID_FILE)
    yield f
    f.unlink()


@pytest.fixture
def github_token():
    os.environ["GITHUB_TOKEN"] = "foobarbazquux"
    yield
    del os.environ["GITHUB_TOKEN"]


@pytest.fixture
def release_s3_bucket():
    with mock_aws():
        s3 = boto3.resource("s3", region_name="eu-central-1")
        s3.create_bucket(Bucket=GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME,
                         CreateBucketConfiguration={
                             'LocationConstraint': 'eu-central-1'})
        yield s3.Bucket(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)


@pytest.fixture
def artifact_for_upload(downloads_dir):
    artifact = S3_DOWNLOADS_DIR / "artifact.log"
    artifact.touch()
    yield artifact
    artifact.unlink()


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


def test_write_to_release_id_file(release_id_file):
    write_to_release_id_file(GARDENLINUX_RELEASE)
    assert release_id_file.read_text() == GARDENLINUX_RELEASE


def test_write_to_release_id_file_broken_file_permissions(release_id_file, caplog):
    release_id_file.touch(0)  # this will make the file unwritable

    with pytest.raises(SystemExit):
        write_to_release_id_file(GARDENLINUX_RELEASE)
    assert any("Could not create" in record.message for record in caplog.records), "Expected a failure log record"


def test_download_metadata_file(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(S3_ARTIFACTS / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}")

    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(GARDENLINUX_RELEASE, GARDENLINUX_COMMIT_SHORT))
    download_metadata_file(s3_artifacts,
                           cname.cname,
                           GARDENLINUX_RELEASE,
                           GARDENLINUX_COMMIT_SHORT,
                           S3_DOWNLOADS_DIR)
    assert (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_release(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(S3_ARTIFACTS / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}")
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


def test_download_metadata_file_no_such_commit(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(S3_ARTIFACTS / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}")

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


def test_download_metadata_file_no_such_release_and_commit(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(S3_ARTIFACTS / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}")

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
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/patchReleaseNotes/{GARDENLINUX_RELEASE}",
            text='{"packageList": []}',
            status_code=200
        )
        assert release_notes_changes_section(GARDENLINUX_RELEASE) == "", \
            "Expected an empty result if GLVD returns an empty package list"


def test_release_notes_changes_section_broken_glvd_response():
    with requests_mock.Mocker() as m:
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


def test_create_github_release_needs_github_token():
    with requests_mock.Mocker():
        with pytest.raises(ValueError) as exn:
            create_github_release(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                GARDENLINUX_COMMIT,
                "")
            assert str(exn.value) == "GITHUB_TOKEN environment variable not set", \
                "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"


def test_create_github_release_raise_on_failure(caplog, github_token):
    with requests_mock.Mocker() as m:
        with pytest.raises(requests.exceptions.HTTPError):
            m.post(
                "https://api.github.com/repos/gardenlinux/gardenlinux/releases",
                text="{}",
                status_code=503
            )
            create_github_release(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                GARDENLINUX_COMMIT,
                "")
        assert any("Failed to create release" in record.message for record in caplog.records), "Expected a failure log record"


def test_create_github_release(caplog, github_token):
    with requests_mock.Mocker() as m:
        m.post(
            "https://api.github.com/repos/gardenlinux/gardenlinux/releases",
            text='{"id": 101}',
            status_code=201
        )
        assert create_github_release(
            "gardenlinux",
            "gardenlinux",
            GARDENLINUX_RELEASE,
            GARDENLINUX_COMMIT,
            "") == 101
        assert any("Release created successfully" in record.message for record in caplog.records), "Expected a success log record"


@mock_aws
def test_github_release_page(monkeypatch, downloads_dir, release_s3_bucket):
    monkeypatch.setattr("gardenlinux.github.__main__.Repo", SubmoduleAsRepo)
    import gardenlinux.github

    release_fixture_path = TEST_DATA_DIR / f"github_release_notes_{GARDENLINUX_RELEASE}.md"
    glvd_response_fixture_path = TEST_DATA_DIR / f"glvd_{GARDENLINUX_RELEASE}.json"

    with requests_mock.Mocker(real_http=True) as m:
        for yaml_file in S3_ARTIFACTS.glob("*.yaml"):
            filename = yaml_file.name
            base = filename[:-len(".s3_metadata.yaml")]
            key = f"meta/singles/{base}-{GARDENLINUX_RELEASE}-{GARDENLINUX_COMMIT}"
            release_s3_bucket.upload_file(str(yaml_file), key)

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


def test_upload_to_github_release_page_dryrun(caplog, artifact_for_upload):
    with requests_mock.Mocker():
        assert upload_to_github_release_page(
            "gardenlinux",
            "gardenlinux",
            GARDENLINUX_RELEASE,
            artifact_for_upload,
            dry_run=True) is None
        assert any("Dry run: would upload" in record.message for record in caplog.records), "Expected a dry‑run log entry"


def test_upload_to_github_release_page_needs_github_token(downloads_dir, artifact_for_upload):
    with requests_mock.Mocker():
        with pytest.raises(ValueError) as exn:
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                artifact_for_upload,
                dry_run=False)
            assert str(exn.value) == "GITHUB_TOKEN environment variable not set", \
                "Expected an exception to be raised on missing GITHUB_TOKEN environment variable"


def test_upload_to_github_release_page(downloads_dir, caplog, github_token, artifact_for_upload):
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=201
        )

        upload_to_github_release_page(
            "gardenlinux",
            "gardenlinux",
            GARDENLINUX_RELEASE,
            artifact_for_upload,
            dry_run=False)
        assert any("Upload successful" in record.message for record in caplog.records), \
            "Expected an upload confirmation log entry"


def test_upload_to_github_release_page_unreadable_artifact(downloads_dir, caplog, github_token, artifact_for_upload):
    artifact_for_upload.chmod(0)

    upload_to_github_release_page(
        "gardenlinux",
        "gardenlinux",
        GARDENLINUX_RELEASE,
        artifact_for_upload,
        dry_run=False)
    assert any("Error reading file" in record.message for record in caplog.records), \
        "Expected an error message log entry"


def test_upload_to_github_release_page_failed(downloads_dir, caplog, github_token, artifact_for_upload):
    with requests_mock.Mocker(real_http=True) as m:
        m.post(
            f"https://uploads.github.com/repos/gardenlinux/gardenlinux/releases/{GARDENLINUX_RELEASE}/assets?name=artifact.log",
            text="{}",
            status_code=503
        )

        with pytest.raises(requests.exceptions.HTTPError):
            upload_to_github_release_page(
                "gardenlinux",
                "gardenlinux",
                GARDENLINUX_RELEASE,
                artifact_for_upload,
                dry_run=False)
        assert any("Upload failed with status code 503:" in record.message for record in caplog.records), \
            "Expected an error HTTP status code to be logged"


def test_script_parse_args_wrong_command(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["gh", "rejoice"])

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "argument command: invalid choice: 'rejoice'" in captured.err, "Expected help message printed"


def test_script_parse_args_create_command_required_args(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["gh", "create", "--owner", "gardenlinux", "--repo", "gardenlinux"])

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "the following arguments are required: --tag, --commit" in captured.err, \
        "Expected help message on missing arguments for 'create' command"


def test_script_parse_args_upload_command_required_args(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["gh", "upload", "--owner", "gardenlinux", "--repo", "gardenlinux"])

    with pytest.raises(SystemExit):
        gh.main()
    captured = capfd.readouterr()

    assert "the following arguments are required: --release_id, --file_path" in captured.err, \
        "Expected help message on missing arguments for 'upload' command"


def test_script_create_dry_run(monkeypatch, capfd):

    monkeypatch.setattr(sys, "argv", ["gh", "create", "--owner", "gardenlinux", "--repo",
                        "gardenlinux", "--tag", GARDENLINUX_RELEASE, "--commit", GARDENLINUX_COMMIT, "--dry-run"])
    monkeypatch.setattr("gardenlinux.github.__main__.create_github_release_notes",
                        lambda tag, commit: f"{tag} {commit}")

    gh.main()
    captured = capfd.readouterr()

    assert captured.out == f"{GARDENLINUX_RELEASE} {GARDENLINUX_COMMIT}\n", \
        "Expected dry-run create to return generated release notes text"


def test_script_create(monkeypatch, caplog):
    monkeypatch.setattr(sys, "argv", ["gh", "create", "--owner", "gardenlinux", "--repo",
                        "gardenlinux", "--tag", GARDENLINUX_RELEASE, "--commit", GARDENLINUX_COMMIT])
    monkeypatch.setattr("gardenlinux.github.__main__.create_github_release_notes",
                        lambda tag, commit: f"{tag} {commit}")
    monkeypatch.setattr("gardenlinux.github.__main__.create_github_release",
                        lambda a1, a2, a3, a4, a5: GARDENLINUX_RELEASE)

    gh.main()

    assert any(f"Release created with ID: {GARDENLINUX_RELEASE}" in record.message for record in caplog.records), \
        "Expected a release creation confirmation log entry"


def test_script_upload_dry_run(monkeypatch, capfd):
    monkeypatch.setattr(sys, "argv", ["gh", "upload", "--owner", "gardenlinux", "--repo",
                        "gardenlinux", "--release_id", GARDENLINUX_RELEASE, "--file_path", "foo", "--dry-run"])
    monkeypatch.setattr("gardenlinux.github.__main__.upload_to_github_release_page",
                        lambda a1, a2, a3, a4, dry_run: print(f"dry-run: {dry_run}"))

    gh.main()
    captured = capfd.readouterr()

    assert captured.out == "dry-run: True\n"
