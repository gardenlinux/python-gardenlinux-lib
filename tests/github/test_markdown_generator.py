import pytest
import requests_mock
from moto import mock_aws

from gardenlinux.constants import GLVD_BASE_URL
from gardenlinux.github.release import Release
from gardenlinux.github.release.notes import MarkdownGenerator
from gardenlinux.s3.bucket import Bucket

from ..constants import (
    RELEASE_ARTIFACTS_METADATA_FILES,
    RELEASE_NOTES_S3_ARTIFACTS_DIR,
    RELEASE_NOTES_TEST_DATA_DIR,
    REPO_NAME,
    TEST_GARDENLINUX_COMMIT,
    TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
    TEST_GARDENLINUX_RELEASE_MAJOR,
    TEST_GARDENLINUX_RELEASE_MINOR,
)

TEST_FLAVORS = [
    ("foo_bar_baz", "legacy"),
    ("aws-gardener_prod_trustedboot_tpm2-amd64", "legacy"),
    ("openstack-gardener_prod_tpm2_trustedboot-arm64", "tpm2_trustedboot"),
    ("azure-gardener_prod_usi-amd64", "usi"),
    ("", "legacy"),
]


def test_release_notes_changes_section_empty_packagelist(github_token: str) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/{TEST_GARDENLINUX_RELEASE_MINOR}",
            json={"packageList": []},
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = TEST_GARDENLINUX_RELEASE_MINOR
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert (
            "todo release facilitator: fill this in" in generator.changes_and_cves_list
        ), "Expected an placeholder result if GLVD returns an empty package list"


def test_release_notes_changes_section_broken_glvd_response(github_token: str) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/{TEST_GARDENLINUX_RELEASE_MINOR}",
            text="<html><body><h1>Personal Home Page</h1></body></html>",
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = TEST_GARDENLINUX_RELEASE_MINOR
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert (
            "todo release facilitator: fill this in" in generator.changes_and_cves_list
        ), (
            "Expected a placeholder message to be generated if GVLD response is not valid"
        )


def test_release_notes_compare_package_versions_section_legacy_versioning_is_recognized(
    github_token: str,
) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/1.0",
            json={
                "packageList": [
                    {
                        "sourcePackageName": "gardenlinux-release-example",
                        "oldVersion": "0.9pre1",
                        "newVersion": "1.0",
                        "fixedCves": [],
                    }
                ]
            },
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = "1.0"
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert (
            "upgrade 'gardenlinux-release-example'" in generator.changes_and_cves_list
        ), "Legacy versioning is supported"


def test_release_notes_compare_package_versions_section_semver_is_recognized(
    github_token: str,
) -> None:
    with requests_mock.Mocker() as m:
        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/1.20.0",
            json={
                "packageList": [
                    {
                        "sourcePackageName": "gardenlinux-release-example",
                        "oldVersion": "1.19.0",
                        "newVersion": "1.20.0",
                        "fixedCves": [],
                    }
                ]
            },
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = "1.20.0"
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert (
            "upgrade 'gardenlinux-release-example'" in generator.changes_and_cves_list
        ), "Semver is supported"


@mock_aws
def test_github_major_release_page(
    monkeypatch: pytest.MonkeyPatch,
    github_token: str,
    downloads_dir: None,
    release_s3_bucket: Bucket,
) -> None:
    release_fixture_path = (
        RELEASE_NOTES_TEST_DATA_DIR
        / f"github_release_notes_{TEST_GARDENLINUX_RELEASE_MAJOR}.md"
    )
    glvd_response_fixture_path = (
        RELEASE_NOTES_TEST_DATA_DIR / f"glvd_{TEST_GARDENLINUX_RELEASE_MAJOR}.json"
    )

    with requests_mock.Mocker(real_http=True) as m:
        for yaml_file in RELEASE_ARTIFACTS_METADATA_FILES:
            filepath = f"{RELEASE_NOTES_S3_ARTIFACTS_DIR}/{yaml_file}"
            base = yaml_file[: -len(".s3_metadata.yaml")]
            key = f"meta/singles/{base}-{TEST_GARDENLINUX_RELEASE_MAJOR}-{TEST_GARDENLINUX_COMMIT}"
            release_s3_bucket.upload_file(filepath, key)

        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/{TEST_GARDENLINUX_RELEASE_MAJOR}",
            text=glvd_response_fixture_path.read_text(),
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = f"{TEST_GARDENLINUX_RELEASE_MAJOR}"
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert str(generator) == release_fixture_path.read_text()


@mock_aws
def test_github_minor_release_page(
    monkeypatch: pytest.MonkeyPatch,
    github_token: str,
    downloads_dir: None,
    release_s3_bucket: Bucket,
) -> None:
    release_fixture_path = (
        RELEASE_NOTES_TEST_DATA_DIR
        / f"github_release_notes_{TEST_GARDENLINUX_RELEASE_MINOR}.md"
    )
    glvd_response_fixture_path = (
        RELEASE_NOTES_TEST_DATA_DIR / f"glvd_{TEST_GARDENLINUX_RELEASE_MINOR}.json"
    )

    with requests_mock.Mocker(real_http=True) as m:
        for yaml_file in RELEASE_ARTIFACTS_METADATA_FILES:
            filepath = f"{RELEASE_NOTES_S3_ARTIFACTS_DIR}/{yaml_file}"
            base = yaml_file[: -len(".s3_metadata.yaml")]
            key = f"meta/singles/{base}-{TEST_GARDENLINUX_RELEASE_MINOR}-{TEST_GARDENLINUX_COMMIT}"
            release_s3_bucket.upload_file(filepath, key)

        m.get(
            f"{GLVD_BASE_URL}/releaseNotes/{TEST_GARDENLINUX_RELEASE_MINOR}",
            text=glvd_response_fixture_path.read_text(),
            status_code=200,
        )

        release = Release(REPO_NAME)
        release.tag = TEST_GARDENLINUX_RELEASE_MINOR
        release.commitish = TEST_GARDENLINUX_COMMIT

        generator = MarkdownGenerator(
            release,
            TEST_GARDENLINUX_RELEASE_BUCKET_NAME,
        )

        assert str(generator) == release_fixture_path.read_text()
