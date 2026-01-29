# -*- coding: utf-8 -*-

"""
diff-files parser to merge several results into groups
"""

import logging
import os
import re
from os import PathLike
from pathlib import Path
from typing import Any, Optional

import networkx as nx

from gardenlinux.features.parser import Parser


class DiffParser(object):
    """
    This class takes the differ_files results from the reproducibility check and detects problems
    It also analyzes the features of the affected flavors

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    _remove_arch = re.compile("(-arm64|-amd64)$")
    _GARDENLINUX_ROOT: str = os.getenv("GL_ROOT_DIR", ".")
    _SUFFIX = "-diff.txt"

    def __init__(
        self,
        gardenlinux_root: Optional[str] = None,
        feature_dir_name: str = "features",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(DiffParser)

        :param gardenlinux_root:        GardenLinux root directory
        :param feature_dir_name:        Name of the features directory
        :param logger:                  Logger instance

        :since: 1.0.0
        """

        if gardenlinux_root is None:
            gardenlinux_root = self._GARDENLINUX_ROOT
        self._gardenlinux_root = gardenlinux_root
        self._parser = Parser(gardenlinux_root, feature_dir_name, logger)
        self._feature_dir_name = Path(self._gardenlinux_root).joinpath(feature_dir_name)

        self.all = set()
        self.successful = []
        self.whitelist = []
        self.expected_falvors = set()
        self.missing_flavors = set()
        self.unexpected_falvors = set()

    def read_feature_info(self, feature: str) -> dict[str, Any]:
        """
        Read the content of the feature info.yaml

        :param feature:                 The queried feature

        :return: dict[str, Any]         Parsed content of the features' info.yaml file
        :since: 1.0.0
        """
        return self._parser.read_feature_yaml(
            self._feature_dir_name.joinpath(f"{feature}/info.yaml")
        )["content"]

    def parse(
        self,
        flavors_matrix: dict[str, list[dict[str, str]]],
        bare_flavors_matrix: dict[str, list[dict[str, str]]],
        diff_dir: PathLike[str] = Path("diffs"),
    ) -> None:
        """
        Parses a diff result and sets the corresponding attributes

        :param flavors_matrix:          The flavors matrix to identify missing diff files
        :param bare_flavors_matrix:     The bare flavors matrix to identify missing diff files
        :param diff_dir:                Directory containing the diff files

        :since:  1.0.0
        """

        self.all = set()
        self.successful = []
        self.whitelist = []
        failed = {}  # {flavor: [files...]}

        diff_dir = Path(self._gardenlinux_root).joinpath(diff_dir)

        self.expected_falvors = set(
            [
                f"{variant['flavor']}-{variant['arch']}"
                for variant in (
                    flavors_matrix["include"] + bare_flavors_matrix["include"]
                )
            ]
        )

        for flavor in os.listdir(diff_dir):
            if flavor.endswith(self._SUFFIX):
                with open(diff_dir.joinpath(flavor), "r") as f:
                    content = f.read()

                flavor = flavor.rstrip(self._SUFFIX)
                self.all.add(flavor)
                if content == "":
                    self.successful.append(flavor)
                elif content == "whitelist\n":
                    self.successful.append(flavor)
                    self.whitelist.append(flavor)
                else:
                    failed[flavor] = content.split("\n")[:-1]

        self.missing_flavors = self.expected_falvors - self.all
        self.unexpected_falvors = self.all - self.expected_falvors

        # Map files to flavors
        affected: dict[str, set[str]] = {}  # {file: {flavors...}}
        for flavor in failed:
            for file in failed[flavor]:
                if file not in affected:
                    affected[file] = set()
                affected[file].add(flavor)

        # Merge files affected by the same flavors by mapping flavor sets to files
        self._bundled: dict[frozenset[str], set[str]] = {}  # {{flavors...}: {files...}}
        for file in affected:
            if frozenset(affected[file]) not in self._bundled:
                self._bundled[frozenset(affected[file])] = set()
            self._bundled[frozenset(affected[file])].add(file)

    def intersectionTrees(
        self,
    ) -> dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]:
        """
        Intersects all features of the affected flavors and removes all features from unaffected flavors to identify features causing the issue

        :return: (dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]) Dict in the form of {{files...}: ({flavors..., intersectionTree})}
        :since:  1.0.0
        """

        # Compute the intersecting features of the affected flavors and store them in a graph to allow hierarchical formatting
        trees = {}
        for flavors in self._bundled:
            first = True
            tree = None
            # Compute the intersecting features of all affected flavors
            for flavor in flavors:
                # Ignore bare flavors, as they may not be affected due to removing the file and could therefore disrupt the analysis
                if not flavor.startswith("bare-"):
                    t = self._parser.filter(self._remove_arch.sub("", flavor))
                    if first:
                        first = False
                        tree = t
                    else:
                        tree = nx.intersection(tree, t)

            # Remove any features which are contained in unaffected flavors, as they cannot cause the problem
            if tree is not None:
                unaffected = self.all - flavors
                for flavor in unaffected:
                    # Again, ignore bare flavors
                    if not flavor.startswith("bare-"):
                        t = self._parser.filter(self._remove_arch.sub("", flavor))
                        tree.remove_nodes_from(n for n in t)
            else:
                tree = nx.DiGraph()

            trees[frozenset(self._bundled[flavors])] = (flavors, tree)

        return trees
