# -*- coding: utf-8 -*-

"""
diff files Markdown generator for reproducibility checker workflow
"""

import logging
import os
import pathlib
import re
from os import PathLike
from typing import Collection, Optional

import networkx as nx
import yaml
from attr import dataclass
from networkx.algorithms.traversal.depth_first_search import dfs_tree

from gardenlinux.features.parser import Parser


@dataclass
class Nightly:
    run_number: str
    id: str
    commit: str


class Formatter(object):
    """
    This class takes the differ_files results from the reproducibility check and generates a Result.md
    The differ_files contain paths of files which were different when building the flavor two times

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2025 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    remove_arch = re.compile("(-arm64|-amd64)$")

    def __init__(
        self,
        flavors_matrix: dict[str, list[dict[str, str]]],
        bare_flavors_matrix: dict[str, list[dict[str, str]]],
        diff_dir: PathLike[str] = pathlib.Path("diffs"),
        nightly_stats: PathLike[str] = pathlib.Path("nightly_stats"),
        gardenlinux_root: Optional[str] = None,
        feature_dir_name: str = "features",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(Formatter)

        :param flavors_matrix:          The flavors matrix to identify missing diff files
        :param bare_flavors_matrix:     The bare flavors matrix to identify missing diff files
        :param diff_dir:                Directory containing the diff files
        :param nightly_stats:           File containing infos about nightly runs
        :param gardenlinux_root:        GardenLinux root directory
        :param feature_dir_name:        Name of the features directory
        :param logger:                  Logger instance

        :since: 1.0.0
        """

        self._parser = Parser(gardenlinux_root, feature_dir_name, logger)
        if gardenlinux_root is None:
            gardenlinux_root = self._parser._GARDENLINUX_ROOT
        diff_dir = pathlib.Path(gardenlinux_root).joinpath(diff_dir)

        self._all = set()
        self._flavors = os.listdir(diff_dir)
        self._nightly_stats = pathlib.Path(nightly_stats)
        self._feature_dir_name = feature_dir_name

        self._successful = []
        self._whitelist = []
        failed = {}  # {flavor: [files...]}

        self._expected_falvors = set(
            [
                f"{variant['flavor']}-{variant['arch']}"
                for variant in (
                    flavors_matrix["include"] + bare_flavors_matrix["include"]
                )
            ]
        )

        for flavor in self._flavors:
            if flavor.endswith("-diff"):
                with open(diff_dir.joinpath(flavor), "r") as f:
                    content = f.read()

                flavor = flavor[:-5]
                self._all.add(flavor)
                if content == "":
                    self._successful.append(flavor)
                elif content == "whitelist\n":
                    self._successful.append(flavor)
                    self._whitelist.append(flavor)
                else:
                    failed[flavor] = content.split("\n")[:-1]

        self._missing_flavors = self._expected_falvors - self._all
        self._unexpected_falvors = self._all - self._expected_falvors

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

    def _node_key(self, node: str) -> str:
        """
        Key order function to sort platforms before elements, platforms before flags and elements before flags

        :param node:                    The node name (can be any of platform, element or flag)

        :return: ("1-" || "2-" || "2-") + node
        :since:  1.0.0
        """

        with open(
            self._parser._feature_base_dir.joinpath(f"{node}/info.yaml"), "r"
        ) as f:
            info = yaml.safe_load(f.read())
        if info["type"] == "platform":
            return "1-" + node
        elif info["type"] == "element":
            return "2-" + node
        else:
            return "3-" + node

    def _generateIntersectionTrees(
        self,
    ) -> dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]:
        """
        Intersects all features of the affected flavors and removes all features from unaffected flavors to identify features causing the issue

        :return: (dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]) Dict in the form of {{files...}: ({flavors..., intersectionTree})}
        :since:  1.0.0
        """

        trees = {}
        for flavors in self._bundled:
            first = True
            tree = None
            for flavor in flavors:
                if not flavor.startswith("bare-"):
                    t = self._parser.filter(self.remove_arch.sub("", flavor))
                    if first:
                        first = False
                        tree = t
                    else:
                        tree = nx.intersection(tree, t)

            if tree is not None:
                unaffected = self._all - flavors
                for flavor in unaffected:
                    if not flavor.startswith("bare-"):
                        t = self._parser.filter(self.remove_arch.sub("", flavor))
                        tree.remove_nodes_from(n for n in t)
            else:
                tree = nx.DiGraph()

            trees[frozenset(self._bundled[flavors])] = (flavors, tree)

        return trees

    def _treeStr(
        self, graph: nx.DiGraph, found: Optional[set[str]] = None
    ) -> tuple[str, set[str]]:
        """
        Returns a string representation of the graph containg each node exactly once

        :param graph:                  Graph to be converted
        :param found:                  Nodes excluded for further rendering

        :return: (str) Graph as string
        :since:  1.0.0
        """

        if found is None:
            found = set()

        s = ""
        for node in sorted(graph, key=self._node_key):
            if node not in found and len(list(graph.predecessors(node))) == 0:
                found.add(node)
                if len(set(graph.successors(node)) - found) == 0:
                    s += str(node) + "\n"
                else:
                    s += str(node) + ":\n"
                    for successor in sorted(
                        set(graph.successors(node)) - found, key=self._node_key
                    ):
                        st, fnd = self._treeStr(dfs_tree(graph, successor), found)
                        found.update(fnd)
                        s += "  " + st.replace("\n", "\n  ") + "\n"
        # Remove last linebreak as the last line can contain spaces
        return "\n".join(s.split("\n")[:-1]), found

    @staticmethod
    def _dropdown(items: Collection[str]) -> str:
        """
        Converts the items into a markdown dropwon list if the length is 10 or more

        :param items:                  List of items

        :return: (str) List or dropown
        :since:  1.0.0
        """

        if len(items) <= 10:
            return "<br>".join([f"`{item}`" for item in sorted(items)])
        else:
            for first in sorted(items):
                return (
                    f"<details><summary>{first}...</summary>"
                    + "<br>".join([f"`{item}`" for item in sorted(items)])
                    + "</details>"
                )
            return ""

    def __str__(self) -> str:
        """
        Returns final markdown for the configured reproducibility check

        :return: (str) Markdown
        :since:  1.0.0
        """
        trees = self._generateIntersectionTrees()

        result = """# Reproducibility Test Results

{emoji} **{successrate}%** of **{total_count}** tested flavors were reproducible.{problem_count}

## Detailed Result{explanation}

| Affected Files | Flavors | Features Causing the Problem |
|----------------|---------|------------------------------|
{rows}"""

        successrate = round(
            100 * (len(self._successful) / len(self._expected_falvors)), 1
        )

        emoji = (
            "✅"
            if len(self._expected_falvors) == len(self._successful)
            else ("⚠️" if successrate >= 50.0 else "❌")
        )

        total_count = len(self._expected_falvors)

        problem_count = (
            ""
            if len(trees) == 0
            else (
                "\n**1** Problem detected."
                if len(trees) == 1
                else f"\n**{len(trees)}** Problems detected."
            )
        )

        explanation = ""

        if self._nightly_stats.is_file():
            with open(self._nightly_stats, "r") as f:
                nightly_a, nightly_b = (
                    Nightly(*n.split(",")) for n in f.read().rstrip().split(";")
                )
            if nightly_a.run_number != "":
                explanation += f"\n\nComparison of nightly **[#{nightly_a.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_a.id})** \
and **[#{nightly_b.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_b.id})**"
                if nightly_a.commit != nightly_b.commit:
                    explanation += f"\n\n⚠️ The nightlies used different commits: `{nightly_a.commit[:7]}` (#{nightly_a.run_number}) != `{nightly_b.commit[:7]}` (#{nightly_b.run_number})"
                if nightly_a.run_number == nightly_b.run_number:
                    explanation += f"\n\n⚠️ Comparing the nightly **[#{nightly_a.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_a.id})** to itself can not reveal any issues"
            else:
                explanation += f"\n\nComparison of the latest nightly **[#{nightly_b.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_b.id})** \
with a new build"
                if nightly_a.commit != nightly_b.commit:
                    explanation += f"\n\n⚠️ The build used different commits: `{nightly_b.commit[:7]}` (#{nightly_b.run_number}) != `{nightly_a.commit[:7]}` (new build)"

        if len(self._whitelist) > 0:
            explanation += (
                "\n\n<details><summary>📃 These flavors only passed due to the nightly whitelist</summary><pre>"
                + "<br>".join(sorted(self._whitelist))
                + "</pre></details>"
            )

        if len(self._unexpected_falvors) > 0:
            # This should never happen, but print a warning if it somehow does
            explanation += (
                "\n\n<details><summary>⁉️ These flavors were not expected to appear in the results, please check for errors in the workflow\
</summary><pre>"
                + "<br>".join(sorted(self._unexpected_falvors))
                + "</pre></details>"
            )

        explanation += (
            ""
            if len(self._expected_falvors) <= len(self._successful)
            else "\n\n*The mentioned features are included in every affected flavor and not included in every unaffected flavor.*"
        )

        rows = ""

        if len(self._missing_flavors) > 0:
            row = "|❌ Workflow run did not produce any results|"
            row += f"**{round(100 * (len(self._missing_flavors) / len(self._expected_falvors)), 1)}%** affected<br>"
            row += self._dropdown(self._missing_flavors)
            row += "|No analysis available|\n"
            rows += row

        # Sort the problems by affected flavors in descending order and by files names for problems with the same number of affected flavors
        # to get a derterministic ordering for testing
        def sorting_function(files: frozenset[str]) -> tuple[int, str]:
            return (-len(trees[files][0]), ",".join(sorted(files)))

        for files in sorted(trees, key=sorting_function):
            flavors, tree = trees[files]
            row = "|"
            row += self._dropdown(files)
            row += "|"
            row += f"**{round(100 * (len(flavors) / len(self._expected_falvors)), 1)}%** affected<br>"
            row += self._dropdown(flavors)
            row += "|"
            if len(tree) == 0:
                row += "No analysis available"
            else:
                row += "<pre>" + self._treeStr(tree)[0].replace("\n", "<br>") + "</pre>"
            row += "|\n"
            rows += row

        if len(self._successful) > 0:
            # Success row
            row = "|"
            row += "✅ No problems found"
            row += "|"
            row += f"**{round(100 * (len(self._successful) / len(self._expected_falvors)), 1)}%**<br>"
            row += self._dropdown(self._successful)
            row += "|"
            row += "-"
            row += "|\n"
            rows += row

        if len(self._successful) < len(self._expected_falvors):
            rows += "\n*To add affected files to the whitelist, edit the `whitelist` variable in `.github/workflows/generate_diff.sh`*\n"

        return result.format(
            emoji=emoji,
            successrate=successrate,
            total_count=total_count,
            problem_count=problem_count,
            explanation=explanation,
            rows=rows,
        )
