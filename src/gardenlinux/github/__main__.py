import argparse
import gzip
import io
import json
import os
import re
import shutil
import sys
import textwrap
from pathlib import Path

import requests
import yaml
from git import Repo
from yaml.loader import SafeLoader

from ..apt import DebsrcFile, GardenLinuxRepo
from ..apt.package_repo_info import compare_repo
from ..features import CName
from ..flavors import Parser as FlavorsParser
from ..logger import LoggerSetup
from ..s3 import S3Artifacts

LOGGER = LoggerSetup.get_logger("gardenlinux.github")

GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME = "gardenlinux-github-releases"

RELEASE_ID_FILE = ".github_release_id"

REQUESTS_TIMEOUTS = (5, 30)  # connect, read

CLOUD_FULLNAME_DICT = {
    "ali": "Alibaba Cloud",
    "aws": "Amazon Web Services",
    "gcp": "Google Cloud Platform",
    "azure": "Microsoft Azure",
    "openstack": "OpenStack",
    "openstackbaremetal": "OpenStack Baremetal",
}

# https://github.com/gardenlinux/gardenlinux/issues/3044
# Empty string is the 'legacy' variant with traditional root fs and still needed/supported
IMAGE_VARIANTS = ["", "_usi", "_tpm2_trustedboot"]

# Variant display names and order for consistent use across functions
VARIANT_ORDER = ["legacy", "usi", "tpm2_trustedboot"]
VARIANT_NAMES = {
    "legacy": "Default",
    "usi": "USI (Unified System Image)",
    "tpm2_trustedboot": "TPM2 Trusted Boot",
}

# Mapping from image variant suffixes to variant keys
VARIANT_SUFFIX_MAP = {
    "": "legacy",
    "_usi": "usi",
    "_tpm2_trustedboot": "tpm2_trustedboot",
}

# Short display names for table view
VARIANT_TABLE_NAMES = {"legacy": "Default", "usi": "USI", "tpm2_trustedboot": "TPM2"}


def get_variant_from_flavor(flavor_name):
    """
    Determine the variant from a flavor name by checking for variant suffixes.
    Returns the variant key (e.g., 'legacy', 'usi', 'tpm2_trustedboot').
    """
    match flavor_name:
        case name if "_usi" in name:
            return "usi"
        case name if "_tpm2_trustedboot" in name:
            return "tpm2_trustedboot"
        case _:
            return "legacy"


def get_platform_release_note_data(metadata, platform):
    """
    Get the appropriate cloud release note data based on platform.
    Returns the structured data dictionary.
    """
    match platform:
        case "ali":
            return _ali_release_note(metadata)
        case "aws":
            return _aws_release_note(metadata)
        case "gcp":
            return _gcp_release_note(metadata)
        case "azure":
            return _azure_release_note(metadata)
        case "openstack":
            return _openstack_release_note(metadata)
        case "openstackbaremetal":
            return _openstackbaremetal_release_note(metadata)
        case _:
            LOGGER.error(f"unknown platform {platform}")
            return None


def get_file_extension_for_platform(platform):
    """
    Get the correct file extension for a given platform.
    """
    match platform:
        case "ali":
            return ".qcow2"
        case "gcp":
            return ".gcpimage.tar.gz"
        case "azure":
            return ".vhd"
        case "aws" | "openstack" | "openstackbaremetal":
            return ".raw"
        case _:
            return ".raw"  # Default fallback


def get_platform_display_name(platform):
    """
    Get the display name for a platform.
    """
    match platform:
        case "ali" | "openstackbaremetal" | "openstack" | "azure" | "gcp" | "aws":
            return CLOUD_FULLNAME_DICT[platform]
        case _:
            return platform.upper()


def _ali_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    regions = []
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            regions.append({"region": p["region_id"], "image_id": p["image_id"]})

    return {"flavor": flavor_name, "regions": regions}


def _aws_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    regions = []
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            regions.append({"region": p["aws_region_id"], "image_id": p["ami_id"]})

    return {"flavor": flavor_name, "regions": regions}


