from gardenlinux.constants import GL_MEDIA_TYPE_LOOKUP, GL_MEDIA_TYPES

from gardenlinux.features import Parser
from typing import Optional
import networkx
import os
import re
import subprocess
import yaml


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

def get_features_dict(
    cname: str, gardenlinux_root: str, feature_dir_name: str = "features"
) -> dict:
    """
    :param str cname: the target cname to get the feature dict for
    :param str gardenlinux_root: path of garden linux src root
    :return: dict with list of features for a given cname, split into platform, element and flag

    """

    return Parser(gardenlinux_root, feature_dir_name).filter_as_dict(cname)

def get_features_graph(
    cname: str, gardenlinux_root: str, feature_dir_name: str = "features"
) -> networkx.Graph:
    """
    :param str cname: the target cname to get the feature dict for
    :param str gardenlinux_root: path of garden linux src root
    :return: list of features for a given cname

    """

    return Parser(gardenlinux_root, feature_dir_name).filter(cname)

def get_features_list(
    cname: str, gardenlinux_root: str, feature_dir_name: str = "features"
) -> list:
    """
    :param str cname: the target cname to get the feature dict for
    :param str gardenlinux_root: path of garden linux src root
    :return: list of features for a given cname

    """

    return Parser(gardenlinux_root, feature_dir_name).filter_as_list(cname)

def get_features(
    cname: str, gardenlinux_root: str, feature_dir_name: str = "features"
) -> str:
    """
    :param str cname: the target cname to get the feature set for
    :param str gardenlinux_root: path of garden linux src root
    :return: a comma separated string with the expanded feature set for the cname
    """

    return Parser(gardenlinux_root, feature_dir_name).filter_as_string(cname)

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

def sort_set(input_set, order_list):
    return [item for item in order_list if item in input_set]