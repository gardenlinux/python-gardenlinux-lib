# -*- coding: utf-8 -*-

import subprocess
import json
import base64

from ..logger import LoggerSetup


class GitHub(object):
    """
    GitHub operations handler using GitHub CLI.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      0.9.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, owner="gardenlinux", repo="gardenlinux", logger=None):
        """
        Constructor __init__(GitHub)

        :param owner: GitHub repository owner
        :param repo: GitHub repository name
        :param logger: Logger instance

        :since: 0.9.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.github")

        self._owner = owner
        self._repo = repo
        self._logger = logger

        self._logger.debug(f"GitHub initialized for {owner}/{repo}")

    def api(self, endpoint, **kwargs):
        """
        Execute a GitHub API call using gh cli.

        :param endpoint: GitHub API endpoint (e.g. "/repos/owner/repo/contents/file.yaml")
        :param kwargs: Additional parameters for the API call

        :return: (dict) Parsed JSON response
        :since: 0.9.0
        """

        command = ["gh", "api", endpoint]

        # Add any additional parameters to the command
        for key, value in kwargs.items():
            if key.startswith("--"):
                command.extend([key, str(value)])
            else:
                command.extend([f"--{key}", str(value)])

        self._logger.debug(f"Executing GitHub API call: {' '.join(command)}")

        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
            )

            return json.loads(result.stdout)

        except subprocess.CalledProcessError as e:
            self._logger.error(f"GitHub API call failed: {e.stderr}")
            raise RuntimeError(
                f"GitHub API call failed for endpoint {endpoint}: {e.stderr}"
            )
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to parse GitHub API response: {e}")
            raise RuntimeError(f"Failed to parse GitHub API response: {e}")

    def get_file_content(self, file_path, ref=None):
        """
        Get file content from GitHub repository.

        :param file_path: Path to file in repository (e.g. "flavors.yaml")
        :param ref: Git reference (commit, branch, tag). If None, uses default branch

        :return: (str) File content
        :since: 0.9.0
        """

        endpoint = f"/repos/{self._owner}/{self._repo}/contents/{file_path}"

        # Add ref parameter if specified
        if ref is not None:
            endpoint = f"{endpoint}?ref={ref}"

        self._logger.debug(
            f"Fetching file content: {file_path} (ref: {ref or 'default'})"
        )

        try:
            response = self.api(endpoint)

            # Decode base64 content
            content = base64.b64decode(response["content"]).decode("utf-8")

            self._logger.debug(
                f"Successfully fetched {len(content)} characters from {file_path}"
            )

            return content

        except Exception as e:
            self._logger.error(f"Failed to fetch file content for {file_path}: {e}")
            raise RuntimeError(f"Failed to fetch file content for {file_path}: {e}")

    def get_flavors_yaml(self, commit="latest"):
        """
        Get flavors.yaml content from the repository.

        :param commit: Commit hash or "latest" for default branch

        :return: (str) flavors.yaml content
        :since: 0.9.0
        """

        ref = None if commit == "latest" else commit
        commit_short = commit if commit == "latest" else commit[:8]

        self._logger.debug(f"Fetching flavors.yaml for commit {commit_short}")

        try:
            content = self.get_file_content("flavors.yaml", ref=ref)
            self._logger.debug(
                f"Successfully fetched flavors.yaml for commit {commit_short}"
            )
            return content

        except Exception as e:
            self._logger.error(
                f"Failed to fetch flavors.yaml for commit {commit_short}: {e}"
            )
            raise RuntimeError(
                f"Failed to fetch flavors.yaml for commit {commit_short}: {e}"
            )

    @property
    def repository_url(self):
        """
        Returns the GitHub repository URL.

        :return: (str) GitHub repository URL
        :since: 0.9.0
        """

        return f"https://github.com/{self._owner}/{self._repo}"

    @property
    def api_url(self):
        """
        Returns the GitHub API base URL for this repository.

        :return: (str) GitHub API base URL
        :since: 0.9.0
        """

        return f"https://api.github.com/repos/{self._owner}/{self._repo}"
