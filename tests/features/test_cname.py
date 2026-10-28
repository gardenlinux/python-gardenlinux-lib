import pytest

from gardenlinux.features import CName


@pytest.mark.parametrize(
    "input_cname, expected_output",
    [
        (
            "aws-gardener_prod",
            "aws-gardener_prod",
        ),
        (
            "metal-khost_dev",
            "metal-khost_dev",
        ),
        (
            "metal_pxe",
            "metal_pxe",
        ),
        (
            "container",
            "container",
        ),
    ],
)
def test_cname(input_cname: str, expected_output: str) -> None:
    """
    Tests if cname returns the dict with expected features.

    If you discover that this test failed, you may want to verify if the included
    features have changed since writing this test. In this case, update the expected output accordingly.
    You can print the output of cname so you have the dict in the expected format.
    """

    cname = CName(input_cname)
    assert str(cname) == expected_output
