from glob import glob
from typing import Callable, Optional
import logging
import networkx
import os
import re
import subprocess
import yaml


class Parser(object):
    def __init__(self, gardenlinux_root: str = ".", feature_dir_name: str = "features", logger: Optional[logging.Logger] = None):
        feature_base_dir = os.path.join(gardenlinux_root, feature_dir_name)

        if not os.access(feature_base_dir, os.R_OK):
            raise ValueError("Feature directory given is invalid: {0}".format(feature_base_dir))

        self._feature_base_dir = feature_base_dir

        self._graph = None
        self._logger = logger

        if self._logger is None:
            self._logger = logging.getLogger("gardenlinux.features")

        if not self._logger.hasHandlers():
            self._logger.addHandler(logging.NullHandler())

        self._logger.debug("features.Parser initialized for directory: {0}".format(feature_base_dir))

    @property
    def graph(self) -> networkx.Graph:
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
                        if not os.path.isfile("{0}/{1}/info.yaml".format(self._feature_base_dir, ref)):
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
        additional_filter_func: Optional[Callable[(str,), bool]] = None
    ) -> networkx.Graph:
        input_features = Parser.get_cname_as_feature_set(cname)
        filter_set = input_features.copy()

        for feature in input_features:
            filter_set.update(networkx.descendants(Parser._get_graph_view_for_attr(self.graph, "include"), feature))

        graph = networkx.subgraph_view(self.graph, filter_node = self._get_filter_set_callable(filter_set, additional_filter_func))

        if not ignore_excludes:
            Parser._exclude_from_filter_set(graph, input_features, filter_set)

        return graph

    def filter_as_dict(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None
    ) -> dict:
        """
:param str cname: the target cname to get the feature dict for
:param str gardenlinux_root: path of garden linux src root

:return: dict with list of features for a given cname, split into platform, element and flag
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
        additional_filter_func: Optional[Callable[(str,), bool]] = None
    ) -> list:
        """
:param str cname: the target cname to get the feature dict for
:param str gardenlinux_root: path of garden linux src root

:return: list of features for a given cname
        """

        graph = self.filter(cname, ignore_excludes, additional_filter_func)
        return Parser.sort_reversed_graph_nodes(graph)

    def filter_as_string(
        self,
        cname: str,
        ignore_excludes: bool = False,
        additional_filter_func: Optional[Callable[(str,), bool]] = None
    ) -> str:
        """
:param str cname: the target cname to get the feature set for
:param str gardenlinux_root: path of garden linux src root

:return: a comma separated string with the expanded feature set for the cname
        """

        graph = self.filter(cname, ignore_excludes, additional_filter_func)
        features = Parser.sort_reversed_graph_nodes(graph)

        return ",".join(features)

    def _exclude_from_filter_set(graph, input_features, filter_set):
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
        return node.get("content", {}).get("features", {})

    def _read_feature_yaml(self, feature_yaml_file: str):
        """
        Legacy function copied from gardenlinux/builder

        extracts the feature name from the feature_yaml_file param,
        reads the info.yaml into a dict and outputs a dict containing the cname and the info yaml

        :param str feature_yaml_file: path to the target info.yaml that must be read
        """

        name = os.path.basename(os.path.dirname(feature_yaml_file))

        with open(feature_yaml_file) as f:
            content = yaml.safe_load(f)

        return {"name": name, "content": content}

    @staticmethod
    def get_cname_as_feature_set(cname):
        cname = cname.replace("_", "-_")
        return set(cname.split("-"))

    @staticmethod
    def _get_filter_set_callable(filter_set, additional_filter_func):
        def filter_func(node):
            additional_filter_result = True if additional_filter_func is None else additional_filter_func(node)
            return (node in filter_set and additional_filter_result)

        return filter_func

    @staticmethod
    def _get_graph_view_for_attr(graph, attr):
        return networkx.subgraph_view(
            graph, filter_edge = Parser._get_graph_view_for_attr_callable(graph, attr)
        )

    @staticmethod
    def _get_graph_view_for_attr_callable(graph, attr):
        def filter_func(a, b):
            return graph.get_edge_data(a, b)["attr"] == attr

        return filter_func

    @staticmethod
    def _get_graph_node_type(node):
        return node.get("content", {}).get("type")

    @staticmethod
    def sort_reversed_graph_nodes(graph):
        def key_function(node):
            prefix_map = {"platform": "0", "element": "1", "flag": "2"}
            node_type = Parser._get_graph_node_type(graph.nodes.get(node, {}))
            prefix = prefix_map[node_type]

            return f"{prefix}-{node}"

        return list(networkx.lexicographical_topological_sort(graph.reverse(), key = key_function))
