import json
import sys
from typing import Any, List, Optional, Tuple

import pytest
from oras.client import OrasClient
from oras.provider import Registry

sys.path.append("src")

from gardenlinux.oci.__main__ import main as gl_oci

from ..constants import (
    GARDENLINUX_ROOT_DIR_EXAMPLE,
    REGISTRY,
    REGISTRY_URL,
    REPOSITORY_NAME_ZOT_EXAMPLE,
    TEST_ARCHITECTURES,
    TEST_COMMIT,
    TEST_FEATURE_SET,
    TEST_FEATURE_STRINGS_SHORT,
    TEST_PLATFORMS,
    TEST_VERSION,
    TEST_VERSION_STABLE,
)


def push_manifest(
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    arch: str,
    cname: str,
    additional_tags: Optional[List[str]] = None,
) -> None:
    """Push manifest to registry and return success status"""
    print(f"Pushing manifest for {cname} {arch}")

    args = [
        "gl-oci",
        "push-manifest",
        "--repository",
        REPOSITORY_NAME_ZOT_EXAMPLE,
        "--cname",
        cname,
        "--arch",
        arch,
        "--version",
        version,
        "--commit",
        TEST_COMMIT,
        "--dir",
        GARDENLINUX_ROOT_DIR_EXAMPLE,
        "--cosign-file",
        "digest",
        "--manifest-file",
        "manifests/manifest.json",
        "--insecure",
    ]

    if additional_tags:
        for tag in additional_tags:
            args.extend(["--additional-tag", tag])

    monkeypatch.setattr(
        sys,
        "argv",
        args,
    )

    gl_oci()


def push_manifest_tags(
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    arch: str,
    cname: str,
    tags: Optional[List[str]] = None,
) -> None:
    """Push manifest to registry and return success status"""
    print(f"Pushing manifest for {cname} {arch}")

    args = [
        "gl-oci",
        "push-manifest-tags",
        "--repository",
        REPOSITORY_NAME_ZOT_EXAMPLE,
        "--cname",
        cname,
        "--arch",
        arch,
        "--version",
        version,
        "--commit",
        TEST_COMMIT,
        "--insecure",
    ]

    if tags:
        for tag in tags:
            args.extend(["--tag", tag])

    monkeypatch.setattr(
        sys,
        "argv",
        args,
    )

    gl_oci()


def update_index(
    monkeypatch: pytest.MonkeyPatch,
    version: str,
    additional_tags: Optional[List[str]] = None,
) -> None:
    """Update index in registry and return success status"""
    print("Updating index")

    args = [
        "gl-oci",
        "push-index-from-directory",
        "--index",
        REPOSITORY_NAME_ZOT_EXAMPLE,
        "--index-tag",
        version,
        "--insecure",
    ]

    if additional_tags:
        for tag in additional_tags:
            args.extend(["--additional-tag", tag])

    monkeypatch.setattr(
        sys,
        "argv",
        args,
    )

    gl_oci()


def get_catalog(client: OrasClient) -> List[Any]:
    """Get catalog from registry and return repositories list"""
    catalog_resp = client.do_request(f"{REGISTRY_URL}/v2/_catalog")

    assert catalog_resp.status_code == 200, (
        f"Failed to get catalog, status: {catalog_resp.status_code}"
    )

    catalog_json = json.loads(catalog_resp.text)
    return catalog_json.get("repositories", [])  # type: ignore[no-any-return]


def get_tags(client: OrasClient, repo: str) -> List[str]:
    """Get tags for a repository"""
    tags_resp = client.do_request(f"{REGISTRY_URL}/v2/{repo}/tags/list")

    assert tags_resp.status_code == 200, (
        f"Failed to get tags for {repo}, status: {tags_resp.status_code}"
    )

    tags_json = json.loads(tags_resp.text)
    return tags_json.get("tags", [])  # type: ignore[no-any-return]


