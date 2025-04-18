#!/usr/bin/env python3

from argparse import ArgumentParser
from git import Git
import json
import os
import sys
import yaml

from jsonschema import ValidationError
from .parser import group_by_arch, parse_flavors, validate_flavors


def generate_markdown_table(combinations, no_arch):
    """Generate a markdown table of platforms and their flavors."""
    table = "| Platform   | Architecture       | Flavor                                  |\n"
    table += "|------------|--------------------|------------------------------------------|\n"

    for arch, combination in combinations:
        platform = combination.split("-")[0]
        table += f"| {platform:<10} | {arch:<18} | `{combination}`                   |\n"

    return table

def parse_args():
    parser = ArgumentParser(description="Parse flavors.yaml and generate combinations.")

    parser.add_argument("--no-arch", action="store_true", help="Exclude architecture from the flavor output.")
    parser.add_argument(
        "--include-only",
        action="append",
        default=[],
        help="Restrict combinations to those matching wildcard patterns (can be specified multiple times)."
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude combinations based on wildcard patterns (can be specified multiple times)."
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Filter combinations to include only those with build enabled."
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Filter combinations to include only those with publish enabled."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Filter combinations to include only those with test enabled."
    )
    parser.add_argument(
        "--test-platform",
        action="store_true",
        help="Filter combinations to include only platforms with test-platform: true."
    )
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help="Filter combinations to include only platforms belonging to the specified categories (can be specified multiple times)."
    )
    parser.add_argument(
        "--exclude-category",
        action="append",
        default=[],
        help="Exclude platforms belonging to the specified categories (can be specified multiple times)."
    )
    parser.add_argument(
        "--json-by-arch",
        action="store_true",
        help="Output a JSON dictionary where keys are architectures and values are lists of flavors."
    )
    parser.add_argument(
        "--markdown-table-by-platform",
        action="store_true",
        help="Generate a markdown table by platform."
    )

    return parser.parse_args()

def main():
    args = parse_args()

    repo_path = Git(".").rev_parse("--show-superproject-working-tree")
    flavors_file = os.path.join(repo_path, 'flavors.yaml')

    if not os.path.isfile(flavors_file):
        sys.exit(f"Error: {flavors_file} does not exist.")

    # Load and validate the flavors.yaml
    with open(flavors_file, 'r') as file:
        flavors_data = yaml.safe_load(file)

    try:
        validate_flavors(flavors_data)
    except ValidationError as e:
        sys.exit(f"Validation Error: {e.message}")

    combinations = parse_flavors(
        flavors_data,
        include_only_patterns=args.include_only,
        wildcard_excludes=args.exclude,
        only_build=args.build,
        only_test=args.test,
        only_test_platform=args.test_platform,
        only_publish=args.publish,
        filter_categories=args.category,
        exclude_categories=args.exclude_category
    )

    if args.json_by_arch:
        grouped_combinations = group_by_arch(combinations)

        # If --no-arch, strip architectures from the grouped output
        if args.no_arch:
            grouped_combinations = {
                arch: sorted(set(item.replace(f"-{arch}", "") for item in items))
                for arch, items in grouped_combinations.items()
            }

        print(json.dumps(grouped_combinations, indent=2))
    elif args.markdown_table_by_platform:
        print(generate_markdown_table(combinations, args.no_arch))
    else:
        if args.no_arch:
            printable_combinations = sorted(set(remove_arch(combinations)))
        else:
            printable_combinations = sorted(set(comb[1] for comb in combinations))

        print("\n".join(sorted(set(printable_combinations))))


if __name__ == "__main__":
    # Create a null logger as default
    main()
