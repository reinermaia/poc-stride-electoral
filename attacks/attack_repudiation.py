import requests
import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.token_generator import generate_token
from src.audit import verify_chain, AUDIT_FILE

API_URL = "http://localhost:8000"

def do_upload(operator: str):
    """Realiza upload legítimo como operador específico"""
    token = generate_token(operator)
    from src.signing import generate_keypair, sign_payload
    private_key, _ = generate_keypair()
    result = {
        "id": str(uuid.uuid4()),
        "station_id": "ZONA-001-SECAO-042",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": {"candidato_A": 120, "candidato_B": 98, "candidato_C": 45}
    }
    content = json.dumps(result, sort_keys=True)
    result["hash"] = hashlib.sha256(content.encode()).hexdigest()
    result["signature"] = sign_payload(result, private_key)
    r = requests.post(f"{API_URL}/upload", json=result,
        headers={"Authorization": f"Bearer {token}"})
    return result["id"], r.json()

def attempt_log_tampering():
    """Simula tentativa de adulteração do audit log"""
    if not AUDIT_FILE.exists():
        return {"tampered": False, "reason": "Log não encontrado"}

    lines = AUDIT_FILE.read_text().strip().splitlines()
    if not lines:
        return {"tampered": False, "reason": "Log vazio"}

    # tenta modificar a última entrada
    entries = [json.loads(l) for l in lines]
    entries[-1]["actor"] = "operador-falso"

    with open(AUDIT_FILE, "w") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    return {"tampered": True, "modified_entry": entries[-1]["event"]}

if __name__ == "__main__":
    print("=== ATAQUE REPUDIATION - AUDIT TRAIL ===\n")

    # limpa log anterior
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()

    print("[1] Operador realiza upload legítimo:")
    result_id, response = do_upload("operador-zona-001")
    print(f"    Resposta: {response}")
    print(f"    Result ID: {result_id}\n")

    print("[2] Verifica chain antes da adulteração:")
    chain = verify_chain()
    print(f"    Chain válida: {chain}\n")

    print("[3] Atacante tenta adulterar o audit log:")
    tamper = attempt_log_tampering()
    print(f"    Adulteração: {tamper}\n")

    print("[4] Verifica chain após adulteração:")
    chain_after = verify_chain()
    print(f"    Chain válida: {chain_after}\n")

    if not chain_after["valid"]:
        print(">>> CONTROLE EFICAZ: adulteração detectada pelo hash encadeado")
    else:
        print(">>> VULNERÁVEL: adulteração não detectada")
