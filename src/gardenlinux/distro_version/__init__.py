from typing import Self


class UnsupportedDistroVersion(Exception):
    pass


class NotAPatchRelease(Exception):
    pass


class BaseDistroVersion:
    major: int = 0
    minor: int = 0
    patch: int = 0

    def is_patch_release(self) -> int:
        return self.patch and self.patch > 0


class LegacyDistroVersion(BaseDistroVersion):
    def __init__(self: Self, major: int, patch: int) -> None:
        self.major = major
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.patch}"

    def previous_patch_release(self) -> "LegacyDistroVersion":
        if not self.is_patch_release():
            raise NotAPatchRelease(f"{self} is not a patch release")

        return LegacyDistroVersion(self.major, self.patch - 1)


class SemverDistroVersion(BaseDistroVersion):
    def __init__(self, major: int, minor: int, patch: int) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def previous_patch_release(self) -> "SemverDistroVersion":
        if not self.is_patch_release():
            raise NotAPatchRelease(f"{self} is not a patch release")

        return SemverDistroVersion(self.major, self.minor, self.patch - 1)


def DistroVersion(
    maybe_distro_version: str,
) -> LegacyDistroVersion | SemverDistroVersion:
    version_components = maybe_distro_version.split(".")
    if len(version_components) > 3 or len(version_components) < 2:
        raise UnsupportedDistroVersion(
            f"Unexpected version number format {maybe_distro_version}"
        )

    if not all(map(lambda x: x.isdigit(), version_components)):
        raise UnsupportedDistroVersion(
            f"Unexpected version number format {maybe_distro_version}"
        )

    if len(version_components) == 2:
        return LegacyDistroVersion(*(int(c) for c in version_components))
    elif len(version_components) == 3:
        return SemverDistroVersion(*(int(c) for c in version_components))
    else:
        raise UnsupportedDistroVersion(
            f"Unexpected number of version components: {maybe_distro_version}"
        )
