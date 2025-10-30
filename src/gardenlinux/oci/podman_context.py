# -*- coding: utf-8 -*-

"""
OCI podman context
"""

import logging
from contextlib import ExitStack
from functools import wraps
from os import rmdir
from pathlib import Path
from subprocess import PIPE, Popen, STDOUT
from tempfile import mkdtemp
from time import sleep
from typing import Any, Optional

from podman.client import PodmanClient

from ..constants import PODMAN_CONNECTION_MAX_IDLE_SECONDS
from ..logger import LoggerSetup


class PodmanContext(ExitStack):
    """
    OCI podman context provides a context manager to be used to interact with
    the podman API from Python.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      0.11.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Constructor __init__(PodmanContext)

        :since: 0.11.0
        """

        ExitStack.__init__(self)

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._logger = logger
        self._podman = None
        self._podman_daemon = None
        self._tmpdir = None

    def __enter__(self):
        """
        python.org: Enter the runtime context related to this object.

        :return: (object) Podman context instance
        :since: 0.11.0
        """

        self._tmpdir = mkdtemp()

        podman_sock = str(Path(self._tmpdir, "podman.sock").absolute())

        self._podman = PodmanClient(base_url=f"unix://{podman_sock}")
        self._podman_daemon = Popen(
            args=[
                "podman",
                "system",
                "service",
                f"--time={PODMAN_CONNECTION_MAX_IDLE_SECONDS}",
                f"unix://{podman_sock}",
            ],
            executable="podman",
            stdout=PIPE,
            stderr=STDOUT,
        )

        self.enter_context(self._podman_daemon)
        self._wait_for_socket(podman_sock)
        self.enter_context(self._podman)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        python.org: Exit the runtime context related to this object.

        :return: (bool) True to suppress exceptions
        :since:  0.11.0
        """

        try:
            self._podman_daemon.terminate()
            self._podman_daemon.wait(PODMAN_CONNECTION_MAX_IDLE_SECONDS)

            if exc_type is not None:
                stdout = self._podman_daemon.stdout.read()
                self._logger.error(
                    f"Podman context encountered an error. Process output: {stdout}"
                )
        finally:
            self._podman_daemon = None

            rmdir(self._tmpdir)
            self._tmpdir = None

        return False

    def __getattr__(self, name: str) -> Any:
        """
        python.org: Called when an attribute lookup has not found the attribute in
        the usual places (i.e. it is not an instance attribute nor is it found in the
        class tree for self).

        :param name: Attribute name

        :return: (mixed) Attribute
        :since:  0.11.0
        """

        if self._podman_daemon is None:
            raise RuntimeError("Podman context not ready")

        return getattr(self._podman, name)

    def _wait_for_socket(self, sock: str):
        """
        Waits for the socket file to be created.

        :since: 0.11.0
        """

        sock_path = Path(sock)

        for _ in range(0, 5 * PODMAN_CONNECTION_MAX_IDLE_SECONDS):
            if sock_path.exists():
                break

            sleep(0.2)

        if not sock_path.exists():
            raise TimeoutError()

    @staticmethod
    def wrap(f) -> Any:
        """
        Wraps the given function to provide access to a podman client.

        :since: 0.11.0
        """

        @wraps(f)
        def decorator(*args, **kwargs) -> Any:
            """
            Decorator for wrapping a function or method with a call context.
            """

            if "podman" in kwargs:
                if not isinstance(kwargs["podman"], PodmanContext):
                    raise ValueError(
                        "Podman context wrapped functions can not be called with `kwargs['podman']`"
                    )

                return f(*args, **kwargs)

            with PodmanContext() as podman:
                kwargs["podman"] = podman
                return f(*args, **kwargs)

        return decorator
