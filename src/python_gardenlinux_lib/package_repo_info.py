from apt_repo import APTRepository
from typing import Optional


class GardenLinuxRepo(APTRepository):
    def __init__(
        self,
        dist: str,
        url: Optional[str] = "http://packages.gardenlinux.io/gardenlinux",
        components: Optional[list[str]] = ["main"],
    ) -> None:
        self.components = components
        self.url = url
        self.dist = dist
        self.repo = APTRepository(self.url, self.dist, self.components)

    def get_package_version_by_name(self, name: str) -> list[tuple[str, str]]:
        """
        :param str name: name of package to find
        :returns: packages matching the input name
        """
        return [
            (package.package, package.version)
            for package in self.repo.get_packages_by_name(name)
        ]

    def get_packages_versions(self):
        """
        Returns list of (package, version) tuples
        """
        return [(p.package, p.version) for p in self.repo.packages]


def compare_gardenlinux_repo_version(version_a: str, version_b: str):
    """
    :param str version_a: Version of first Garden Linux repo
    :param str version_b: Version of first Garden Linux repo

    Example: print(compare_gardenlinux_repo_version("1443.2", "1443.1"))
    """
    return compare_repo(GardenLinuxRepo(version_a), GardenLinuxRepo(version_b))


def compare_repo(
    a: GardenLinuxRepo, b: GardenLinuxRepo, available_in_both: Optional[bool] = False
):
    """
    :param a GardenLinuxRepo: first repo to compare
    :param b GardenLinuxRepo: second repo to compare
    :returns: differences between repo a and repo b
    """

    packages_a = dict(a.get_packages_versions())
    packages_b = dict(b.get_packages_versions())
    if available_in_both:
        all_names = set(packages_a.keys()).intersection(set(packages_b.keys()))
    else:
        all_names = set(packages_a.keys()).union(set(packages_b.keys()))

    return [
        (name, packages_a.get(name), packages_b.get(name))
        for name in all_names
        if (
            name in packages_a
            and name in packages_b
            and packages_a[name] != packages_b[name]
        )
        or (name not in packages_b or name not in packages_a)
    ]


# EXAMPLE USAGE.
# print(compare_gardenlinux_repo_version("1443.2", "1443.1"))

# gl_repo = GardenLinuxRepo("today")
# gl_repo_1592 = GardenLinuxRepo("1592.0")
# deb_testing = GardenLinuxRepo("testing", "https://deb.debian.org/debian/")
# print(compare_repo(gl_repo, gl_repo_1592, available_in_both=True))
# print(compare_repo(gl_repo, deb_testing, available_in_both=True))
# # print(gl_repo.get_packages_versions())
# print(gl_repo.get_package_version_by_name("wget"))
