import io
import json
import logging
from base64 import b64encode

import pytest
from requests import Response
from requests.exceptions import HTTPError

from gardenlinux.oci import Container

from ..constants import (
    CONTAINER_NAME_ZOT_EXAMPLE,
    REGISTRY,
    TEST_COMMIT,
    TEST_VERSION,
)


@pytest.fixture(name="Container_login_403")
def patch__Container_login_403(monkeypatch):
    """Patch `login()` to return HTTP 403. `docker.errors.APIError` extends from `requests.exceptions.HTTPError` as well."""

    def login_403(*args, **kwargs):
        response = Response()
        response.status_code = 403
        raise HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(Container, "login", login_403)


@pytest.fixture(name="Container_read_or_generate_403")
def patch__Container_read_or_generate_403(monkeypatch):
    """Patch `read_or_generate_manifest()` to return HTTP 403."""

    def read_or_generate_403(*args, **kwargs):
        response = Response()
        response.status_code = 403
        raise HTTPError("403 Forbidden", response=response)

    monkeypatch.setattr(Container, "read_or_generate_manifest", read_or_generate_403)


@pytest.mark.usefixtures("zot_session")
def test_manifest():
    """Verify a newly created manifest returns correct commit value."""
    # Arrange
    container = Container(f"{CONTAINER_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True)

    manifest = container.read_or_generate_manifest(
        version=TEST_VERSION, commit=TEST_COMMIT
    )

    # Assert
    assert manifest.commit == TEST_COMMIT


@pytest.mark.usefixtures("zot_session")
@pytest.mark.usefixtures("Container_read_or_generate_403")
def test_manifest_403():
    """Verify container calls raises exceptions for certain errors."""
    # Arrange
    container = Container(f"{CONTAINER_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True)

    with pytest.raises(HTTPError):
        container.read_or_generate_manifest(version=TEST_VERSION, commit=TEST_COMMIT)


@pytest.mark.usefixtures("zot_session")
def test_manifest_auth_token(monkeypatch, caplog):
    """Verify container calls use login environment variables if defined."""
    with monkeypatch.context():
        token = "test"
        monkeypatch.setenv("GL_CLI_REGISTRY_TOKEN", token)

        # Arrange
        container = Container(
            f"{CONTAINER_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True
        )

        # Assert
        assert container.auth.token == b64encode(bytes(token, "utf-8")).decode("utf-8")


@pytest.mark.usefixtures("zot_session")
@pytest.mark.usefixtures("Container_login_403")
def test_manifest_login_username_password(monkeypatch, caplog):
    """Verify container calls use login environment variables if defined."""
    with monkeypatch.context():
        monkeypatch.setenv("GL_CLI_REGISTRY_USERNAME", "test")
        monkeypatch.setenv("GL_CLI_REGISTRY_PASSWORD", "test")

        # Arrange
        Container(f"{REGISTRY}/protected/test:{TEST_VERSION}", insecure=True)

        # Assert
        assert "Login error: 403 Forbidden" in caplog.text
