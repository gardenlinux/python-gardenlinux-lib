# -*- coding: utf-8 -*-

import json
import re
from logging import Logger
from string import Template
from typing import Optional

from ....apt import DebsrcFile, GardenLinuxRepo
from ....apt.package_repo_info import compare_repo
from ....constants import GL_CONTAINER_REGISTRY_BASE_URL
from ....distro_version import DistroVersion
from ....logger import LoggerSetup
from ..constants import (
    GL_RELEASE_CHARACTERS_LIMIT,
    GL_RELEASE_CVE_PLACEHOLDER,
    GL_RELEASE_MAJOR_TEMPLATE,
    GL_RELEASE_MINOR_TEMPLATE,
    HIGHLIGHT_PACKAGES,
    IMAGE_VARIANTS,
)
from ..deployment_platform import DeploymentPlatform
from ..release import Release
from ..release_images_metadata import ReleaseImagesMetadata


class MarkdownGenerator(object):
    """
    GitHub release notes generator

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: github
    :since:      1.0.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(
        self,
        release: Release,
        releases_s3_bucket_name: str,
        logger: Optional[Logger] = None,
    ):
        """
        Constructor __init__(MarkdownGenerator)

        :param release: GitHub release instance
        :param releases_s3_bucket_name: S3 release bucket
        :param logger: Logger instance

        :since: 1.0.0
        """

        assert release.commitish is not None

        self._commitish = release.commitish
        self._s3_bucket_name = releases_s3_bucket_name
        self._version = release.tag

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.github")

        self._logger = logger

        self._release_images_metadata = ReleaseImagesMetadata(
            self._version, self._commitish, self._s3_bucket_name, self._logger
        )

    @property
    def changes_and_cves_list(self) -> str:
        """
        Get list of fixed CVEs, grouped by upgraded package.

        Note: This result is not perfect, feel free to edit the generated release notes and
        file issues in glvd for improvement suggestions https://github.com/gardenlinux/glvd/issues
        """

        package_changes = self._release_images_metadata.changes_and_cves_list

        if len(package_changes) < 1:
            return GL_RELEASE_CVE_PLACEHOLDER

        out_list = [
            "The following packages have been upgraded, to address the mentioned CVEs:"
        ]

        for package, package_data in package_changes.items():
            upgrade_line = (
                f"- upgrade '{package}'"
                f" from `{package_data['version']['old']}` to `{package_data['version']['new']}`"
            )

            out_list.append(upgrade_line)

            if len(package_data["fixed_cve_list"]) > 0:
                for cve in package_data["fixed_cve_list"]:
                    out_list.append(f"  - {cve}")

        return "\n".join(out_list)

    @property
    def compared_package_versions_table(self) -> str:
        version = DistroVersion(self._version)

        previous_repo = GardenLinuxRepo(version.previous_patch_release)
        current_repo = GardenLinuxRepo(self._version)
        pkg_diffs = sorted(
            compare_repo(previous_repo, current_repo), key=lambda t: t[0]
        )

        out_list = [f"| Package | {version.previous_patch_release} | {self._version} |"]
        out_list.append("|---------|--------------------|-------------------|")

        for pkg in pkg_diffs:
            out_list.append(
                f"|{pkg[0]} | `{pkg[1] if pkg[1] is not None else '-'}` | `{pkg[2] if pkg[2] is not None else '-'}` |"
            )

        return "\n".join(out_list)

    @property
    def kmodbuild_registry_url(self) -> str:
        return f"{GL_CONTAINER_REGISTRY_BASE_URL}/kmodbuild:{self._version}"

    @property
    def package_list(self) -> DebsrcFile:
        return self._release_images_metadata.package_list

    @property
    def release_images_table(self) -> str:
        """
        Generate the table format with collapsible region details
        """

        grouped_data = self._release_images_metadata.grouped_flavors_metadata
        out_list = []

        for variant in grouped_data.keys():
            for platform in sorted(grouped_data[variant].keys()):
                for arch in sorted(grouped_data[variant][platform].keys()):
                    for metadata in grouped_data[variant][platform][arch]:
                        deployment_platform = DeploymentPlatform.new_instance(metadata)
                        data = deployment_platform.published_images_by_deployment

                        if data is None:
                            continue

                        details_content = self._generate_release_images_region_details(
                            deployment_platform
                        )
                        summary_text = self._generate_release_images_region_summary(
                            deployment_platform
                        )

                        download_url = (
                            deployment_platform.generate_s3_image_url_for_bucket(
                                self._s3_bucket_name
                            )
                        )
                        download_link = f"[{deployment_platform.artifact_base_name}.{deployment_platform.image_extension}]({download_url})"

                        out_list.append(
                            f"| {IMAGE_VARIANTS[variant]} "
                            f"| {deployment_platform.full_name} "
                            f"| {arch} "
                            f"| `{deployment_platform.artifact_base_name}` "
                            f"| <details><summary>{summary_text}</summary><br />\n{details_content}</details> "
                            f"| <details><summary>Download</summary><br />\n{download_link}</details> "
                            "|"
                        )

        return "\n".join(out_list)

    @property
    def software_components(self) -> str:
        packages_re = ""

        for package in HIGHLIGHT_PACKAGES:
            if len(packages_re) > 0:
                packages_re += "|"

            packages_re += f"^{re.escape(package)}$"

        packages_re_object = re.compile(packages_re)
        out_list = []

        for entry in self.package_list.values():
            if packages_re_object.match(entry.deb_source):
                out_list.append(repr(entry))

        return "\n".join(out_list)

    def __str__(self) -> str:
        """
        Returns final markdown for the configured reproducibility check

        :return: (str) Markdown
        :since:  1.0.0
        """

        version = DistroVersion(self._version)

        if version.is_patch_release:
            template = Template(GL_RELEASE_MINOR_TEMPLATE)

            out = template.safe_substitute(
                changes=self.changes_and_cves_list,
                compared_package_versions_table=self.compared_package_versions_table,
                components_versions=self.software_components,
                kmodbuild_registry_url=self.kmodbuild_registry_url,
                previous_release_version=version.previous_patch_release,
                published_images_table=self.release_images_table,
            )
        else:
            template = Template(GL_RELEASE_MAJOR_TEMPLATE)

            out = template.safe_substitute(
                components_versions=self.software_components,
                kmodbuild_registry_url=self.kmodbuild_registry_url,
                published_images_table=self.release_images_table,
            )

        if len(out) > GL_RELEASE_CHARACTERS_LIMIT:
            self._logger.error(
                f"Generated release notes following below exceeded the maximum allowed characters of {GL_RELEASE_CHARACTERS_LIMIT}. Truncating:\n{out}"
            )

            out = out[: GL_RELEASE_CHARACTERS_LIMIT - 12] + " [truncated]"

        return out

    def _generate_release_images_region_details(
        self, deployment_platform: DeploymentPlatform
    ) -> str:
        """
        Generate the detailed region information for the collapsible section
        """

        out_list = []

        published_images = deployment_platform.published_images_by_deployment

        match deployment_platform.published_images_mapping_type:
            case "regions_list":
                for region_data in published_images["regions"]:
                    region_line = (
                        f"**{region_data['region']}:** {region_data['image_id']}"
                    )
                    if "image_name" in region_data:
                        region_line += f" ({region_data['image_name']})"

                    out_list.append(region_line)
            case "metadata_root":
                for key, value in published_images["details"].items():
                    out_list.append(f"**{key.replace('_', ' ').title()}:** {value}")
            case "azure_gallery_and_marketplace_list":
                if "gallery_images" in published_images:
                    out_list.append("**Gallery Images:**")

                    for img in published_images["gallery_images"]:
                        out_list.append(
                            f"**{img['azure_cloud']} ({img['hyper_v_generation']}):** {img['image_id']}"
                        )

                if "marketplace_images" in published_images:
                    out_list.append("**Marketplace Images:**")

                    for img in published_images["marketplace_images"]:
                        out_list.append(
                            f"**{img['hyper_v_generation']}:** {img['urn']}"
                        )
            case _:
                out_list.append("<code>" + json.dumps(published_images) + "</code>")

        return "<br />\n".join(out_list)

    def _generate_release_images_region_summary(
        self, deployment_platform: DeploymentPlatform
    ) -> str:
        """
        Generate the summary text for the collapsible section
        """

        published_images = deployment_platform.published_images_by_deployment

        match deployment_platform.published_images_mapping_type:
            case "regions_list":
                count = len(published_images["regions"])
                return f"{count} regions"
            case "metadata_root":
                return "Global availability"
            case "azure_gallery_and_marketplace_list":
                gallery_count = len(published_images.get("gallery_images", []))
                marketplace_count = len(published_images.get("marketplace_images", []))

                return (
                    f"{gallery_count} gallery + {marketplace_count} marketplace images"
                )
            case _:
                return "Details available"
