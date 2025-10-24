import json
import sys

from gardenlinux.flavors import __main__ as fm


def test_generate_markdown_table():
    # Arrange
    combos = [("amd64", "linux-amd64")]

    # Act
    table = fm.generate_markdown_table(combos, no_arch=False)

    # Assert
    assert table.startswith("| Platform   | Architecture       | Flavor")
    assert "`linux-amd64`" in table
    assert "| linux"


def test_parse_args(monkeypatch):
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


def _make_parser_class(filter_result, group_result=None, remove_result=None):
    """
    Factory to create a fake Parser class
    Instances ignore the favors_data passed to __init__.
    """

    class DummyParser:
        def __init__(self, flavors_data):
            self._data = flavors_data

        def filter(self, **kwargs):
            # return the prepared combinations list
            return filter_result

        @staticmethod
        def group_by_arch(combinations):
            # Return a prepared mapping or derive a simple mapping if None
            if group_result is not None:
                return group_result
            # naive default behaviour: group combinations by arch
            d = {}
            for arch, comb in combinations:
                d.setdefault(arch, []).append(comb)
            return d

        @staticmethod
        def remove_arch(combinations):
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


def _make_git_repository_class(tmp_path):
    """
    Factory to create a fake Parser class
    Instances ignore the favors_data passed to __init__.
    """

    class DummyRepository:
        def __init__(self):
            self.root = tmp_path

    return DummyRepository


def test_main_json_by_arch_prints_json(tmp_path, monkeypatch, capsys):
    # Arrange
    # prepare flavors.yaml at tmp path
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    # define combinations and expected grouped mapping
    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]
    grouped = {"x86": ["linux-x86"], "arm": ["android-arm"]}

    DummyParser = _make_parser_class(filter_result=combinations, group_result=grouped)
    DummyRepository = _make_git_repository_class(str(tmp_path))

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
    tmp_path, monkeypatch, capsys
):
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]
    # group_by_arch returns items that include architecture suffixes
    grouped = {"x86": ["linux-x86"], "arm": ["android-arm"]}

    DummyParser = _make_parser_class(filter_result=combinations, group_result=grouped)
    DummyRepository = _make_git_repository_class(str(tmp_path))

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


def test_main_markdown_table_branch(tmp_path, monkeypatch, capsys):
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    combinations = [("x86_64", "linux-x86_64"), ("armv7", "android-armv7")]

    DummyParser = _make_parser_class(filter_result=combinations)
    DummyRepository = _make_git_repository_class(str(tmp_path))

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


def test_main_default_prints_flavors_list(tmp_path, monkeypatch, capsys):
    # Arrange
    flavors_file = tmp_path / "flavors.yaml"
    flavors_file.write_text("dummy: content")

    # filter returns tuples; main's default branch prints comb[1] values, sorted unique
    combinations = [("x86", "linux-x86"), ("arm", "android-arm")]

    DummyParser = _make_parser_class(filter_result=combinations)
    DummyRepository = _make_git_repository_class(str(tmp_path))

    monkeypatch.setattr(fm, "Parser", DummyParser)
    monkeypatch.setattr(fm, "Repository", DummyRepository)
    monkeypatch.setattr(sys, "argv", ["prog"])

    # Act
    fm.main()
    out = capsys.readouterr().out
    lines = out.strip().splitlines()

    # Assert
    assert sorted(lines) == sorted(["linux-x86", "android-arm"])


def test_main_default_prints_git_flavors_list(tmp_path, monkeypatch, capsys):
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
