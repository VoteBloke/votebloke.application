import base64
import os
import pathlib

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes


def generate_keys() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(ec.SECP256R1())


def export_keys_to_files(private_key: ec.EllipticCurvePrivateKey) -> None:
    serialized_private_key = private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                       format=serialization.PrivateFormat.PKCS8,
                                                       encryption_algorithm=serialization.NoEncryption())

    serialized_public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)

    with open(os.path.join(pathlib.Path.home(), "private.pem"), "wb") as file:
        file.write(serialized_private_key)

    with open(os.path.join(pathlib.Path.home(), "public.pem"), "wb") as file:
        file.write(serialized_public_key)


def encode_public_key(private_key: ec.EllipticCurvePrivateKey) -> str:
    public_key = private_key.public_key()
    return base64.b64encode(public_key.public_bytes(encoding=serialization.Encoding.DER,
                                                    format=serialization.PublicFormat.SubjectPublicKeyInfo)).decode(
        "UTF-8")


def sign_data(data: str, key: ec.EllipticCurvePrivateKey) -> str:
    return base64.b64encode(key.sign(data.encode("UTF-8"), ec.ECDSA(hashes.SHA256()))).decode(
        "UTF-8")


def create_account() -> ec.EllipticCurvePrivateKey:
    return generate_keys()
