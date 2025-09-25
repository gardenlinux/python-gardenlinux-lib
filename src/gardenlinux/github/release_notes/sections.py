import re
import textwrap

import requests

from gardenlinux.constants import GLVD_BASE_URL, REQUESTS_TIMEOUTS
from gardenlinux.logger import LoggerSetup

from .helpers import compare_apt_repo_versions

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release_notes", "INFO")


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
