import sys
from unittest.mock import MagicMock, patch

import pytest

import gardenlinux.s3.__main__ as s3m


@pytest.mark.parametrize(
    "argv,expected_method",
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
        ),
    ],
)
def test_main_calls_correct_artifacts(argv, expected_method):
    with patch.object(sys, "argv", argv):
        with patch.object(s3m, "S3Artifacts") as mock_s3_cls:
            mock_instance = MagicMock()
            mock_s3_cls.return_value = mock_instance

            s3m.main()

            method = getattr(mock_instance, expected_method)
            method.assert_called_once_with("test-cname", "some/path")

            mock_s3_cls.assert_called_once_with("test-bucket")
