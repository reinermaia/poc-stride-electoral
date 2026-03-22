import requests
import time
import statistics
import json
import hashlib
import uuid
from datetime import datetime, timezone
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.token_generator import generate_token
from src.signing import generate_keypair, sign_payload

API_URL = "http://localhost:8000"
PRIVATE_KEY, _ = generate_keypair()

def generate_payload():
    result = {
        "id": str(uuid.uuid4()),
        "station_id": "ZONA-001-SECAO-042",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": {"candidato_A": 120, "candidato_B": 98, "candidato_C": 45}
    }
    content = json.dumps(result, sort_keys=True)
    result["hash"] = hashlib.sha256(content.encode()).hexdigest()
    result["signature"] = sign_payload(result, PRIVATE_KEY)
    return result

def measure_latency(func, n=30):
    times = []
    for _ in range(n):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append((end - start) * 1000)
    return {
        "p50": round(statistics.median(times), 2),
        "p95": round(sorted(times)[int(n * 0.95)], 2),
        "p99": round(sorted(times)[int(n * 0.99)], 2),
        "mean": round(statistics.mean(times), 2)
    }

def upload_sem_assinatura():
    token = generate_token("operador-test")
    payload = generate_payload()
    payload.pop("signature")
    requests.post(f"{API_URL}/upload", json=payload,
        headers={"Authorization": f"Bearer {token}"})

def upload_com_assinatura():
    token = generate_token("operador-test")
    payload = generate_payload()
    requests.post(f"{API_URL}/upload", json=payload,
        headers={"Authorization": f"Bearer {token}"})

if __name__ == "__main__":
    print("=== MEDIÇÃO DE LATÊNCIA - TAMPERING ===\n")
    print("Sem assinatura (bloqueado):")
    print(measure_latency(upload_sem_assinatura))
    print("\nCom assinatura válida (aceito):")
    print(measure_latency(upload_com_assinatura))
