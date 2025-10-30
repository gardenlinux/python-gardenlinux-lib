import json
import pytest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import gardenlinux.oci.__main__ as oci_main
from gardenlinux.oci import Podman
from gardenlinux.oci.podman_context import PodmanContext
from ..constants import REGISTRY, TEST_DATA_DIR


def test_main_build_container(monkeypatch, capsys):
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
            assert podman.images.exists("localhost/container-test:latest") == True
            assert "localhost/container-test:latest" in image.tags
        finally:
            podman.images.remove(image)


def test_main_build_container_and_save_as_oci_archive(monkeypatch, capsys):
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


def test_main_load_containers_from_directory(monkeypatch, capsys):
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


def test_main_save_container(monkeypatch):
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
