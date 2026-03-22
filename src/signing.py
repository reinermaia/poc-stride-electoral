from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import base64, json

def generate_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key, private_key.public_key()

def sign_payload(payload: dict, private_key) -> str:
    content = json.dumps(payload, sort_keys=True).encode()
    signature = private_key.sign(content, padding.PKCS1v15(), hashes.SHA256())
    return base64.b64encode(signature).decode()

def verify_signature(payload: dict, signature_b64: str, public_key) -> bool:
    try:
        content = json.dumps(payload, sort_keys=True).encode()
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, content, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False

if __name__ == "__main__":
    private_key, public_key = generate_keypair()
    payload = {"id": "abc", "candidates": {"A": 120, "B": 98}}
    sig = sign_payload(payload, private_key)
    valid = verify_signature(payload, sig, public_key)
    print(f"Assinatura: {sig[:40]}...")
    print(f"Válida: {valid}")
    tampered = {"id": "abc", "candidates": {"A": 9999, "B": 0}}
    print(f"Adulterado válido: {verify_signature(tampered, sig, public_key)}")
