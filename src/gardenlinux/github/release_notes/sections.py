import re
import textwrap

import requests
import yaml
from yaml import SafeLoader

from gardenlinux.constants import GLVD_BASE_URL, REQUESTS_TIMEOUTS
from gardenlinux.logger import LoggerSetup

from .deployment_platform.ali_cloud import AliCloud
from .deployment_platform.amazon_web_services import AmazonWebServices
from .deployment_platform.azure import Azure
from .deployment_platform.google_cloud import GoogleCloud
from .deployment_platform.openstack import OpenStack
from .deployment_platform.openstack_baremetal import OpenStackBareMetal
from .helpers import compare_apt_repo_versions, get_variant_from_flavor

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release_notes", "INFO")

IMAGE_IDS_VARIANT_ORDER = ["legacy", "usi", "tpm2_trustedboot"]
IMAGE_IDS_VARIANT_TABLE_NAMES = {"legacy": "Default", "usi": "USI", "tpm2_trustedboot": "TPM2"}
IMAGE_IDS_VARIANT_NAMES = {
    "legacy": "Default",
    "usi": "USI (Unified System Image)",
    "tpm2_trustedboot": "TPM2 Trusted Boot",
}
PLATFORMS = {
    "ali": AliCloud(),
    "aws": AmazonWebServices(),
    "gcp": GoogleCloud(),
    "azure": Azure(),
    "openstack": OpenStack(),
    "openstackbaremetal": OpenStackBareMetal(),
}


def release_notes_changes_section(gardenlinux_version):
    """
    Get list of fixed CVEs, grouped by upgraded package.
    Note: This result is not perfect, feel free to edit the generated release notes and
    file issues in glvd for improvement suggestions https://github.com/gardenlinux/glvd/issues
    """
    try:
        url = f"{GLVD_BASE_URL}/patchReleaseNotes/{gardenlinux_version}"
        response = requests.get(url, timeout=REQUESTS_TIMEOUTS)
        response.raise_for_status()
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
        # There are expected error cases,
        # for example with versions not supported by glvd (1443.x)
        # or when the api is not available
        # Fail gracefully by adding the placeholder we previously used,
        # so that the release note generation does not fail.
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


def generate_table_format(grouped_data):
    """
    Generate the table format with collapsible region details
    """
    output = "| Variant | Platform | Architecture | Flavor | Regions & Image IDs | Download Links |\n"
    output += "|---------|----------|--------------|--------|---------------------|----------------|\n"

    for variant in IMAGE_IDS_VARIANT_ORDER:
        if variant not in grouped_data:
            continue

        for platform in sorted(grouped_data[variant].keys()):
            for arch in sorted(grouped_data[variant][platform].keys()):
                for metadata in grouped_data[variant][platform][arch]:
                    data = PLATFORMS[platform].published_images_by_regions(metadata)
                    if data is None:
                        continue

                    details_content = PLATFORMS[platform].region_details()
                    summary_text = PLATFORMS[platform].summary_text()

                    download_link = PLATFORMS[platform].artifact_for_flavor(data['flavor'])

                    variant_display = IMAGE_IDS_VARIANT_TABLE_NAMES[variant]
                    output += (f"| {variant_display} "
                               f"| {PLATFORMS[platform].full_name()} "
                               f"| {arch} "
                               f"| `{data['flavor']}` "
                               f"| <details><summary>{summary_text}</summary><br>{details_content}</details> "
                               f"| <details><summary> Download </summary> <br> {download_link} </details> "
                               "|\n")

    return output


def release_notes_image_ids_section(metadata_files):
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

    output = "## Published Images\n\n"

    output += "<details>\n<summary>📊 Table View</summary>\n\n"
    output += generate_table_format(grouped_data)
    output += "\n</details>\n\n"

    return output
