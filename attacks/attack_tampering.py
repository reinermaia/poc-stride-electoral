import requests
import json
import hashlib
import uuid
from datetime import datetime, timezone
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.token_generator import generate_token
from src.signing import generate_keypair, sign_payload

API_URL = "http://localhost:8000"

# chaves do ATACANTE (não são as chaves do servidor)
ATTACKER_PRIVATE_KEY, _ = generate_keypair()

def generate_legit_payload(private_key):
    """Gera payload legítimo com hash e assinatura corretos"""
    result = {
        "id": str(uuid.uuid4()),
        "station_id": "ZONA-001-SECAO-042",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": {"candidato_A": 120, "candidato_B": 98, "candidato_C": 45}
    }
    content = json.dumps(result, sort_keys=True)
    result["hash"] = hashlib.sha256(content.encode()).hexdigest()
    result["signature"] = sign_payload(result, private_key)
    return result

if __name__ == "__main__":
    token = generate_token("operador-zona-001")
    headers = {"Authorization": f"Bearer {token}"}

    print("=== ATAQUE TAMPERING - COM CONTROLES (hash + assinatura digital) ===\n")

    # payload legítimo assinado com chave do ATACANTE
    payload = generate_legit_payload(ATTACKER_PRIVATE_KEY)

    print("[1] Upload legítimo com chave do atacante (chave errada):")
    r = requests.post(f"{API_URL}/upload", json=payload, headers=headers)
    print(f"    Resultado: {r.json()}\n")

    print("[2] Upload com votos ADULTERADOS (hash inválido, sem assinatura):")
    tampered = payload.copy()
    tampered["candidates"] = {"candidato_A": 9999, "candidato_B": 0, "candidato_C": 0}
    tampered["signature"] = None
    r = requests.post(f"{API_URL}/upload", json=tampered, headers=headers)
    print(f"    Resultado: {r.json()}\n")

    print("[3] Upload com votos ADULTERADOS (hash recalculado, assinatura do atacante):")
    tampered2 = payload.copy()
    tampered2["candidates"] = {"candidato_A": 9999, "candidato_B": 0, "candidato_C": 0}
    content = json.dumps({k: tampered2[k] for k in ["id","station_id","timestamp","candidates"]}, sort_keys=True)
    tampered2["hash"] = hashlib.sha256(content.encode()).hexdigest()
    tampered2["signature"] = sign_payload(tampered2, ATTACKER_PRIVATE_KEY)
    r = requests.post(f"{API_URL}/upload", json=tampered2, headers=headers)
    print(f"    Resultado: {r.json()}\n")

    print(">>> COM CONTROLES: todos os ataques devem ser BLOQUEADOS")
