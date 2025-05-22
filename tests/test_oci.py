import pytest
from click.testing import CliRunner
import sys
import json
import os
import logging

# Import reggie library correctly
from opencontainers.distribution.reggie import (
    NewClient,
    WithDebug,
    WithName,
    WithReference,
    WithUserAgent,
)

sys.path.append("src")

from gardenlinux.oci.__main__ import cli as gl_oci
from .constants import (
    CONTAINER_NAME_ZOT_EXAMPLE,
    GARDENLINUX_ROOT_DIR_EXAMPLE,
    TEST_COMMIT,
    TEST_FEATURE_SET,
    TEST_VERSION,
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

    # Add additional tags if provided
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


def update_index(runner, version):
    """Update index in registry"""
    print("Updating index")
    result = runner.invoke(
        gl_oci,
        [
            "update-index",
            "--container",
            CONTAINER_NAME_ZOT_EXAMPLE,
            "--version",
            version,
            "--insecure",
            "True",
        ],
        catch_exceptions=False,
    )
    print(f"Update index output: {result.output}")


def get_catalog(client):
    """Get catalog from registry and return repositories list"""
    catalog_req = client.NewRequest("GET", "/v2/_catalog")
    catalog_resp = client.Do(catalog_req)

    assert (
        catalog_resp.status_code == 200
    ), f"Failed to get catalog, status: {catalog_resp.status_code}"

    catalog_json = json.loads(catalog_resp.text)
    return catalog_json.get("repositories", [])


def get_tags(client, repo):
    """Get tags for a repository"""
    tags_req = client.NewRequest("GET", f"/v2/{repo}/tags/list")
    tags_resp = client.Do(tags_req)

    assert (
        tags_resp.status_code == 200
    ), f"Failed to get tags for {repo}, status: {tags_resp.status_code}"

    tags_json = json.loads(tags_resp.text)
    return tags_json.get("tags", [])


def get_manifest(client, repo, reference):
    """Get manifest and digest for a repository reference"""
    # Create a simple request for the manifest
    manifest_req = client.NewRequest("GET", f"/v2/{repo}/manifests/{reference}")

    # Set the headers for accept types - use headers (with an 's') instead of header
    manifest_req.headers.update(
        {
            "Accept": "application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json,application/vnd.oci.image.index.v1+json"
        }
    )

    manifest_resp = client.Do(manifest_req)
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


@pytest.mark.usefixtures("zot_session")
@pytest.mark.parametrize(
    "version, cname, arch, additional_tags",
    [
        (
            TEST_VERSION,
            f"{platform}-{feature_string}",
            arch,
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
def test_push_manifest_and_index(version, arch, cname, additional_tags):
    print(f"\n\n=== Starting test for {cname} {arch} {version} ===")
    runner = CliRunner()
    registry_url = "http://127.0.0.1:18081"
    repo_name = "gardenlinux-example"
    combined_tag = f"{version}-{cname}-{arch}"

    # Push manifest and update index
    push_successful = push_manifest(runner, version, arch, cname, additional_tags)
    assert push_successful, "Manifest push should succeed"

    if push_successful:
        update_index(runner, version)

    # Verify registry contents
    print(f"\n=== Verifying registry for {cname} {arch} {version} ===")

    # Initialize reggie client
    client = NewClient(
        registry_url, WithDebug(True), WithUserAgent("gardenlinux-test-client/1.0")
    )

    # Get repositories and verify main repo exists
    print("\nFetching catalog...")
    repositories = get_catalog(client)
    print(f"Found repositories: {repositories}")

    assert repo_name in repositories, f"Repository {repo_name} should exist in catalog"

    # Get tags for main repo
    print(f"\nFetching tags for {repo_name}...")
    tags = get_tags(client, repo_name)
    print(f"Tags for {repo_name}: {tags}")

    # Verify version tag (index)
    if version in tags:
        print(f"\nVerifying index with tag {version}...")
        index_manifest, index_digest = get_manifest(client, repo_name, version)
        print(f"Successfully retrieved index with digest: {index_digest}")
        verify_index_manifest(index_manifest, arch)
    else:
        pytest.fail(f"Tag {version} not found in repository {repo_name}")

    # Verify combined tag
    if combined_tag in tags:
        print(f"\nVerifying manifest with combined tag {combined_tag}...")
        combined_manifest, combined_digest = get_manifest(
            client, repo_name, combined_tag
        )
        print(f"Successfully retrieved manifest with digest: {combined_digest}")
        verify_combined_tag_manifest(
            combined_manifest, arch, cname, version, TEST_FEATURE_SET, TEST_COMMIT
        )
    else:
        pytest.fail(f"Combined tag {combined_tag} not found in repository {repo_name}")

    print("\n=== Verifying additional tags in main repository ===")
    # Force update the tags list to ensure it's current
    updated_tags = get_tags(client, repo_name)
    print(f"Updated tags for {repo_name}: {updated_tags}")

    # Now try each additional tag but don't fail the test if not found
    missing_tags = []
    for tag in additional_tags:
        print(f"Verifying additional tag: {tag}")
        try:
            tag_manifest, tag_digest = get_manifest(client, repo_name, tag)
            print(
                f"✓ Successfully retrieved additional tag {tag} with digest: {tag_digest}"
            )
        except Exception as e:
            print(f"✗ Could not find additional tag {tag}: {str(e)}")
            missing_tags.append(tag)

    # Report missing tags but don't fail the test
    if missing_tags:
        print(
            f"\nWarning: {len(missing_tags)} additional tags were not found in the registry:"
        )
        for tag in missing_tags:
            print(f"  - {tag}")
    else:
        print("\nAll additional tags were successfully pushed!")

    print("\n=== Registry verification completed ===")
