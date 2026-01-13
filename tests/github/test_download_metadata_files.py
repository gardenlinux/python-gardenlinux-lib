import pytest

from gardenlinux.constants import S3_DOWNLOADS_DIR
from gardenlinux.features import CName
from gardenlinux.github.release_notes.helpers import download_metadata_file
from gardenlinux.s3 import Bucket, S3Artifacts

from ..constants import (
    RELEASE_NOTES_S3_ARTIFACTS_DIR,
    TEST_GARDENLINUX_COMMIT_SHORT,
    TEST_GARDENLINUX_RELEASE,
    TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
)


def test_download_metadata_file(downloads_dir: None, release_s3_bucket: Bucket) -> None:
    release_s3_bucket.upload_file(
        str(
            RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml"
        ),
        f"meta/singles/test-aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT_SHORT}",
    )

    s3_artifacts = S3Artifacts(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)
    s3_artifacts._bucket = release_s3_bucket

    cname = CName("test-aws-gardener_prod", "amd64", TEST_GARDENLINUX_COMMIT_SHORT)
    download_metadata_file(
        s3_artifacts,
        cname,
        TEST_GARDENLINUX_RELEASE,
        TEST_GARDENLINUX_COMMIT_SHORT,
        S3_DOWNLOADS_DIR,
    )
    assert (S3_DOWNLOADS_DIR / "test-aws-gardener_prod-amd64.s3_metadata.yaml").exists()


def test_download_metadata_file_no_such_release(
    downloads_dir: None, release_s3_bucket: Bucket
) -> None:
    release_s3_bucket.upload_file(
        str(
            RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml"
        ),
        f"meta/singles/test-aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT_SHORT}",
    )
    s3_artifacts = S3Artifacts(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)
    s3_artifacts._bucket = release_s3_bucket

    release = "0000.0"
    commit = TEST_GARDENLINUX_COMMIT_SHORT
    cname = CName("aws-gardener_prod", "amd64", commit)

    with pytest.raises(IndexError):
        download_metadata_file(
            s3_artifacts,
            cname,
            release,
            TEST_GARDENLINUX_COMMIT_SHORT,
            S3_DOWNLOADS_DIR,
        )
    assert not (
        S3_DOWNLOADS_DIR / "test-aws-gardener_prod-amd64.s3_metadata.yaml"
    ).exists()


def test_download_metadata_file_no_such_commit(
    downloads_dir: None, release_s3_bucket: Bucket
) -> None:
    release_s3_bucket.upload_file(
        str(
            RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml"
        ),
        f"meta/singles/test-aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT_SHORT}",
    )

    s3_artifacts = S3Artifacts(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)
    s3_artifacts._bucket = release_s3_bucket

    release = TEST_GARDENLINUX_RELEASE
    commit = "deadbeef"
    cname = CName("test-aws-gardener_prod", "amd64", commit)

    with pytest.raises(IndexError):
        download_metadata_file(
            s3_artifacts,
            cname,
            release,
            commit,
            S3_DOWNLOADS_DIR,
        )
    assert not (
        S3_DOWNLOADS_DIR / "test-aws-gardener_prod-amd64.s3_metadata.yaml"
    ).exists()


def test_download_metadata_file_no_such_release_and_commit(
    downloads_dir: None, release_s3_bucket: Bucket
) -> None:
    release_s3_bucket.upload_file(
        str(
            RELEASE_NOTES_S3_ARTIFACTS_DIR / "aws-gardener_prod-amd64.s3_metadata.yaml"
        ),
        f"meta/singles/test-aws-gardener_prod-amd64-{TEST_GARDENLINUX_RELEASE}-{TEST_GARDENLINUX_COMMIT_SHORT}",
    )

    s3_artifacts = S3Artifacts(TEST_GARDENLINUX_RELEASE_BUCKET_NAME)
    s3_artifacts._bucket = release_s3_bucket

    release = "0000.0"
    commit = "deadbeef"
    cname = CName("test-aws-gardener_prod", "amd64", commit)
    print(f"{cname.cname=}")

    with pytest.raises(IndexError):
        download_metadata_file(
            s3_artifacts,
            cname,
            release,
            TEST_GARDENLINUX_COMMIT_SHORT,
            S3_DOWNLOADS_DIR,
        )
    assert not (
        S3_DOWNLOADS_DIR / "test-aws-gardener_prod-amd64.s3_metadata.yaml"
    ).exists()
