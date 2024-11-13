from glob import glob
from git.objects import commit
import yaml
import networkx
import os
import re
import subprocess
from typing import Optional

from pygments.filter import apply_filters

# It is important that this list is sorted in descending length of the entries
GL_MEDIA_TYPES = [
    "gcpimage.tar.gz.log",
    "firecracker.tar.gz",
    "platform.test.log",
    "platform.test.xml",
    "gcpimage.tar.gz",
    "chroot.test.log",
    "chroot.test.xml",
    "pxe.tar.gz.log",
    "root.squashfs",
    "manifest.log",
    "release.log",
    "pxe.tar.gz",
    "qcow2.log",
    "test-log",
    "boot.efi",
    "manifest",
    "vmdk.log",
    "tar.log",
    "uki.log",
    "vmlinuz",
    "release",
    "vhd.log",
    "ova.log",
    "raw.log",
    "oci.log",
    "initrd",
    "tar.gz",
    "qcow2",
    "tar",
    "iso",
    "oci",
    "vhd",
    "vmdk",
    "ova",
    "uki",
    "raw",
]


GL_MEDIA_TYPE_LOOKUP = {
    "tar": "application/io.gardenlinux.image.archive.format.tar",
    "tar.gz": "application/io.gardenlinux.image.archive.format.tar.gz",
    "pxe.tar.gz": "application/io.gardenlinux.image.archive.format.pxe.tar.gz",
    "iso": "application/io.gardenlinux.image.archive.format.iso",
    "oci": "application/io.gardenlinux.image.archive.format.oci",
    "firecracker.tar.gz": "application/io.gardenlinux.image.archive.format.firecracker.tar.gz",
    "qcow2": "application/io.gardenlinux.image.format.qcow2",
    "vhd": "application/io.gardenlinux.image.format.vhd",
    "gcpimage.tar.gz": "application/io.gardenlinux.image.format.gcpimage.tar.gz",
    "vmdk": "application/io.gardenlinux.image.format.vmdk",
    "ova": "application/io.gardenlinux.image.format.ova",
    "uki": "application/io.gardenlinux.uki",
    "uki.log": "application/io.gardenlinux.log",
    "raw": "application/io.gardenlinux.image.archive.format.raw",
    "manifest.log": "application/io.gardenlinux.log",
    "release.log": "application/io.gardenlinux.log",
    "test-log": "application/io.gardenlinux.test-log",
    "manifest": "application/io.gardenlinux.manifest",
    "tar.log": "application/io.gardenlinux.log",
    "release": "application/io.gardenlinux.release",
    "raw.log": "application/io.gardenlinux.log",
    "qcow2.log": "application/io.gardenlinux.log",
    "pxe.tar.gz.log": "application/io.gardenlinux.log",
    "gcpimage.tar.gz.log": "application/io.gardenlinux.log",
    "vmdk.log": "application/io.gardenlinux.log",
    "vhd.log": "application/io.gardenlinux.log",
    "ova.log": "application/io.gardenlinux.log",
    "vmlinuz": "application/io.gardenlinux.kernel",
    "initrd": "application/io.gardenlinux.initrd",
    "root.squashfs": "application/io.gardenlinux.squashfs",
    "boot.efi": "application/io.gardenlinux.efi",
    "platform.test.log": "application/io.gardenlinux.io.platform.test.log",
    "platform.test.xml": "application/io.gardenlinux.io.platform.test.xml",
    "chroot.test.log": "application/io.gardenlinux.io.chroot.test.log",
    "chroot.test.xml": "application/io.gardenlinux.io.chroot.test.xml",
    "oci.log": "application/io.gardenlinux.log",
}


def get_gardenlinux_commit(gardenlinux_root: str, limit: Optional[int] = None) -> str:
    """
    :param str gardenlinux_root: path to garden linux src
    :return: output of get_commit script from gardenlinux src
    """
    get_commit_process_result = subprocess.run(
        [f"{gardenlinux_root}/get_commit"],
        capture_output=True,
    )

    if not get_commit_process_result.stdout:
        raise ValueError(
            f"{gardenlinux_root}/get_commit did not return any output, could not determine correct commit hash"
        )

    commit_str = get_commit_process_result.stdout.decode("UTF-8").strip("\n")

    if commit_str.count("\n") > 1:
        raise ValueError(f"{commit_str} contains multiple lines")

    if limit:
        if limit >= len(commit_str):
            return commit_str
        return commit_str[:limit]
    else:
        return commit_str


def get_features_dict(cname: str, gardenlinux_root: str) -> dict:
    """
    :param str cname: the target cname to get the feature dict for
    :param str gardenlinux_root: path of garden linux src root
    :return: dict with list of features for a given cname, split into platform, element and flag

    """
    feature_base_dir = f"{gardenlinux_root}/features"
    input_features = __reverse_cname_base(cname)
    feature_graph = read_feature_files(feature_base_dir)
    graph = filter_graph(feature_graph, input_features)
    features = __reverse_sort_nodes(graph)
    features_by_type = dict()
    for type in ["platform", "element", "flag"]:
        features_by_type[type] = [
            feature
            for feature in features
            if __get_node_type(graph.nodes[feature]) == type
        ]
    return features_by_type


