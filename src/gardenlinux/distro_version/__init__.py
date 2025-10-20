from typing import Optional


class UnsupportedDistroVersion(Exception):
    pass


class NotAPatchRelease(Exception):
    pass


class DistroVersion:
    major: Optional[int] = None
    minor: Optional[int] = None
    patch: Optional[int] = None

    def __init__(self, maybe_version_str):
        version_components = maybe_version_str.split(".")
        if len(version_components) > 3 or len(version_components) < 2:
            raise UnsupportedDistroVersion(
                f"Unexpected version number format {maybe_version_str}"
            )

        if not all(map(lambda x: x.isdigit(), version_components)):
            raise UnsupportedDistroVersion(
                f"Unexpected version number format {maybe_version_str}"
            )

        self.major = int(version_components[0])

        if len(version_components) == 2:
            self.patch = int(version_components[1])

        if len(version_components) == 3:
            self.minor = int(version_components[1])
            self.patch = int(version_components[2])

    def __str__(self):
        return (
            f"{self.major}.{self.minor}.{self.patch - 1}"
            if self.minor
            else f"{self.major}.{self.patch - 1}"
        )

    def is_patch_release(self):
        return self.patch > 0

    def previous_patch_release(self):
        if not self.is_patch_release():
            raise NotAPatchRelease(f"{self} is not a patch release")
        return self.__str__()
