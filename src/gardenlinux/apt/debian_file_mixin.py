# -*- coding: utf-8 -*-

from os import PathLike
from pathlib import Path


class DebianFileMixin(object):
    def _generate(self, target_dir, file_name, content, chmod_octet=0o644):
        if not isinstance(target_dir, PathLike):
            target_dir = Path(target_dir)

        if not target_dir.is_dir():
            raise ValueError("Target directory given is invalid")

        file_path_name = target_dir.joinpath(file_name)

        if file_path_name.is_file():
            raise RuntimeError(
                f"Target directory already contains a '{file_path_name}' file"
            )

        file_path_name.write_text(content)
        file_path_name.chmod(chmod_octet)
