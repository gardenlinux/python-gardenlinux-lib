# -*- coding: utf-8 -*-

"""
OCI podman context
"""

import logging
from functools import wraps
from typing import Any, Optional

from requests import Response

from ..logger import LoggerSetup
from .podman_context import PodmanContext


class PodmanObjectContext(object):
    """
    Podman object context handles access to the podman context for API calls.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: oci
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Constructor __init__(PodmanObjectContext)

        :since: 1.0.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.oci")

        self._logger = logger

    @PodmanContext.wrap
    def _raw_request(
        self,
        method: str,
        path_and_parameters: str,
        podman: PodmanContext,
        **kwargs: Any,
    ) -> Response:
        """
        Returns the podman API response for the request given.

        :param method: Podman API method
        :param path_and_parameters: Podman API path and query parameters
        :param podman: Podman context

        :return: (Response) Podman API response
        :since:  1.0.0
        """

        method_callable = getattr(podman.api, method)
        return method_callable(path_and_parameters, **kwargs)  # type: ignore[no-any-return]

    @staticmethod
    def wrap(f: Any) -> Any:
        """
        Wraps the given function to provide access to a podman client.

        :since: 1.0.0
        """

        @wraps(f)
        @PodmanContext.wrap
        def decorator(*args: Any, **kwargs: Any) -> Any:
            """
            Decorator for wrapping a function or method with a call context.
            """

            podman = kwargs.get("podman")

            if podman is None:
                raise RuntimeError("Podman context not ready")

            del kwargs["podman"]

            return f(podman=podman, *args, **kwargs)

        return decorator
