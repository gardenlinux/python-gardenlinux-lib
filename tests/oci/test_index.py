import json

import pytest

from gardenlinux.oci.index import Index


def test_index_init_and_json():
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


def test_manifests_as_dict():
    """Verify manifests_as_dict returns correct keys for cname and digest cases."""
    # Arrange
    idx = Index()
    manifest_cname = {"digest": "sha256:abc", "annotations": {"cname": "foo"}}
    manifest_no_cname = {"digest": "sha256:def"}
    idx["manifests"] = [manifest_cname, manifest_no_cname]

    # Act
    result = idx.manifests_as_dict

    # Assert
    assert result["foo"] == manifest_cname
    assert result["sha256:def"] == manifest_no_cname


def test_append_manifest_replace():
    """Ensure append_manifest replaces existing manifest with same cname."""
    # Arrange
    idx = Index()
    idx["manifests"] = [
        {"annotations": {"cname": "old"}, "digest": "sha256:old"},
        {"annotations": {"cname": "other"}, "digest": "sha256:other"},
    ]
    new_manifest = {"annotations": {"cname": "old"}, "digest": "sha256:new"}

    # Act
    idx.append_manifest(new_manifest)

    # Assert
    cnames = [manifest["annotations"]["cname"] for manifest in idx["manifests"]]
    assert "old" in cnames
    assert any(manifest["digest"] == "sha256:new" for manifest in idx["manifests"])


def test_append_manifest_cname_not_found():
    """Test appending new manifest if cname isn't found."""
    # Arrange
    idx = Index()
    idx["manifests"] = [{"annotations": {"cname": "foo"}, "digest": "sha256:foo"}]
    new_manifest = {"annotations": {"cname": "bar"}, "digest": "sha256:bar"}

    # Act
    idx.append_manifest(new_manifest)

    # Assert
    cnames = [manifest["annotations"]["cname"] for manifest in idx["manifests"]]
    assert "bar" in cnames


@pytest.mark.parametrize(
    "bad_manifest",
    [
        "not-a-dict",
        {"annotations": {}},
    ],
)
def test_append_invalid_input_raises(bad_manifest):
    """Test proper error handling for invalid append_manifest input."""
    # Arrange
    idx = Index()

    # Act / Assert
    with pytest.raises(RuntimeError):
        idx.append_manifest(bad_manifest)