def get_features(cname: str, gardenlinux_root: str) -> str:
    """
    :param str cname: the target cname to get the feature set for
    :param str gardenlinux_root: path of garden linux src root
    :return: a comma separated string with the expanded feature set for the cname
    """
    feature_base_dir = f"{gardenlinux_root}/features"
    input_features = __reverse_cname_base(cname)
    feature_graph = read_feature_files(feature_base_dir)
    graph = filter_graph(feature_graph, input_features)
    features = __reverse_sort_nodes(graph)
    return ",".join(features)


def construct_layer_metadata(
    filetype: str, cname: str, version: str, arch: str, commit: str
) -> dict:
    """
    :param str filetype: filetype of blob
    :param str cname: the cname of the target image
    :param str version: the version of the target image
    :param str arch: the arch of the target image
    :param str commit: commit of the garden linux source
    :return: dict of oci layer metadata for a given layer file
    """
    media_type = lookup_media_type_for_filetype(filetype)
    return {
        "file_name": f"{cname}-{arch}-{version}-{commit}.{filetype}",
        "media_type": media_type,
        "annotations": {"io.gardenlinux.image.layer.architecture": arch},
    }


def construct_layer_metadata_from_filename(filename: str, arch: str) -> dict:
    """
    :param str filename: filename of the blob
    :param str arch: the arch of the target image
    :return: dict of oci layer metadata for a given layer file
    """
    media_type = lookup_media_type_for_file(filename)
    return {
        "file_name": filename,
        "media_type": media_type,
        "annotations": {"io.gardenlinux.image.layer.architecture": arch},
    }


def get_file_set_from_cname(cname: str, version: str, arch: str, gardenlinux_root: str):
    """
    :param str cname: the target cname of the image
    :param str version: the version of the target image
    :param str arch: the arch of the target image
    :param str gardenlinux_root: path of garden linux src root
    :return: set of file names for a given cname
    """
    file_set = set()
    features_by_type = get_features_dict(cname, gardenlinux_root)
    commit_str = get_gardenlinux_commit(gardenlinux_root, 8)

    if commit_str == "local":
        raise ValueError("Using local commit. Refusing to upload to OCI Registry")
    for platform in features_by_type["platform"]:
        image_file_types = deduce_filetypes(f"{gardenlinux_root}/features/{platform}")
        for ft in image_file_types:
            file_set.add(
                f"{cname}-{arch}-{version}-{commit_str}.{ft}",
            )
    return file_set


def get_oci_metadata_from_fileset(fileset: list, arch: str):
    """
    :param str arch: arch of the target image
    :param set fileset: a list of filenames (not paths) to set oci_metadata for
    :return: list of dicts, where each dict represents a layer
    """
    oci_layer_metadata_list = list()

    for file in fileset:
        oci_layer_metadata_list.append(
            construct_layer_metadata_from_filename(file, arch)
        )

    return oci_layer_metadata_list


def get_oci_metadata(cname: str, version: str, arch: str, gardenlinux_root: str):
    """
    :param str cname: the target cname of the image
    :param str version: the target version of the image
    :param str arch: arch of the target image
    :param str gardenlinux_root: path of garden linux src root
    :return: list of dicts, where each dict represents a layer
    """

    # This is the feature deduction approach (glcli oci push)
    file_set = get_file_set_from_cname(cname, version, arch, gardenlinux_root)

    # This is the tarball extraction approach (glcli oci push-tarball)
    oci_layer_metadata_list = list()

    for file in file_set:
        oci_layer_metadata_list.append(
            construct_layer_metadata_from_filename(file, arch)
        )

    return oci_layer_metadata_list


def lookup_media_type_for_filetype(filetype: str) -> str:
    """
    :param str filetype: filetype of the target layer
    :return: mediatype
    """
    if filetype in GL_MEDIA_TYPE_LOOKUP:
        return GL_MEDIA_TYPE_LOOKUP[filetype]
    else:
        raise ValueError(
            f"media type for {filetype} is not defined. You may want to add the definition to parse_features_lib"
        )


def lookup_media_type_for_file(filename: str) -> str:
    """
    :param str filename: filename of the target layer
    :return: mediatype
    """
    for suffix in GL_MEDIA_TYPES:
        if filename.endswith(suffix):
            return GL_MEDIA_TYPE_LOOKUP[suffix]
    else:
        raise ValueError(
            f"media type for {filename} is not defined. You may want to add the definition to parse_features_lib"
        )


def deduce_feature_name(feature_dir: str):
    """
    :param str feature_dir: Directory of single Feature
    :return: string of feature name
    """
    parsed = parse_feature_yaml(feature_dir)
    if "name" not in parsed:
        raise ValueError("Expected name from parse_feature_yaml function to be set")
    return parsed["name"]


