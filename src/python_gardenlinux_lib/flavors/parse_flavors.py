#!/usr/bin/env python

from git import Git
import base64
import json
import logging
import os
import subprocess
import yaml

from .parser import (
    group_by_arch,
    remove_arch,
    should_include_only,
    should_exclude,
    validate_flavors
)

from .parser import parse_flavors as parse_flavors_data

from ..constants import GL_FLAVORS_SCHEMA

# Define the schema for validation
SCHEMA = GL_FLAVORS_SCHEMA


def find_repo_root():
    """Finds the root directory of the Git repository."""

    return Git(".").rev_parse("--show-superproject-working-tree")

def _get_flavors_from_github(commit):
    """Returns the flavors.yaml from GitHub if readable."""

    # Try flavors.yaml first
    api_path = "/repos/gardenlinux/gardenlinux/contents/flavors.yaml"
    if commit != "latest":
        api_path = f"{api_path}?ref={commit}"
    command = ["gh", "api", api_path]
    logger.debug(f"Fetching flavors.yaml from GitHub for commit {commit_short}")
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    if result.returncode == 0:
        content_data = json.loads(result.stdout)
        return base64.b64decode(content_data["content"]).decode("utf-8")
    else:
        raise RuntimeError("Failed receiving result from GitHub: {0}".format(result.stderr))


def parse_flavors_commit(
    commit=None,
    version=None,
    query_s3=False,
    s3_objects=None,
    logger=None,
    include_only_patterns=None,
    wildcard_excludes=None,
    only_build=False,
    only_test=False,
    only_test_platform=False,
    only_publish=False,
    filter_categories=None,
    exclude_categories=None,
):
    """
    Parse flavors for a specific commit, optionally checking S3 artifacts.

    Args:
        commit (str): The git commit hash to check
        version (dict, optional): Version info with 'major' and optional 'minor' keys
        query_s3 (bool): Whether to check S3 artifacts if no flavors.yaml found
        s3_objects (dict, optional): Pre-fetched S3 artifacts data
        logger (logging.Logger): Logger instance to use
        include_only_patterns (list): Restrict combinations to those matching wildcard patterns
        wildcard_excludes (list): Exclude combinations based on wildcard patterns
        only_build (bool): Filter combinations to include only those with build enabled
        only_test (bool): Filter combinations to include only those with test enabled
        only_test_platform (bool): Filter combinations to include only platforms with test-platform: true
        only_publish (bool): Filter combinations to include only those with publish enabled
        filter_categories (list): Filter combinations to include only platforms belonging to specified categories
        exclude_categories (list): Exclude platforms belonging to specified categories

    Returns:
        list: List of flavor strings, or empty list if no flavors found
    """

    if logger is None:
        logger = logging.getLogger("gardenlinux.lib.flavors")
        logger.addHandler(logging.NullHandler())

    version_info = (
        f"{version['major']}.{version.get('minor', 0)}" if version else "unknown"
    )
    if commit is None:
        commit = "latest"
    commit_short = commit[:8]

    logger.debug(
        f"Checking flavors for version {version_info} (commit {commit_short})"
    )

    flavors_content = None

    if os.access("./flavors.yaml", os.F_OK | os.R_OK):
        with open("./flavors.yaml", "r") as fp:
            flavors_content = fp.read()
    else:
        try:
            flavors_content = _get_flavors_from_github()
        except Exception as exc:
            logger.debug(exc)

    if flavors_content is not None:
        # Parse flavors with all filters
        combinations = parse_flavors_data(
            yaml.safe_load(flavors_content),
            include_only_patterns=include_only_patterns or [],
            wildcard_excludes=wildcard_excludes or [],
            only_build=only_build,
            only_test=only_test,
            only_test_platform=only_test_platform,
            only_publish=only_publish,
            filter_categories=filter_categories or [],
            exclude_categories=exclude_categories or [],
        )

        all_flavors = set()
        for _, combination in combinations:
            all_flavors.add(combination)

        if all_flavors:
            logger.info(f"Found {len(all_flavors)} flavors in flavors.yaml")
            return sorted(all_flavors)
        else:
            logger.info("No flavors found in flavors.yaml")
    elif query_s3 and s3_objects and isinstance(s3_objects, dict):
        logger.debug("Checking S3 artifacts")
        index = s3_objects.get("index", {})
        artifacts = s3_objects.get("artifacts", [])

        # Try index lookup first
        search_key = f"{version_info}-{commit_short}"
        if search_key in index:
            flavors = index[search_key]
            logger.debug(f"Found flavors in S3 index for {search_key}")
        else:
            # If no index match, search through artifacts
            found_flavors = set()

            # Search for artifacts matching version and commit
            for key in artifacts:
                if version_info in key and commit_short in key:
                    try:
                        parts = key.split("/")
                        if len(parts) >= 2:
                            flavor_with_version = parts[1]
                            flavor = flavor_with_version.rsplit(
                                "-" + version_info, 1
                            )[0]
                            if flavor:
                                found_flavors.add(flavor)
                    except Exception as e:
                        logger.debug(f"Error parsing artifact key {key}: {e}")
                        continue

            flavors = list(found_flavors)

        # Apply filters to S3 flavors
        filtered_flavors = []
        for flavor in flavors:
            # Create a dummy combination with amd64 architecture for filtering
            combination = ("amd64", flavor)
            if should_include_only(
                flavor, include_only_patterns or []
            ) and not should_exclude(flavor, wildcard_excludes or [], []):
                filtered_flavors.append(flavor)

        if filtered_flavors:
            logger.info(
                f"Found {len(filtered_flavors)} flavors in S3 artifacts after filtering"
            )
            return sorted(filtered_flavors)
        else:
            logger.info(
                f"No flavors found in S3 for version {version_info} and commit {commit_short} after filtering"
            )

        return []
