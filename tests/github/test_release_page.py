import os
import shutil
from pathlib import Path

import pytest
import requests_mock
from git import Repo

from gardenlinux.apt.debsource import DebsrcFile
from gardenlinux.features import CName
from gardenlinux.github.__main__ import (
    GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME, _get_package_list,
    download_metadata_file, get_variant_from_flavor)
from gardenlinux.s3 import S3Artifacts

GARDENLINUX_RELEASE = "1877.3"
GARDENLINUX_COMMIT = "75df9f401a842914563f312899ec3ce34b24515c"
GARDENLINUX_COMMIT_SHORT = GARDENLINUX_COMMIT[:8]

GLVD_BASE_URL = "https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1"
GL_REPO_BASE_URL = "https://packages.gardenlinux.io/gardenlinux"

TEST_DATA_DIR = Path(os.path.dirname(__file__)) / ".." / ".." / "test-data" / "release_notes"
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


def test_github_release_page(monkeypatch, downloads_dir):
    monkeypatch.setattr("gardenlinux.github.__main__.Repo", SubmoduleAsRepo)
    import gardenlinux.github

    release_fixture_path = TEST_DATA_DIR / f"github_release_notes_{GARDENLINUX_RELEASE}.md"
    glvd_response_fixture_path = TEST_DATA_DIR / f"glvd_{GARDENLINUX_RELEASE}.json"

    with requests_mock.Mocker(real_http=True) as m:
        with open(glvd_response_fixture_path) as resp_json:
            m.get(
                f"{GLVD_BASE_URL}/patchReleaseNotes/{GARDENLINUX_RELEASE}",
                text=resp_json.read(),
                status_code=200
            )
            generated_release_notes = gardenlinux.github.create_github_release_notes(
                GARDENLINUX_RELEASE,
                GARDENLINUX_COMMIT
            )

            with open(release_fixture_path) as md:
                release_notes_fixture = md.read()
                assert generated_release_notes == release_notes_fixture
