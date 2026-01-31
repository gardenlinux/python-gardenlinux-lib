# -*- coding: utf-8 -*-

from glob import glob
from os import PathLike
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import tarfile

from ..cname import CName
from ..parser import Parser
from .changelog_file import ChangelogFile
from .control_file import ControlFile
from .copyright_file import CopyrightFile
from .docs_file import DocsFile
from .install_file import InstallFile
from .postinst_file import PostinstFile
from .prerm_file import PrermFile
from .rules_file import RulesFile


class DebPacker(object):
    def __init__(self, version, target_dir):
        if not isinstance(target_dir, PathLike):
            target_dir = Path(target_dir)

        if not target_dir.is_dir():
            raise ValueError("Target directory given is invalid")

        self._target_dir = target_dir
        self._version = version

    def pack(self):
        feature_parser = Parser()
        features_dir_path = feature_parser.features_dir_path

        for feature_dir_entry in features_dir_path.iterdir():
            if feature_dir_entry.is_dir():
                self.pack_feature(feature_dir_entry.name, feature_parser)

    def pack_feature(self, feature, feature_parser=None):
        if feature_parser is None:
            feature_parser = Parser()

        feature_graph = feature_parser.filter(feature, ignore_excludes=True)
        feature_dir_path = feature_parser.features_dir_path.joinpath(feature)

        feature_package_name = self._get_feature_package_name_from_content(
            feature, feature_graph.nodes[feature]["content"]
        )

        package_name = f"gardenlinux-{feature_package_name}"

        tarfile_path_name = self._target_dir.joinpath(
            f"{package_name}-{self._version}.tar.gz"
        )

        if tarfile_path_name.is_file():
            raise RuntimeError(f"tar archive '{tarfile_path_name}' already exists")

        with TemporaryDirectory(dir=self._target_dir) as tmp:
            tmp_path = Path(tmp)
            debian_path = tmp_path.joinpath("debian")

            debian_path.mkdir()

            postinst_file = PostinstFile()
            prerm_file = PrermFile()

            ChangelogFile(feature_package_name, self._version).generate(debian_path)

            self._generate_control_file(
                feature_graph.nodes, feature, feature_dir_path, debian_path
            )

            CopyrightFile(feature_package_name).generate(debian_path)

            self._generate_docs_file(feature_dir_path, debian_path)

            source_path_names = self._generate_sources(
                feature_dir_path,
                feature_package_name,
                tmp_path,
                postinst_file,
                prerm_file,
            )

            if not postinst_file.empty:
                postinst_file.generate(debian_path)

            if not prerm_file.empty:
                prerm_file.generate(debian_path)

            self._generate_install_file(
                feature_package_name, tmp_path, debian_path, source_path_names
            )

            RulesFile().generate(debian_path)

            package_name = f"gardenlinux-{feature_package_name}"

            tarfile_path_name = self._target_dir.joinpath(
                f"{package_name}-{self._version}.tar.gz"
            )

            with tarfile.open(tarfile_path_name, "w:gz") as tar_archive:
                tar_archive.add(tmp_path, ".")

    def _generate_control_file(self, features, feature, feature_dir_path, debian_path):
        feature_content = features[feature]["content"]

        feature_package_name = self._get_feature_package_name_from_content(
            feature,
            feature_content,
        )

        control_file = ControlFile(feature_package_name, feature)

        for feature in feature_content.get("features", {}).get("include", []):
            parent_feature_content = features[feature]["content"]

            parent_feature_package_name = self._get_feature_package_name_from_content(
                feature,
                parent_feature_content,
            )

            control_file.add_dependency(
                f"gardenlinux-{parent_feature_package_name} (= {self._version})"
            )

        pkg_include_file = feature_dir_path.joinpath("pkg.include")

        if pkg_include_file.is_file():
            for pkg in pkg_include_file.read_text().splitlines():
                pkg = pkg.strip()

                if len(pkg) < 1 or pkg.startswith("#"):
                    continue

                control_file.add_dependency(pkg)

        for feature in feature_content.get("features", {}).get("exclude", []):
            if feature in features:
                parent_feature_content = features[feature]["content"]
            else:
                feature_graph = Parser().filter(feature, ignore_excludes=True)
                parent_feature_content = feature_graph.nodes[feature]["content"]

            parent_feature_package_name = self._get_feature_package_name_from_content(
                feature, parent_feature_content
            )

            control_file.add_conflict(f"gardenlinux-{parent_feature_package_name}")

        pkg_exclude_file = feature_dir_path.joinpath("pkg.exclude")

        if pkg_exclude_file.is_file():
            for pkg in pkg_exclude_file.read_text().splitlines():
                pkg = pkg.strip()

                if len(pkg) < 1 or pkg.startswith("#"):
                    continue

                control_file.add_breaking_package(pkg)

        control_file.generate(debian_path)

    def _generate_docs_file(self, feature_dir_path, debian_path):
        readme_file = feature_dir_path.joinpath("README.md")

        if readme_file.is_file():
            docs_file = DocsFile()
            docs_file.add_file(readme_file)
            docs_file.generate(debian_path)

    def _generate_install_file(
        self, feature_package_name, tmp_path, debian_path, source_path_names
    ):
        if len(source_path_names) > 0:
            package_name = f"gardenlinux-{feature_package_name}"
            source_dir_path = tmp_path.joinpath(f"{package_name}-{self._version}")

            install_file = InstallFile(tmp_path, feature_package_name)

            for source_path_name in source_path_names:
                source_path = source_dir_path.joinpath(source_path_name)

                if source_path.is_dir():
                    install_file.add_directory(source_path, str(source_path_name))
                else:
                    install_file.add_entry(source_path, str(source_path_name))

            install_file.generate(debian_path)

    def _generate_sources(
        self,
        feature_dir_path,
        feature_package_name,
        tmp_path,
        postinst_file,
        prerm_file,
    ):
        source_path_names = []

        package_name = f"gardenlinux-{feature_package_name}"
        source_dir_path = tmp_path.joinpath(f"{package_name}-{self._version}")
        source_dir_path.mkdir()

        file_include_dir_path = feature_dir_path.joinpath("file.include")

        if file_include_dir_path.is_dir():
            for root_path, _, files in file_include_dir_path.walk():
                relative_path = root_path.relative_to(file_include_dir_path)

                if relative_path.is_relative_to("usr/local"):
                    # self._logger.warn(f"Moving '{relative_path}' to '/usr' as Debian packages conformance requirements")

                    target_dir_path = source_dir_path.joinpath("usr")

                    if relative_path != Path("usr", "local"):
                        target_dir_path = target_dir_path.joinpath(
                            *relative_path.parts[2:]
                        )
                else:
                    target_dir_path = source_dir_path.joinpath(relative_path)

                hidden_files_count = 0

                for file_name in files:
                    if file_name.startswith("."):
                        hidden_files_count += 1

                only_hidden_files = hidden_files_count == len(files)

                for file_name in files:
                    if not target_dir_path.is_dir():
                        if not only_hidden_files:
                            source_path_names.append(str(target_dir_path.relative_to(source_dir_path)))

                        target_dir_path.mkdir(exist_ok=True, parents=True)

                    file_path = target_dir_path.joinpath(file_name)

                    root_path.joinpath(file_name).copy(
                        file_path,
                        preserve_metadata=True,
                        follow_symlinks=False,
                    )

                    if (
                        file_path.name.startswith(".")
                        or root_path == file_include_dir_path
                    ):
                        source_path_names.append(
                            str(file_path.relative_to(source_dir_path))
                        )

        file_stat_file = feature_dir_path.joinpath("file.include.stat")

        if file_stat_file.is_file():
            re_object = re.compile("\\s+")
            for file_line in file_stat_file.read_text().splitlines():
                file_line = file_line.strip()

                if len(file_line) < 1 or file_line.startswith("#"):
                    continue

                file_data = re_object.split(file_line, 3)

                if len(file_data) != 4:
                    # self._logger.warn(f"{file_stat_file} contains invalid stat definition lines")
                    continue

                file_glob = file_data[3]

                if file_glob.startswith("/"):
                    file_glob_list = glob(file_data[3][1:], root_dir=source_dir_path)
                else:
                    file_glob_list = glob(file_data[3], root_dir=source_dir_path)

                if len(file_glob_list) < 1:
                    # self._logger.warn(f"{file_stat_file} contains stat definition lines not matching any files")
                    pass

                for file_name in file_glob_list:
                    postinst_file.add_code(
                        f'dpkg-statoverride --add {file_data[0]} {file_data[1]} {file_data[2]} "/{file_name}"'
                    )

                    prerm_file.add_code(f'dpkg-statoverride --remove "/{file_name}"')

        return source_path_names

    def _get_feature_package_name_from_content(self, feature, feature_content):
        if feature.startswith("_"):
            feature = feature[1:]

        feature = CName.get_camel_case_name_for_feature(feature, "-")

        return f"{feature_content['type']}-{feature}"
