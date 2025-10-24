import importlib

from gardenlinux import flavors


def test_parser_exposed_at_top_level():
    """Parser should be importable directly from the package."""
    from gardenlinux.flavors import parser

    assert flavors.Parser is parser.Parser


def test___all___is_correct():
    """__all__ should only contain Parser."""
    assert flavors.__all__ == ["Parser"]


def test_star_import(monkeypatch):
    """from flavors import * should bring Parser into locals()."""
    # Arrange
    namespace = {}

    # Act
    module = importlib.import_module("gardenlinux.flavors")
    for name in getattr(module, "__all__", []):
        namespace[name] = getattr(module, name)

    # Assert
    assert "Parser" in namespace
    assert namespace["Parser"] is flavors.Parser


def test_import_module():
    """Importing the package should not raise exceptions."""
    importlib.reload(flavors)  # Should succeed without errors