def get_manifest(
    client: OrasClient, repo: str, reference: str
) -> Tuple[Any, str | None]:
    """Get manifest and digest for a repository reference"""
    # Create a simple request for the manifest
    manifest_resp = client.do_request(
        f"{REGISTRY_URL}/v2/{repo}/manifests/{reference}",
        headers={
            "Accept": "application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.index.v1+json"
        },
    )

    assert manifest_resp.status_code == 200, (
        f"Failed to get manifest for {repo}:{reference}, status: {manifest_resp.status_code}"
    )

    # Get the digest and content - use headers.get() instead of header.Get()
    digest = manifest_resp.headers.get("Docker-Content-Digest")
    manifest_json = json.loads(manifest_resp.text)

    return manifest_json, digest


def verify_index_manifest(manifest: Any, expected_arch: str) -> None:
    """Verify the index manifest has expected content"""
    assert manifest.get("schemaVersion") == 2, "Manifest should have schema version 2"
    assert "manifests" in manifest, "Manifest should contain manifests array"

    # Verify the manifests list contains an entry for the expected architecture
    found = False
    for m in manifest.get("manifests", []):
        if m.get("platform", {}).get("architecture") == expected_arch:
            found = True
            break

    assert found, f"Manifest should contain an entry for architecture {expected_arch}"


def verify_combined_tag_manifest(
    manifest: Any,
    arch: str,
    cname: str,
    version: str,
    feature_set: str,
    commit: str,
) -> None:
    """Verify the combined tag manifest has expected content"""
    assert manifest.get("schemaVersion") == 2, "Manifest should have schema version 2"
    assert "layers" in manifest, "Manifest should contain layers array"
    assert "annotations" in manifest, "Manifest should contain annotations"

    annotations = manifest.get("annotations", {})

    assert annotations.get("cname") == cname, f"Manifest should have cname {cname}"

    assert annotations.get("architecture") == arch, (
        f"Manifest should have architecture {arch}"
    )

    if feature_set:
        assert annotations.get("feature_set") == feature_set, (
            f"Manifest should have feature_set {feature_set}"
        )

    assert annotations.get("version") == version, (
        f"Manifest should have version {version}"
    )

    if commit:
        assert annotations.get("commit") == commit, (
            f"Manifest should have commit {commit}"
        )


def verify_additional_tags(
    client: OrasClient,
    repo: str,
    additional_tags: List[str],
    reference_digest: Optional[str] = None,
    fail_on_missing: bool = True,
) -> List[str]:
    """
    Verify that all additional tags exist and match the reference digest if provided.

    Args:
        client: Reggie client
        repo: Repository name
        additional_tags: List of tags to verify
        reference_digest: Optional digest to compare against
        fail_on_missing: If True, fail the test when tags are missing

    Returns:
        List of missing tags
    """
    missing_tags = []

    for tag in additional_tags:
        print(f"Verifying additional tag: {tag}")
        try:
            # Create a simple request for the manifest
            tag_resp = client.do_request(
                f"{REGISTRY_URL}/v2/{repo}/manifests/{tag}",
                headers={
                    "Accept": "application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.index.v1+json"
                },
            )

            if tag_resp.status_code != 200:
                print(
                    f"✗ Could not find additional tag {tag}: status {tag_resp.status_code}"
                )
                missing_tags.append(tag)
                continue

            # Get the digest
            digest = tag_resp.headers.get("Docker-Content-Digest")

            # Check digest if reference provided
            if reference_digest and digest != reference_digest:
                print(
                    f"✗ Tag {tag} has different digest: {digest} (expected {reference_digest})"
                )
                missing_tags.append(tag)
                continue

            print(f"✓ Successfully verified additional tag {tag} with digest: {digest}")

        except Exception as e:
            print(f"✗ Error verifying tag {tag}: {str(e)}")
            missing_tags.append(tag)

    # If any tags are missing and fail_on_missing is True, fail the test
    if missing_tags and fail_on_missing:
        missing_tags_str = "\n  - ".join(missing_tags)
        pytest.fail(f"Missing tags:\n  - {missing_tags_str}")

    return missing_tags


