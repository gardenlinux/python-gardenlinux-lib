from types import SimpleNamespace
from typing import List, Tuple

import pytest

import gardenlinux.apt.package_repo_info as repoinfo


class FakeAPTRepo:
    """
    Fake replacement for apt_repo.APTRepository.

    - stores the constructor args for assertions
    - exposes `.packages` and `get_packages_by_name(name)`
    """

    def __init__(self, url: str, dist: str, components: List[str]) -> None:
        self.url = url
        self.dist = dist
        self.components = components
        # list of objects with .package and .version attributes
        self.packages: List[SimpleNamespace] = []

    def get_packages_by_name(self, name: str) -> List[SimpleNamespace]:
        return [p for p in self.packages if p.package == name]


# Fake GardenLinuxRepo subclass to avoid incomplete type issues in compare tests
class FakeRepo(repoinfo.GardenLinuxRepo):
    def __init__(self, versions: List[Tuple[str, str]]) -> None:
        # Skip calling the real constructor
        self._versions = versions

    def get_packages_versions(self) -> List[Tuple[str, str]]:
        return self._versions


def test_gardenlinuxrepo_init(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test if GardenLinuxRepo creates an internal APTRepo
    """
    # Arrange
    monkeypatch.setattr(repoinfo, "APTRepository", FakeAPTRepo)

    # Act
    gr = repoinfo.GardenLinuxRepo("dist-123")

    # Assert
    assert gr.dist == "dist-123"
    assert gr.url == "http://packages.gardenlinux.io/gardenlinux"
    assert gr.components == ["main"]
    # Assert that patch works
    assert isinstance(gr.repo, FakeAPTRepo)
    # Assert that constructor actually built an internal repo instance
    assert gr.repo.url == gr.url
    assert gr.repo.dist == gr.dist
    assert gr.repo.components == gr.components


def test_get_package_version_by_name(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(repoinfo, "APTRepository", FakeAPTRepo)
    gr = repoinfo.GardenLinuxRepo("d")
    # Fake package objects
    gr.repo.packages = [
        SimpleNamespace(package="pkg-a", version="1.0"),
        SimpleNamespace(package="pkg-b", version="2.0"),
    ]

    # Act
    result = gr.get_package_version_by_name("pkg-a")

    # Assert
    assert result == [("pkg-a", "1.0")]


def test_get_packages_versions_returns_all_pairs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setattr(repoinfo, "APTRepository", FakeAPTRepo)
    gr = repoinfo.GardenLinuxRepo("d")
    gr.repo.packages = [
        SimpleNamespace(package="aa", version="0.1"),
        SimpleNamespace(package="bb", version="0.2"),
    ]

    # Act
    pv = gr.get_packages_versions()

    # Assert
    assert pv == [("aa", "0.1"), ("bb", "0.2")]


def test_compare_repo_union_returns_all() -> None:
    """
    When available_in_both=False, compare_repo returns entries for:
    - only names in A
    - only names in B
    - names in both but with different versions
    """
    # Arrange
    a = FakeRepo([("a", "1"), ("b", "2")])
    b = FakeRepo([("b", "3"), ("c", "4")])

    # Act
    result = repoinfo.compare_repo(a, b, available_in_both=False)

    # Assert
    expected = {
        ("a", "1", None),
        ("b", "2", "3"),
        ("c", None, "4"),
    }
    assert set(result) == expected


def test_compare_repo_intersection_only() -> None:
    """
    When available_in_both=True, only intersection names are considered;
    differences are only returned if versions differ.
    """
    # Arrange
    a = FakeRepo([("a", "1"), ("b", "2")])
    b = FakeRepo([("b", "3"), ("c", "4")])

    # Act
    result = repoinfo.compare_repo(a, b, available_in_both=True)

    # Assert
    assert set(result) == {("b", "2", "3")}


def test_compare_same_returns_empty() -> None:
    """
    When both sets are identical, compare_repo should return an empty set.
    """
    # Arrange
    a = FakeRepo([("a", "1"), ("b", "2")])
    b = FakeRepo([("a", "1"), ("b", "2")])

    # Act / Assert
    assert repoinfo.compare_repo(a, b, available_in_both=False) == []


def test_compare_empty_returns_empty() -> None:
    """
    If both sets are empty, compare_repo should return an empty set.
    """
    # Arrange
    a = FakeRepo([])
    b = FakeRepo([])

    # Act / Assert
    assert repoinfo.compare_repo(a, b, available_in_both=True) == []
