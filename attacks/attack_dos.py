import requests
import time
import statistics
import uuid
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.token_generator import generate_token

API_URL = "http://localhost:8000"

def legit_health_check():
    start = time.perf_counter()
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": r.status_code, "latency_ms": round(elapsed, 2), "type": "legit"}
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "timeout", "latency_ms": round(elapsed, 2), "type": "legit"}

def attack_flood_health():
    """Flooding no /health — sem restrição de token"""
    start = time.perf_counter()
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": r.status_code, "latency_ms": round(elapsed, 2), "type": "attack"}
    except Exception:
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "timeout", "latency_ms": round(elapsed, 2), "type": "attack"}

def run_scenario(attack_workers: int, legit_workers: int, duration_seconds: int):
    results = []
    end_time = time.time() + duration_seconds

    def flood_loop():
        while time.time() < end_time:
            results.append(attack_flood_health())

    def legit_loop():
        while time.time() < end_time:
            results.append(legit_health_check())
            time.sleep(0.1)

    with ThreadPoolExecutor(max_workers=attack_workers + legit_workers) as executor:
        futures = []
        for _ in range(attack_workers):
            futures.append(executor.submit(flood_loop))
        for _ in range(legit_workers):
            futures.append(executor.submit(legit_loop))
        for f in as_completed(futures):
            pass

    return results

def analyze(results, label):
    legit = [r for r in results if r["type"] == "legit"]
    attacks = [r for r in results if r["type"] == "attack"]
    legit_ok = [r for r in legit if r["status"] == 200]
    legit_fail = [r for r in legit if r["status"] != 200]
    latencies = [r["latency_ms"] for r in legit_ok] or [0]
    print(f"\n--- {label} ---")
    print(f"Requisições de ataque:         {len(attacks)}")
    print(f"Checks legítimos:              {len(legit)}")
    print(f"Legítimos OK (200):            {len(legit_ok)}")
    print(f"Legítimos falha/timeout:       {len(legit_fail)}")
    print(f"Taxa de disponibilidade:       {round(len(legit_ok)/max(len(legit),1)*100, 1)}%")
    if latencies[0] > 0:
        print(f"Latência p50 (ms):             {round(statistics.median(latencies), 2)}")
        print(f"Latência mean (ms):            {round(statistics.mean(latencies), 2)}")

if __name__ == "__main__":
    print("=== ATAQUE DoS - FLOODING DO PIPELINE ===\n")

    print("[1] Baseline: sem ataque")
    r1 = run_scenario(attack_workers=0, legit_workers=3, duration_seconds=10)
    analyze(r1, "SEM ATAQUE")

    print("\n[2] Sob ataque: 20 workers de flooding")
    r2 = run_scenario(attack_workers=20, legit_workers=3, duration_seconds=10)
    analyze(r2, "SOB ATAQUE DoS (sem rate limiting no /health)")

    print("\n[3] Impacto na latência: degradação percentual")
    legit1 = [r for r in r1 if r["type"] == "legit" and r["status"] == 200]
    legit2 = [r for r in r2 if r["type"] == "legit" and r["status"] == 200]
    if legit1 and legit2:
        mean1 = statistics.mean([r["latency_ms"] for r in legit1])
        mean2 = statistics.mean([r["latency_ms"] for r in legit2])
        print(f"\n    Latência mean sem ataque:  {round(mean1, 2)}ms")
        print(f"    Latência mean sob ataque:  {round(mean2, 2)}ms")
        print(f"    Degradação:                +{round((mean2-mean1)/mean1*100, 1)}%")
