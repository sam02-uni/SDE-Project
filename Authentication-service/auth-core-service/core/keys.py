from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

KID = "auth-key-1"

def load_private_key(path="keys/private.pem"):
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )

PRIVATE_KEY = load_private_key()
PUBLIC_KEY = PRIVATE_KEY.public_key()
NUMBERS = PUBLIC_KEY.public_numbers()

def b64(n: int) -> str:
    return base64.urlsafe_b64encode(
        n.to_bytes((n.bit_length() + 7)//8, "big")
    ).decode().rstrip("=")
