from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest

import gardenlinux.oci.layer as gl_layer


class DummyLayer:
    """Minimal stub for oras.oci.Layer"""

    def __init__(
        self, blob_path: str, media_type: Optional[str] = None, is_dir: bool = False
    ):
        self._init_args = (blob_path, media_type, is_dir)

    def to_dict(self) -> Dict[str, Any]:
        return {"dummy": True}


@pytest.fixture(autouse=True)  # type: ignore[misc]
def patch__Layer(monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Replace oras.oci.Layer with DummyLayer in Layer's module."""
    monkeypatch.setattr(gl_layer, "_Layer", DummyLayer)
    yield


def test_dict_property_returns_with_annotations(tmp_path: Path) -> None:
    """dict property should merge _Layer.to_dict() with annotations."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")

    # Act
    layer = gl_layer.Layer(blob)
    result = layer.dict

    # Assert
    assert result["dummy"] is True
    assert "annotations" in result
    assert result["annotations"]["org.opencontainers.image.title"] == "blob.txt"


def test_getitem_and_delitem_annotations(tmp_path: Path) -> None:
    """getitem should return annotations, delitem should clear them."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    layer = gl_layer.Layer(blob)

    # Act / Assert (__getitem__)
    ann = layer["annotations"]
    assert isinstance(ann, dict)
    assert "org.opencontainers.image.title" in ann

    # Act / Assert (__delitem__)
    layer.__delitem__("annotations")
    assert layer._annotations == {}


def test_getitem_invalid_key_raises(tmp_path: Path) -> None:
    """getitem with unsupported key should raise KeyError."""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    layer = gl_layer.Layer(blob)

    # Act / Assert
    with pytest.raises(KeyError):
        _ = layer["invalid"]


def test_setitem_annotations(tmp_path: Path) -> None:
    """setitem with supported keys should set annotations"""
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    layer = gl_layer.Layer(blob)

    # Act
    new_ann = {"x": "y"}
    layer.__setitem__("annotations", new_ann)

    # Assert
    assert layer._annotations == new_ann


def test_setitem_annotations_invalid_raises(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    layer = gl_layer.Layer(blob)

    # Act / Assert
    with pytest.raises(KeyError):
        _ = layer["invalid"]


def test_len_iter(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")
    layer = gl_layer.Layer(blob)

    # Act
    keys = list(iter(layer))

    # Assert
    assert keys == ["annotations"]
    assert len(keys) == 1


def test_gen_metadata_from_file(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.tar"
    blob.write_text("data")

    # Act
    arch = "amd64"
    metadata = gl_layer.Layer.generate_metadata_from_file_name(blob, arch)

    # Assert
    assert metadata["file_name"] == "blob.tar"
    assert "media_type" in metadata
    assert metadata["annotations"]["io.gardenlinux.image.layer.architecture"] == arch


def test_lookup_media_type_for_file_name(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.tar"
    blob.write_text("data")

    # Act
    media_type = gl_layer.Layer.lookup_media_type_for_file_name(blob)
    from gardenlinux.constants import GL_MEDIA_TYPE_LOOKUP

    assert media_type == GL_MEDIA_TYPE_LOOKUP["tar"]


def test_lookup_media_type_for_file_name_invalid_raises(
    tmp_path: Path,
) -> None:
    # Arrange / Act / Assert
    with pytest.raises(ValueError):
        gl_layer.Layer.lookup_media_type_for_file_name(tmp_path / "unknown.xyz")
