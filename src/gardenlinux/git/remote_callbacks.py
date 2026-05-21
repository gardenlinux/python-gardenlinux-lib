# -*- coding: utf-8 -*-

"""
Git credentials provider
"""

from typing import Any, Optional

from pygit2 import KeypairFromAgent
from pygit2 import RemoteCallbacks as _RemoteCallbacks
from pygit2 import UserPass
from pygit2.enums import CredentialType


class RemoteCallbacks(_RemoteCallbacks):  # type: ignore[misc]
    """
    pygit2.org: Base class for pygit2 remote callbacks.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: git
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        *args: Any,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ):
        """
        Constructor __init__(RemoteCallbacks)

        :param token: GitHub/Git access token for HTTPS authentication.
                      Falls back to the GITHUB_TOKEN environment variable if not provided.

        :since: 1.0.0
        """

        self._username = ""
        self._password = ""

        if username and password:
            self._username = username
            self._password = password

    def credentials(
        self,
        url: str,
        username_from_url: Optional[str],
        allowed_types: CredentialType,
    ) -> Optional[UserPass | KeypairFromAgent]:
        """
        pygit2.org: Credentials callback. If the remote server requires
        authentication, this function will be called and its return value
        used for authentication.

                :param url: The URL being accessed (after any insteadOf rewrites)
                :param username_from_url: Username extracted from the URL, if any
                :param allowed_types: Bitmask of credential types the server accepts

                :return: A pygit2 credential object
                :since:  1.0.0
        """

        if allowed_types & CredentialType.USERPASS_PLAINTEXT:
            if self._password:
                return UserPass(self._username, self._password)

        if allowed_types & CredentialType.SSH_KEY:
            return KeypairFromAgent(username_from_url or "git")

        return _RemoteCallbacks.credentials(url, username_from_url, allowed_types)
