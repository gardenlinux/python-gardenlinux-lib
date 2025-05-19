import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta

import pytest
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dotenv import load_dotenv

from .helper import call_command, spawn_background_process

TEST_DATA_DIR = "test-data"
GL_ROOT_DIR = f"{TEST_DATA_DIR}/gardenlinux"
CERT_DIR = f"{TEST_DATA_DIR}/cert"


def generate_test_certificates():
    """Generate self-signed certificates for testing using cryptography library"""

    os.makedirs(CERT_DIR, exist_ok=True)
    key_path = os.path.join(CERT_DIR, "oci-sign.key")
    cert_path = os.path.join(CERT_DIR, "oci-sign.crt")

    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    # Generate certificate
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(
                NameOID.COMMON_NAME, "Garden Linux test signing key for oci"
            ),
        ]
    )

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=365))
        .sign(private_key, hashes.SHA256())
    )

    # Write private key
    with open(key_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    os.chmod(key_path, 0o600)

    # Write certificate
    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    print(f"Generated test certificates in {CERT_DIR}")


def write_zot_config(config_dict, file_path):
    with open(file_path, "w") as config_file:
        json.dump(config_dict, config_file, indent=4)


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
    generate_test_certificates()
    call_command("./test-data/build-test-data.sh --dummy")


def pytest_sessionfinish(session):
    if os.path.isfile(CERT_DIR + "/oci-sign.crt"):
        os.remove(CERT_DIR + "/oci-sign.crt")
    if os.path.isfile(CERT_DIR + "/oci-sign.key"):
        os.remove(CERT_DIR + "/oci-sign.key")
