import pytest
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory

from gardenlinux.oci import Podman
from gardenlinux.oci.podman_context import PodmanContext

from ..constants import TEST_DATA_DIR


def test_podman_tag_list(monkeypatch, capsys):
    with PodmanContext() as podman_context, TemporaryDirectory() as tmpdir:
        podman = Podman()

        image_id = podman.build(f"{TEST_DATA_DIR}/oci/build", podman=podman_context)

        try:
            podman.tag_list(
                image_id,
                Podman.get_container_tag_list("container-test", ["a", "b", "c"]),
            )

            image = podman_context.images.get(image_id)

            assert len(image.tags) == 3
            assert "localhost/container-test:a" in image.tags
            assert "localhost/container-test:b" in image.tags
            assert "localhost/container-test:c" in image.tags
        finally:
            image = podman_context.images.get(image_id)
            podman_context.images.remove(image, force=True)


def test_podmancontext_socket_timeout(monkeypatch):
    @contextmanager
    def Popen(*args, **kwargs):
        yield

    monkeypatch.setattr("gardenlinux.oci.podman_context.Popen", Popen)

    with pytest.raises(TimeoutError):
        with PodmanContext() as podman_context:
            pass


def test_podmancontext_podman_argument():
    with PodmanContext() as podman_context:
        with pytest.raises(
            ValueError, match="Podman context wrapped functions can not be called with"
        ):
            Podman().get_image_id("container-test", podman=object())
