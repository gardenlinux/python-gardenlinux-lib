import pytest

from gardenlinux.distro_version import (
    DistroVersion,
    NotAPatchRelease,
    UnsupportedDistroVersion,
)


def test_distro_version_unrecognizable_non_numeric_version():
    with pytest.raises(UnsupportedDistroVersion):
        DistroVersion("garden.linux")


def test_distro_version_unrecognizable_numeric_version():
    with pytest.raises(UnsupportedDistroVersion):
        DistroVersion("1.2.3.4")
    with pytest.raises(UnsupportedDistroVersion):
        DistroVersion("1.100.-10")


def test_distro_version_unrecognizable_too_short_version():
    with pytest.raises(UnsupportedDistroVersion):
        DistroVersion("1")


def test_distro_version_legacy_version_is_parsable():
    assert isinstance(DistroVersion("1.2"), DistroVersion)


def test_distro_version_semver_version_is_parsable():
    assert isinstance(DistroVersion("1.2.3"), DistroVersion)


def test_distro_version_patch_release_is_recognized():
    assert DistroVersion("1.1").is_patch_release()
    assert DistroVersion("1.1.100").is_patch_release()
    assert not DistroVersion("1.0").is_patch_release()
    assert not DistroVersion("1.0.0").is_patch_release()


def test_distro_version_previous_patch_release_is_recognized():
    assert DistroVersion("1.1").previous_patch_release() == "1.0"
    assert DistroVersion("1.1.100").previous_patch_release() == "1.1.99"
    with pytest.raises(NotAPatchRelease):
        DistroVersion("1.0").previous_patch_release()
    with pytest.raises(NotAPatchRelease):
        DistroVersion("1.100.0").previous_patch_release()