def _gcp_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    details = {}
    if "gcp_image_name" in published_image_metadata:
        details["image_name"] = published_image_metadata["gcp_image_name"]
    if "gcp_project_name" in published_image_metadata:
        details["project"] = published_image_metadata["gcp_project_name"]
    details["availability"] = "Global (all regions)"

    return {"flavor": flavor_name, "details": details}


def _openstack_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    regions = []
    if "published_openstack_images" in published_image_metadata:
        for image in published_image_metadata["published_openstack_images"]:
            regions.append(
                {
                    "region": image["region_name"],
                    "image_id": image["image_id"],
                    "image_name": image["image_name"],
                }
            )

    return {"flavor": flavor_name, "regions": regions}


def _openstackbaremetal_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    regions = []
    if "published_openstack_images" in published_image_metadata:
        for image in published_image_metadata["published_openstack_images"]:
            regions.append(
                {
                    "region": image["region_name"],
                    "image_id": image["image_id"],
                    "image_name": image["image_name"],
                }
            )

    return {"flavor": flavor_name, "regions": regions}


def _azure_release_note(metadata):
    published_image_metadata = metadata["published_image_metadata"]
    flavor_name = metadata["s3_key"].split("/")[-1]  # Extract flavor from s3_key

    gallery_images = []
    marketplace_images = []

    for pset in published_image_metadata:
        if pset == "published_gallery_images":
            for gallery_image in published_image_metadata[pset]:
                gallery_images.append(
                    {
                        "hyper_v_generation": gallery_image["hyper_v_generation"],
                        "azure_cloud": gallery_image["azure_cloud"],
                        "image_id": gallery_image["community_gallery_image_id"],
                    }
                )

        if pset == "published_marketplace_images":
            for market_image in published_image_metadata[pset]:
                marketplace_images.append(
                    {
                        "hyper_v_generation": market_image["hyper_v_generation"],
                        "urn": market_image["urn"],
                    }
                )

    return {
        "flavor": flavor_name,
        "gallery_images": gallery_images,
        "marketplace_images": marketplace_images,
    }


def generate_release_note_image_ids(metadata_files):
    """
    Groups metadata files by image variant, then platform, then architecture
    """
    # Group metadata by variant, platform, and architecture
    grouped_data = {}

    for metadata_file_path in metadata_files:
        with open(metadata_file_path) as f:
            metadata = yaml.load(f, Loader=SafeLoader)

        published_image_metadata = metadata["published_image_metadata"]
        # Skip if no publishing metadata found
        if published_image_metadata is None:
            continue

        platform = metadata["platform"]
        arch = metadata["architecture"]

        # Determine variant from flavor name
        flavor_name = metadata["s3_key"].split("/")[-1]
        variant = get_variant_from_flavor(flavor_name)

        if variant not in grouped_data:
            grouped_data[variant] = {}
        if platform not in grouped_data[variant]:
            grouped_data[variant][platform] = {}
        if arch not in grouped_data[variant][platform]:
            grouped_data[variant][platform][arch] = []

        grouped_data[variant][platform][arch].append(metadata)

    # Generate both table and old format
    output = "## Published Images\n\n"

    # Add table format (collapsed by default)
    output += "<details>\n<summary>📊 Table View</summary>\n\n"
    output += generate_table_format(grouped_data)
    output += "\n</details>\n\n"

    # Add old format (collapsed by default)
    output += "<details>\n<summary>📝 Detailed View</summary>\n\n"
    output += generate_detailed_format(grouped_data)
    output += "\n</details>\n\n"

    return output


def generate_table_format(grouped_data):
    """
    Generate the table format with collapsible region details
    """
    output = "| Variant | Platform | Architecture | Flavor | Regions & Image IDs | Download Links |\n"
    output += "|---------|----------|--------------|--------|---------------------|----------------|\n"

    for variant in VARIANT_ORDER:
        if variant not in grouped_data:
            continue

        for platform in sorted(grouped_data[variant].keys()):
            platform_display = get_platform_display_name(platform)

            for arch in sorted(grouped_data[variant][platform].keys()):
                # Process all metadata for this variant/platform/architecture
                for metadata in grouped_data[variant][platform][arch]:
                    data = get_platform_release_note_data(metadata, platform)
                    if data is None:
                        continue

                    # Generate collapsible details for regions
                    details_content = generate_region_details(data, platform)
                    summary_text = generate_summary_text(data, platform)

                    # Generate download links
                    download_links = generate_download_links(data["flavor"], platform)

                    # Use shorter names for table display
                    variant_display = VARIANT_TABLE_NAMES[variant]
                    output += f"| {variant_display} | {platform_display} | {arch} | `{data['flavor']}` | <details><summary>{summary_text}</summary><br>{details_content}</details> | <details><summary>Download</summary><br>{download_links}</details> |\n"

    return output


