import pytest

from gardenlinux.oci import ImageManifest, Layer


def test_ImageManifest_arch():
    # Arrange
    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={"architecture": "amd64"})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.arch == "amd64"

    empty_manifest.arch = "amd64"
    assert empty_manifest.arch == "amd64"

    assert manifest.arch == "amd64"


def test_ImageManifest_cname():
    # Arrange
    cname = "container-amd64-today-local"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={"cname": cname})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.cname == cname

    empty_manifest.cname = cname
    assert empty_manifest.cname == cname

    assert manifest.cname == cname


def test_ImageManifest_feature_set():
    # Arrange
    feature_set = "container"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={"feature_set": feature_set})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.feature_set == feature_set

    empty_manifest.feature_set = feature_set
    assert empty_manifest.feature_set == feature_set

    assert manifest.feature_set == feature_set


def test_ImageManifest_flavor():
    # Arrange
    flavor = "container"
    cname = f"{flavor}-amd64-today-local"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={"cname": cname})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.flavor == flavor

    empty_manifest.cname = cname
    assert empty_manifest.flavor == flavor

    assert manifest.flavor == flavor


def test_ImageManifest_layer(tmp_path):
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
        assert manifest.append_layer({"test": "invalid"})


def test_ImageManifest_version():
    # Arrange
    version = "today"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(annotations={"version": version})

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.version == version

    empty_manifest.version = version
    assert empty_manifest.version == version

    assert manifest.version == version
