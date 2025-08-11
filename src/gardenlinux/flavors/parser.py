# -*- coding: utf-8 -*-

"""
Flavors parser
"""

from jsonschema import validate as jsonschema_validate
import fnmatch
import yaml

from ..constants import GL_FLAVORS_SCHEMA
from ..logger import LoggerSetup


class Parser(object):
    """
    Parser for GardenLinux `flavors.yaml`.

    :author:     Garden Linux Maintainers
    :copyright:  Copyright 2024 SAP SE
    :package:    gardenlinux
    :subpackage: flavors
    :since:      0.7.0
    :license:    https://www.apache.org/licenses/LICENSE-2.0
                 Apache License, Version 2.0
    """

    def __init__(self, data, logger=None):
        """
        Constructor __init__(Parser)

        :param data: Flavors data to parse
        :param logger: Logger instance

        :since: 0.7.0
        """

        flavors_data = yaml.safe_load(data) if isinstance(data, str) else data
        jsonschema_validate(instance=flavors_data, schema=GL_FLAVORS_SCHEMA)

        if logger is None or not logger.hasHandlers():
            logger = LoggerSetup.get_logger("gardenlinux.flavors")

        self._flavors_data = flavors_data
        self._logger = logger

        self._logger.debug(
            "flavors.Parser initialized with data: {0!r}".format(flavors_data)
        )

    def filter(
        self,
        include_only_patterns=[],
        wildcard_excludes=[],
        only_build=False,
        only_test=False,
        only_test_platform=False,
        only_publish=False,
        filter_categories=[],
        exclude_categories=[],
    ):
        """
        Filters flavors data and generates combinations.

        :param include_only_patterns: Include pattern list
        :param wildcard_excludes:     Exclude wildcard list
        :param only_build:            Return only build-enabled flavors
        :param only_test:             Return only test-enabled flavors
        :param only_test_platform:    Return only platform-test-enabled flavors
        :param only_publish:          Return only flavors to be published
        :param filter_categories:     List of categories to include
        :param exclude_categories:    List of categories to exclude

        :return: (list) Filtered flavors
        :since:  0.7.0
        """

        self._logger.debug("flavors.Parser filtering with {0}".format(locals()))

        combinations = []  # Use a list for consistent order

        for target in self._flavors_data["targets"]:
            name = target["name"]
            category = target.get("category", "")

            # Apply category filters
            if filter_categories and category not in filter_categories:
                continue
            if exclude_categories and category in exclude_categories:
                continue

            for flavor in target["flavors"]:
                features = flavor.get("features", [])
                arch = flavor.get("arch", "amd64")
                build = flavor.get("build", False)
                test = flavor.get("test", False)
                test_platform = flavor.get("test-platform", False)
                publish = flavor.get("publish", False)

                # Apply flag-specific filters in the order: build, test, test-platform, publish
                if only_build and not build:
                    continue
                if only_test and not test:
                    continue
                if only_test_platform and not test_platform:
                    continue
                if only_publish and not publish:
                    continue

                # Process features
                formatted_features = f"-{'-'.join(features)}" if features else ""

                # Construct the combination
                combination = f"{name}-{formatted_features}-{arch}"

                # Format the combination to clean up "--" and "-_"
                combination = combination.replace("--", "-").replace("-_", "_")

                # Exclude combinations explicitly
                if Parser.should_exclude(combination, [], wildcard_excludes):
                    continue

                # Apply include-only filters
                if not Parser.should_include_only(combination, include_only_patterns):
                    continue

                combinations.append((arch, combination))

        return sorted(
            combinations, key=lambda platform: platform[1].split("-")[0]
        )  # Sort by platform name

    @staticmethod
    def group_by_arch(combinations):
        """
        Groups combinations by architecture into a dictionary.

        :param combinations: Flavor combinations to group

        :return: (list) Grouped flavor combinations
        :since:  0.7.0
        """

        arch_dict = {}
        for arch, combination in combinations:
            arch_dict.setdefault(arch, []).append(combination)
        for arch in arch_dict:
            arch_dict[arch] = sorted(set(arch_dict[arch]))  # Deduplicate and sort
        return arch_dict

    @staticmethod
    def remove_arch(combinations):
        """
        Removes the architecture from combinations.

        :param combinations: Flavor combinations to remove the architecture

        :return: (list) Changed flavor combinations
        :since:  0.7.0
        """

        return [
            combination.replace(f"-{arch}", "") for arch, combination in combinations
        ]

    @staticmethod
    def should_exclude(combination, excludes, wildcard_excludes):
        """
        Checks if a combination should be excluded based on exact match or wildcard patterns.

        :param combinations:      Flavor combinations
        :param excludes:          List of features to exclude
        :param wildcard_excludes: List of feature wildcards to exclude

        :return: (bool) True if excluded
        :since:  0.7.0
        """

        # Exclude if in explicit excludes
        if combination in excludes:
            return True
        # Exclude if matches any wildcard pattern
        return any(
            fnmatch.fnmatch(combination, pattern) for pattern in wildcard_excludes
        )

    @staticmethod
    def should_include_only(combination, include_only_patterns):
        """
        Checks if a combination should be included based on `--include-only` wildcard patterns.
        If no patterns are provided, all combinations are included by default.

        :param combinations:          Flavor combinations
        :param include_only_patterns: List of features to include

        :return: (bool) True if included
        :since:  0.7.0
        """

        if not include_only_patterns:
            return True
        return any(
            fnmatch.fnmatch(combination, pattern) for pattern in include_only_patterns
        )
