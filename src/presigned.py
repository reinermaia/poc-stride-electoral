import uuid
import hashlib
import time
from datetime import datetime, timezone, timedelta
import json

# simula um storage de URLs pré-assinadas
_url_store = {}

def generate_presigned_url(result_id: str, actor: str, ttl_seconds: int = 300) -> dict:
    """Gera URL pré-assinada com TTL e binding de actor"""
    token = str(uuid.uuid4())
    expires_at = time.time() + ttl_seconds
    entry = {
        "token": token,
        "result_id": result_id,
        "actor": actor,
        "expires_at": expires_at,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    _url_store[token] = entry
    url = f"http://localhost:8000/download/{result_id}?token={token}"
    return {"url": url, "token": token, "expires_at": expires_at, "ttl_seconds": ttl_seconds}

def validate_presigned_url(token: str, actor: str) -> dict:
    """Valida token: TTL + binding de actor"""
    if token not in _url_store:
        return {"valid": False, "reason": "Token não encontrado"}

    entry = _url_store[token]

    if time.time() > entry["expires_at"]:
        del _url_store[token]
        return {"valid": False, "reason": "Token expirado"}

    if entry["actor"] != actor:
        return {"valid": False, "reason": f"Token pertence a outro actor: {entry['actor']}"}

    return {"valid": True, "result_id": entry["result_id"], "actor": entry["actor"]}

def revoke_url(token: str):
    """Revoga URL após uso (one-time use)"""
    if token in _url_store:
        del _url_store[token]

if __name__ == "__main__":
    url_data = generate_presigned_url("resultado-abc", actor="operador-001", ttl_seconds=5)
    print(f"URL gerada: {url_data['url']}")

    print("\nValidação com actor correto:")
    print(validate_presigned_url(url_data["token"], actor="operador-001"))

    print("\nValidação com actor errado (atacante):")
    print(validate_presigned_url(url_data["token"], actor="atacante"))

    print("\nAguardando TTL expirar (6s)...")
    import time; time.sleep(6)
    print("Validação após expiração:")
    print(validate_presigned_url(url_data["token"], actor="operador-001"))
