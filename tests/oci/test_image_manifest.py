from pathlib import Path

import pytest

from gardenlinux.oci import ImageManifest, Layer


def test_ImageManifest_arch() -> None:
    # Arrange
    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={ImageManifest.ANNOTATION_ARCH_KEY: "amd64"})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.arch == "amd64"

    empty_manifest.arch = "amd64"
    assert empty_manifest.arch == "amd64"

    assert manifest.arch == "amd64"


def test_ImageManifest_cname() -> None:
    # Arrange
    cname = "container-amd64-today-local"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={ImageManifest.ANNOTATION_CNAME_KEY: cname})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.cname == cname

    empty_manifest.cname = cname
    assert empty_manifest.cname == cname

    assert manifest.cname == cname


def test_ImageManifest_feature_set() -> None:
    # Arrange
    feature_set = "container"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(
        annotations={ImageManifest.ANNOTATION_FEATURE_SET_KEY: feature_set}
    )

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.feature_set == feature_set

    empty_manifest.feature_set = feature_set
    assert empty_manifest.feature_set == feature_set

    assert manifest.feature_set == feature_set


def test_ImageManifest_flavor() -> None:
    # Arrange
    flavor = "container"
    cname = f"{flavor}-amd64-today-local"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={ImageManifest.ANNOTATION_CNAME_KEY: cname})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.flavor == flavor

    empty_manifest.cname = cname
    assert empty_manifest.flavor == flavor

    assert manifest.flavor == flavor


def test_ImageManifest_layer(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")

    # Act
    layer = Layer(blob)

    manifest = ImageManifest()
    manifest.append_layer(layer)

    # Assert

    assert len(manifest.layers_as_dict) == 1
    assert manifest.layers_as_dict.popitem()[0] == "blob.txt"

    # Assert
    with pytest.raises(RuntimeError):
        manifest.append_layer({"test": "invalid"})


def test_ImageManifest_version() -> None:
    # Arrange
    version = "today"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(
        annotations={ImageManifest.ANNOTATION_VERSION_KEY: version}
    )

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.version == version

    empty_manifest.version = version
    assert empty_manifest.version == version

    assert manifest.version == version
