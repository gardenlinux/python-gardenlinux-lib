# -*- coding: utf-8 -*-

"""
diff-files markdown generator for reproducibility test workflow
"""

import logging
from os import PathLike
from pathlib import Path
from typing import Collection, Optional

import networkx as nx
from attr import dataclass
from networkx.algorithms.traversal.depth_first_search import dfs_tree

from gardenlinux.features.reproducibility.diff_parser import DiffParser


@dataclass
class Nightly:
    run_number: str
    id: str
    commit: str


class MarkdownFormatter(object):
    """
    This class takes the diff-files results from the reproducibility check and generates a markdown of the result
    The diff-files contain paths of files which were different when building the flavor two times
    They can be generated using the Comparator class

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2026 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    _DROPDOWN_THRESHOLD = 10

    def __init__(
        self,
        flavors_matrix: dict[str, list[dict[str, str]]],
        bare_flavors_matrix: dict[str, list[dict[str, str]]],
        diff_dir: PathLike[str] = Path("diffs"),
        nightly_stats: PathLike[str] = Path("nightly_stats.csv"),
        gardenlinux_root: Optional[str] = None,
        feature_dir_name: str = "features",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(MarkdownFormatter)

        :param flavors_matrix:          The flavors matrix to identify missing diff files
        :param bare_flavors_matrix:     The bare flavors matrix to identify missing diff files
        :param diff_dir:                Directory containing the diff-files
        :param nightly_stats:           File containing infos about nightly runs
        :param gardenlinux_root:        GardenLinux root directory
        :param feature_dir_name:        Name of the features directory
        :param logger:                  Logger instance

        :since: 1.0.0
        """

        self._diff_parser = DiffParser(gardenlinux_root, feature_dir_name, logger)
        self._diff_parser.parse(flavors_matrix, bare_flavors_matrix, diff_dir)

        self._nightly_stats = Path(nightly_stats)

    def _node_key(self, node: str) -> str:
        """
        Key order function to sort platforms before elements, platforms before flags and elements before flags

        :param node:                    The node name (can be any of platform, element or flag)

        :return: ("1-" || "2-" || "2-") + node
        :since:  1.0.0
        """

        info = self._diff_parser.read_feature_info(node)
        if info["type"] == "platform":
            return "1-" + node
        elif info["type"] == "element":
            return "2-" + node
        else:
            return "3-" + node

    def _treeStr(
        self, graph: nx.DiGraph, found: Optional[set[str]] = None
    ) -> tuple[str, set[str]]:
        """
        Returns a string representation of the graph containing each node exactly once

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
        return s.rstrip(), found

    def _dropdown(self, items: Collection[str]) -> str:
        """
        Converts the items into a markdown dropwon list if the length is 10 or more

        :param items:                  List of items

        :return: (str) List or dropown
        :since:  1.0.0
        """

        if len(items) <= self._DROPDOWN_THRESHOLD:
            return "<br>".join([f"`{item}`" for item in sorted(items)])
        else:
            for first in sorted(items):
                return (
                    f"<details><summary>{first}...</summary>"
                    + "<br>".join([f"`{item}`" for item in sorted(items)])
                    + "</details>"
                )
            return ""

    def _format_nighlty_stats(self) -> str:
        """
        Parses nightly_stats file and formats a human readable result

        :return: (str) Markdown
        :since:  1.0.0
        """

        result = ""

        with open(self._nightly_stats, "r") as f:
            nightly_a, nightly_b = (
                Nightly(*n.split(",")) for n in f.read().rstrip().split("\n")
            )
            if nightly_a.run_number != "":
                result += f"\n\nComparison of nightly **[#{nightly_a.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_a.id})** \
and **[#{nightly_b.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_b.id})**"
                if nightly_a.commit != nightly_b.commit:
                    result += f"\n\n⚠️ The nightlies used different commits: `{nightly_a.commit[:7]}` (#{nightly_a.run_number}) != `{nightly_b.commit[:7]}` (#{nightly_b.run_number})"
                if nightly_a.run_number == nightly_b.run_number:
                    result += f"\n\n⚠️ Comparing the nightly **[#{nightly_a.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_a.id})** to itself can not reveal any issues"
            else:
                result += f"\n\nComparison of the latest nightly **[#{nightly_b.run_number}](https://github.com/gardenlinux/gardenlinux/actions/runs/{nightly_b.id})** \
with a new build"
                if nightly_a.commit != nightly_b.commit:
                    result += f"\n\n⚠️ The build used different commits: `{nightly_b.commit[:7]}` (#{nightly_b.run_number}) != `{nightly_a.commit[:7]}` (new build)"

        return result

    def _header(
        self, trees: dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]
    ) -> str:
        """
        Formats general information about the test run

        :param trees:                   The generated trees

        :return: (str) Markdown
        :since:  1.0.0
        """

        header = """# Reproducibility Test Results

