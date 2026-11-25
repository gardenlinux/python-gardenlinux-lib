from pathlib import Path

import pytest

from gardenlinux.oci import ImageManifest, Layer

from ..constants import TEST_GARDENLINUX_COMMIT, TEST_GARDENLINUX_COMMIT_SHORT


def test_ImageManifest_artifact_base_name() -> None:
    # Arrange
    arch = "amd64"
    cname = "container"
    version = "today"
    commit = "local"
    artifact_base_name = f"{cname}-{arch}-{version}-{commit}"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(
        annotations={
            ImageManifest.ANNOTATION_CNAME_KEY: cname,
            ImageManifest.ANNOTATION_ARCH_KEY: arch,
            ImageManifest.ANNOTATION_VERSION_KEY: version,
            ImageManifest.ANNOTATION_COMMIT_KEY: commit,
        }
    )

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.artifact_base_name == artifact_base_name

    empty_manifest.artifact_base_name = artifact_base_name
    assert empty_manifest.artifact_base_name == artifact_base_name

    assert manifest.artifact_base_name == artifact_base_name


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


def test_ImageManifest_commit() -> None:
    # Arrange
    empty_manifest = ImageManifest()

    manifest = ImageManifest(
        annotations={ImageManifest.ANNOTATION_COMMIT_KEY: TEST_GARDENLINUX_COMMIT}
    )

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.commit == TEST_GARDENLINUX_COMMIT
        assert empty_manifest.commit_id == TEST_GARDENLINUX_COMMIT_SHORT

    empty_manifest.commit = TEST_GARDENLINUX_COMMIT
    assert empty_manifest.commit == TEST_GARDENLINUX_COMMIT
    assert empty_manifest.commit_id == TEST_GARDENLINUX_COMMIT_SHORT

    assert manifest.commit == TEST_GARDENLINUX_COMMIT
    assert manifest.commit_id == TEST_GARDENLINUX_COMMIT_SHORT


def test_ImageManifest_cname() -> None:
    # Arrange
    arch = "amd64"
    cname = "container"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(
        annotations={
            ImageManifest.ANNOTATION_CNAME_KEY: cname,
            ImageManifest.ANNOTATION_ARCH_KEY: arch,
        }
    )

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
    arch = "amd64"
    cname = "container"
    flavor = f"{cname}-{arch}"

    empty_manifest = ImageManifest()
    manifest = ImageManifest(
        annotations={
            ImageManifest.ANNOTATION_CNAME_KEY: cname,
            ImageManifest.ANNOTATION_ARCH_KEY: arch,
        }
    )

    # Assert
    with pytest.raises(RuntimeError):
        assert empty_manifest.cname == cname

    empty_manifest.flavor = flavor
    assert empty_manifest.cname == cname
    assert empty_manifest.arch == arch

    assert manifest.flavor == flavor


def test_ImageManifest_layer(tmp_path: Path) -> None:
    # Arrange
    blob = tmp_path / "blob.txt"
    blob.write_text("data")

    # Act
    layer = Layer(blob)

    manifest = ImageManifest()
    manifest.add_layer(layer)

    # Assert

    assert len(manifest.layers_as_dict) == 1
    assert manifest.layers_as_dict.popitem()[0] == "blob.txt"

    # Assert
    with pytest.raises(RuntimeError):
        manifest.add_layer({"test": "invalid"})


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
