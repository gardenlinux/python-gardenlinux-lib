from typing import Any, Dict, List

import pytest

from gardenlinux.features import Parser

from ..constants import GL_ROOT_DIR


@pytest.mark.parametrize(  # type: ignore[misc]
    "input_cname, expected_output",
    [
        (
            "aws-gardener_prod",
            {
                "platform": ["aws"],
                "element": [
                    "log",
                    "sap",
                    "ssh",
                    "base",
                    "server",
                    "cloud",
                    "multipath",
                    "iscsi",
                    "nvme",
                    "gardener",
                ],
                "flag": ["_fwcfg", "_legacy", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "gcp-gardener_prod",
            {
                "platform": ["gcp"],
                "element": [
                    "log",
                    "sap",
                    "ssh",
                    "base",
                    "server",
                    "cloud",
                    "multipath",
                    "iscsi",
                    "nvme",
                    "gardener",
                ],
                "flag": ["_fwcfg", "_legacy", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "azure-gardener_prod",
            {
                "platform": ["azure"],
                "element": [
                    "log",
                    "sap",
                    "ssh",
                    "base",
                    "server",
                    "cloud",
                    "multipath",
                    "iscsi",
                    "nvme",
                    "gardener",
                ],
                "flag": ["_fwcfg", "_legacy", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "ali-gardener_prod",
            {
                "platform": ["ali"],
                "element": [
                    "log",
                    "sap",
                    "ssh",
                    "base",
                    "server",
                    "cloud",
                    "multipath",
                    "iscsi",
                    "nvme",
                    "gardener",
                ],
                "flag": ["_fwcfg", "_legacy", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "metal-khost_dev",
            {
                "platform": ["metal"],
                "element": [
                    "firewall",
                    "log",
                    "sap",
                    "ssh",
                    "base",
                    "server",
                    "chost",
                    "khost",
                ],
                "flag": ["_dev", "_fwcfg", "_legacy", "_selinux", "_slim"],
            },
        ),
    ],
)
def test_parser_filter_as_dict(
    input_cname: str, expected_output: Dict[str, Any]
) -> None:
    """
    Tests if parser_filter_as_dict returns the dict with expected features.

    If you discover that this test failed, you may want to verify if the included
    features have changed since writing this test. In this case, update the expected output accordingly.
    You can print the output of parser_filter_as_dict so you have the dict in the expected format.
    """
    features_dict = Parser(GL_ROOT_DIR).filter_as_dict(input_cname)
    assert features_dict == expected_output


def test_parser_return_intersection_subset() -> None:
    # Arrange
    input_set = {"a", "c"}
    order_list = ["a", "b", "c", "d"]

    # Act
    result = Parser.subset(input_set, order_list)

    # Assert
    assert result == ["a", "c"]


def test_get_flavor_from_feature_set() -> None:
    # Arrange
    sorted_features = ["base", "_hidden", "extra"]

    # Act
    result = Parser.get_flavor_from_feature_set(sorted_features)

    # Assert
    assert result == "base_hidden-extra"


def test_gget_flavor_from_feature_set_empty_raises() -> None:
    # get_flavor with empty iterable raises TypeError
    with pytest.raises(TypeError):
        Parser.get_flavor_from_feature_set([])


def test_parser_subset_nomatch() -> None:
    # Arrange
    input_set = {"x", "y"}
    order_list = ["a", "b", "c"]

    # Act
    result = Parser.subset(input_set, order_list)

    # Assert
    assert result == []


def test_parser_subset_with_empty_order_list() -> None:
    # Arrange
    input_set = {"a", "b"}
    order_list: List[str] = []

    result = Parser.subset(input_set, order_list)

    assert result == []
