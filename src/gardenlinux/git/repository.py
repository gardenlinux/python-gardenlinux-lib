# -*- coding: utf-8 -*-

from logging import Logger
from os import PathLike
from pathlib import Path
from typing import Any, List, Optional

from pygit2 import Oid
from pygit2 import Repository as _Repository
from pygit2 import init_repository

from ..constants import GL_REPOSITORY_URL
from ..logger import LoggerSetup


class Repository(_Repository):  # type: ignore[misc]
    """
    Repository operations handler based on the given Git directory.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: git
    :since:      0.10.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        git_directory: PathLike[str] | str = ".",
        logger: Optional[Logger] = None,
        **kwargs: Any,
    ):
        """
        Constructor __init__(Repository)

        :param git_directory: Git directory
        :param logger: Logger instance

        :since: 0.10.0
        """

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.git")

        git_directory = Path(git_directory)

        if not git_directory.exists():
            raise RuntimeError(f"Git directory given is invalid: {git_directory}")

        _Repository.__init__(self, git_directory, **kwargs)

        self._git_directory = git_directory
        self._logger = logger

    @property
    def commit_id(self) -> str:
        """
        Returns the commit ID for Git `HEAD`.

        :return: (str) Git commit ID
        :since:  0.10.0
        """

        return str(self.root_repo.head.target)

    @property
    def root(self) -> Path:
        """
        Returns the root directory of the current Git repository.

        :return: (object) Git root directory
        :since:  0.10.0
        """

        root_dir: Path = Path(self.workdir)

        if self.is_bare:
            root_dir = Path(self.path)

        usual_git_dir = root_dir / ".git"

        # Possible submodule Git repository. Validate repository containing `.git` directory.
        if self.path != str(usual_git_dir):
            try:
                repo = Repository(usual_git_dir, self._logger)

                if self.path != repo.path:
                    root_dir = repo.root
            except Exception as exc:
                self._logger.warning(f"Failed to inspect Git directory: {exc}")

        self._logger.debug(f"Git root directory: {root_dir}")
        return Path(root_dir)

    @property
    def root_repo(self) -> Any:
        """
        Returns the root Git `Repository` instance.

        :return: (object) Git root `Repository` instance
        :since:  0.10.0
        """

        repo = self

        if self._git_directory != self.root:
            repo = Repository(self.root, self._logger)

        return repo

    @staticmethod
    def checkout_repo(
        git_directory: PathLike[str] | str,
        repo_url: str = GL_REPOSITORY_URL,
        branch: str = "main",
        commit: Optional[str] = None,
        pathspecs: Optional[List[str]] = None,
        logger: Optional[Logger] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Returns the root Git `Repo` instance.

        :return: (object) Git `Repo` instance
        :since:  0.10.0
        """

        git_directory = Path(git_directory)

        if not git_directory.is_dir() or git_directory.match("/*"):
            raise RuntimeError(
                "Git directory should not exist or be empty before checkout"
            )

        repo = init_repository(git_directory, origin_url=repo_url)
        repo.remotes["origin"].fetch()

        if commit is None:
            refish = f"origin/{branch}"
            resolved = repo.resolve_refish(refish)
            commit = str(resolved[0].id)

        checkout_tree_kwargs = kwargs
        if pathspecs is not None:
            checkout_tree_kwargs["paths"] = pathspecs

        repo.checkout_tree(repo[Oid(hex=commit)], **checkout_tree_kwargs)

        return Repository(git_directory, logger)

    @staticmethod
    def checkout_repo_sparse(
        git_directory: PathLike[str] | str,
        pathspecs: List[str] = [],
        repo_url: str = GL_REPOSITORY_URL,
        branch: str = "main",
        commit: Optional[str] = None,
        logger: Optional[Logger] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Sparse checkout given Git repository and return the `Repository` instance.

        :return: (object) Git `Repository` instance
        :since:  0.10.0
        """

        # @TODO: pygit2 does not support sparse checkouts. We use the `paths` parameter at the moment.
        return Repository.checkout_repo(
            git_directory,
            repo_url=repo_url,
            branch=branch,
            commit=commit,
            pathspecs=pathspecs,
            logger=logger,
        )
