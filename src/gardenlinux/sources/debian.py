import re
import apt
import yaml
import itertools


def get_pkg_attr(package_name, attribute_key, packages_per_repo):

    current_package = {}
    found_package = False
    for packages in packages_per_repo.values():
        for line in packages.split('\n'):
            # Check for new package section or end of file
            if line.startswith("Package: ") or line.strip() == "":
                if found_package:
                    # Return the attribute if it exists
                    return current_package.get(attribute_key)
                current_package = {}
                found_package = False

            key_value = line.split(": ", 1)
            if len(key_value) == 2:
                key, value = key_value
                current_package[key.strip()] = value.strip()

            # Check if current section is the desired package
            if current_package.get("Package") == package_name:
                found_package = True


def get_package_list(repositories, architecture):
    '''Get Packages lists from repository and return it as dictionary.
    '''
    packages_dict = {}
    cache = apt.Cache()
    for repo in repositories:
        repo_entries = repo.split(' ')
        uri = repo_entries[0]
        suite = repo_entries[1]
        components = repo_entries[2:]
        for component in components:
            for arch in ['all'] + architecture:
                pkg_info = ""
                for pkg in cache:
                    if not pkg.candidate:
                        continue
                    for origin in pkg.candidate.origins:
                        if origin.site == uri and origin.archive == suite and origin.component == component:
                            # Only add package if its candidate’s architecture exactly matches OR we allow 'all'
                            if pkg.candidate.architecture == arch or arch == 'all':
                                pkg_info += f"Package: {pkg.name}\nVersion: {pkg.candidate.version}\nArchitecture: {pkg.candidate.architecture}\n\n"
                                break  # Break from origins loop once matched
                if pkg_info:
                    packages_dict[f"{uri}-{suite}-{component}-{arch}"] = pkg_info

    assert len(packages_dict) != 0, "Expected to find packages"
    return packages_dict


def get_package_urls(package_list, package_name, resolve_depends=True):
    '''Check if kernel headers and their dependencies are available. Returns a list
    with the complete urls to all found kernel header packages and their dependencies.
    '''
    header_packages = []
    dependencies = []
    for repo, packages in package_list.items():
        uri = re.match('(.*?)-.*', repo).group(1)
        for line in packages.split('\n'):
            if resolve_depends and line.startswith('Depends:'):
                dependencies = re.sub(' ?\(.*?\),?|,', '', re.match("Depends: (.*)", line).group(1)).split(' ')
            if line.startswith('Filename:') and f'/{package_name}' in line:
                filename = re.match("Filename: (.*)", line).group(1)
                header_packages.append(f'{uri}/{filename}')
                if resolve_depends:
                    for dependency in dependencies:
                        header_packages.extend(get_package_urls(package_list, dependency, False))

    return header_packages


def check_urls(linux_versions, header_package_urls, architecture):
    '''Pick the package urls that match the Linux image versions.
    '''
    result = {}
    versions = {}
    for arch, version in itertools.product(architecture, linux_versions):
        if arch not in result:
            result[arch] = {}
        result[arch][version] = []
    for version, arch, package in itertools.product(linux_versions, architecture, header_package_urls):
        if version in package and arch in package:
            result[arch][version].append(package)
            versions[version] = re.match(".*?(_.*)\.deb", package).group(1)
        # Workaround for linux compiler package name on arm64 architecture
        if 'arm64' in package and arch == 'arm64' and re.match('.*/gcc-\d\d_.*', package):
            result[arch][version].append(package)
    for version, arch, package in itertools.product(versions, architecture, header_package_urls):
        if versions[version] in package and arch in package and 'linux-headers' not in package:
            result[arch][version].append(package)

    for key, value in result.items():
        for nested_key, nested_value in value.items():
            result[key][nested_key] = list(dict.fromkeys(nested_value))

    return result


def output_urls(package_urls):

    yaml_output = "```yaml\n"
    yaml_output += ""
    yaml_output += yaml.dump(package_urls)
    yaml_output += "```\n"
    yaml_output += ""
    return yaml_output
