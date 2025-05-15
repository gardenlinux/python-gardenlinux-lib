import json
import os
import shutil
import subprocess
import sys
import tempfile

import pytest
from dotenv import load_dotenv

from .helper import call_command, spawn_background_process

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test-data")
GL_ROOT_DIR = os.path.join(TEST_DATA_DIR, "gardenlinux")
CERT_DIR = os.path.join(TEST_DATA_DIR, "cert")


def write_zot_config(config_dict, file_path):
    with open(file_path, "w") as config_file:
        json.dump(config_dict, config_file, indent=4)


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


@pytest.fixture(autouse=False, scope="function")
def zot_session():
    load_dotenv()
    print("start zot session")
    zot_config = {
        "distSpecVersion": "1.1.0",
        "storage": {"rootDirectory": "output/registry/zot"},
        "http": {"address": "127.0.0.1", "port": "18081"},
        "log": {"level": "warn"},
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_config_file:
        write_zot_config(zot_config, temp_config_file.name)
        zot_config_file_path = temp_config_file.name

    print(f"Spawning zot registry with config {zot_config_file_path}")
    zot_process = spawn_background_process(
        f"{TEST_DATA_DIR}/zot serve {zot_config_file_path}",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )

    yield zot_process
    print("clean up zot session")

    zot_process.terminate()

    if os.path.isdir("./output"):
        shutil.rmtree("./output")
    if os.path.isfile(zot_config_file_path):
        os.remove(zot_config_file_path)


def pytest_sessionstart(session):
    # Generate certificates directly with Python function
    generate_test_certificates()

    # Try to call the build-test-data.sh script with proper permissions
    script_path = f"{TEST_DATA_DIR}/build-test-data.sh"
    call_command(f"{script_path} --dummy")


def pytest_sessionfinish(session):
    if os.path.isfile(f"{CERT_DIR}/oci-sign.crt"):
        os.remove(f"{CERT_DIR}/oci-sign.crt")
    if os.path.isfile(f"{CERT_DIR}/oci-sign.key"):
        os.remove(f"{CERT_DIR}/oci-sign.key")
