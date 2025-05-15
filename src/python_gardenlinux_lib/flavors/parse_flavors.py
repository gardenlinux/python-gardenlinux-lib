#!/usr/bin/env python
import argparse
import base64
import fnmatch
import json
import logging
import os
import re
import subprocess
import sys
import time

import boto3
from botocore.exceptions import ClientError
from jsonschema import validate, ValidationError
import yaml

# Create a null logger as default
null_logger = logging.getLogger("gardenlinux.lib.flavors")
null_logger.addHandler(logging.NullHandler())

# Define the schema for validation
SCHEMA = {
    "type": "object",
    "properties": {
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "flavors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "features": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "arch": {"type": "string"},
                                "build": {"type": "boolean"},
                                "test": {"type": "boolean"},
                                "test-platform": {"type": "boolean"},
                                "publish": {"type": "boolean"},
                            },
                            "required": [
                                "features",
                                "arch",
                                "build",
                                "test",
                                "test-platform",
                                "publish",
                            ],
                        },
                    },
                },
                "required": ["name", "category", "flavors"],
            },
        },
    },
    "required": ["targets"],
}


def find_repo_root():
    """Finds the root directory of the Git repository."""
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        return root
    except subprocess.CalledProcessError:
        sys.exit("Error: Unable to determine Git repository root.")


def validate_flavors(data):
    """Validate the flavors.yaml data against the schema."""
    try:
        validate(instance=data, schema=SCHEMA)
    except ValidationError as e:
        sys.exit(f"Validation Error: {e.message}")


def should_exclude(combination, excludes, wildcard_excludes):
    """
    Checks if a combination should be excluded based on exact match or wildcard patterns.
    """
    # Exclude if in explicit excludes
    if combination in excludes:
        return True
    # Exclude if matches any wildcard pattern
    return any(fnmatch.fnmatch(combination, pattern) for pattern in wildcard_excludes)


def should_include_only(combination, include_only_patterns):
    """
    Checks if a combination should be included based on `--include-only` wildcard patterns.
    If no patterns are provided, all combinations are included by default.
    """
    if not include_only_patterns:
        return True
    return any(
        fnmatch.fnmatch(combination, pattern) for pattern in include_only_patterns
    )


def parse_flavors_data(
    data,
    include_only_patterns=None,
    wildcard_excludes=None,
    only_build=False,
    only_test=False,
    only_test_platform=False,
    only_publish=False,
    filter_categories=None,
    exclude_categories=None,
):
    """Parse flavors.yaml data and generate combinations."""
    combinations = []

    # Validate input data against schema
    validate_flavors(data)

    # Process each target platform
    for target in data["targets"]:
        platform_name = target["name"]
        platform_category = target["category"]

        # Skip if platform category is in exclude list
        if exclude_categories and platform_category in exclude_categories:
            continue

        # Skip if filtering by category and platform category not in filter list
        if filter_categories and platform_category not in filter_categories:
            continue

        # Skip if platform test-platform flag doesn't match filter
        if only_test_platform and not target.get("test-platform", False):
            continue

        # Process each flavor configuration for this platform
        for flavor in target["flavors"]:
            # Skip if build/test/publish flags don't match filters
            if only_build and not flavor.get("build", False):
                continue
            if only_test and not flavor.get("test", False):
                continue
            if only_publish and not flavor.get("publish", False):
                continue

            # Generate the flavor string with architecture
            features = flavor["features"]
            arch = flavor["arch"]

            # Build the flavor string
            if features:
                # Sort features to ensure consistent order
                # Remove any leading/trailing underscores and handle special cases
                cleaned_features = []
                for feature in sorted(features):
                    # Remove leading/trailing underscores
                    feature = feature.strip("_")
                    # Handle special cases (like 'gardener' that should come first)
                    if feature == "gardener":
                        cleaned_features.insert(0, feature)
                    else:
                        cleaned_features.append(feature)

                # Join features with underscores
                feature_string = "_".join(cleaned_features)
                # Combine platform and features
                combination = f"{platform_name}-{feature_string}-{arch}"
            else:
                combination = f"{platform_name}-{arch}"

            # Add to combinations if it matches include patterns and doesn't match exclude patterns
            if should_include_only(
                combination, include_only_patterns or []
            ) and not should_exclude(combination, wildcard_excludes or [], []):
                combinations.append((arch, combination))

    return combinations


def group_by_arch(combinations):
    """Groups combinations by architecture into a JSON dictionary."""
    arch_dict = {}
    for arch, combination in combinations:
        arch_dict.setdefault(arch, []).append(combination)
    for arch in arch_dict:
        arch_dict[arch] = sorted(set(arch_dict[arch]))  # Deduplicate and sort
    return arch_dict


def remove_arch(combinations):
    """Removes the architecture from combinations."""
    return [combination.replace(f"-{arch}", "") for arch, combination in combinations]


