# -*- coding: utf-8 -*-

"""
APT repositories
"""

from typing import Optional

from apt_repo import APTRepository


class GardenLinuxRepo(APTRepository):
    """
    Class to reflect APT based GardenLinux repositories.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: apt
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        dist: str,
        url: Optional[str] = "http://packages.gardenlinux.io/gardenlinux",
        components: Optional[list[str]] = ["main"],
    ):
        """
        Constructor __init__(GardenLinuxRepo)

        :param dist:       Repository dist
        :param url:        Repository url
        :param components: Repository components provided

        :since: 0.7.0
        """

        self.components = components
        self.url = url
        self.dist = dist
        self.repo = APTRepository(self.url, self.dist, self.components)

    def get_package_version_by_name(self, name: str) -> list[tuple[str, str]]:
        """
        Returns the package version matching the given name.

        :param name: name of package to find

        :return: (list) Packages matching the input name
        :since: 0.7.0
        """

        return [
            (package.package, package.version)
            for package in self.repo.get_packages_by_name(name)
        ]

    def get_packages_versions(self) -> list[tuple[str, str]]:
        """
        Returns list of (package, version) tuples

        :return: (list) Packages versions
        :since: 0.7.0
        """

        return [(p.package, p.version) for p in self.repo.packages]


def compare_gardenlinux_repo_version(
    version_a: str, version_b: str
) -> list[tuple[str, str | None, str | None]]:
    """
    Compares differences between repository versions given.

    Example: print(compare_gardenlinux_repo_version("1443.2", "1443.1"))

    :param version_a: Version of first Garden Linux repo
    :param version_b: Version of first Garden Linux repo

    :return: (list) Differences between repo a and repo b
    :since:  0.7.0
    """

    return compare_repo(GardenLinuxRepo(version_a), GardenLinuxRepo(version_b))


def compare_repo(
    a: GardenLinuxRepo, b: GardenLinuxRepo, available_in_both: Optional[bool] = False
) -> list[tuple[str, str | None, str | None]]:
    """
    Compares differences between repositories given.

    Example:
    gl_repo = GardenLinuxRepo("today")
    gl_repo_1592 = GardenLinuxRepo("1592.0")
    deb_testing = GardenLinuxRepo("testing", "https://deb.debian.org/debian/")
    print(compare_repo(gl_repo, gl_repo_1592, available_in_both=True))
    print(compare_repo(gl_repo, deb_testing, available_in_both=False))

    :param a GardenLinuxRepo: First repo to compare
    :param b GardenLinuxRepo: Second repo to compare
    :param available_in_both: Compare packages available in both repos only

    :return: (list) Differences between repo a and repo b
    :since:  0.7.0
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
