import sys
from pathlib import Path
from typing import List, Optional

import pytest

import gardenlinux.features.__main__ as fema
from gardenlinux.features import ArtifactBaseName

from ..constants import GL_ROOT_DIR
from .constants import generate_container_release_metadata

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
        RuntimeError, match="Error while generating graph: CName is None!"
    ):
        fema.graph_as_mermaid_markup(None, MockGraph())


def test_get_version_and_commit_from_file(tmp_path: Path) -> None:
    # Arrange
    commit_file = tmp_path / "COMMIT"
    commit_file.write_text("abcdef12\n")
    version_file = tmp_path / "VERSION"
    version_file.write_text("1.2.3\n")

    # Act
    version, commit = ArtifactBaseName.get_version_and_commit_id_from_files(
        str(tmp_path)
    )

    # Arrange
    assert version == "1.2.3"
    assert commit == "abcdef12"


# -------------------------------
# Tests for main()
# -------------------------------


@pytest.mark.parametrize(
    "input_argv, monkeypatch_version, release_metadata, ignored_features, expected_output",
    [
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "flav",
                "--version",
                "1.0",
                "--commit",
                "local",
                "arch",
            ],
            False,
            None,
            "",
            "amd64",
        ),
        (
            [
                "--arch",
                "arm64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "arch",
            ],
            False,
            generate_container_release_metadata("today", "local", "arm64"),
            "",
            "arm64",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container-pythonDev",
                "artifact-base-name",
            ],
            True,
            None,
            "",
            "container-pythonDev-amd64-1.2.3-abcdef12",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "artifact-base-name",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "container-amd64-today-local",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container-pythonDev",
                "artifact-base-name",
            ],
            True,
            None,
            "_archgrouped",
            "container-pythonDev-amd64-1.2.3-abcdef12",
        ),
        (
            ["--arch", "amd64", "--cname", "flav", "cname"],
            True,
            None,
            "",
            "flav",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "cname",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "container",
        ),
        (
            ["--arch", "amd64", "--cname", "flav", "commit-id"],
            True,
            None,
            "",
            "abcdef12",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "commit-id",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "local",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container-pythonDev",
                "--version",
                "1.0",
                "--commit",
                "local",
                "container-name",
            ],
            True,
            None,
            "",
            "container-python-dev",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "flav",
                "--version",
                "1.0",
                "--commit",
                "post1",
                "container-tag",
            ],
            False,
            None,
            "",
            "1-0-post1",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "elements"],
            True,
            None,
            "",
            "python,pythonDev,base",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "elements",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "base",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "features"],
            True,
            None,
            "",
            "python,pythonDev,_archgrouped,_slim,base,container",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "features"],
            True,
            None,
            "_archgrouped",
            "python,pythonDev,_slim,base,container",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "features",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "_archgrouped,_slim,base,container",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "features",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "_archgrouped",
            "_slim,base,container",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "flags"],
            True,
            None,
            "",
            "_archgrouped,_slim",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "flags"],
            True,
            None,
            "_archgrouped",
            "_slim",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "flags",
            ],
            False,
            generate_container_release_metadata("today", "local"),
            "",
            "_archgrouped,_slim",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "flavor"],
            True,
            None,
            "",
            "container-pythonDev-amd64",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "platform"],
            True,
            None,
            "",
            "container",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "platform",
            ],
            False,
            generate_container_release_metadata(
                "today", "local", variant="magicMachine"
            ),
            "",
            "container",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "platforms"],
            True,
            None,
            "",
            "container",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "--version",
                "today",
                "--commit",
                "local",
                "platform-variant",
            ],
            False,
            generate_container_release_metadata(
                "today", "local", variant="magicMachine"
            ),
            "",
            "magicMachine",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "version"],
            True,
            None,
            "",
            "1.2.3",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container-pythonDev",
                "version_and_commit-id",
            ],
            True,
            None,
            "",
            "1.2.3-abcdef12",
        ),
        (
            [
                "--arch",
                "amd64",
                "--cname",
                "container",
                "version_and_commit-id",
            ],
            True,
            generate_container_release_metadata("1.2.3", "abcdef12"),
            "",
            "1.2.3-abcdef12",
        ),
        (
            ["--arch", "amd64", "--cname", "container-pythonDev", "versioned-flavor"],
            True,
            None,
            "",
            "container-pythonDev-amd64-1.2.3",
        ),
    ],
)
def test_main_prints_result(
    input_argv: List[str],
    monkeypatch_version: bool,
    release_metadata: Optional[str],
    ignored_features: Optional[str],
    expected_output: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    # Arrange
    argv = [
        "gl-feature-parse",
        "--feature-dir",
        f"{GL_ROOT_DIR}/features",
    ] + input_argv

    if release_metadata:
        os_release_file = Path(tmp_path, "os_release")

        with os_release_file.open("w") as fp:
            fp.write(release_metadata)

        argv += [
            "--release-file",
            str(os_release_file),
        ]

    if ignored_features:
        argv += [
            "--ignore",
            str(ignored_features),
        ]

    monkeypatch.setattr(sys, "argv", argv)
    # monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    if monkeypatch_version:
        monkeypatch.setattr(
            "gardenlinux.features.artifact_base_name.ArtifactBaseName.get_version_and_commit_id_from_files",
            lambda root: ("1.2.3", "abcdef12"),
        )

    # Act
    fema.main()

    # Assert
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_output


def test_get_version_missing_file_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # Arrange (one file only)
    (tmp_path / "COMMIT").write_text("abcdef1234\n")

    argv = [
        "prog",
        "--arch",
        "amd64",
        "--cname",
        "flav",
        "version",
    ]

    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    assert ArtifactBaseName.get_version_and_commit_id_from_files(str(tmp_path)) == (
        None,
        None,
    )

    with pytest.raises(ValueError, match="Argument missing: version"):
        fema.main()


def test_main_requires_cname(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    monkeypatch.setattr(sys, "argv", ["prog", "arch"])
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(
        ValueError,
        match="Argument missing: At least one of artifact_base_name, cname, flavor or versioned_flavor",
    ):
        fema.main()


def test_main_cname_raises_missing_commit_id(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    # args.type == 'cname, arch is None and no default_arch set
    argv = [
        "prog",
        "--cname",
        "flav",
        "--arch",
        "amd64",
        "--version",
        "1.0",
        "cname",
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(ValueError, match="Argument missing: version"):
        fema.main()


def test_main_raises_no_arch_no_default(monkeypatch: pytest.MonkeyPatch) -> None:
    # Arrange
    # args.type == 'cname, arch is None and no default_arch set
    argv = ["prog", "--cname", "flav", "cname"]
    monkeypatch.setattr(sys, "argv", argv)

    # Act / Assert
    with pytest.raises(ValueError, match="Argument missing: arch"):
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
        "version_and_commit-id",
    ]
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(fema, "Parser", lambda *a, **kw: None)

    # Act / Assert
    with pytest.raises(ValueError, match="Argument missing: version"):
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
