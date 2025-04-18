from jsonschema import validate as jsonschema_validate
import fnmatch

from ..constants import GL_FLAVORS_SCHEMA

def validate_flavors(data):
    """Validate the flavors.yaml data against the schema."""
    jsonschema_validate(instance=data, schema=GL_FLAVORS_SCHEMA)

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
    return any(fnmatch.fnmatch(combination, pattern) for pattern in include_only_patterns)

def parse_flavors(
    data,
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
    combinations = []  # Use a list for consistent order

    for target in data['targets']:
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
            if should_exclude(combination, [], wildcard_excludes):
                continue

            # Apply include-only filters
            if not should_include_only(combination, include_only_patterns):
                continue

            combinations.append((arch, combination))

    return sorted(combinations, key=lambda x: x[1].split("-")[0])  # Sort by platform name

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
