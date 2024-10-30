import hashlib


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
