import builtins
from pathlib import Path

import pytest

import gardenlinux.oci.layer as gl_layer


class DummyLayer:
    """Minimal stub for oras.oci.Layer"""

    def __init__(self, blob_path, media_type=None, is_dir=False):
        self._init_args = (blob_path, media_type, is_dir)

    def to_dict(self):
        return {"dummy": True}


@pytest.fixture(autouse=True)
def patch__Layer(monkeypatch):
    """Replace oras.oci.Layer with DummyLayer in Layer's module."""
    monkeypatch.setattr(gl_layer, "_Layer", DummyLayer)
    yield


def test_dict_property_returns_with_annotations(tmp_path):
    """dict property should merge _Layer.to_dict() with annotations."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")

    # Act
    l = gl_layer.Layer(blob)
    result = l.dict

    # Assert
    assert result["dummy"] is True
    assert "annotations" in result
    assert result["annotations"]["org.opencontainers.image.title"] == "blob.txt"


def test_getitem_and_delitem_annotations(tmp_path):
    """getitem should return annotations, delitem should clear them."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act / Assert (__getitem__)
    ann = l["annotations"]
    assert isinstance(ann, dict)
    assert "org.opencontainers.image.title" in ann

    # Act / Assert (__delitem__)
    l.__delitem__("annotations")
    assert l._annotations == {}


def test_getitem_invalid_key_raises(tmp_path):
    """getitem with unsupported key should raise KeyError."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act / Assert
    with pytest.raises(KeyError):
        _ = l["invalid"]


def test_setitem_annotations(tmp_path):
    """setitem with supported keys should set annotations"""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act
    new_ann = {"x": "y"}
    l.__setitem__("annotations", new_ann)

    # Assert
    assert l._annotations == new_ann


def test_setitem_annotations_invalid_raises(tmp_path):
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act / Assert
    with pytest.raises(KeyError):
        _ = l["invalid"]


def test_len_iter(tmp_path):
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act
    keys = list(iter(l))

    # Assert
    assert keys == ["annotations"]
    assert len(keys) == 1


def test_gen_metadata_from_file(tmp_path):
    # Arrange
    blob = tmp_path / "blob.tar"
    blob.write_text("data")
    l = gl_layer.Layer(blob)

    # Act
    arch = "amd64"
    metadata = gl_layer.Layer.generate_metadata_from_file_name(blob, arch)

    # Assert
    assert metadata["file_name"] == "blob.tar"
    assert "media_type" in metadata
    assert metadata["annotations"]["io.gardenlinux.image.layer.architecture"] == arch


def test_lookup_media_type_for_file_name(tmp_path):
    # Arrange
    blob = tmp_path / "blob.tar"
    blob.write_text("data")

    # Act
    media_type = gl_layer.Layer.lookup_media_type_for_file_name(blob)
    from gardenlinux.constants import GL_MEDIA_TYPE_LOOKUP

    assert media_type == GL_MEDIA_TYPE_LOOKUP["tar"]


def test_lookup_media_type_for_file_name_invalid_raises(tmp_path):
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        gl_layer.Layer.lookup_media_type_for_file_name(tmp_path / "unknown.xyz")
