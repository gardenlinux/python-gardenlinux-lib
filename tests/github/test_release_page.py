import importlib
import os
from pathlib import Path

import git
from git import Repo


class SubmoduleAsRepo(Repo):
    """This will fake a git submodule as a git repository object."""
    def __new__(cls, *args, **kwargs):
        r = super().__new__(Repo)
        r.__init__(*args, **kwargs)

        maybe_gl_submodule = [submodule for submodule in r.submodules if submodule.name.endswith("/gardenlinux")]
        if not maybe_gl_submodule:
            return r
        else:
            gl = maybe_gl_submodule[0]

        sr = gl.module()
        sr.remotes.origin.pull("main")
        return sr


def test_github_release_page(monkeypatch):
    monkeypatch.setattr(git, "Repo", SubmoduleAsRepo)
    import gardenlinux.github
    importlib.reload(gardenlinux.github)

    generated_release_notes = gardenlinux.github.create_github_release_notes(
        "1877.3",
        "75df9f401a842914563f312899ec3ce34b24515c"
    )
    fixture_path = Path(os.path.dirname(__file__)) / ".." / ".." / "test-data" / "github_release_notes_1877.3.md"
    with open(fixture_path) as md:
        release_notes_fixture = md.read()
        assert generated_release_notes == release_notes_fixture
