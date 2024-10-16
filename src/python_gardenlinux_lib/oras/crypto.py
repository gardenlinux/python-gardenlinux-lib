import hashlib
import logging
import os

import boto3
from babel.messages import Message
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography import x509
import base64


class Signer:
    """
    Signer

    abstract class defining the methods for signing and verifying data
    """

    def sign_data(self, data_str: str) -> str:
        pass

    def verify_signature(self, data_str: str, signature: str):
        pass


class KMSSigner(Signer):
    """
    KMSSigner

    implementation of Signer interface using AWS KMS
    """

    def __init__(self, arn: str):
        self.kms_client = boto3.client("kms")
        # check if client works
        key_info = self.kms_client.describe_key(KeyId=arn)

        if "SIGN" not in key_info["KeyMetadata"]["KeyUsage"]:
            raise Exception("Key is missing the sign property")
        if "VERIFY" not in key_info["KeyMetadata"]["KeyUsage"]:
            raise Exception("Key is missing the verify property")
        if "RSASSA_PSS_SHA_256" not in key_info["KeyMetadata"]["SigningAlgorithms"]:
            raise Exception(
                "Key is missing the required signing algorithm (RSASSA_PSS_SHA_256)"
            )
        # seems to be fine, use it
        self.arn = arn

    def sign_data(self, data_str: str) -> str:
        signature = self.kms_client.sign(
            KeyId=self.arn,
            MessageType="RAW",
            SigningAlgorithm="RSASSA_PSS_SHA_256",
            Message=data_str.encode("utf-8"),
        )["Signature"]
        return base64.b64encode(signature).decode("utf-8")

    def verify_signature(self, data_str: str, signature: str):
        if not self.kms_client.verify(
            KeyId=self.arn,
            Message=data_str.encode("utf-8"),
            MessageType="RAW",
            Signature=base64.b64decode(signature),
            SigningAlgorithm="RSASSA_PSS_SHA_256",
        )["SignatureValid"]:
            raise ValueError(f"Invalid Signature {signature} for data: {data_str}")


class LocalSigner(Signer):
    """
    LocalSigner

    implementation of Signer interface using local certificates

    :param private_key_file_path
    :param public_key_file_path
    """

    def __init__(self, private_key_file_path: str, public_key_file_path: str):
        with open(private_key_file_path, "rb") as key_file:
            self.private_key = load_pem_private_key(
                key_file.read(), password=None, backend=default_backend()
            )
        with open(public_key_file_path, "rb") as cert_file:
            cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
            self.public_key = cert.public_key()

    def sign_data(self, data_str: str) -> str:
        signature = self.private_key.sign(
            data_str.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(
                    hashes.SHA256()
                ),  # Mask generation function based on SHA-256
                salt_length=padding.PSS.MAX_LENGTH,  # Maximum salt length
            ),
            hashes.SHA256(),
        )
        return base64.b64encode(signature).decode("utf-8")

    def verify_signature(self, data_str: str, signature: str):
        try:
            self.public_key.verify(
                base64.b64decode(signature),
                data_str.encode("utf-8"),
                padding.PSS(
                    mgf=padding.MGF1(
                        hashes.SHA256()
                    ),  # Mask generation function based on SHA-256
                    salt_length=padding.PSS.MAX_LENGTH,  # Maximum salt length
                ),
                hashes.SHA256(),
            )
        except InvalidSignature:
            raise ValueError(f"Invalid Signature {signature} for data: {data_str}")


def verify_sha256(checksum: str, data: bytes):
    data_checksum = f"sha256:{hashlib.sha256(data).hexdigest()}"
    if checksum != data_checksum:
        raise ValueError(f"Invalid checksum. {checksum} != {data_checksum}")


def calculate_sha256(file_path: str) -> str:
    """Calculate the SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()
