import gzip
import io
import shutil
from pathlib import Path

import requests
from git import Repo

from gardenlinux.apt import DebsrcFile, GardenLinuxRepo
from gardenlinux.apt.package_repo_info import compare_repo
from gardenlinux.constants import (
    GL_DEB_REPO_BASE_URL,
    IMAGE_VARIANTS,
    REQUESTS_TIMEOUTS,
)
from gardenlinux.features import CName
from gardenlinux.flavors import Parser as FlavorsParser
from gardenlinux.logger import LoggerSetup
from gardenlinux.s3 import S3Artifacts

LOGGER = LoggerSetup.get_logger("gardenlinux.github.release_notes.helpers", "INFO")


def get_package_list(gardenlinux_version):
    url = f"{GL_DEB_REPO_BASE_URL}/dists/{gardenlinux_version}/main/binary-amd64/Packages.gz"
    response = requests.get(url, timeout=REQUESTS_TIMEOUTS)
    response.raise_for_status()

    d = DebsrcFile()

    with io.BytesIO(response.content) as buf:
        with gzip.open(buf, "rt") as f:
            d.read(f)

    return d


def compare_apt_repo_versions(previous_version, current_version):
    previous_repo = GardenLinuxRepo(previous_version)
    current_repo = GardenLinuxRepo(current_version)
    pkg_diffs = sorted(compare_repo(previous_repo, current_repo), key=lambda t: t[0])

    output = f"| Package | {previous_version} | {current_version} |\n"
    output += "|---------|--------------------|-------------------|\n"

    for pkg in pkg_diffs:
        output += f"|{pkg[0]} | `{pkg[1] if pkg[1] is not None else '-'}` | `{pkg[2] if pkg[2] is not None else '-'}` |\n"
    return output


def download_all_metadata_files(version, commitish, s3_bucket_name):
    repo = Repo(".")
    commit = repo.commit(commitish)
    flavors_data = commit.tree["flavors.yaml"].data_stream.read().decode("utf-8")
    flavors = FlavorsParser(flavors_data).filter(only_publish=True)

    local_dest_path = Path("s3_downloads")
    if local_dest_path.exists():
        shutil.rmtree(local_dest_path)
    local_dest_path.mkdir(mode=0o755, exist_ok=False)

    s3_artifacts = S3Artifacts(s3_bucket_name)

    for flavor in flavors:
        LOGGER.debug(f"{flavor=} {version=} {commitish=}")
        cname = CName(flavor[1], flavor[0], commitish)
        # Filter by image variants - only download if the flavor matches one of the variants
        flavor_matches_variant = False
        for variant_suffix in IMAGE_VARIANTS:
            if variant_suffix == "":
                last_part = cname.cname.split("-")[-1]
                if "_" not in last_part:
                    flavor_matches_variant = True
                    break
            elif variant_suffix in cname.cname:
                # Specific variant (any non-empty string in IMAGE_VARIANTS)
                flavor_matches_variant = True
                break

        if not flavor_matches_variant:
            LOGGER.info(
                f"Skipping flavor {cname.cname} - not matching image variants filter"
            )
            continue

        try:
            commit_short = commitish[:8]
            download_metadata_file(
                s3_artifacts, cname, version, commit_short, local_dest_path
            )
        except IndexError:
            LOGGER.warning(f"No artifacts found for flavor {cname.cname}, skipping...")
            continue

    return [str(artifact) for artifact in local_dest_path.iterdir()]


def download_metadata_file(s3_artifacts, cname, version, commit_short, artifacts_dir):
    """
    Download metadata file (s3_metadata.yaml)
    """
    LOGGER.debug(
        f"{s3_artifacts=} | {cname.cname=} | {version=} | {cname.commit_id=} | {commit_short=} | {artifacts_dir=}"
    )
    maybe_release_objects = s3_artifacts.bucket.objects.filter(
        Prefix=f"meta/singles/{cname.cname}-{version}-{commit_short}"
    )

    release_object = list(maybe_release_objects)[0]
    LOGGER.debug(f"{release_object.bucket_name=} | {release_object.key=}")

    s3_artifacts.bucket.download_file(
        release_object.key,
        artifacts_dir.joinpath(f"{cname.cname}.s3_metadata.yaml"),
    )


def get_variant_from_flavor(flavor_name):
    """
    Determine the variant from a flavor name by checking for variant suffixes.
    Returns the variant key (e.g., 'legacy', 'usi', 'tpm2_trustedboot').
    """
    match flavor_name:
        case name if "_usi" in name:
            return "usi"
        case name if "_tpm2_trustedboot" in name:
            return "tpm2_trustedboot"
        case _:
            return "legacy"
