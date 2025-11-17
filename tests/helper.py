import shlex
import subprocess
from typing import Any, Optional


def spawn_background_process(
    cmd: str, stdout: Optional[Any] = None, stderr: Optional[Any] = None
) -> subprocess.Popen[Any]:
    args = shlex.split(cmd)
    process = subprocess.Popen(args, shell=False, stdout=stdout, stderr=stderr)
    return process


def call_command(cmd: str) -> str:
    try:
        args = shlex.split(cmd)
        result = subprocess.run(
            args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output = result.stdout.decode("utf-8")
        return output

    except subprocess.CalledProcessError as e:
        error_message = e.stderr.decode("utf-8")
        return f"An error occurred: {error_message}"
