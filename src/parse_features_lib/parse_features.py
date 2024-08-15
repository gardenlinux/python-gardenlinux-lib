from glob import glob
import yaml
import networkx
import os
import re


def deduce_feature_name(feature_dir: str):
    """
    :param str feature_dir: Directory of single Feature
    :return: string of feature name
    """
    parsed = parse_feature_yaml(feature_dir)
    if "name" not in parsed:
        raise ValueError("Expected name from parse_feature_yaml function to be set")
    return parsed["name"]


def deduce_archive_filetype(feature_dir):
    """
    :param str feature_dir: Directory of single Feature
    :return: str of filetype for archive
    """
    return deduce_filetype_from_string(feature_dir, "image")


def deduce_image_filetype(feature_dir):
    """
    :param str feature_dir: Directory of single Feature
    :return: str of filetype for image
    """
    return deduce_filetype_from_string(feature_dir, "convert")


def deduce_filetype_from_string(feature_dir: str, script_base_name: str):
    result = list()

    for filename in os.listdir(feature_dir):
        if re.search(f"{script_base_name}.*", filename):
            result.append(filename.split(f"{script_base_name}.")[1])

    return sorted(result)


def read_feature_files(feature_dir):
    feature_yaml_files = glob(f"{feature_dir}/*/info.yaml")
    features = [parse_feature_yaml(i) for i in feature_yaml_files]
    feature_graph = networkx.DiGraph()
    for feature in features:
        feature_graph.add_node(feature["name"], content=feature["content"])
    for node in feature_graph.nodes():
        node_features = get_node_features(feature_graph.nodes[node])
        for attr in node_features:
            if attr not in ["include", "exclude"]:
                continue
            for ref in node_features[attr]:
                assert os.path.isfile(
                    f"{feature_dir}/{ref}/info.yaml"
                ), f"feature {node} references feature {ref}, but {feature_dir}/{ref}/info.yaml does not exist"
                feature_graph.add_edge(node, ref, attr=attr)
    assert networkx.is_directed_acyclic_graph(feature_graph)
    return feature_graph


def parse_feature_yaml(feature_yaml_file):
    assert os.path.basename(feature_yaml_file) == "info.yaml"
    name = os.path.basename(os.path.dirname(feature_yaml_file))
    content = yaml.load(open(feature_yaml_file), Loader=yaml.FullLoader)
    return {"name": name, "content": content}


def get_node_features(node):
    return node.get("content", {}).get("features", {})


def filter_graph(feature_graph, feature_set, ignore_excludes=False):
    filter_set = set(feature_graph.nodes())
    filter_func = lambda node: node in filter_set
    graph = networkx.subgraph_view(feature_graph, filter_node=filter_func)
    graph_by_edge = dict()
    for attr in ["include", "exclude"]:
        edge_filter_func = (
            lambda attr: lambda a, b: graph.get_edge_data(a, b)["attr"] == attr
        )(attr)
        graph_by_edge[attr] = networkx.subgraph_view(
            graph, filter_edge=edge_filter_func
        )
    while True:
        include_set = feature_set.copy()
        for feature in feature_set:
            include_set.update(networkx.descendants(graph_by_edge["include"], feature))
        filter_set = include_set
        if ignore_excludes:
            break
        exclude_list = []
        for node in networkx.lexicographical_topological_sort(graph):
            for exclude in graph_by_edge["exclude"].successors(node):
                exclude_list.append(exclude)
        if not exclude_list:
            break
        exclude = exclude_list[0]
        assert (
            exclude not in feature_set
        ), f"excluding explicitly included feature {exclude}, unsatisfiable condition"
        filter_set.remove(exclude)
    assert (not graph_by_edge["exclude"].edges()) or ignore_excludes
    return graph