def generate_region_details(data, platform):
    """
    Generate the detailed region information for the collapsible section
    """
    details = ""

    match data:
        case {"regions": regions}:
            for region in regions:
                match region:
                    case {
                        "region": region_name,
                        "image_id": image_id,
                        "image_name": image_name,
                    }:
                        details += f"**{region_name}:** {image_id} ({image_name})<br>"
                    case {"region": region_name, "image_id": image_id}:
                        details += f"**{region_name}:** {image_id}<br>"
        case {"details": details_dict}:
            for key, value in details_dict.items():
                details += f"**{key.replace('_', ' ').title()}:** {value}<br>"
        case {
            "gallery_images": gallery_images,
            "marketplace_images": marketplace_images,
        }:
            if gallery_images:
                details += "**Gallery Images:**<br>"
                for img in gallery_images:
                    details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
            if marketplace_images:
                details += "**Marketplace Images:**<br>"
                for img in marketplace_images:
                    details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"
        case {"gallery_images": gallery_images}:
            details += "**Gallery Images:**<br>"
            for img in gallery_images:
                details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
        case {"marketplace_images": marketplace_images}:
            details += "**Marketplace Images:**<br>"
            for img in marketplace_images:
                details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"

    return details


def generate_summary_text(data, platform):
    """
    Generate the summary text for the collapsible section
    """
    match data:
        case {"regions": regions}:
            count = len(regions)
            return f"{count} regions"
        case {"details": _}:
            return "Global availability"
        case {
            "gallery_images": gallery_images,
            "marketplace_images": marketplace_images,
        }:
            gallery_count = len(gallery_images)
            marketplace_count = len(marketplace_images)
            return f"{gallery_count} gallery + {marketplace_count} marketplace images"
        case {"gallery_images": gallery_images}:
            gallery_count = len(gallery_images)
            return f"{gallery_count} gallery images"
        case {"marketplace_images": marketplace_images}:
            marketplace_count = len(marketplace_images)
            return f"{marketplace_count} marketplace images"
        case _:
            return "Details available"


def generate_download_links(flavor, platform):
    """
    Generate download links for the flavor with correct file extension based on platform
    """
    base_url = "https://gardenlinux-github-releases.s3.amazonaws.com/objects"
    file_ext = get_file_extension_for_platform(platform)
    filename = f"{flavor}{file_ext}"
    download_url = f"{base_url}/{flavor}/{filename}"
    return f"[{filename}]({download_url})"


