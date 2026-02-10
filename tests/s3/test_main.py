import re
import sys
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

import gardenlinux.s3.__main__ as s3m

from .conftest import S3Env
from .constants import RELEASE_DATA, S3_METADATA


@pytest.mark.parametrize(
    "argv, expected_method, expected_args, expected_kwargs",
    [
        (
            [
                "__main__.py",
                "--bucket",
                "test-bucket",
                "--path",
                "some/path",
                "download-artifacts-from-bucket",
                "--cname",
                "test-cname",
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
                "--path",
                "some/path",
                "upload-artifacts-to-bucket",
                "--artifact-name",
                "test-cname",
            ],
            "upload_from_directory",
            ["test-cname", "some/path"],
            {"dry_run": False},
        ),
    ],
)
def test_main_calls_correct_artifacts(
    argv: List[str],
    expected_method: str,
    expected_args: List[Any],
    expected_kwargs: Dict[str, Any],
) -> None:
    with (
        patch.object(sys, "argv", argv),
        patch.object(s3m, "S3Artifacts") as mock_s3_cls,
    ):
        mock_instance = MagicMock()
        mock_s3_cls.return_value = mock_instance

        s3m.main()

        method = getattr(mock_instance, expected_method)
        method.assert_called_once_with(*expected_args, **expected_kwargs)

        mock_s3_cls.assert_called_once_with("test-bucket")


def test_main_with_expected_result(
    s3_setup: S3Env, capsys: pytest.CaptureFixture[str]
) -> None:
    env = s3_setup

    # Arrange
    with patch.object(
        sys,
        "argv",
        [
            "__main__.py",
            "--dry-run",
            "--bucket",
            env.bucket_name,
            "--path",
            str(env.tmp_path),
            "upload-artifacts-to-bucket",
            "--artifact-name",
            env.cname,
        ],
    ):
        release_path = env.tmp_path / f"{env.cname}.release"
        release_path.write_text(RELEASE_DATA)

        s3m.main()

        result = capsys.readouterr().out.strip()

        result = re.sub(
            "^(.*)build_timestamp\\: .+$",
            "\\1build_timestamp: {build_timestamp}",
            result,
            flags=re.M,
        )

        result = re.sub(
            "^(.*)(md5sum|sha256sum)\\: .+$", "\\1\\2: {\\2}", result, flags=re.M
        )

        assert result == S3_METADATA
