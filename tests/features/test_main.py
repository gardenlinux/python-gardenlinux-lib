import sys
import types
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, List, Tuple

import pytest

import gardenlinux.features.__main__ as fema
from gardenlinux.features import CName

from ..constants import GL_ROOT_DIR
from .constants import generate_container_amd64_release_metadata

# -------------------------------
# Helper function tests
# -------------------------------


def test_graph_mermaid() -> None:
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


def test_graph_mermaid_raises_no_flavor() -> None:
    # Arrange
    class MockGraph:
        edges = [("x", "y"), ("y", "z")]

    # Act / Assert
    with pytest.raises(
        RuntimeError, match="Error while generating graph: Flavor is None!"
    ):
        fema.graph_as_mermaid_markup(None, MockGraph())


def test_get_minimal_feature_set_filters() -> None:
    # Arrange
    class FakeGraph:
        def in_degree(self) -> List[Tuple[str, int]]:
            return [("a", 0), ("b", 1), ("c", 0)]

    graph = FakeGraph()

    # Act
    result = fema.get_minimal_feature_set(graph)

    # Assert
    assert result == {"a", "c"}


def test_get_version_and_commit_from_file(tmp_path: Path) -> None:
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


def test_get_version_missing_file_raises(tmp_path: Path) -> None:
    # Arrange (one file only)
    (tmp_path / "COMMIT").write_text("abcdef1234\n")

    # Act / Assert
    with pytest.raises(RuntimeError):
        fema.get_version_and_commit_id_from_files(str(tmp_path))


# -------------------------------
# Tests for main()
# -------------------------------
def test_main_prints_arch(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    argv = ["prog", "--arch", "amd64", "--cname", "flav", "--version", "1.0", "arch"]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "amd64" in out


def test_main_prints_container_name(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    argv = [
        "prog",
        "--arch",
        "amd64",
        "--cname",
        "container-pythonDev",
        "--version",
        "1.0",
        "container_name",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "container-python-dev" in out


def test_main_prints_container_tag(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    argv = [
        "prog",
        "--arch",
        "amd64",
        "--cname",
        "flav",
        "--version",
        "1.0",
        "--commit",
        "~post1",
        "container_tag",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out.strip()
    assert "1-0-post1" == out


def test_main_prints_commit_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
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


def test_main_prints_flags_elements_platforms(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
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
        def __init__(self, *a: Any, **k: Any):
            CName.__init__(self, *a, **k)
            self._feature_flags_cached = ["flag1"]

    monkeypatch.setattr(fema, "CName", FakeCName)

    # Act
    fema.main()

    # Assert
    out = capsys.readouterr().out
    assert "flag1" in out


def test_main_prints_version(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
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


def test_main_prints_version_and_commit_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
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


def test_main_requires_cname(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(sys, "argv", ["prog", "arch"])
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(SystemExit):
        fema.main()


def test_main_cname_raises_missing_commit_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    # args.type == 'cname, arch is None and no default_arch set
    argv = [
        "prog",
        "--cname",
        "flav",
        "--default-arch",
        "amd64",
        "--version",
        "1.0",
        "cname",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(RuntimeError, match="Version and commit ID"):
        fema.main()


def test_main_raises_no_arch_no_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    # args.type == 'cname, arch is None and no default_arch set
    argv = ["prog", "--cname", "flav", "cname"]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(RuntimeError, match="Architecture could not be determined"):
        fema.main()


def test_main_raises_missing_commit_id(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    argv = [
        "prog",
        "--arch",
        "amd64",
        "--cname",
        "flav",
        "--version",
        "1.0",
        "version_and_commit_id",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(RuntimeError, match="Commit ID not specified"):
        fema.main()


def test_main_with_exclude_cname_print_elements(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--feature-dir",
            f"{GL_ROOT_DIR}/features",
            "--cname",
            "kvm-gardener_prod",
            "--ignore",
            "cloud",
            "--arch",
            "amd64",
            "--version",
            "local",
            "--commit",
            "today",
            "elements",
        ],
    )

    # Act
    fema.main()

    # Assert
    captured = capsys.readouterr().out.strip()

    assert "log,sap,ssh,base,server,multipath,iscsi,nvme,gardener" == captured


def test_main_with_exclude_cname_print_features(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "prog",
            "--feature-dir",
            f"{GL_ROOT_DIR}/features",
            "--cname",
            "kvm-gardener_prod",
            "--ignore",
            "log",
            "--arch",
            "amd64",
            "--version",
            "local",
            "--commit",
            "today",
            "features",
        ],
    )

    # Act
    fema.main()

    # Assert
    captured = capsys.readouterr().out.strip()

    assert (
        "sap,ssh,_fwcfg,_ignite,_legacy,_nopkg,_prod,_slim,base,server,cloud,kvm,multipath,iscsi,nvme,gardener"
        == captured
    )


def test_cname_release_file(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """
    Test validation between release metadata and arguments given
    """
    # Arrange
    with TemporaryDirectory() as tmpdir:
        os_release_file = Path(tmpdir, "os_release")

        with os_release_file.open("w") as fp:
            fp.write(generate_container_amd64_release_metadata("today", "local"))

        argv = [
            "prog",
            "--cname",
            "container-amd64-today-local",
            "--release-file",
            str(os_release_file),
            "cname",
        ]
        monkeypatch.setattr(sys, "argv", argv)

        # Act / Assert
        fema.main()

        # Assert
        out = capsys.readouterr().out
        assert "container-amd64-today-local" in out
