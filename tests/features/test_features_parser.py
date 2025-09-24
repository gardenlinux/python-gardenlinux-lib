import pytest

from gardenlinux.features import Parser

from ..constants import GL_ROOT_DIR


@pytest.mark.parametrize(
    "input_cname, expected_output",
    [
        (
            "aws-gardener_prod",
            {
                "platform": ["aws"],
                "element": ["log", "sap", "ssh", "base", "server", "cloud", "gardener"],
                "flag": ["_boot", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "gcp-gardener_prod",
            {
                "platform": ["gcp"],
                "element": ["log", "sap", "ssh", "base", "server", "cloud", "gardener"],
                "flag": ["_boot", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "azure-gardener_prod",
            {
                "platform": ["azure"],
                "element": ["log", "sap", "ssh", "base", "server", "cloud", "gardener"],
                "flag": ["_boot", "_nopkg", "_prod", "_slim"],
            },
        ),
        (
            "ali-gardener_prod",
            {
                "platform": ["ali"],
                "element": ["log", "sap", "ssh", "base", "server", "cloud", "gardener"],
                "flag": ["_boot", "_nopkg", "_prod", "_slim"],
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
                "flag": ["_boot", "_dev", "_selinux", "_slim"],
            },
        ),
    ],
)
def test_parser_filter_as_dict(input_cname: str, expected_output: dict):
    """
    Tests if parser_filter_as_dict returns the dict with expected features.

    If you discover that this test failed, you may want to verify if the included
    features have changed since writing this test. In this case, update the expected output accordingly.
    You can print the output of parser_filter_as_dict so you have the dict in the expected format.
    """
    features_dict = Parser(GL_ROOT_DIR).filter_as_dict(input_cname)
    assert features_dict == expected_output
