# -*- coding: utf-8 -*-

"""
diff-files parser to merge several results into groups
"""

import logging
import os
import re
from os import PathLike
from pathlib import Path
from typing import Dict, Optional

import networkx as nx

from gardenlinux.features.parser import Parser


class DiffParser(object):
    """
    This class takes the differ_files results from the reproducibility check and detects problems
    It also analyzes the features of the affected cnames

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

        self.all_cnames: set[str] = set()
        self.reproducible_cnames: set[str] = set()
        self.passed_by_whitelist: set[str] = set()
        self.expected_cnames: set[str] = set()
        self.missing_cnames: set[str] = set()
        self.unexpected_cnames: set[str] = set()

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
        cnames_matrix: Dict[str, list[Dict[str, str]]],
        bare_cnames_matrix: Dict[str, list[Dict[str, str]]],
        diff_dir: PathLike[str] = Path("diffs"),
    ) -> None:
        """
        Parses a diff result and sets the corresponding attributes

        :param cnames_matrix:          The cnames matrix to identify missing diff files
        :param bare_cnames_matrix:     The bare cnames matrix to identify missing diff files
        :param diff_dir:                Directory containing the diff files

        :since:  1.0.0
        """

        self.all_cnames = set()
        self.reproducible_cnames = set()
        self.passed_by_whitelist = set()
        non_reproducible_cnames = {}  # {cname: [files...]}

        diff_dir = Path(self._gardenlinux_root).joinpath(diff_dir)

        self.expected_cnames = {
            f"{variant['cname']}-{variant['arch']}"
            for variant in (cnames_matrix["include"] + bare_cnames_matrix["include"])
        }

        for cname in os.listdir(diff_dir):
            if cname.endswith(self._SUFFIX):
                with open(diff_dir.joinpath(cname), "r") as f:
                    content = f.read()

                cname = cname.rstrip(self._SUFFIX)
                self.all_cnames.add(cname)
                if content == "":
                    self.reproducible_cnames.add(cname)
                elif content == "whitelist\n":
                    self.reproducible_cnames.add(cname)
                    self.passed_by_whitelist.add(cname)
                else:
                    non_reproducible_cnames[cname] = content.split("\n")[:-1]

        self.missing_cnames = self.expected_cnames - self.all_cnames
        self.unexpected_cnames = self.all_cnames - self.expected_cnames

        # Map files to cnames
        affected_cnames: Dict[str, set[str]] = {}  # {file: {cnames...}}
        for cname in non_reproducible_cnames:
            for file in non_reproducible_cnames[cname]:
                if file not in affected_cnames:
                    affected_cnames[file] = set()
                affected_cnames[file].add(cname)

        # Merge files affected_cnames by the same cnames by mapping cname sets to files
        self._bundled: Dict[frozenset[str], set[str]] = {}  # {{cnames...}: {files...}}
        for file in affected_cnames:
            if frozenset(affected_cnames[file]) not in self._bundled:
                self._bundled[frozenset(affected_cnames[file])] = set()
            self._bundled[frozenset(affected_cnames[file])].add(file)

    def intersectionTrees(
        self,
    ) -> Dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]:
        """
        Intersects all features of the affected cnames and removes all features from unaffected cnames to identify features causing the issue

        :return: (Dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]) Dict in the form of {{files...}: ({cnames..., intersectionTree})}
        :since:  1.0.0
        """

        # Compute the intersecting features of the affected cnames and store them in a graph to allow hierarchical formatting
        trees = {}
        for cnames in self._bundled:
            tree = None
            # Compute the intersecting features of all affected cnames
            for cname in cnames:
                # Ignore bare cnames, as they may not be affected due to removing the file and could therefore disrupt the analysis
                if not cname.startswith("bare-"):
                    # Compute intersecting features
                    tree = self._parser.filter(
                        self._remove_arch.sub("", cname),
                        additional_filter_func=tree.__contains__
                        if tree is not None
                        else lambda _: True,
                    )

            # Remove any features which are contained in unaffected cnames, as they cannot cause the problem
            if tree is not None:
                # Unfreeze tree
                tree = nx.DiGraph(tree)
                unaffected = self.all_cnames - cnames
                merged_features: set[str] = set()
                for cname in unaffected:
                    # Again, ignore bare cnames
                    if not cname.startswith("bare-"):
                        merged_features.update(
                            self._parser.filter(self._remove_arch.sub("", cname))
                        )
                tree.remove_nodes_from(n for n in merged_features)
            else:
                tree = nx.DiGraph()

            trees[frozenset(self._bundled[cnames])] = (cnames, tree)

        return trees