{emoji} **{successrate}%** of **{total_count}** tested flavors were reproducible.{problem_count}

## Detailed Result{explanation}

"""

        successrate = round(
            100 * (len(self._diff_parser.successful) / len(self._diff_parser.expected_falvors)), 1
        )

        emoji = (
            "✅"
            if len(self._diff_parser.expected_falvors)
            == len(self._diff_parser.successful)
            else ("⚠️" if successrate >= 50.0 else "❌")
        )

        total_count = len(self._diff_parser.expected_falvors)

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
            explanation += self._format_nighlty_stats()

        if len(self._diff_parser.whitelist) > 0:
            explanation += (
                "\n\n<details><summary>📃 These flavors only passed due to the nightly whitelist</summary><pre>"
                + "<br>".join(sorted(self._diff_parser.whitelist))
                + "</pre></details>"
            )

        if len(self._diff_parser.unexpected_falvors) > 0:
            # This should never happen, but print a warning if it somehow does
            explanation += (
                "\n\n<details><summary>⁉️ These flavors were not expected to appear in the results, please check for errors in the workflow\
</summary><pre>"
                + "<br>".join(sorted(self._diff_parser.unexpected_falvors))
                + "</pre></details>"
            )

        explanation += (
            ""
            if len(self._diff_parser.expected_falvors)
            <= len(self._diff_parser.successful)
            else "\n\n*The mentioned features are included in every affected flavor and not included in every unaffected flavor.*"
        )

        return header.format(
            emoji=emoji,
            successrate=successrate,
            total_count=total_count,
            problem_count=problem_count,
            explanation=explanation,
        )

    def _table(
        self, trees: dict[frozenset[str], tuple[frozenset[str], nx.DiGraph]]
    ) -> str:
        """
        Formats the trees into a table

        :param trees:                   The generated trees

        :return: (str) Markdown
        :since:  1.0.0
        """

        table = """| Affected Files | Flavors | Features Causing the Problem |
|----------------|---------|------------------------------|
{rows}"""

        rows = ""

        if len(self._diff_parser.missing_flavors) > 0:
            row = "|❌ Workflow run did not produce any results|"
            row += f"**{round(100 * (len(self._diff_parser.missing_flavors) / len(self._diff_parser.expected_falvors)), 1)}%** affected<br>"
            row += self._dropdown(self._diff_parser.missing_flavors)
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
            row += f"**{round(100 * (len(flavors) / len(self._diff_parser.expected_falvors)), 1)}%** affected<br>"
            row += self._dropdown(flavors)
            row += "|"
            if len(tree) == 0:
                row += "No analysis available"
            else:
                row += "<pre>" + self._treeStr(tree)[0].replace("\n", "<br>") + "</pre>"
            row += "|\n"
            rows += row

        if len(self._diff_parser.successful) > 0:
            # Success row
            row = "|"
            row += "✅ No problems found"
            row += "|"
            row += f"**{round(100 * (len(self._diff_parser.successful) / len(self._diff_parser.expected_falvors)), 1)}%**<br>"
            row += self._dropdown(self._diff_parser.successful)
            row += "|"
            row += "-"
            row += "|\n"
            rows += row

        if len(self._diff_parser.successful) < len(self._diff_parser.expected_falvors):
            rows += "\n*To add affected files to the whitelist, edit the `whitelist` variable in python-gardenlinux-lib `src/gardenlinux/features/reproducibility/comparator.py`*\n"

        return table.format(rows=rows)

    def __str__(self) -> str:
        """
        Returns final markdown for the configured reproducibility check

        :return: (str) Markdown
        :since:  1.0.0
        """

        trees = self._diff_parser.intersectionTrees()

        return self._header(trees) + self._table(trees)
