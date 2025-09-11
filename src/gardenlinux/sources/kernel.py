from .debian import (
    get_package_list,
    get_package_urls,
    get_pkg_attr,
    check_urls,
    output_urls
)


def get_kernel_urls(gardenlinux_version):
    if not gardenlinux_version:
        print("You need to specify gardenlinux_version")
    repositories = [f'http://packages.gardenlinux.io/gardenlinux {gardenlinux_version} main']

    # Temporary for as long as we need to perform releases for versions < 1443
    if "1312" in gardenlinux_version:
        repositories = [f'http://repo.gardenlinux.io/gardenlinux {gardenlinux_version} main']

    architecture = ["arm64", "amd64"]
    packages = get_package_list(repositories, architecture)

    # find all Linux kernel versions available for the specified Gardenlinux version

    # We want to only list the packages for the specific kernel used for a given release
    # GL uses always the latest available kernel in the given repo, even if older kernel versions would be available.
    # Ideally we would parse the version of the package linux-headers-${arch}, which specifies the actual version.
    # Here, it is safe enough for the release notes to take the highest version available.
    latest_version = get_pkg_attr("linux-headers-amd64", "Version", packages)
    package_urls = check_urls([latest_version], get_package_urls(packages, 'linux-headers'), architecture)
    return output_urls(package_urls)
