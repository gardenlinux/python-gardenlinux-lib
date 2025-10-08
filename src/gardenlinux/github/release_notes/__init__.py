from .helpers import download_all_metadata_files, get_package_list
from .sections import (
    release_notes_changes_section,
    release_notes_compare_package_versions_section,
    release_notes_image_ids_section,
    release_notes_software_components_section,
)


def create_github_release_notes(gardenlinux_version, commitish, releases_s3_bucket_name):
    package_list = get_package_list(gardenlinux_version)

    output = ""

    output += release_notes_changes_section(gardenlinux_version)

    output += release_notes_software_components_section(package_list)

    output += release_notes_compare_package_versions_section(
        gardenlinux_version, package_list
    )

    metadata_files = download_all_metadata_files(gardenlinux_version, commitish, releases_s3_bucket_name)

    output += release_notes_image_ids_section(metadata_files)

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