def generate_detailed_format(grouped_data):
    """
    Generate the old detailed format with YAML
    """
    output = ""

    for variant in VARIANT_ORDER:
        if variant not in grouped_data:
            continue

        output += (
            f"<details>\n<summary>Variant - {VARIANT_NAMES[variant]}</summary>\n\n"
        )
        output += f"### Variant - {VARIANT_NAMES[variant]}\n\n"

        for platform in sorted(grouped_data[variant].keys()):
            platform_long_name = CLOUD_FULLNAME_DICT.get(platform, platform)
            output += f"<details>\n<summary>{platform.upper()} - {platform_long_name}</summary>\n\n"
            output += f"#### {platform.upper()} - {platform_long_name}\n\n"

            for arch in sorted(grouped_data[variant][platform].keys()):
                output += f"<details>\n<summary>{arch}</summary>\n\n"
                output += f"##### {arch}\n\n"
                output += "```\n"

                # Process all metadata for this variant/platform/architecture
                for metadata in grouped_data[variant][platform][arch]:
                    data = get_platform_release_note_data(metadata, platform)
                    if data is None:
                        continue

                    # Format the data according to the new structure as YAML
                    output += f"- flavor: {data['flavor']}\n"

                    # Add download link with correct file extension
                    file_ext = get_file_extension_for_platform(platform)

                    filename = f"{data['flavor']}{file_ext}"
                    download_url = f"https://gardenlinux-github-releases.s3.amazonaws.com/objects/{data['flavor']}/{filename}"
                    output += f"  download_url: {download_url}\n"

                    if "regions" in data:
                        output += "  regions:\n"
                        for region in data["regions"]:
                            if "image_name" in region:
                                output += f"    - region: {region['region']}\n"
                                output += f"      image_id: {region['image_id']}\n"
                                output += f"      image_name: {region['image_name']}\n"
                            else:
                                output += f"    - region: {region['region']}\n"
                                output += f"      image_id: {region['image_id']}\n"
                    elif "details" in data and platform != "gcp":
                        output += "  details:\n"
                        for key, value in data["details"].items():
                            output += f"    {key}: {value}\n"
                    elif platform == "gcp" and "details" in data:
                        # For GCP, move details up to same level as flavor
                        for key, value in data["details"].items():
                            output += f"  {key}: {value}\n"
                    elif "gallery_images" in data or "marketplace_images" in data:
                        if data.get("gallery_images"):
                            output += "  gallery_images:\n"
                            for img in data["gallery_images"]:
                                output += f"    - hyper_v_generation: {img['hyper_v_generation']}\n"
                                output += f"      azure_cloud: {img['azure_cloud']}\n"
                                output += f"      image_id: {img['image_id']}\n"
                        if data.get("marketplace_images"):
                            output += "  marketplace_images:\n"
                            for img in data["marketplace_images"]:
                                output += f"    - hyper_v_generation: {img['hyper_v_generation']}\n"
                                output += f"      urn: {img['urn']}\n"

                output += "```\n\n"
                output += "</details>\n\n"

            output += "</details>\n\n"

        output += "</details>\n\n"

    return output


def download_metadata_file(
    s3_artifacts, cname, version, commitish_short, artifacts_dir
):
    """
    Download metadata file (s3_metadata.yaml)
    """
    LOGGER.debug(
        f"{s3_artifacts=} | {cname=} | {version=} | {commitish_short=} | {artifacts_dir=}"
    )
    release_object = list(
        s3_artifacts._bucket.objects.filter(
            Prefix=f"meta/singles/{cname}-{version}-{commitish_short}"
        )
    )[0]
    LOGGER.debug(f"{release_object.bucket_name=} | {release_object.key=}")

    s3_artifacts._bucket.download_file(
        release_object.key, artifacts_dir.joinpath(f"{cname}.s3_metadata.yaml")
    )


def download_all_metadata_files(version, commitish):
    repo = Repo(".")
    commit = repo.commit(commitish)
    flavors_data = commit.tree["flavors.yaml"].data_stream.read().decode("utf-8")
    flavors = FlavorsParser(flavors_data).filter(only_publish=True)

    local_dest_path = Path("s3_downloads")
    if local_dest_path.exists():
        shutil.rmtree(local_dest_path)
    local_dest_path.mkdir(mode=0o755, exist_ok=False)

    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)

    commitish_short = commitish[:8]

    for flavor in flavors:
        cname = CName(flavor[1], flavor[0], "{0}-{1}".format(version, commitish_short))
        LOGGER.debug(f"{flavor=} {version=} {commitish=}")
        # Filter by image variants - only download if the flavor matches one of the variants
        flavor_matches_variant = False
        for variant_suffix in IMAGE_VARIANTS:
            if variant_suffix == "":
                last_part = cname.cname.split("-")[-1]
                if "_" not in last_part:
                    flavor_matches_variant = True
                    break
            elif variant_suffix in cname.cname:
                # Specific variant (any non-empty string in IMAGE_VARIANTS)
                flavor_matches_variant = True
                break

        if not flavor_matches_variant:
            LOGGER.info(
                f"Skipping flavor {cname.cname} - not matching image variants filter"
            )
            continue

        try:
            download_metadata_file(
                s3_artifacts, cname.cname, version, commitish_short, local_dest_path
            )
        except IndexError:
            LOGGER.warn(f"No artifacts found for flavor {cname.cname}, skipping...")
            continue

    return [str(artifact) for artifact in local_dest_path.iterdir()]


