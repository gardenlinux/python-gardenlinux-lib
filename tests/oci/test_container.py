import io
import json
import pytest

from gardenlinux.oci import Container
from requests import Response
from requests.exceptions import HTTPError

from ..constants import (
    CONTAINER_NAME_ZOT_EXAMPLE,
    TEST_COMMIT,
    TEST_VERSION,
)


@pytest.fixture(name="Container_read_or_generate_403")
def patch__Container(monkeypatch):
    """Replace oras.oci.Layer with DummyLayer in Layer's module."""
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
def test_manifest():
    """Verify container calls raises exceptions for certain errors."""
    # Arrange
    container = Container(f"{CONTAINER_NAME_ZOT_EXAMPLE}:{TEST_VERSION}", insecure=True)

    with pytest.raises(HTTPError):
        container.read_or_generate_manifest(
            version=TEST_VERSION, commit=TEST_COMMIT
        )