def deduce_archive_filetypes(feature_dir):
    """
    :param str feature_dir: Directory of single Feature
    :return: str list of filetype for archive
    """
    return deduce_filetypes_from_string(feature_dir, "image")


def deduce_image_filetypes(feature_dir):
    """
    :param str feature_dir: Directory of single Feature
    :return: str list of filetype for image
    """
    return deduce_filetypes_from_string(feature_dir, "convert")


def deduce_filetypes(feature_dir):
    """
    :param str feature_dir: Directory of single Feature
    :return: str list of filetypes for the feature
    """
    image_file_types = deduce_image_filetypes(feature_dir)
    archive_file_types = deduce_archive_filetypes(feature_dir)
    if not image_file_types:
        image_file_types.append("raw")
    if not archive_file_types:
        archive_file_types.append("tar")
    image_file_types.extend(archive_file_types)
    return image_file_types


def deduce_filetypes_from_string(feature_dir: str, script_base_name: str):
    """
    Garden Linux features can optionally have an image.<filetype> or convert.<filetype> script,
    where the <filetype> indicates the target filetype.

    image.<filetype> script converts the .tar to <filetype> archive.

    convert.<filetype> script converts the .raw to <filetype> image type.

    Both scripts are bash scripts invoked by the builder, but this function does only read the file ending

    :param str feature_dir: feature directory of garden linux
    :param str script_base_name: typically it is either image or convert
    :return: list of available filetypes deduced on the available script_base_name.<filetype>
    """
    result = list()

    for filename in os.listdir(feature_dir):
        if re.search(f"{script_base_name}.*", filename):
            result.append(filename.split(f"{script_base_name}.")[1])

    return sorted(result)


def read_feature_files(feature_dir):
    """
    Legacy function copied from gardenlinux/builder

    TODO: explain the structure of the graph

    :param str feature_dir: feature directory to create the graph for
    :returns: an networkx based feature graph
    """
    feature_yaml_files = glob(f"{feature_dir}/*/info.yaml")
    features = [parse_feature_yaml(i) for i in feature_yaml_files]
    feature_graph = networkx.DiGraph()
    for feature in features:
        feature_graph.add_node(feature["name"], content=feature["content"])
    for node in feature_graph.nodes():
        node_features = __get_node_features(feature_graph.nodes[node])
        for attr in node_features:
            if attr not in ["include", "exclude"]:
                continue
            for ref in node_features[attr]:
                if not os.path.isfile(f"{feature_dir}/{ref}/info.yaml"):
                    raise ValueError(
                        f"feature {node} references feature {ref}, but {feature_dir}/{ref}/info.yaml does not exist"
                    )
                feature_graph.add_edge(node, ref, attr=attr)
    if not networkx.is_directed_acyclic_graph(feature_graph):
        raise ValueError("Graph is not directed acyclic graph")
    return feature_graph


def parse_feature_yaml(feature_yaml_file: str):
    """
    Legacy function copied from gardenlinux/builder

    extracts the feature name from the feature_yaml_file param,
    reads the info.yaml into a dict and outputs a dict containing the cname and the info yaml

    :param str feature_yaml_file: path to the target info.yaml that must be read
    """
    if os.path.basename(feature_yaml_file) != "info.yaml":
        raise ValueError("expected info.yaml")
    name = os.path.basename(os.path.dirname(feature_yaml_file))
    with open(feature_yaml_file) as f:
        content = yaml.safe_load(f)
    return {"name": name, "content": content}


def __get_node_features(node):
    return node.get("content", {}).get("features", {})


def filter_graph(feature_graph, feature_set, ignore_excludes=False):
    filter_set = set(feature_graph.nodes())

    def filter_func(node):
        return node in filter_set

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
        if exclude in feature_set:
            raise ValueError(
                f"excluding explicitly included feature {exclude}, unsatisfiable condition"
            )
        filter_set.remove(exclude)
    if graph_by_edge["exclude"].edges() and (not ignore_excludes):
        raise ValueError("Including explicitly excluded feature")
    return graph


def sort_set(input_set, order_list):
    return [item for item in order_list if item in input_set]


def __sort_key(graph, node):
    prefix_map = {"platform": "0", "element": "1", "flag": "2"}
    node_type = __get_node_type(graph.nodes.get(node, {}))
    prefix = prefix_map[node_type]
    return f"{prefix}-{node}"


def __sort_nodes(graph):
    def key_function(node):
        return __sort_key(graph, node)

    return list(networkx.lexicographical_topological_sort(graph, key=key_function))


def __reverse_cname_base(cname):
    cname = cname.replace("_", "-_")
    return set(cname.split("-"))


def __reverse_sort_nodes(graph):
    reverse_graph = graph.reverse()
    assert networkx.is_directed_acyclic_graph(reverse_graph)
    return __sort_nodes(reverse_graph)


def __get_node_type(node):
    return node.get("content", {}).get("type")
