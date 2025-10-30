import sys
import types

import pytest

import gardenlinux.features.__main__ as fema
from gardenlinux.features import CName

# -------------------------------
# Helper function tests
# -------------------------------


def test_get_flavor():
    # Arrange
    sorted_features = ["base", "_hidden", "extra"]

    # Act
    result = fema.get_flavor(sorted_features)

    # Assert
    assert result == "base_hidden-extra"


def test_get_flavor_empty_raises():
    # get_flavor with empty iterable raises TypeError
    with pytest.raises(TypeError):
        fema.get_flavor([])


def test_sort_return_intersection_subset():
    # Arrange
    input_set = {"a", "c"}
    order_list = ["a", "b", "c", "d"]

    # Act
    result = fema.sort_subset(input_set, order_list)

    # Assert
    assert result == ["a", "c"]


def test_sort_subset_nomatch():
    # Arrange
    input_set = {"x", "y"}
    order_list = ["a", "b", "c"]

    # Act
    result = fema.sort_subset(input_set, order_list)

    # Assert
    assert result == []


def test_sort_subset_with_empty_order_list():
    # Arrange
    input_set = {"a", "b"}
    order_list = []

    result = fema.sort_subset(input_set, order_list)

    assert result == []


def test_graph_mermaid():
    # Arrange
    class FakeGraph:
        edges = [("a", "b"), ("b", "c")]

    flavor = "test"

    # Act
    markup = fema.graph_as_mermaid_markup(flavor, FakeGraph())

    # Assert
    assert "graph TD" in markup
    assert "a-->b" in markup
    assert "b-->c" in markup


def test_graph_mermaid_raises_no_flavor():
    # Arrange
    class MockGraph:
        edges = [("x", "y"), ("y", "z")]

    # Act / Assert
    with pytest.raises(
        RuntimeError, match="Error while generating graph: Flavor is None!"
    ):
        fema.graph_as_mermaid_markup(None, MockGraph())


def test_get_minimal_feature_set_filters():
    # Arrange
    class FakeGraph:
        def in_degree(self):
            return [("a", 0), ("b", 1), ("c", 0)]

    graph = FakeGraph()

    # Act
    result = fema.get_minimal_feature_set(graph)

    # Assert
    assert result == {"a", "c"}


def test_get_version_and_commit_from_file(tmp_path):
    # Arrange
    commit_file = tmp_path / "COMMIT"
    commit_file.write_text("abcdef12\n")
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n")

    # Act
    version, commit = fema.get_version_and_commit_id_from_files(str(tmp_path))

    # Arrange
    assert version == "1.2.3"
    assert commit == "abcdef12"


def test_get_version_missing_file_raises(tmp_path):
    # Arrange (one file only)
    (tmp_path / "COMMIT").write_text("abcdef1234\n")

    # Act / Assert
    with pytest.raises(RuntimeError):
        fema.get_version_and_commit_id_from_files(str(tmp_path))


# -------------------------------
# Tests for main()
# -------------------------------
def test_main_prints_arch(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "--version", "1.0", "arch"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "amd64" in out


def test_main_prints_container_name(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "container-pythonDev", "--version", "1.0", "container_name"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "container-python-dev" in out


def test_main_prints_container_tag(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "--version", "1.0", "--commit", "~post1", "container_tag"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out.strip()
    assert "1-0-post1" == out


def test_main_prints_commit_id(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "commit_id"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(
        fema,
        "Parser",
        lambda *a, **kw: types.SimpleNamespace(filter=lambda *a, **k: None),
    )
    # Patch get_version_and_commit_id_from_files
    monkeypatch.setattr(
        fema, "get_version_and_commit_id_from_files", lambda root: ("1.2.3", "abcdef12")
    )

    # Act
    fema.main()

    captured = capsys.readouterr()
    assert "abcdef12" == captured.out.strip()


def test_main_prints_flags_elements_platforms(monkeypatch, capsys):
    # Arrange
    argv = [
        "prog",
        "--arch",
        "amd64",
        "--cname",
        "flav",
        "--version",
        "1.0",
        "flags",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    class FakeCName(CName):
        def __init__(self, *a, **k):
            CName.__init__(self, *a, **k)
            self._feature_flags_cached = ["flag1"]

    monkeypatch.setattr(fema, "CName", FakeCName)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "flag1" in out


def test_main_prints_version(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "version"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(
        fema,
        "Parser",
        lambda *a, **kw: types.SimpleNamespace(filter=lambda *a, **k: None),
    )
    # Patch get_version_and_commit_id_from_files
    monkeypatch.setattr(
        fema, "get_version_and_commit_id_from_files", lambda root: ("1.2.3", "abcdef12")
    )

    # Act
    fema.main()

    captured = capsys.readouterr()
    assert "1.2.3" == captured.out.strip()


def test_main_prints_version_and_commit_id(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "version_and_commit_id"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(
        fema,
        "Parser",
        lambda *a, **kw: types.SimpleNamespace(filter=lambda *a, **k: None),
    )
    # Patch get_version_and_commit_id_from_files
    monkeypatch.setattr(
        fema, "get_version_and_commit_id_from_files", lambda root: ("1.2.3", "abcdef12")
    )

    # Act
    fema.main()

    captured = capsys.readouterr()
    assert "1.2.3-abcdef12" == captured.out.strip()


def test_main_arch_raises_missing_verison(monkeypatch, capsys):
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "arch"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(RuntimeError):
        fema.main()


def test_main_with_cname_print_cname(monkeypatch, capsys):
    # Arrange
    class FakeGraph:
        def in_degree(self):
            # Simulate a graph where one feature has no dependencies
            return [("f1", 0)]

    class FakeParser:
        def __call__(self, *a, **k):
            return types.SimpleNamespace(filter=lambda *a, **k: FakeGraph())

        @staticmethod
        def get_cname_as_feature_set(f):
            return {"f1"}

        @staticmethod
        def sort_graph_nodes(graph):
            return ["f1"]

        @staticmethod
        def sort_subset(subset, length):
            return []

    monkeypatch.setattr(fema, "Parser", FakeParser())

    monkeypatch.setattr(
        sys,
        "argv",
        ["prog", "--cname", "flav", "--arch", "amd64", "--version", "1.0", "cname"],
    )

    # Act
    fema.main()

    # Assert
    captured = capsys.readouterr()
    assert "flav" in captured.out


def test_main_requires_cname(monkeypatch):
    # Arrange
    monkeypatch.setattr(sys, "argv", ["prog", "arch"])
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(SystemExit):
        fema.main()


def test_main_raises_no_arch_no_default(monkeypatch):
    # Arrange
    # args.type == 'cname, arch is None and no default_arch set
    argv = ["prog", "--cname", "flav", "cname"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(
        fema,
        "Parser",
        lambda *a, **kw: types.SimpleNamespace(filter=lambda *a, **k: None),
    )

    # Act / Assert
    with pytest.raises(RuntimeError, match="Architecture could not be determined"):
        fema.main()