def generate_markdown_table(combinations, no_arch):
    """Generate a markdown table of platforms and their flavors."""
    table = "| Platform   | Architecture       | Flavor                                  |\n"
    table += "|------------|--------------------|------------------------------------------|\n"

    for arch, combination in combinations:
        platform = combination.split("-")[0]
        table += (
            f"| {platform:<10} | {arch:<18} | `{combination}`                   |\n"
        )

    return table


def parse_flavors_commit(
    commit=None,
    version=None,
    query_s3=False,
    s3_objects=None,
    logger=null_logger,
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
    try:
        version_info = (
            f"{version['major']}.{version.get('minor', 0)}" if version else "unknown"
        )
        if commit is None:
            commit = "latest"
        commit_short = commit[:8]

        logger.debug(
            f"Checking flavors for version {version_info} (commit {commit_short})"
        )

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
            yaml_content = base64.b64decode(content_data["content"]).decode("utf-8")
            flavors_data = yaml.safe_load(yaml_content)

            # Parse flavors with all filters
            combinations = parse_flavors_data(
                flavors_data,
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

        # If no flavors.yaml found and query_s3 is enabled, try S3 artifacts
        if query_s3 and s3_objects and isinstance(s3_objects, dict):
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

    except Exception as e:
        logger.error(f"Error parsing flavors for commit {commit_short}: {e}")
        return []


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parse flavors.yaml and generate combinations."
    )
    parser.add_argument(
        "--commit",
        type=str,
        default="latest",
        help="The git commit hash (short or long) to use.",
    )
    parser.add_argument(
        "--no-arch",
        action="store_true",
        help="Exclude architecture from the flavor output.",
    )
    parser.add_argument(
        "--include-only",
        action="append",
        help="Restrict combinations to those matching wildcard patterns (can be specified multiple times).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude combinations based on wildcard patterns (can be specified multiple times).",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Filter combinations to include only those with build enabled.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Filter combinations to include only those with test enabled.",
    )
    parser.add_argument(
        "--test-platform",
        action="store_true",
        help="Filter combinations to include only platforms with test-platform: true.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Filter combinations to include only those with publish enabled.",
    )
    parser.add_argument(
        "--category",
        action="append",
        help="Filter combinations to include only platforms belonging to the specified categories (can be specified multiple times).",
    )
    parser.add_argument(
        "--exclude-category",
        action="append",
        help="Exclude platforms belonging to the specified categories (can be specified multiple times).",
    )
    parser.add_argument(
        "--json-by-arch",
        action="store_true",
        help="Output a JSON dictionary where keys are architectures and values are lists of flavors.",
    )
    parser.add_argument(
        "--markdown-table-by-platform",
        action="store_true",
        help="Generate a markdown table by platform.",
    )
    args = parser.parse_args()
    return args


def main():
    """Main function for command line usage."""
    args = parse_arguments()

    # Get flavors using parse_flavors_commit
    flavors = parse_flavors_commit(
        commit=args.commit,
        include_only_patterns=args.include_only or [],
        wildcard_excludes=args.exclude or [],
        only_build=args.build,
        only_test=args.test,
        only_test_platform=args.test_platform,
        only_publish=args.publish,
        filter_categories=args.category or [],
        exclude_categories=args.exclude_category or [],
    )

    if not flavors:
        sys.exit(1)

    # Output the results in the requested format
    if args.json_by_arch:
        # Convert flavors to (arch, flavor) tuples for grouping
        combinations = []
        for flavor in flavors:
            arch = flavor.split("-")[-1]  # Get architecture from the end
            combinations.append((arch, flavor))

        grouped_combinations = group_by_arch(combinations)
        # If --no-arch, strip architectures from the grouped output
        if args.no_arch:
            grouped_combinations = {
                arch: sorted(set(item.replace(f"-{arch}", "") for item in items))
                for arch, items in grouped_combinations.items()
            }
        print(json.dumps(grouped_combinations, indent=2))
    elif args.markdown_table_by_platform:
        # Convert flavors to (arch, flavor) tuples for table
        combinations = []
        for flavor in flavors:
            arch = flavor.split("-")[-1]  # Get architecture from the end
            combinations.append((arch, flavor))

        markdown_table = generate_markdown_table(combinations, args.no_arch)
        print(markdown_table)
    else:
        if args.no_arch:
            # Remove architecture from each flavor
            no_arch_flavors = []
            for flavor in flavors:
                no_arch_flavor = "-".join(
                    flavor.split("-")[:-1]
                )  # Remove last component (arch)
                no_arch_flavors.append(no_arch_flavor)
            print("\n".join(sorted(set(no_arch_flavors))))
        else:
            print("\n".join(sorted(flavors)))


if __name__ == "__main__":
    main()