@pytest.mark.usefixtures("zot_session")
@pytest.mark.parametrize(
    "version, cname, arch, additional_tags_index, additional_tags_manifest",
    [
        (
            TEST_VERSION,
            f"{platform}-{feature_string}",
            arch,
            [
                f"{TEST_VERSION}-patch",
                f"{TEST_VERSION}-patch-{TEST_COMMIT}",
                f"{TEST_VERSION_STABLE}",
                f"{TEST_VERSION_STABLE}-stable",
                "latest",
            ],
            [
                f"{TEST_VERSION}-patch-{platform}-{feature_string}-{arch}",
                f"{TEST_VERSION}-{TEST_COMMIT}-patch-{platform}-{feature_string}-{arch}",
                f"{platform}-{feature_string}-{TEST_VERSION}-{TEST_COMMIT}-{arch}",
            ],
        )
        for platform in TEST_PLATFORMS
        for feature_string in TEST_FEATURE_STRINGS_SHORT
        for arch in TEST_ARCHITECTURES
    ],
)
def test_push_manifest_and_index(
    version: str,
    arch: str,
    cname: str,
    additional_tags_index: List[str],
    additional_tags_manifest: List[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    print(f"\n\n=== Starting test for {cname} {arch} {version} ===")
    repo_name = "gardenlinux-example"
    combined_tag = f"{version}-{cname}-{arch}-{version}-{TEST_COMMIT}-{arch}"

    post_push_manifest_tags = []

    # Push manifest and update index
    if cname.startswith(f"{TEST_PLATFORMS[1]}-"):
        post_push_manifest_tags = additional_tags_manifest
        additional_tags_manifest = []

    push_manifest(monkeypatch, version, arch, cname, additional_tags_manifest)

    if len(post_push_manifest_tags) > 0:
        push_manifest_tags(monkeypatch, version, arch, cname, post_push_manifest_tags)

    update_index(monkeypatch, version, additional_tags_index)

    # Verify registry contents
    print(f"\n=== Verifying registry for {cname} {arch} {version} ===")

    # Initialize reggie client
    client = Registry(hostname=REGISTRY, insecure=True)

    # Get repositories and verify main repo exists
    print("\nFetching catalog...")
    repositories = get_catalog(client)
    print(f"Found repositories: {repositories}")

    assert repo_name in repositories, f"Repository {repo_name} should exist in catalog"

    # Get tags for main repo
    print(f"\nFetching tags for {repo_name}...")
    tags = get_tags(client, repo_name)
    print(f"Tags for {repo_name}: {tags}")

    # FIRST: Verify manifest with combined tag (the actual artifact)
    print(f"\n=== Verifying manifest with combined tag {combined_tag} ===")
    if combined_tag in tags:
        manifest, manifest_digest = get_manifest(client, repo_name, combined_tag)
        print(f"Successfully retrieved manifest with digest: {manifest_digest}")
        verify_combined_tag_manifest(
            manifest, arch, cname, version, TEST_FEATURE_SET, TEST_COMMIT
        )

        # Verify additional tags for manifest
        print("\n=== Verifying additional tags for manifest ===")
        verify_additional_tags(
            client,
            repo_name,
            additional_tags_manifest,
            reference_digest=manifest_digest,
            fail_on_missing=True,
        )
    else:
        pytest.fail(f"Combined tag {combined_tag} not found in repository {repo_name}")

    # SECOND: Verify index (the collection of manifests)
    print(f"\n=== Verifying index with tag {version} ===")
    if version in tags:
        index_manifest, index_digest = get_manifest(client, repo_name, version)
        print(f"Successfully retrieved index with digest: {index_digest}")
        verify_index_manifest(index_manifest, arch)

        # Verify additional tags for index
        print("\n=== Verifying additional tags for index ===")
        verify_additional_tags(
            client,
            repo_name,
            additional_tags_index,
            reference_digest=index_digest,
            fail_on_missing=True,
        )
    else:
        pytest.fail(f"Tag {version} not found in repository {repo_name}")

    print("\n=== Registry verification completed ===")
