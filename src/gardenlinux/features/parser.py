# -*- coding: utf-8 -*-

"""
Features parser based on networkx.Digraph
"""

from glob import glob
from typing import Callable, Optional
import logging
import networkx
import os
import re
import subprocess
import yaml

from ..constants import (
    ARCHS,
    BARE_FLAVOR_FEATURE_CONTENT,
    BARE_FLAVOR_LIBC_FEATURE_CONTENT,
)

from ..logger import LoggerSetup


class Parser(object):
    """
    Parser for GardenLinux features.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: features
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    _GARDENLINUX_ROOT: str = "."
    """
    Default GardenLinux root directory
    """

    def __init__(
        self,
        gardenlinux_root: Optional[str] = None,
        feature_dir_name: Optional[str] = "features",
        logger: Optional[logging.Logger] = None,
    ):
        """
        Constructor __init__(Parser)

        :param gardenlinux_root: GardenLinux root directory
        :param feature_dir_name: Name of the features directory
        :param logger: Logger instance

        :since: 0.7.0
        """

        if gardenlinux_root is None:
            gardenlinux_root = Parser._GARDENLINUX_ROOT

        feature_base_dir = os.path.join(gardenlinux_root, feature_dir_name)

        if not os.access(feature_base_dir, os.R_OK):
            raise ValueError(
                "Feature directory given is invalid: {0}".format(feature_base_dir)
            )

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.features")

        self._feature_base_dir = feature_base_dir

        self._graph = None
        self._logger = logger

        self._logger.debug(
            "features.Parser initialized for directory: {0}".format(feature_base_dir)
        )

    @property
    def graph(self) -> networkx.Graph:
        """
        Returns the features graph based on the GardenLinux features directory.

        :return: (networkx.Graph) Features graph
        :since:  0.7.0
        """

        if self._graph is None:
            feature_yaml_files = glob("{0}/*/info.yaml".format(self._feature_base_dir))
            features = [self._read_feature_yaml(i) for i in feature_yaml_files]

            feature_graph = networkx.DiGraph()

            for feature in features:
                feature_graph.add_node(feature["name"], content=feature["content"])

            for node in feature_graph.nodes():
                node_features = self._get_node_features(feature_graph.nodes[node])

                for attr in node_features:
                    if attr not in ["include", "exclude"]:
                        continue

                    for ref in node_features[attr]:
                        if not os.path.isfile(
                            "{0}/{1}/info.yaml".format(self._feature_base_dir, ref)
                        ):
                            raise ValueError(
                                f"feature {node} references feature {ref}, but {feature_dir}/{ref}/info.yaml does not exist"
                            )

                        feature_graph.add_edge(node, ref, attr=attr)

            if not networkx.is_directed_acyclic_graph(feature_graph):
                raise ValueError("Graph is not directed acyclic graph")

            self._graph = feature_graph

        return self._graph

    def filter(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None,
    ) -> networkx.Graph:
        """
        Filters the features graph.

        :param cname:                  Canonical name to filter
        :param ignore_excludes:        Ignore `exclude` feature files
        :param additional_filter_func: Additional filter function

        :return: (networkx.Graph) Filtered features graph
        :since:  0.7.0
        """

        input_features = Parser.get_cname_as_feature_set(cname)
        filter_set = input_features.copy()

        # @TODO: Remove "special" handling once "bare" is a first-class citizen of the feature graph
        if "bare" in input_features:
            if not self.graph.has_node("bare"):
                self.graph.add_node("bare", content=BARE_FLAVOR_FEATURE_CONTENT)
            if not self.graph.has_node("libc"):
                self.graph.add_node("libc", content=BARE_FLAVOR_LIBC_FEATURE_CONTENT)

        for feature in input_features:
            filter_set.update(
                networkx.descendants(
                    Parser._get_graph_view_for_attr(self.graph, "include"), feature
                )
            )

        graph = networkx.subgraph_view(
            self.graph,
            filter_node=self._get_filter_set_callable(
                filter_set, additional_filter_func
            ),
        )

        if not ignore_excludes:
            Parser._exclude_from_filter_set(graph, input_features, filter_set)

        return graph

    def filter_as_dict(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None,
    ) -> dict:
        """
        Filters the features graph and returns it as a dict.

        :param cname:                  Canonical name to filter
        :param ignore_excludes:        Ignore `exclude` feature files
        :param additional_filter_func: Additional filter function

        :return: (dict) List of features for a given cname, split into platform, element and flag
        :since:  0.7.0
        """

        graph = self.filter(cname, ignore_excludes, additional_filter_func)
        features = Parser.sort_reversed_graph_nodes(graph)

        features_by_type = {}

        for feature in features:
            node_type = Parser._get_graph_node_type(graph.nodes[feature])

            if node_type not in features_by_type:
                features_by_type[node_type] = []

            features_by_type[node_type].append(feature)

        return features_by_type

    def filter_as_list(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None,
    ) -> list:
        """
        Filters the features graph and returns it as a list.

        :param cname:                  Canonical name to filter
        :param ignore_excludes:        Ignore `exclude` feature files
        :param additional_filter_func: Additional filter function

        :return: (list) Features list for a given cname
        :since:  0.7.0
        """

        graph = self.filter(cname, ignore_excludes, additional_filter_func)
        return Parser.sort_reversed_graph_nodes(graph)

    def filter_as_string(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None,
    ) -> str:
        """
        Filters the features graph and returns it as a string.

        :param cname:                  Canonical name to filter
        :param ignore_excludes:        Ignore `exclude` feature files
        :param additional_filter_func: Additional filter function

        :return: (str) Comma separated string with the expanded feature set for the cname
        :since:  0.7.0
        """

        graph = self.filter(cname, ignore_excludes, additional_filter_func)
        features = Parser.sort_reversed_graph_nodes(graph)

        return ",".join(features)

    def _exclude_from_filter_set(graph, input_features, filter_set):
        """
        Removes the given `filter_set` out of `input_features`.

        :param input_features: Features
        :param filter_set: Set to filter out

        :since: 0.7.0
        """

        exclude_graph_view = Parser._get_graph_view_for_attr(graph, "exclude")
        exclude_list = []

        for node in networkx.lexicographical_topological_sort(graph):
            for exclude in exclude_graph_view.successors(node):
                if exclude not in exclude_list:
                    exclude_list.append(exclude)

        for exclude in exclude_list:
            if exclude in input_features:
                raise ValueError(
                    f"Excluding explicitly included feature {exclude}, unsatisfiable condition"
                )

            if exclude in filter_set:
                filter_set.remove(exclude)

        if exclude_graph_view.edges():
            raise ValueError("Including explicitly excluded feature")

    def _get_node_features(self, node):
        """
        Returns the features for a given features node.

        :param node: Graph node

        :return: (dict) Features content dictionary
        :since:  0.7.0
        """

        return node.get("content", {}).get("features", {})

    def _read_feature_yaml(self, feature_yaml_file: str):
        """
        Reads and returns the content of the given features file.

        :param feature_yaml_file: Features file to read

        :return: (dict) Features content dictionary
        :since:  0.7.0
        """

        name = os.path.basename(os.path.dirname(feature_yaml_file))

        with open(feature_yaml_file) as f:
            content = yaml.safe_load(f)

        return {"name": name, "content": content}

    @staticmethod
    def get_cname_as_feature_set(cname):
        """
        Returns the features of a given canonical name.

        :param cname: Canonical name

        :return: (set) Features of the cname
        :since:  0.7.0
        """

        cname = cname.replace("_", "-_")
        return set(cname.split("-"))

    @staticmethod
    def _get_filter_set_callable(filter_set, additional_filter_func):
        """
        Returns the filter function used for the graph.

        :param filter_set: Filter set
        :param additional_filter_func: Additional filter function to apply

        :return: (callable) Filter function
        :since:  0.7.0
        """

        def filter_func(node):
            additional_filter_result = (
                True if additional_filter_func is None else additional_filter_func(node)
            )
            return node in filter_set and additional_filter_result

        return filter_func

    @staticmethod
    def _get_graph_view_for_attr(graph, attr):
        """
        Returns a graph view to return `attr` data.

        :param filter_set:             Filter set
        :param additional_filter_func: Additional filter function to apply

        :return: (object) networkx view
        :since:  0.7.0
        """

        return networkx.subgraph_view(
            graph, filter_edge=Parser._get_graph_view_for_attr_callable(graph, attr)
        )

    @staticmethod
    def _get_graph_view_for_attr_callable(graph, attr):
        """
        Returns the filter function used to filter for `attr` data.

        :param graph: Graph to filter
        :param attr: Graph edge attribute to filter for

        :return: (callable) Filter function
        :since:  0.7.0
        """

        def filter_func(a, b):
            return graph.get_edge_data(a, b)["attr"] == attr

        return filter_func

    @staticmethod
    def _get_graph_node_type(node):
        """
        Returns the node feature type.

        :param node: Graph node

        :return: (str) Feature type
        :since:  0.7.0
        """

        return node.get("content", {}).get("type")

    @staticmethod
    def set_default_gardenlinux_root_dir(root_dir):
        """
        Sets the default GardenLinux root directory used.

        :param root_dir: GardenLinux root directory

        :since: 0.7.0
        """

        Parser._GARDENLINUX_ROOT = root_dir

    @staticmethod
    def sort_graph_nodes(graph):
        """
        Sorts graph nodes by feature type.

        :param graph: Graph to sort

        :return: (list) Sorted feature set
        :since:  0.7.0
        """

        def key_function(node):
            prefix_map = {"platform": "0", "element": "1", "flag": "2"}
            node_type = Parser._get_graph_node_type(graph.nodes.get(node, {}))
            prefix = prefix_map[node_type]

            return f"{prefix}-{node}"

        return list(networkx.lexicographical_topological_sort(graph, key=key_function))

    @staticmethod
    def sort_reversed_graph_nodes(graph):
        """
        Sorts graph nodes by feature type.

        :param graph: Graph to reverse and sort

        :return: (list) Reversed and sorted feature set
        :since:  0.7.0
        """

        return Parser.sort_graph_nodes(graph.reverse())
