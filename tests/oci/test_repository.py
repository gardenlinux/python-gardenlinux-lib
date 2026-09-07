from base64 import b64encode
from typing import Any

import pytest
from requests import Response
from requests.exceptions import HTTPError

from gardenlinux.oci import Repository

from ..constants import REGISTRY, REPOSITORY_NAME_ZOT_EXAMPLE, TEST_COMMIT, TEST_VERSION


@pytest.fixture(name="Repository_login_403")
def patch_Repository_login_403(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch `login()` to return HTTP 403. `docker.errors.APIError` extends from `requests.exceptions.HTTPError` as well."""

    def login_403(*args: Any, **kwargs: Any) -> None:
        response = Response()
        response.status_code = 403
        raise HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(Repository, "login", login_403)


@pytest.fixture(name="Repository_read_or_generate_403")
def patch_Repository_read_or_generate_403(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch `read_or_generate_manifest()` to return HTTP 403."""

    def read_or_generate_403(*args: Any, **kwargs: Any) -> None:
        response = Response()
        response.status_code = 403
        raise HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(Repository, "read_or_generate_manifest", read_or_generate_403)


@pytest.mark.usefixtures("zot_session")
def test_manifest() -> None:
    """Verify a newly created manifest returns correct commit value."""
    # Arrange
    repository = Repository(
        f"{REPOSITORY_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True
    )

    manifest = repository.read_or_generate_manifest(
        version=TEST_VERSION, commit=TEST_COMMIT
    )

    # Assert
    assert manifest.commit == TEST_COMMIT


@pytest.mark.usefixtures("zot_session")
@pytest.mark.usefixtures("Repository_read_or_generate_403")
def test_manifest_403() -> None:
    """Verify repository calls raises exceptions for certain errors."""
    # Arrange
    repository = Repository(
        f"{REPOSITORY_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True
    )

    with pytest.raises(HTTPError):
        repository.read_or_generate_manifest(version=TEST_VERSION, commit=TEST_COMMIT)


@pytest.mark.usefixtures("zot_session")
def test_manifest_auth_token(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Verify repository calls use login environment variables if defined."""
    with monkeypatch.context():
        token = "test"
        monkeypatch.setenv("GL_CLI_REGISTRY_TOKEN", token)

        # Arrange
        repository = Repository(
            f"{REPOSITORY_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True
        )

        # Assert
        assert repository.auth.token == b64encode(bytes(token, "utf-8")).decode("utf-8")


@pytest.mark.usefixtures("zot_session")
@pytest.mark.usefixtures("Repository_login_403")
def test_manifest_login_username_password(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    """Verify repository calls use login environment variables if defined."""
    with monkeypatch.context():
        monkeypatch.setenv("GL_CLI_REGISTRY_USERNAME", "test")
        monkeypatch.setenv("GL_CLI_REGISTRY_PASSWORD", "test")

        # Arrange
        Repository(f"{REGISTRY}/protected/test:{TEST_VERSION}", insecure=True)

        # Assert
        assert "Login error: 403 Forbidden" in caplog.text
