from contextlib import contextmanager
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from gardenlinux.oci import Podman
from gardenlinux.oci.podman_context import PodmanContext

from ..constants import TEST_DATA_DIR


def test_podman_tag_list(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with PodmanContext() as podman_context, TemporaryDirectory():
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


def test_podmancontext_socket_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    @contextmanager
    def Popen(*args: Any, **kwargs: Any) -> Any:
        yield

    monkeypatch.setattr("gardenlinux.oci.podman_context.Popen", Popen)

    with pytest.raises(TimeoutError):
        with PodmanContext():
            pass


def test_podmancontext_podman_argument() -> None:
    with PodmanContext():
        with pytest.raises(
            ValueError, match="Podman context wrapped functions can not be called with"
        ):
            Podman().get_image_id("container-test", podman=object())
