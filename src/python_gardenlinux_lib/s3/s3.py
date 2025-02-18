#!/usr/bin/env python
import argparse
import json
import logging
import os
import re
import sys
import time

import boto3
import yaml

# Create a null logger as default
null_logger = logging.getLogger("gardenlinux.lib.s3")
null_logger.addHandler(logging.NullHandler())


def get_s3_client():
    """Get or create an S3 client."""
    if not hasattr(get_s3_client, "_client"):
        get_s3_client._client = boto3.client("s3")
    return get_s3_client._client


def fetch_s3_bucket_contents(bucket_name, prefix="", logger=null_logger):
    """
    Fetch contents of an S3 bucket with prefix.

    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): Prefix for filtering objects
        logger (logging.Logger): Logger instance to use

    Returns:
        list: List of S3 object contents
    """
    s3_client = get_s3_client()
    objects = []

    try:
        paginator = s3_client.get_paginator("list_objects_v2")

        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if "Contents" in page:
                objects.extend(page["Contents"])

        return objects
    except Exception as e:
        logger.error(f"Error fetching objects from bucket {bucket_name}: {e}")
        return []


def get_s3_artifacts(
    bucket_name,
    prefix,
    cache_file=".artifacts_cache.json",
    cache_ttl=3600,
    logger=null_logger,
):
    """
    Get and cache S3 artifacts list with indexed searching.

    Args:
        bucket_name (str): Name of the S3 bucket
        prefix (str): Prefix for S3 objects
        cache_file (str): Path to cache file
        cache_ttl (int): Cache time-to-live in seconds
        logger (logging.Logger): Logger instance to use

    Returns:
        dict: Dictionary containing 'index' and 'artifacts' keys
    """
    index_file = ".artifacts_index.json"

    try:
        # Check if cache files exist and are fresh
        if os.path.exists(cache_file) and os.path.exists(index_file):
            cache_age = time.time() - os.path.getmtime(cache_file)
            if cache_age < cache_ttl:
                try:
                    with open(cache_file, "r") as f:
                        artifacts = json.load(f)
                    with open(index_file, "r") as f:
                        index = json.load(f)
                    logger.debug("Using cached artifacts data")
                    return {"index": index, "artifacts": artifacts}
                except json.JSONDecodeError:
                    logger.warning("Cache files corrupted, will fetch fresh data")
                    try:
                        os.remove(cache_file)
                        os.remove(index_file)
                    except OSError:
                        pass

        # If no cache or expired, fetch from artifacts bucket
        logger.info(f"Fetching artifacts from s3://{bucket_name}/{prefix}")
        objects = fetch_s3_bucket_contents(bucket_name, prefix, logger)

        if not objects:
            logger.warning("No objects found in artifacts bucket")
            return {"index": {}, "artifacts": []}

        # Extract just the keys
        artifacts = [obj["Key"] for obj in objects]
        logger.debug(f"Found {len(artifacts)} artifacts")

        # Build the index
        index = build_artifact_index(artifacts)
        logger.debug(f"Built index with {len(index)} entries")

        # Save to cache files
        try:
            with open(cache_file, "w") as f:
                json.dump(artifacts, f)
            with open(index_file, "w") as f:
                json.dump(index, f)
            logger.debug("Saved artifacts and index to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache files: {e}")

        return {"index": index, "artifacts": artifacts}

    except Exception as e:
        logger.error(f"Error getting S3 artifacts: {e}")
        return {"index": {}, "artifacts": []}


def build_artifact_index(artifacts):
    """
    Build an index mapping version-commit to flavors for faster lookups.

    Args:
        artifacts (list): List of artifact paths

    Returns:
        dict: Dictionary mapping version-commit to list of flavors
    """
    index = {}

    for artifact in artifacts:
        try:
            # Split path into components
            parts = artifact.split("/")
            if len(parts) < 3:
                continue

            # Extract version and commit from path
            version_commit = parts[0]  # Format: "version-commit"
            flavor = parts[1]  # The flavor name

            # Skip if flavor is actually a version number
            if flavor and not re.match(r"^\d+\.\d+", flavor):
                # Add to index
                if version_commit not in index:
                    index[version_commit] = []
                if flavor not in index[version_commit]:  # Avoid duplicates
                    index[version_commit].append(flavor)

        except Exception:
            continue

    return index
