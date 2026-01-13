import logging
import sys
import types
from typing import Any, List, Tuple

import networkx
import pytest

import gardenlinux.features.cname_main as cname_main
from gardenlinux.features import Parser


def test_main_happy(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test the "Happy Path" of the main() function.
    """
    # Arrange
    argv = ["prog", "--arch", "amd64", "--version", "1.0-abc123", "flav-amd64"]
    monkeypatch.setattr(sys, "argv", argv)

    class FakeGraph:
        def in_degree(self) -> List[Tuple[str, int]]:
            return [("f1", 0)]

        edges = [("f1", "f2")]

    class FakeParser(Parser):
        def __init__(self, *a: Any, **k: Any):
            pass

        def filter(self, *a: Any, **k: Any) -> networkx.Graph:
            return FakeGraph()

        @staticmethod
        def sort_graph_nodes(graph: networkx.Graph) -> List[str]:
            return ["f1", "f2"]

    monkeypatch.setattr(cname_main, "Parser", FakeParser)

    # Act
    cname_main.main()

    # Assert
    out = capsys.readouterr().out
    assert "f1" in out
    assert "amd64" in out


def test_main_version_from_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    "Happy Path" test for grabbing the version and commit id from file in main().
    """
    # Arrange
    argv = ["prog", "--arch", "amd64", "flav-amd64"]
    monkeypatch.setattr(sys, "argv", argv)

    monkeypatch.setattr(
        cname_main,
        "get_version_and_commit_id_from_files",
        lambda root: ("2.0", "abcdef12"),
    )

    class FakeParser(Parser):
        def __init__(self, *a: Any, **k: Any):
            pass

        def filter(self, *a: Any, **k: Any) -> networkx.Graph:
            return types.SimpleNamespace(in_degree=lambda: [("f1", 0)], edges=[])

        @staticmethod
        def sort_graph_nodes(graph: networkx.Graph) -> List[str]:
            return ["f1"]

    monkeypatch.setattr(cname_main, "Parser", FakeParser)

    # Act
    cname_main.main()

    # Assert
    assert "2.0-abcdef12" in capsys.readouterr().out


def test_cname_main_version_file_missing_warns(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """
    Check if a warning is logged when it fails to read version and commit id files.

    Specifically, this test simulates a scenario where the helper function
    `get_version_and_commit_id_from_files` raises a RuntimeError, which would occur
    if the expected version or commit files are missing or unreadable.
    """
    # Arrange
    argv = ["prog", "--arch", "amd64", "flav-amd64"]
    monkeypatch.setattr(sys, "argv", argv)

    # Patch version fatch function to raise RuntimeError (Simulates missing files)
    def raise_runtime(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("missing")

    monkeypatch.setattr(
        cname_main, "get_version_and_commit_id_from_files", raise_runtime
    )

    # Patch Parser for minimal valid graph
    class FakeParser(Parser):
        def __init__(self, *a: Any, **k: Any):
            pass

        # Return object with in_degree method returning a node with zero dependencies
        def filter(self, *a: Any, **k: Any) -> networkx.Graph:
            return types.SimpleNamespace(in_degree=lambda: [("f1", 0)], edges=[])

        @staticmethod
        def sort_graph_nodes(graph: networkx.Graph) -> List[str]:
            return ["f1"]

    monkeypatch.setattr(cname_main, "Parser", FakeParser)

    # Capture any logs with WARNING level
    caplog.set_level(logging.WARNING)

    # Act
    cname_main.main()

    # Assert
    assert "Failed to parse version information" in caplog.text


def test_cname_main_invalid_cname_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test if AssertionError is raised with an invalid or malformed cname.
    """
    # Arrange
    argv = ["prog", "--arch", "amd64", "--version", "1.0", "INVALID@NAME"]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(AssertionError):
        cname_main.main()


def test_cname_main_missing_arch_in_cname_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Test if an assertion error is raised when the arch argument is missing.
    """
    # Arrange
    argv = ["prog", "--version", "1.0", "flav"]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(AssertionError):
        cname_main.main()