def release_notes_changes_section(gardenlinux_version):
    """
    Get list of fixed CVEs, grouped by upgraded package.
    Note: This result is not perfect, feel free to edit the generated release notes and
    file issues in glvd for improvement suggestions https://github.com/gardenlinux/glvd/issues
    """
    try:
        url = f"https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1/patchReleaseNotes/{gardenlinux_version}"
        response = requests.get(url, timeout=REQUESTS_TIMEOUTS)
        response.raise_for_status()  # Will raise an error for bad responses
        data = response.json()

        if len(data["packageList"]) == 0:
            return ""

        output = [
            "## Changes",
            "The following packages have been upgraded, to address the mentioned CVEs:",
        ]
        for package in data["packageList"]:
            upgrade_line = (
                f"- upgrade '{package['sourcePackageName']}' from `{package['oldVersion']}` "
                f"to `{package['newVersion']}`"
            )
            output.append(upgrade_line)

            if package["fixedCves"]:
                for fixedCve in package["fixedCves"]:
                    output.append(f"  - {fixedCve}")

        return "\n".join(output) + "\n\n"
    except Exception as exn:
        # There are expected error cases, for example with versions not supported by glvd (1443.x) or when the api is not available
        # Fail gracefully by adding the placeholder we previously used, so that the release note generation does not fail.
        LOGGER.error(f"Failed to process GLVD API output: {exn}")
        return textwrap.dedent(
            """
        ## Changes
        The following packages have been upgraded, to address the mentioned CVEs:
        **todo release facilitator: fill this in**
        """
        )


def release_notes_software_components_section(package_list):
    output = "## Software Component Versions\n"
    output += "```"
    output += "\n"
    packages_regex = re.compile(
        r"^linux-image-amd64$|^systemd$|^containerd$|^runc$|^curl$|^openssl$|^openssh-server$|^libc-bin$"
    )
    for entry in package_list.values():
        if packages_regex.match(entry.deb_source):
            output += f"{entry!r}\n"
    output += "```"
    output += "\n\n"
    return output


def release_notes_compare_package_versions_section(gardenlinux_version, package_list):
    output = ""
    version_components = gardenlinux_version.split(".")
    # Assumes we always have version numbers like 1443.2
    if len(version_components) == 2:
        try:
            major = int(version_components[0])
            patch = int(version_components[1])

            if patch > 0:
                previous_version = f"{major}.{patch - 1}"

                output += (
                    f"## Changes in Package Versions Compared to {previous_version}\n"
                )
                output += compare_apt_repo_versions(
                    previous_version, gardenlinux_version
                )
            elif patch == 0:
                output += f"## Full List of Packages in Garden Linux version {major}\n"
                output += "<details><summary>Expand to see full list</summary>\n"
                output += "<pre>"
                output += "\n"
                for entry in package_list.values():
                    output += f"{entry!r}\n"
                output += "</pre>"
                output += "\n</details>\n\n"

        except ValueError:
            LOGGER.error(
                f"Could not parse {gardenlinux_version} as the Garden Linux version, skipping version compare section"
            )
    else:
        LOGGER.error(
            f"Unexpected version number format {gardenlinux_version}, expected format (major is int).(patch is int)"
        )
    return output


def compare_apt_repo_versions(previous_version, current_version):
    previous_repo = GardenLinuxRepo(previous_version)
    current_repo = GardenLinuxRepo(current_version)
    pkg_diffs = sorted(compare_repo(previous_repo, current_repo), key=lambda t: t[0])

    output = f"| Package | {previous_version} | {current_version} |\n"
    output += "|---------|--------------------|-------------------|\n"

    for pkg in pkg_diffs:
        output += f"|{pkg[0]} | {pkg[1] if pkg[1] is not None else '-'} | {pkg[2] if pkg[2] is not None else '-'} |\n"
    return output


def _get_package_list(gardenlinux_version):
    url = f"https://packages.gardenlinux.io/gardenlinux/dists/{gardenlinux_version}/main/binary-amd64/Packages.gz"
    response = requests.get(url, timeout=REQUESTS_TIMEOUTS)
    response.raise_for_status()

    d = DebsrcFile()

    with io.BytesIO(response.content) as buf:
        with gzip.open(buf, "rt") as f:
            d.read(f)

    return d


