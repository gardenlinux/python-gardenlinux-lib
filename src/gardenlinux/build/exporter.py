# -*- coding: utf-8 -*-

import os
import pathlib
import re
import shutil
import subprocess
from os import PathLike

from elftools.common.exceptions import ELFError
from elftools.elf.elffile import ELFFile

from ..logger import LoggerSetup

# Parses dependencies from ld output
parse_output = re.compile("(?:.*=>)?\\s*(/\\S*).*\n")
# Remove leading /
remove_root = re.compile("^/")


# Check for ELF header
def _isElf(path: str | PathLike[str]) -> bool:
    """
    Checks if a file is an ELF by looking for the ELF header.

    :param path:    Path to file

    :return: (bool) If the file found at path is an ELF
    :since:  TODO
    """

    with open(path, "rb") as f:
        try:
            ELFFile(f)
            return True
        except ELFError:
            return False


def _getInterpreter(path: str | PathLike[str], logger) -> pathlib.Path:
    """
    Returns the interpreter of an ELF. Supported architectures: x86_64, aarch64, i686.

    :param path:    Path to file
    :param logger:  Logger to log errors

    :return: (str) Path of the interpreter
    :since:  TODO
    """

    with open(path, "rb") as f:
        elf = ELFFile(f)
        interp = elf.get_section_by_name(".interp")

        if interp:
            return pathlib.Path(interp.data().split(b"\x00")[0].decode())
        else:
            match elf.header["e_machine"]:
                case "EM_AARCH64":
                    return pathlib.Path("/lib/ld-linux-aarch64.so.1")
                case "EM_386":
                    return pathlib.Path("/lib/ld-linux.so.2")
                case "EM_X86_64":
                    return pathlib.Path("/lib64/ld-linux-x86-64.so.2")
                case arch:
                    logger.error(
                        f"Error: Unsupported architecture for {path}: only support x86_64 (003e), aarch64 (00b7) and i686 (0003), but was {arch}"
                    )
                    exit(1)

def _get_python_from_path() -> pathlib.Path | None:
    interpreter = None
    for dir in os.environ["PATH"].split(":"):
        binary = pathlib.Path(dir).joinpath("python3")
        if binary.is_file():
            interpreter = binary
            break
    return interpreter

def _get_default_package_dir() -> pathlib.Path | None:
    """
    Finds the default site-packages or dist-packages directory of the default python3 environment

    :return: (str) Path to directory
    :since:  TODO
    """
    
    # Needs to escape the virtual environment python-gardenlinx-lib is running in
    interpreter = _get_python_from_path()
    if interpreter:
        out = subprocess.run(
            [interpreter, "-c", "import site; print(site.getsitepackages()[0])"],
            stdout=subprocess.PIPE,
        )
        return pathlib.Path(out.stdout.decode().strip())
    else:
        return None


def export(
    output_dir: str | PathLike[str] = "/required_libs",
    package_dir: str | PathLike[str] | None = None,
    logger=None,
) -> None:
    """
    Identifies shared library dependencies of `package_dir` and copies them to `output_dir`.

    :param output_dir:  Path to output_dir
    :param package_dir: Path to package_dir
    :param logger:      Logger to log errors

    :since:  TODO
    """

    if not package_dir:
        package_dir = _get_default_package_dir()
        if not package_dir:
            logger.error(
                f"Error: Couldn't identify a default python package directory. Please specifiy one using the --package-dir option. Use -h for more information."
            )
            exit(1)
    else:
        package_dir = pathlib.Path(package_dir)
    output_dir = pathlib.Path(output_dir)
        
    if logger is None or not logger.hasHandlers():
        logger = LoggerSetup.get_logger("gardenlinux.export_libs")
    # Collect ld dependencies for installed pip packages
    dependencies = set()
    for root, dirs, files in package_dir.walk():
        for file in files:
            path = root.joinpath(file)
            if not path.is_symlink() and _isElf(path):
                out = subprocess.run(
                    [_getInterpreter(path, logger), "--inhibit-cache", "--list", path],
                    stdout=subprocess.PIPE,
                )
                for dependency in parse_output.findall(out.stdout.decode()):
                    dependencies.add(os.path.realpath(dependency))

    # Copy dependencies into output_dir folder
    if not output_dir.is_dir():
        output_dir.mkdir()

    for dependency in dependencies:
        path = output_dir.joinpath(remove_root.sub("", dependency))
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dependency, path)

    # Reset timestamps of the parent directories
    if len(dependencies) > 0:
        mtime = int(os.stat(dependencies.pop()).st_mtime)
        os.utime(output_dir, (mtime, mtime))
        for root, dirs, _ in output_dir.walk():
            for dir in dirs:
                os.utime(root.joinpath(dir), (mtime, mtime))
