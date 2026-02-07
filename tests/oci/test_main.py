import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

import gardenlinux.oci.__main__ as oci_main
from gardenlinux.oci import Container, Podman
from gardenlinux.oci.podman_context import PodmanContext

from ..constants import REGISTRY, REPO_NAME, TEST_DATA_DIR


def test_main_build_container(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "__main__.py",
            "build-container",
            "--dir",
            f"{TEST_DATA_DIR}/oci/build",
            "--container",
            "container-test",
            "--tag",
            "latest",
        ],
    )

    with pytest.raises(SystemExit, match="0"):
        oci_main.main()

    captured = capsys.readouterr()
    image_id = captured.out.strip()

    with PodmanContext() as podman:
        image = podman.images.get(image_id)

        try:
            assert podman.images.exists("localhost/container-test:latest")
            assert "localhost/container-test:latest" in image.tags
        finally:
            podman.images.remove(image)


def test_main_build_container_and_save_as_oci_archive(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "__main__.py",
                "build-container",
                "--dir",
                f"{TEST_DATA_DIR}/oci/build",
                "--container",
                "container-test",
                "--tag",
                "latest",
                "--oci_archive",
                f"{tmpdir}/archive.oci",
            ],
        )

        image_id = None

        try:
            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            captured = capsys.readouterr()
            image_id = captured.out.strip()

            assert Path(tmpdir, "archive.oci").exists()
        finally:
            if image_id is not None:
                with PodmanContext() as podman:
                    image = podman.images.get(image_id)
                    podman.images.remove(image)


def test_main_load_container(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with PodmanContext() as podman_context, TemporaryDirectory() as tmpdir:
        podman = Podman()

        image_id = podman.build(f"{TEST_DATA_DIR}/oci/build", podman=podman_context)

        try:
            podman.save_oci_archive(
                image_id, f"{tmpdir}/archive.oci", podman=podman_context
            )

            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "__main__.py",
                    "load-container",
                    "--oci_archive",
                    f"{tmpdir}/archive.oci",
                ],
            )

            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            captured = capsys.readouterr()
            image_id_exported = captured.out.strip()

            assert Path(tmpdir, "archive.oci").exists()
            assert image_id_exported == image_id
        finally:
            image = podman_context.images.get(image_id)
            podman_context.images.remove(image)


def test_main_load_containers_from_directory(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with PodmanContext() as podman_context, TemporaryDirectory() as tmpdir:
        podman = Podman()

        image_id = podman.build(f"{TEST_DATA_DIR}/oci/build", podman=podman_context)

        try:
            podman.save_oci_archive(image_id, f"{tmpdir}/1.oci", podman=podman_context)
            podman.save_oci_archive(image_id, f"{tmpdir}/2.oci", podman=podman_context)
            podman.save_oci_archive(image_id, f"{tmpdir}/3.oci", podman=podman_context)

            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "__main__.py",
                    "load-containers-from-directory",
                    "--dir",
                    f"{tmpdir}",
                ],
            )

            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            captured = capsys.readouterr()
            result = json.loads(captured.out)

            assert len(result) == 3
            assert "1.oci" in result
            assert "2.oci" in result
            assert "3.oci" in result
        finally:
            image = podman_context.images.get(image_id)
            podman_context.images.remove(image)


@pytest.mark.usefixtures("zot_session")
def test_main_push_container(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with PodmanContext() as podman_context, TemporaryDirectory():
        podman = Podman(insecure=True)

        image_built = None
        image_id = podman.build(f"{TEST_DATA_DIR}/oci/build", podman=podman_context)

        try:
            image_built = podman_context.images.get(image_id)

            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "__main__.py",
                    "push-container",
                    "--container",
                    image_id,
                    "--destination",
                    f"docker://{REGISTRY}/{REPO_NAME}/kidden:latest",
                    "--insecure",
                    "true",
                ],
            )

            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            container = Container(
                f"http://{REGISTRY}/{REPO_NAME}/kidden:latest", insecure=True
            )
            # Assert - the following read would fail if push has not been successful
            _ = container.read_manifest()
        finally:
            if image_built is not None:
                podman_context.images.remove(image_built)


def test_main_tag_container(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    with PodmanContext() as podman_context, TemporaryDirectory():
        podman = Podman()

        image = None
        image_id = podman.build(f"{TEST_DATA_DIR}/oci/build", podman=podman_context)

        try:
            image = podman_context.images.get(image_id)

            monkeypatch.setattr(
                sys,
                "argv",
                [
                    "__main__.py",
                    "tag-container",
                    "--container",
                    image_id,
                    "--additional_tag",
                    "latest",
                    "--additional_tag",
                    "test:latest",
                    "--additional_tag",
                    "localhost/kidden:latest",
                ],
            )

            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            image = podman_context.images.get(image_id)

            assert len(image.tags) == 3
            assert f"localhost/{image_id}:latest" in image.tags
            assert "localhost/test:latest" in image.tags
            assert "localhost/kidden:latest" in image.tags
        finally:
            if image is not None:
                podman_context.images.remove(image, force=True)


def test_main_save_container(monkeypatch: pytest.MonkeyPatch) -> None:
    with PodmanContext() as podman, TemporaryDirectory() as tmpdir:
        image_id = Podman().build(
            f"{TEST_DATA_DIR}/oci/build", oci_tag="container-test:latest", podman=podman
        )

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "__main__.py",
                "save-container",
                "--container",
                "container-test:latest",
                "--tag",
                "localhost/container-test:latest",
                "--oci_archive",
                f"{tmpdir}/archive.oci",
            ],
        )

        try:
            with pytest.raises(SystemExit, match="0"):
                oci_main.main()

            assert Path(tmpdir, "archive.oci").exists()
        finally:
            image = podman.images.get(image_id)
            podman.images.remove(image)
