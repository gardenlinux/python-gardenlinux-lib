import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import md5, sha256
from gardenlinux.s3.s3_artifacts import S3Artifacts


# Dummy CName replacement
class DummyCName:
    def __init__(self, cname):
        self.platform = "aws"
        self.arch = "amd64"
        self.version = "1234.1"
        self.commit_id = "abc123"


# Helpers to compute digests for fake files
def dummy_digest(data: bytes, algo: str) -> str:
    """
    Dummy for file_digest() to compute hashes for in-memory byte streams
    """
    content = data.read()
    data.seek(0) # Reset byte cursor to start for multiple uses

    if algo == "md5":
        return md5(content)
    elif algo == "sha256":
        return sha256(content)
    else:
        raise ValueError(f"Unsupported algo: {algo}")


@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_s3artifacts_init_success(mock_bucket_class):
    """
    Sanity test to assert correct instantiation of S3Artifacts object
    """
    mock_bucket_instance = MagicMock()
    mock_bucket_class.return_value = mock_bucket_instance

    s3 = S3Artifacts("my-bucket")

    mock_bucket_class.assert_called_once_with("my-bucket", None, None)
    assert s3._bucket == mock_bucket_instance


@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_s3_artifacts_invalid_bucket(mock_bucket):
    """
    Sanity test to check proper Error raising when using non-existing bucket
    """
    # Simulate an exception being raised when trying to create the Bucket
    mock_bucket.side_effect = RuntimeError("Bucket does not exist")

    with pytest.raises(RuntimeError, match="Bucket does not exist"):
        S3Artifacts("invalid-bucket")


@patch("gardenlinux.s3.s3_artifacts.CName", new=DummyCName)
@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_download_to_directory_success(mock_bucket_class):
    """
    Test download of mutliple files to directory on disk.
    """
    # Arrange
    # Create mock bucket instance
    mock_bucket = MagicMock()

    # Mock release object
    release_object = MagicMock()
    release_object.key = "meta/singles/testcname"

    # Mock objects to be downloaded
    s3_obj1 = MagicMock()
    s3_obj1.key = "objects/testcname/file1"
    s3_obj2 = MagicMock()
    s3_obj2.key = "objects/testcname/file2"

    # Mock return value of .filter().all() from boto3
    class MockFilterReturn:
        def all(self):
            return [s3_obj1, s3_obj2]

    # Mock teh behaviour of .objects.filter(Prefix=...)
    # Lets us simulate different responses depending on prefix
    def filter_side_effect(Prefix):
        # When fetching metadata
        if Prefix == "meta/singles/testcname":
            return [release_object] # return list with release file
        # When fetching actual artifact
        elif Prefix == "objects/testcname":
            return MockFilterReturn() # return mock object
        return [] # Nothing found

    # Act
    mock_bucket.objects.filter.side_effect = filter_side_effect
    mock_bucket_class.return_value = mock_bucket

    with TemporaryDirectory() as tmpdir:
        artifacts_dir = Path(tmpdir)

        s3 = S3Artifacts("test-bucket")
        s3.download_to_directory("testcname", artifacts_dir)

        # Assert
        # Validate download_file called with correct metadata path
        mock_bucket.download_file.assert_any_call(
            "meta/singles/testcname",
            artifacts_dir / "testcname.s3_metadata.yaml",
        )

        # Validate files were downloaded from object keys
        mock_bucket.download_file.assert_any_call(
            "objects/testcname/file1", artifacts_dir / "file1"
        )
        mock_bucket.download_file.assert_any_call(
            "objects/testcname/file2", artifacts_dir / "file2"
        )

        assert mock_bucket.download_file.call_count == 3


@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_download_to_directory_invalid_path(mock_bucket):
    """
    Sanity Test to test behaviour on invalid paths
    """
    s3 = S3Artifacts("bucket")
    with pytest.raises(RuntimeError):
        s3.download_to_directory("test-cname", "/invalid/path/does/not/exist")


@patch("gardenlinux.s3.s3_artifacts.file_digest", side_effect=dummy_digest)
@patch("gardenlinux.s3.s3_artifacts.CName", new=DummyCName)
@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_upload_from_directory_success(mock_bucket_class, mock_digest):
    """
    Test upload of multiple artifacts from disk to bucket
    """
    # Arrange
    mock_bucket = MagicMock()
    mock_bucket.name = "test-bucket"
    mock_bucket_class.return_value = mock_bucket

    # Create a fake .release file
    release_data = """
    GARDENLINUX_VERSION = 1234.1
    GARDENLINUX_COMMIT_ID = abc123
    GARDENLINUX_COMMIT_ID_LONG = abc123long
    GARDENLINUX_FEATURES = _usi,_trustedboot
    """

    # Create a fake release file and two artifact files
    with TemporaryDirectory() as tmpdir:
        artifacts_dir = Path(tmpdir)
        cname = "testcname"

        # Write .release file
        release_path = artifacts_dir / f"{cname}.release"
        release_path.write_text(release_data)

        # Create dummy files for upload
        for name in [f"{cname}-file1", f"{cname}-file2"]:
            (artifacts_dir / name).write_bytes(b"dummy content")

        s3 = S3Artifacts("test-bucket")

        # Act
        s3.upload_from_directory(cname, artifacts_dir)

        # Assert
        calls = mock_bucket.upload_file.call_args_list

        # Check that for each file, upload_file was called with ExtraArgs containing "Tagging"
        for name in [f"{cname}-file1", f"{cname}-file2"]:
            key = f"objects/{cname}/{name}"
            path = artifacts_dir / name

            # Look for a call with matching positional args (path, key)
            matching_calls = [
                call
                for call in calls
                if call.args[0] == path
                and call.args[1] == key
                and isinstance(call.kwargs.get("ExtraArgs"), dict)
                and "Tagging" in call.kwargs["ExtraArgs"]
            ]
            assert matching_calls, f"upload_file was not called with Tagging for {name}"


@patch("gardenlinux.s3.s3_artifacts.file_digest", side_effect=dummy_digest)
@patch("gardenlinux.s3.s3_artifacts.CName", new=DummyCName)
@patch("gardenlinux.s3.s3_artifacts.Bucket")
def test_upload_from_directory_with_delete(mock_bucket_class, mock_digest, tmp_path):
    """
    Test that upload_from_directory deletes existing files before uploading
    when delete_before_push=True
    """
    mock_bucket = MagicMock()
    mock_bucket.name = "test-bucket"
    mock_bucket_class.return_value = mock_bucket

    s3 = S3Artifacts("test-bucket")
    cname = "test-cname"

    release = tmp_path / f"{cname}.release"
    release.write_text(
        "GARDENLINUX_VERSION = 1234.1\n"
        "GARDENLINUX_COMMIT_ID = abc123\n"
        "GARDENLINUX_COMMIT_ID_LONG = abc123long\n"
        "GARDENLINUX_FEATURES = _usi,_trustedboot\n"
    )

    artifact = tmp_path / f"{cname}.kernel"
    artifact.write_bytes(b"fake")

    s3.upload_from_directory(cname, tmp_path, delete_before_push=True)

    mock_bucket.delete_objects.assert_any_call(Delete={"Objects": [{"Key": f"objects/{cname}/{artifact.name}"}]})
    mock_bucket.delete_objects.assert_any_call(Delete={"Objects": [{"Key": f"meta/singles/{cname}"}]})
