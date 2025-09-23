import os
import shlex
import subprocess

from .constants import CERT_DIR, GL_ROOT_DIR, ZOT_CONFIG_FILE


def spawn_background_process(cmd, stdout=None, stderr=None):
    args = shlex.split(cmd)
    process = subprocess.Popen(args, shell=False, stdout=stdout, stderr=stderr)
    return process


def call_command(cmd):
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
