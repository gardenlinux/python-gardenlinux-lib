import sys
from unittest.mock import MagicMock, patch

import pytest

import gardenlinux.s3.__main__ as s3m


@pytest.mark.parametrize(
    "argv, expected_method, expected_args, expected_kwargs",
    [
        (
            [
                "__main__.py",
                "--bucket",
                "test-bucket",
                "--cname",
                "test-cname",
                "--path",
                "some/path",
                "download-artifacts-from-bucket",
            ],
            "download_to_directory",
            ["test-cname", "some/path"],
            {},
        ),
        (
            [
                "__main__.py",
                "--bucket",
                "test-bucket",
                "--cname",
                "test-cname",
                "--path",
                "some/path",
                "upload-artifacts-to-bucket",
            ],
            "upload_from_directory",
            ["test-cname", "some/path"],
            {"dry_run": False},
        ),
    ],
)
def test_main_calls_correct_artifacts(
    argv, expected_method, expected_args, expected_kwargs
):
    with patch.object(sys, "argv", argv):
        with patch.object(s3m, "S3Artifacts") as mock_s3_cls:
            mock_instance = MagicMock()
            mock_s3_cls.return_value = mock_instance

            s3m.main()

            method = getattr(mock_instance, expected_method)
            method.assert_called_once_with(*expected_args, **expected_kwargs)

            mock_s3_cls.assert_called_once_with("test-bucket")
