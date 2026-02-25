# -*- coding: utf-8 -*-

"""
diff-files parser to merge several results into groups
"""

import logging
import os
import re
from os import PathLike
from pathlib import Path
from typing import Any, Dict, Optional

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

        self.all_flavors: set[str] = set()
        self.reproducible_flavors: set[str] = set()
        self.passed_by_whitelist: set[str] = set()
        self.expected_falvors: set[str] = set()
        self.missing_flavors: set[str] = set()
        self.unexpected_falvors: set[str] = set()

    def sort_features(self, graph: nx.DiGraph) -> list[str]:
        """
        Forward sorting implemented in the parser

        :param graph:                   The feature graph

        :return: list[str]              Sorted features considering the type
        :since: 1.0.0
        """
        return self._parser.sort_graph_nodes(graph)

    def parse(
        self,
        flavors_matrix: Dict[str, list[Dict[str, str]]],
        bare_flavors_matrix: Dict[str, list[Dict[str, str]]],
        diff_dir: PathLike[str] = Path("diffs"),
    ) -> None:
        """
        Parses a diff result and sets the corresponding attributes

        :param flavors_matrix:          The flavors matrix to identify missing diff files
        :param bare_flavors_matrix:     The bare flavors matrix to identify missing diff files
        :param diff_dir:                Directory containing the diff files

        :since:  1.0.0
        """

        self.all_flavors = set()
        self.reproducible_flavors = set()
        self.passed_by_whitelist = set()
        non_reproducible_flavors = {}  # {flavor: [files...]}

        diff_dir = Path(self._gardenlinux_root).joinpath(diff_dir)

        self.expected_falvors = {
            f"{variant['flavor']}-{variant['arch']}"
            for variant in (flavors_matrix["include"] + bare_flavors_matrix["include"])
        }

        for flavor in os.listdir(diff_dir):
            if flavor.endswith(self._SUFFIX):
                with open(diff_dir.joinpath(flavor), "r") as f:
                    content = f.read()

                flavor = flavor.rstrip(self._SUFFIX)
                self.all_flavors.add(flavor)
                if content == "":
                    self.reproducible_flavors.add(flavor)
                elif content == "whitelist\n":
                    self.reproducible_flavors.add(flavor)
                    self.passed_by_whitelist.add(flavor)
                else:
                    non_reproducible_flavors[flavor] = content.split("\n")[:-1]

        self.missing_flavors = self.expected_falvors - self.all_flavors
        self.unexpected_falvors = self.all_flavors - self.expected_falvors

        # Map files to flavors
        affected_flavors: Dict[str, set[str]] = {}  # {file: {flavors...}}
        for flavor in non_reproducible_flavors:
            for file in non_reproducible_flavors[flavor]:
                if file not in affected_flavors:
                    affected_flavors[file] = set()
                affected_flavors[file].add(flavor)

        # Merge files affected_flavors by the same flavors by mapping flavor sets to files
        self._bundled: Dict[frozenset[str], set[str]] = {}  # {{flavors...}: {files...}}
        for file in affected_flavors:
            if frozenset(affected_flavors[file]) not in self._bundled:
                self._bundled[frozenset(affected_flavors[file])] = set()
            self._bundled[frozenset(affected_flavors[file])].add(file)

    def intersectionTrees(
        self,
    ) -> Dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]:
        """
        Intersects all features of the affected flavors and removes all features from unaffected flavors to identify features causing the issue

        :return: (Dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]) Dict in the form of {{files...}: ({flavors..., intersectionTree})}
        :since:  1.0.0
        """

        # Compute the intersecting features of the affected flavors and store them in a graph to allow hierarchical formatting
        trees = {}
        for flavors in self._bundled:
            tree = None
            # Compute the intersecting features of all affected flavors
            for flavor in flavors:
                # Ignore bare flavors, as they may not be affected due to removing the file and could therefore disrupt the analysis
                if not flavor.startswith("bare-"):
                    # Compute intersecting features
                    tree = self._parser.filter(
                        self._remove_arch.sub("", flavor),
                        additional_filter_func=tree.__contains__
                        if tree is not None
                        else lambda _: True,
                    )

            # Remove any features which are contained in unaffected flavors, as they cannot cause the problem
            if tree is not None:
                # Unfreeze tree
                tree = nx.DiGraph(tree)
                unaffected = self.all_flavors - flavors
                merged_features: set[str] = set()
                for flavor in unaffected:
                    # Again, ignore bare flavors
                    if not flavor.startswith("bare-"):
                        merged_features.update(
                            self._parser.filter(self._remove_arch.sub("", flavor))
                        )
                tree.remove_nodes_from(n for n in merged_features)
            else:
                tree = nx.DiGraph()

            trees[frozenset(self._bundled[flavors])] = (flavors, tree)

        return trees
