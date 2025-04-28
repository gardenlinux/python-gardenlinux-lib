from jsonschema import validate as jsonschema_validate
import fnmatch
import logging
import yaml

from ..constants import GL_FLAVORS_SCHEMA

class Parser(object):
    def __init__(self, data, logger = None):
        flavors_data = (yaml.safe_load(data) if isinstance(data, str) else data)
        jsonschema_validate(instance=flavors_data, schema=GL_FLAVORS_SCHEMA)

        self._flavors_data = flavors_data
        self._logger = logger

        if self._logger is None:
            self._logger = logging.getLogger("gardenlinux.flavors")

        if not self._logger.hasHandlers():
            self._logger.addHandler(logging.NullHandler())

        self._logger.debug("flavors.Parser initialized with data: {0!r}".format(flavors_data))

    def filter(
        self,
        include_only_patterns=[],
        wildcard_excludes=[],
        only_build=False,
        only_test=False,
        only_test_platform=False,
        only_publish=False,
        filter_categories=[],
        exclude_categories=[]
    ):
        """Parses the flavors.yaml file and generates combinations."""
        self._logger.debug("flavors.Parser filtering with {0}".format(locals()))

        combinations = []  # Use a list for consistent order

        for target in self._flavors_data['targets']:
            name = target['name']
            category = target.get('category', '')

            # Apply category filters
            if filter_categories and category not in filter_categories:
                continue
            if exclude_categories and category in exclude_categories:
                continue

            for flavor in target['flavors']:
                features = flavor.get('features', [])
                arch = flavor.get('arch', 'amd64')
                build = flavor.get('build', False)
                test = flavor.get('test', False)
                test_platform = flavor.get('test-platform', False)
                publish = flavor.get('publish', False)

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

        return sorted(combinations, key=lambda platform: platform[1].split("-")[0])  # Sort by platform name

    @staticmethod
    def group_by_arch(combinations):
        """Groups combinations by architecture into a JSON dictionary."""
        arch_dict = {}
        for arch, combination in combinations:
            arch_dict.setdefault(arch, []).append(combination)
        for arch in arch_dict:
            arch_dict[arch] = sorted(set(arch_dict[arch]))  # Deduplicate and sort
        return arch_dict

    @staticmethod
    def remove_arch(combinations):
        """Removes the architecture from combinations."""
        return [combination.replace(f"-{arch}", "") for arch, combination in combinations]

    @staticmethod
    def should_exclude(combination, excludes, wildcard_excludes):
        """
        Checks if a combination should be excluded based on exact match or wildcard patterns.
        """
        # Exclude if in explicit excludes
        if combination in excludes:
            return True
        # Exclude if matches any wildcard pattern
        return any(fnmatch.fnmatch(combination, pattern) for pattern in wildcard_excludes)

    @staticmethod
    def should_include_only(combination, include_only_patterns):
        """
        Checks if a combination should be included based on `--include-only` wildcard patterns.
        If no patterns are provided, all combinations are included by default.
        """
        if not include_only_patterns:
            return True
        return any(fnmatch.fnmatch(combination, pattern) for pattern in include_only_patterns)
