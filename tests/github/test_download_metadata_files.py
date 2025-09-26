import pytest

from gardenlinux.constants import (
    GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME,
    S3_DOWNLOADS_DIR,
)
from gardenlinux.features import CName
from gardenlinux.github.release_notes.helpers import download_metadata_file
from gardenlinux.s3 import S3Artifacts

from ..constants import (
    RELEASE_NOTES_S3_ARTIFACTS_DIR,
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_COMMIT_SHORT,
    TEST_GARDENLINUX_RELEASE,
)


def test_download_metadata_file(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT}")

    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(TEST_GARDENLINUX_RELEASE, TEST_GARDENLINUX_COMMIT_SHORT))
    download_metadata_file(s3_artifacts,
                           cname.cname,
                           TEST_GARDENLINUX_RELEASE,
                           TEST_GARDENLINUX_COMMIT_SHORT,
                           S3_DOWNLOADS_DIR)
    assert (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_release(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT}")
    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    release = "0000.0"
    commit = TEST_GARDENLINUX_COMMIT_SHORT
    cname = CName("aws-gardener_prod", "amd64", "{0}-{1}".format(release, commit))
    with pytest.raises(IndexError):
        download_metadata_file(s3_artifacts,
                               cname.cname,
                               release,
                               commit,
                               S3_DOWNLOADS_DIR)
    assert not (S3_DOWNLOADS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_commit(downloads_dir, release_s3_bucket):
    release_s3_bucket.upload_file(RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT}")

    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)
    release = TEST_GARDENLINUX_RELEASE
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
    release_s3_bucket.upload_file(RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml",
                                  f"meta/singles/aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT}")

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