def create_github_release_notes(gardenlinux_version, commitish):
    package_list = _get_package_list(gardenlinux_version)

    output = ""

    output += release_notes_changes_section(gardenlinux_version)

    output += release_notes_software_components_section(package_list)

    output += release_notes_compare_package_versions_section(
        gardenlinux_version, package_list
    )

    metadata_files = download_all_metadata_files(gardenlinux_version, commitish)

    output += generate_release_note_image_ids(metadata_files)

    output += "\n"
    output += "## Kernel Module Build Container (kmodbuild)"
    output += "\n"
    output += "```"
    output += "\n"
    output += f"ghcr.io/gardenlinux/gardenlinux/kmodbuild:{gardenlinux_version}"
    output += "\n"
    output += "```"
    output += "\n"
    return output


def write_to_release_id_file(release_id):
    try:
        with open(RELEASE_ID_FILE, "w") as file:
            file.write(release_id)
        LOGGER.info(f"Created {RELEASE_ID_FILE} successfully.")
    except IOError as e:
        LOGGER.error(f"Could not create {RELEASE_ID_FILE} file: {e}")
        sys.exit(1)


def create_github_release(owner, repo, tag, commitish, body):

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    data = {
        "tag_name": tag,
        "target_commitish": commitish,
        "name": tag,
        "body": body,
        "draft": False,
        "prerelease": False,
    }

    response = requests.post(
        f"https://api.github.com/repos/{owner}/{repo}/releases",
        headers=headers,
        data=json.dumps(data),
        timeout=REQUESTS_TIMEOUTS
    )

    if response.status_code == 201:
        LOGGER.info("Release created successfully")
        response_json = response.json()
        return response_json.get("id")
    else:
        LOGGER.error("Failed to create release")
        LOGGER.debug(response.json())
        response.raise_for_status()


def upload_to_github_release_page(
    github_owner, github_repo, gardenlinux_release_id, file_to_upload, dry_run
):
    if dry_run:
        LOGGER.info(
            f"Dry run: would upload {file_to_upload} to release {gardenlinux_release_id} in repo {github_owner}/{github_repo}"
        )
        return

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/octet-stream",
    }

    upload_url = f"https://uploads.github.com/repos/{github_owner}/{github_repo}/releases/{gardenlinux_release_id}/assets?name={os.path.basename(file_to_upload)}"

    try:
        with open(file_to_upload, "rb") as f:
            file_contents = f.read()
    except IOError as e:
        LOGGER.error(f"Error reading file {file_to_upload}: {e}")
        return

    response = requests.post(upload_url, headers=headers, data=file_contents, timeout=REQUESTS_TIMEOUTS)
    if response.status_code == 201:
        LOGGER.info("Upload successful")
    else:
        LOGGER.error(
            f"Upload failed with status code {response.status_code}: {response.text}"
        )
        response.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="GitHub Release Script")
    subparsers = parser.add_subparsers(dest="command")

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--owner", default="gardenlinux")
    create_parser.add_argument("--repo", default="gardenlinux")
    create_parser.add_argument("--tag", required=True)
    create_parser.add_argument("--commit", required=True)
    create_parser.add_argument("--dry-run", action="store_true", default=False)

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--owner", default="gardenlinux")
    upload_parser.add_argument("--repo", default="gardenlinux")
    upload_parser.add_argument("--release_id", required=True)
    upload_parser.add_argument("--file_path", required=True)
    upload_parser.add_argument("--dry-run", action="store_true", default=False)

    args = parser.parse_args()

    if args.command == "create":
        body = create_github_release_notes(args.tag, args.commit)
        if args.dry_run:
            print(body)
        else:
            release_id = create_github_release(
                args.owner, args.repo, args.tag, args.commit, body
            )
            write_to_release_id_file(f"{release_id}")
            LOGGER.info(f"Release created with ID: {release_id}")
    elif args.command == "upload":
        upload_to_github_release_page(
            args.owner, args.repo, args.release_id, args.file_path, args.dry_run
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
