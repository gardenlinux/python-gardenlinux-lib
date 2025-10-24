import pytest
import yaml

from gardenlinux.flavors.parser import Parser


@pytest.fixture
def valid_data():
    """Minimal data for valid GL_FLAVORS_SCHEMA."""
    return {
        "targets": [
            {
                "name": "linux",
                "category": "cat1",
                "flavors": [
                    {
                        "features": ["f1"],
                        "arch": "amd64",
                        "build": True,
                        "test": True,
                        "test-platform": False,
                        "publish": True,
                    },
                    {
                        "features": [],
                        "arch": "arm64",
                        "build": False,
                        "test": False,
                        "test-platform": False,
                        "publish": False,
                    },
                ],
            },
            {
                "name": "android",
                "category": "cat2",
                "flavors": [
                    {
                        "features": ["f2"],
                        "arch": "arm64",
                        "build": False,
                        "test": False,
                        "test-platform": True,
                        "publish": False,
                    }
                ],
            },
        ]
    }


def make_parser(data):
    """
    Construct Parser from dict.
    """
    return Parser(data)


def test_init_accepts_yaml_and_dict(valid_data):
    # Arrange
    yaml_str = yaml.safe_dump(valid_data)

    # Act
    p_from_dict = Parser(valid_data)
    p_from_yaml = Parser(yaml_str)

    # Assert
    assert p_from_dict._flavors_data == valid_data
    assert p_from_yaml._flavors_data == valid_data


def test_filter_defaults(valid_data):
    # Arrange
    parser = make_parser(valid_data)

    # Act
    combos = parser.filter()
    combo_names = [c[1] for c in combos]

    # Assert
    assert any("linux-f1-amd64" in name for name in combo_names)
    assert any("linux-arm64" in name for name in combo_names)


def test_filter_category_and_exclude(valid_data):
    # Arrange
    parser = make_parser(valid_data)

    # Act
    linux_combos = parser.filter(filter_categories=["cat1"])
    android_combos = parser.filter(exclude_categories=["cat1"])

    # Assert
    assert all("linux" in name for _, name in linux_combos)
    assert all("android" in name for _, name in android_combos)


@pytest.mark.parametrize("flag", ["only_build", "only_test", "only_publish"])
def test_filter_with_flags(valid_data, flag):
    # Arrange
    parser = make_parser(valid_data)

    # Act
    combos = parser.filter(**{flag: True})

    # Assert
    assert all("linux-f1-amd64" in name for _, name in combos)


def test_filter_only_test_platform(valid_data):
    # Arrange
    parser = make_parser(valid_data)

    # Act
    combos = parser.filter(only_test_platform=True)

    # Assert
    assert combos == [("arm64", "android-f2-arm64")]


def test_filter_with_excludes(valid_data):
    # Arrange
    parser = make_parser(valid_data)

    # Act
    combos = parser.filter(wildcard_excludes=["linux*"])

    # Assert
    assert all(not name.startswith("linux") for _, name in combos)


def test_group_by_arch_and_remove_arch():
    # Arrange
    combos = [
        ("amd64", "linux-amd64"),
        ("arm64", "android-arm64"),
        ("amd64", "foo-amd64"),
    ]

    # Act
    grouped = Parser.group_by_arch(combos)
    removed = Parser.remove_arch(combos)

    # Assert
    assert grouped["amd64"] == ["foo-amd64", "linux-amd64"]
    assert grouped["arm64"] == ["android-arm64"]
    assert "linux" in removed and "android" in removed


def test_exclude_include_only():
    # Arrange / Act / Assert
    assert Parser.should_exclude("abc", ["abc"], []) is True
    assert Parser.should_exclude("abc", [], ["a*"]) is True
    assert Parser.should_exclude("abc", [], ["z*"]) is False

    assert Parser.should_include_only("abc", ["a*"]) is True
    assert Parser.should_include_only("zzz", ["a*"]) is False
    assert Parser.should_include_only("abc", []) is True
