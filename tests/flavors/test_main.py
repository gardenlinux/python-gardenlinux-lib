import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest

from gardenlinux.flavors import __main__ as fm


def test_generate_markdown_table() -> None:
    # Arrange
    combos = [("amd64", "linux-amd64")]

    # Act
    table = fm.generate_markdown_table(combos)

    # Assert
    assert table.startswith("| Platform   | Architecture       | Flavor")
    assert "`linux-amd64`" in table
    assert "| linux"


def test_parse_args(monkeypatch: pytest.MonkeyPatch) -> None:
    """simulate CLI invocation and make sure parse_args reads them correctly"""
    # Arrange
    argv = [
        "prog",
        "--no-arch",
        "--include-only",
        "a*",
        "--exclude",
        "b*",
        "--build",
        "--publish",
        "--test",
        "--test-platform",
        "--category",
        "cat1",
        "--exclude-category",
        "cat2",
        "--json-by-arch",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Act
    args = fm.parse_args()

    # Assert
    assert args.no_arch is True
    assert args.include_only == ["a*"]
    assert args.exclude == ["b*"]
    assert args.build is True
    assert args.publish is True
    assert args.test is True
    assert args.test_platform is True
    assert args.category == ["cat1"]
    assert args.exclude_category == ["cat2"]
    assert args.json_by_arch is True


def _make_parser_class(
    filter_result: List[Tuple[Any, str]],
    group_result: Optional[Dict[str, List[str]]] = None,
    remove_result: Optional[List[str]] = None,
) -> Any:
    """
    Factory to create a fake Parser class
    Instances ignore the favors_data passed to __init__.
    """

    class DummyParser:
        def __init__(self, flavors_data: str):
            self._data = flavors_data

        def filter(self, **kwargs: Any) -> List[Tuple[Any, str]]:
            # return the prepared combinations list
            return filter_result

        @staticmethod
        def group_by_arch(combinations: List[Tuple[Any, str]]) -> Dict[str, List[str]]:
            # Return a prepared mapping or derive a simple mapping if None
            if group_result is not None:
                return group_result
            # naive default behaviour: group combinations by arch
            d: Dict[str, List[str]] = {}
            for arch, comb in combinations:
                d.setdefault(arch, []).append(comb)
            return d

        @staticmethod
        def remove_arch(combinations: List[Tuple[Any, str]]) -> List[str]:
            if remove_result is not None:
                return remove_result
            # naive default: remote '-{arch}' suffix if present
            out = []
            for arch, comb in combinations:
                suffix = f"-{arch}"
                if comb.endswith(suffix):
                    out.append(comb[: -len(suffix)])
                else:
                    out.append(comb)
            return out

    return DummyParser


def _make_git_repository_class(tmp_path: Path) -> Any:
    """
    Factory to create a fake Parser class
    Instances ignore the favors_data passed to __init__.
    """

    class DummyRepository:
        def __init__(self):  # type: ignore[no-untyped-def]
            self.root = tmp_path

    return DummyRepository


def test_main_json_by_arch_prints_json(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    # prepare flavors.yaml at tmp path
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    # define combinations and expected grouped mapping
    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]
    grouped = {"x86": ["linux-x86"], "arm": ["android-arm"]}

    DummyParser = _make_parser_class(filter_result=combinations, group_result=grouped)
    DummyRepository = _make_git_repository_class(Path(tmp_path))

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(fm, "Repository", DummyRepository)
    monkeypatch.setattr(sys, "argv", ["prog", "--json-by-arch"])

    # Act
    fm.main()
    out = capsys.readouterr().out

    # Assert
    parsed = json.loads(out)
    assert parsed == grouped


def test_main_json_by_arch_with_no_arch_strips_arch_suffix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]
    # group_by_arch returns items that include architecture suffixes
    grouped = {"x86": ["linux-x86"], "arm": ["android-arm"]}

    DummyParser = _make_parser_class(filter_result=combinations, group_result=grouped)
    DummyRepository = _make_git_repository_class(Path(tmp_path))

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(fm, "Repository", DummyRepository)
    monkeypatch.setattr(sys, "argv", ["prog", "--json-by-arch", "--no-arch"])

    # Act
    fm.main()
    out = capsys.readouterr().out

    # Assert
    parsed = json.loads(out)
    # with --no-arch, main removes '-<arch>' from each flavor string
    assert parsed == {"x86": ["linux"], "arm": ["android"]}


def test_main_markdown_table_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    combinations = [("x86_64", "linux-x86_64"), ("armv7", "android-armv7")]

    DummyParser = _make_parser_class(filter_result=combinations)
    DummyRepository = _make_git_repository_class(Path(tmp_path))

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(fm, "Repository", DummyRepository)
    monkeypatch.setattr(sys, "argv", ["prog", "--markdown-table-by-platform"])

    # Act
    fm.main()
    out = capsys.readouterr().out

    # Assert
    assert "`linux-x86_64`" in out
    assert "`android-armv7`" in out
    assert "| Platform" in out


def test_main_default_prints_flavors_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    # filter returns tuples; main's default branch prints comb[1] values, sorted unique
    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]

    DummyParser = _make_parser_class(filter_result=combinations)
    DummyRepository = _make_git_repository_class(Path(tmp_path))

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(fm, "Repository", DummyRepository)
    monkeypatch.setattr(sys, "argv", ["prog"])

    # Act
    fm.main()
    out = capsys.readouterr().out
    lines = out.strip().splitlines()

    # Assert
    assert sorted(lines) == sorted(["linux-x86", "android-arm"])


def test_main_default_prints_git_flavors_list(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # filter returns tuples; main's default branch prints comb[1] values, sorted unique
    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]

    DummyParser = _make_parser_class(filter_result=combinations)

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(sys, "argv", ["prog"])

    # Act
    fm.main()
    out = capsys.readouterr().out
    lines = out.strip().splitlines()

    # Assert
    assert sorted(lines) == sorted(["linux-x86", "android-arm"])
