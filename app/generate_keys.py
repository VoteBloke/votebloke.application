import base64

import ecdsa


def generate_keys() -> ecdsa.SigningKey:
    return ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)


def export_keys_to_file(signing_keys: ecdsa.SigningKey, path: str) -> None:
    with open(path + "private.pem", "wmb") as f:
        f.write(signing_keys.to_pem())
    with open(path + "public.pem", "wb") as f:
        f.write(signing_keys.verifying_key.to_pem())


def key_to_string(key: ecdsa.SigningKey) -> str:
    return base64.b64encode(key.to_string()).decode("UTF-8")
