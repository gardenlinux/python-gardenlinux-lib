import subprocess
import shlex

import os

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


def generate_test_certificates():
    """Generate self-signed certificates for testing"""
    os.makedirs(CERT_DIR, exist_ok=True)
    key_path = os.path.join(CERT_DIR, "oci-sign.key")
    cert_path = os.path.join(CERT_DIR, "oci-sign.crt")
    cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:4096",
        "-keyout",
        key_path,
        "-out",
        cert_path,
        "-days",
        "365",
        "-nodes",
        "-subj",
        "/CN=Garden Linux test signing key for oci",
    ]
    try:
        subprocess.run(cmd, check=True)
        # Set proper permissions
        os.chmod(key_path, 0o600)
        print(f"Generated test certificates in {CERT_DIR}")
    except subprocess.CalledProcessError as e:
        print(f"Error generating certificates: {e}")
        raise
