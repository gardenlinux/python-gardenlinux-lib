from semver import Version


class UnsupportedDistroVersion(Exception):
    pass


class NotAPatchRelease(Exception):
    pass


class DistroVersion(Version):  # type: ignore[misc]
    def __init__(self, version: str | Version):
        self._version_format_without_patch_number = False

        try:
            if isinstance(version, Version):
                version_parsed = version
            elif len(version.split(".")) == 2:
                # Support version strings without patch numbers
                version_parsed = Version.parse(f"{version}.0")
                self._version_format_without_patch_number = True
            else:
                version_parsed = Version.parse(version)
        except Exception as exc:
            raise UnsupportedDistroVersion(exc)

        Version.__init__(
            self,
            version_parsed.major,
            version_parsed.minor,
            version_parsed.patch,
            version_parsed.prerelease,
            version_parsed.build,
        )

    @property
    def is_patch_release(self) -> bool:
        if self._version_format_without_patch_number:
            return self.minor > 0  # type: ignore[no-any-return]

        return self.patch > 0  # type: ignore[no-any-return]

    @property
    def previous_patch_release(self) -> str:
        if not self.is_patch_release:
            raise NotAPatchRelease(f"{self} is not a patch release")

        if self._version_format_without_patch_number:
            previous_version = DistroVersion(
                Version(self.major, self.minor - 1, self.patch)
            )
            return f"{previous_version.major}.{previous_version.minor}"

        return str(
            Version(
                self.major,
                self.minor,
                self.patch - 1,
                prerelease=self.prerelease,
                build=self.build,
            )
        )
