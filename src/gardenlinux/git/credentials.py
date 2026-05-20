# -*- coding: utf-8 -*-

"""
Git credentials provider
"""

import os
from typing import Optional, Union

from pygit2 import KeypairFromAgent, UserPass
from pygit2.enums import CredentialType


class Credentials:
    """
    Git credentials provider for pygit2 remote operations.

    Handles authentication dynamically based on the server's allowed credential
    types. This accounts for git config `url.<base>.insteadOf` rules that may
    rewrite HTTPS URLs to SSH at the libgit2 transport layer.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: git
    :since:      0.10.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, token: Optional[str] = None):
        """
        Constructor __init__(Credentials)

        :param token: GitHub/Git access token for HTTPS authentication.
                      Falls back to the GITHUB_TOKEN environment variable if not provided.

        :since: 0.10.0
        """

        self._token = token

        if self._token is None:
            self._token = os.environ.get("GITHUB_TOKEN")

    def __call__(
        self,
        url: str,
        username_from_url: Optional[str],
        allowed_types: CredentialType,
    ) -> Optional[Union[UserPass, KeypairFromAgent]]:
        """
        Pygit2 credentials callback.

        Called by libgit2 when authentication is required during remote
        operations. Returns the appropriate credential object based on what
        the server allows.

        :param url: The URL being accessed (after any insteadOf rewrites)
        :param username_from_url: Username extracted from the URL, if any
        :param allowed_types: Bitmask of credential types the server accepts

        :return: A pygit2 credential object, or None if no credentials available
        :since:  0.10.0
        """

        if allowed_types & CredentialType.USERPASS_PLAINTEXT:
            if self._token:
                return UserPass(self._token, "x-oauth-basic")

        if allowed_types & CredentialType.SSH_KEY:
            return KeypairFromAgent(username_from_url or "git")

        return None
