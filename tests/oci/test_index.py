import json
from typing import Any, Dict

import pytest

from gardenlinux.oci import ImageManifest, Index


def test_index_init_and_json() -> None:
    """Ensure Index init works correctly"""
    # Arrange
    idx = Index()

    # Act
    json_bytes = idx.json
    decoded = json.loads(json_bytes.decode("utf-8"))

    # Assert
    assert "schemaVersion" in idx
    assert isinstance(json_bytes, bytes)
    assert decoded == idx


def test_manifests_as_dict() -> None:
    """Verify manifests_as_dict returns correct keys for cname and digest cases."""
    # Arrange
    idx = Index()
    manifest_abn = {
        "digest": "sha256:abc",
        "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "foo"},
    }
    manifest_no_abn = {"digest": "sha256:def"}
    idx["manifests"] = [manifest_abn, manifest_no_abn]

    # Act
    result = idx.manifests_as_dict

    # Assert
    assert result["foo"] == manifest_abn
    assert result["sha256:def"] == manifest_no_abn


def test_append_manifest_replace() -> None:
    """Ensure append_manifest replaces existing manifest with same cname."""
    # Arrange
    idx = Index()
    idx["manifests"] = [
        {
            "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "old"},
            "digest": "sha256:old",
        },
        {
            "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "other"},
            "digest": "sha256:other",
        },
    ]
    new_manifest = {
        "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "old"},
        "digest": "sha256:new",
    }

    # Act
    idx.append_manifest(new_manifest)

    # Assert
    abns = [
        manifest["annotations"][ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY]
        for manifest in idx["manifests"]
    ]
    assert "old" in abns
    assert any(manifest["digest"] == "sha256:new" for manifest in idx["manifests"])


def test_append_manifest_cname_not_found() -> None:
    """Test appending new manifest if cname isn't found."""
    # Arrange
    idx = Index()
    idx["manifests"] = [
        {
            "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "foo"},
            "digest": "sha256:foo",
        }
    ]
    new_manifest = {
        "annotations": {ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY: "bar"},
        "digest": "sha256:bar",
    }

    # Act
    idx.append_manifest(new_manifest)

    # Assert
    abns = [
        manifest["annotations"][ImageManifest.ANNOTATION_ARTIFACT_BASE_NAME_KEY]
        for manifest in idx["manifests"]
    ]
    assert "bar" in abns


@pytest.mark.parametrize(
    "manifest",
    [
        {"annotations": {}},
        {"annotations": {}, "digest": "sha256:foo"},
    ],
)
def test_append_accept_all_manifests(manifest: Dict[str, Any]) -> None:
    """Test proper error handling for invalid append_manifest input."""
    # Arrange
    idx = Index()
    idx.append_manifest(manifest)

    # Act
    assert len(idx.manifests_as_dict) == 1


@pytest.mark.parametrize(
    "bad_manifest",
    [
        "not-a-dict",
    ],
)
def test_append_invalid_input_raises(bad_manifest: Dict[str, Any]) -> None:
    """Test proper error handling for invalid append_manifest input."""
    # Arrange
    idx = Index()

    # Act / Assert
    with pytest.raises((TypeError, ValueError)):
        idx.append_manifest(bad_manifest)
