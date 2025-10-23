#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
gl-flavors-parse main entrypoint
"""

import json
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory

from ..constants import GL_REPOSITORY_URL
from ..git import Repository
from .parser import Parser


def _get_flavors_file_data(flavors_file):
    if not flavors_file.exists():
        raise RuntimeError(f"Error: {flavors_file} does not exist.")

    # Load and validate the flavors.yaml
    with flavors_file.open("r") as fp:
        return fp.read()


def generate_markdown_table(combinations, no_arch):
    """
    Generate a markdown table of platforms and their flavors.

    :param combinations: List of tuples of architectures and flavors
    :param no_arch: Noop

    :return: (str) Markdown table
    :since:  0.7.0
    """

    table = "| Platform   | Architecture       | Flavor                                  |\n"
    table += "|------------|--------------------|------------------------------------------|\n"

    for arch, combination in combinations:
        platform = combination.split("-")[0]
        table += (
            f"| {platform:<10} | {arch:<18} | `{combination}`                   |\n"
        )

    return table


def parse_args():
    """
    Parses arguments used for main()

    :return: (object) Parsed argparse.ArgumentParser namespace
    :since:  0.7.0
    """

    parser = ArgumentParser(description="Parse flavors.yaml and generate combinations.")

    parser.add_argument(
        "--commit",
        default=None,
        help="Commit hash to fetch flavors.yaml from GitHub. An existing 'flavors.yaml' file will be preferred.",
    )
    parser.add_argument(
        "--no-arch",
        action="store_true",
        help="Exclude architecture from the flavor output.",
    )
    parser.add_argument(
        "--include-only",
        action="append",
        default=[],
        help="Restrict combinations to those matching wildcard patterns (can be specified multiple times).",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Exclude combinations based on wildcard patterns (can be specified multiple times).",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Filter combinations to include only those with build enabled.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Filter combinations to include only those with publish enabled.",
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
        "--category",
        action="append",
        default=[],
        help="Filter combinations to include only platforms belonging to the specified categories (can be specified multiple times).",
    )
    parser.add_argument(
        "--exclude-category",
        action="append",
        default=[],
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

    return parser.parse_args()


def main():
    """
    gl-flavors-parse main()

    :since: 0.7.0
    """

    args = parse_args()

    try:
        flavors_data = _get_flavors_file_data(Path(Repository().root, "flavors.yaml"))
    except RuntimeError:
        with TemporaryDirectory() as git_directory:
            repo = Repository.checkout_repo_sparse(
                git_directory,
                ["flavors.yaml"],
                repo_url=GL_REPOSITORY_URL,
                commit=args.commit,
            )

            flavors_data = _get_flavors_file_data(Path(repo.root, "flavors.yaml"))

    combinations = Parser(flavors_data).filter(
        include_only_patterns=args.include_only,
        wildcard_excludes=args.exclude,
        only_build=args.build,
        only_test=args.test,
        only_test_platform=args.test_platform,
        only_publish=args.publish,
        filter_categories=args.category,
        exclude_categories=args.exclude_category,
    )

    if args.json_by_arch:
        grouped_combinations = Parser.group_by_arch(combinations)

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
            printable_combinations = sorted(set(Parser.remove_arch(combinations)))
        else:
            printable_combinations = sorted(set(comb[1] for comb in combinations))

        print("\n".join(sorted(set(printable_combinations))))


if __name__ == "__main__":
    # Create a null logger as default
    main()
