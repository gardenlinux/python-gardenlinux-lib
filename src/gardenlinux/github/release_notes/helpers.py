import gzip
import io

import requests

from gardenlinux.apt import DebsrcFile, GardenLinuxRepo
from gardenlinux.apt.package_repo_info import compare_repo
from gardenlinux.constants import REQUESTS_TIMEOUTS


def get_package_list(gardenlinux_version):
    url = f"https://packages.gardenlinux.io/gardenlinux/dists/{gardenlinux_version}/main/binary-amd64/Packages.gz"
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
        output += f"|{pkg[0]} | {pkg[1] if pkg[1] is not None else '-'} | {pkg[2] if pkg[2] is not None else '-'} |\n"
    return output
