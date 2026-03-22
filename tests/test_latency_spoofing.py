import requests
import time
import statistics
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.token_generator import generate_token

API_URL = "http://localhost:8000"

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

def upload_sem_token():
    requests.post(f"{API_URL}/upload", json={
        "id": "test", "station_id": "ZONA-001",
        "timestamp": "2026-03-22T20:00:00Z",
        "candidates": {"A": 1}, "hash": "abc"
    })

def upload_com_token_valido():
    token = generate_token("operador-test")
    requests.post(f"{API_URL}/upload", json={
        "id": "test", "station_id": "ZONA-001",
        "timestamp": "2026-03-22T20:00:00Z",
        "candidates": {"A": 1}, "hash": "abc"
    }, headers={"Authorization": f"Bearer {token}"})

if __name__ == "__main__":
    print("=== MEDIÇÃO DE LATÊNCIA - SPOOFING ===\n")
    print("Sem token (bloqueado):")
    print(measure_latency(upload_sem_token))
    print("\nCom token válido (aceito):")
    print(measure_latency(upload_com_token_valido))
