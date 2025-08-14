import pytest
from click.testing import CliRunner
import sys
import json

# Import reggie library correctly
from oras.provider import Registry

sys.path.append("src")

from gardenlinux.oci.__main__ import cli as gl_oci

from ..constants import (
    CONTAINER_NAME_ZOT_EXAMPLE,
    GARDENLINUX_ROOT_DIR_EXAMPLE,
    REGISTRY,
    REGISTRY_URL,
    TEST_COMMIT,
    TEST_FEATURE_SET,
    TEST_VERSION,
    TEST_VERSION_STABLE,
    TEST_PLATFORMS,
    TEST_FEATURE_STRINGS_SHORT,
    TEST_ARCHITECTURES,
)


def push_manifest(runner, version, arch, cname, additional_tags=None):
    """Push manifest to registry and return success status"""
    print(f"Pushing manifest for {cname} {arch}")

    cmd = [
        "push-manifest",
        "--container",
        CONTAINER_NAME_ZOT_EXAMPLE,
        "--version",
        version,
        "--arch",
        arch,
        "--cname",
        cname,
        "--dir",
        GARDENLINUX_ROOT_DIR_EXAMPLE,
        "--insecure",
        "True",
        "--cosign_file",
        "digest",
        "--manifest_file",
        "manifests/manifest.json",
    ]

    if additional_tags:
        for tag in additional_tags:
            cmd.extend(["--additional_tag", tag])

    try:
        result = runner.invoke(
            gl_oci,
            cmd,
            catch_exceptions=False,
        )
        print(f"Push manifest output: {result.output}")
        return result.exit_code == 0
    except Exception as e:
        print(f"Error during push manifest: {str(e)}")
        return False


def update_index(runner, version, additional_tags=None):
    """Update index in registry and return success status"""
    print("Updating index")

    cmd = [
        "update-index",
        "--container",
        CONTAINER_NAME_ZOT_EXAMPLE,
        "--version",
        version,
        "--insecure",
        "True",
    ]

    if additional_tags:
        for tag in additional_tags:
            cmd.extend(["--additional_tag", tag])

    try:
        result = runner.invoke(
            gl_oci,
            cmd,
            catch_exceptions=False,
        )
        print(f"Update index output: {result.output}")
        return result.exit_code == 0
    except Exception as e:
        print(f"Error during update index: {str(e)}")
        return False


def get_catalog(client):
    """Get catalog from registry and return repositories list"""
    catalog_resp = client.do_request(f"{REGISTRY_URL}/v2/_catalog")

    assert (
        catalog_resp.status_code == 200
    ), f"Failed to get catalog, status: {catalog_resp.status_code}"

    catalog_json = json.loads(catalog_resp.text)
    return catalog_json.get("repositories", [])


def get_tags(client, repo):
    """Get tags for a repository"""
    tags_resp = client.do_request(f"{REGISTRY_URL}/v2/{repo}/tags/list")

    assert (
        tags_resp.status_code == 200
    ), f"Failed to get tags for {repo}, status: {tags_resp.status_code}"

    tags_json = json.loads(tags_resp.text)
    return tags_json.get("tags", [])


def get_manifest(client, repo, reference):
    """Get manifest and digest for a repository reference"""
    # Create a simple request for the manifest
    manifest_resp = client.do_request(
        f"{REGISTRY_URL}/v2/{repo}/manifests/{reference}",
        headers={
            "Accept": "application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.index.v1+json"
        },
    )

    assert (
        manifest_resp.status_code == 200
    ), f"Failed to get manifest for {repo}:{reference}, status: {manifest_resp.status_code}"

    # Get the digest and content - use headers.get() instead of header.Get()
    digest = manifest_resp.headers.get("Docker-Content-Digest")
    manifest_json = json.loads(manifest_resp.text)

    return manifest_json, digest


def verify_index_manifest(manifest, expected_arch):
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


def verify_combined_tag_manifest(manifest, arch, cname, version, feature_set, commit):
    """Verify the combined tag manifest has expected content"""
    assert manifest.get("schemaVersion") == 2, "Manifest should have schema version 2"
    assert "layers" in manifest, "Manifest should contain layers array"
    assert "annotations" in manifest, "Manifest should contain annotations"

    annotations = manifest.get("annotations", {})
    assert (
        annotations.get("architecture") == arch
    ), f"Manifest should have architecture {arch}"
    assert annotations.get("cname") == cname, f"Manifest should have cname {cname}"
    assert (
        annotations.get("version") == version
    ), f"Manifest should have version {version}"

    if feature_set:
        assert (
            annotations.get("feature_set") == feature_set
        ), f"Manifest should have feature_set {feature_set}"

    if commit:
        assert (
            annotations.get("commit") == commit
        ), f"Manifest should have commit {commit}"


def verify_additional_tags(
    client, repo, additional_tags, reference_digest=None, fail_on_missing=True
):
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
                f"latest",
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
    version, arch, cname, additional_tags_index, additional_tags_manifest
):
    print(f"\n\n=== Starting test for {cname} {arch} {version} ===")
    runner = CliRunner()
    repo_name = "gardenlinux-example"
    combined_tag = f"{version}-{cname}-{arch}"

    # Push manifest and update index
    push_successful = push_manifest(
        runner, version, arch, cname, additional_tags_manifest
    )
    assert push_successful, "Manifest push should succeed"

    if push_successful:
        update_index_successful = update_index(runner, version, additional_tags_index)
        assert update_index_successful, "Index update should succeed"

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
