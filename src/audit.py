import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = Path("/home/reiner/poc-stride-electoral/data/audit.log")

def _last_hash() -> str:
    if not AUDIT_FILE.exists():
        return "GENESIS"
    lines = AUDIT_FILE.read_text().strip().splitlines()
    if not lines:
        return "GENESIS"
    last = json.loads(lines[-1])
    return last.get("entry_hash", "GENESIS")

def _compute_entry_hash(entry: dict) -> str:
    """Computa hash de uma entrada SEM o campo entry_hash"""
    e = {k: v for k, v in entry.items() if k != "entry_hash"}
    return hashlib.sha256(json.dumps(e, sort_keys=True).encode()).hexdigest()

def append_log(event: str, data: dict, actor: str = "system") -> dict:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "actor": actor,
        "data": data,
        "prev_hash": _last_hash()
    }
    entry["entry_hash"] = _compute_entry_hash(entry)

    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return entry

def verify_chain() -> dict:
    if not AUDIT_FILE.exists():
        return {"valid": False, "reason": "Arquivo de log não encontrado"}

    lines = AUDIT_FILE.read_text().strip().splitlines()
    if not lines:
        return {"valid": False, "reason": "Log vazio"}

    prev_hash = "GENESIS"
    for i, line in enumerate(lines):
        entry = json.loads(line)
        stored_hash = entry["entry_hash"]
        expected_prev = entry.get("prev_hash")

        if expected_prev != prev_hash:
            return {"valid": False, "reason": f"Chain quebrado na entrada {i+1} — prev_hash não corresponde"}

        computed_hash = _compute_entry_hash(entry)
        if computed_hash != stored_hash:
            return {"valid": False, "reason": f"Hash adulterado na entrada {i+1}"}

        prev_hash = stored_hash

    return {"valid": True, "entries": len(lines)}

if __name__ == "__main__":
    import os
    if AUDIT_FILE.exists():
        AUDIT_FILE.unlink()
    append_log("upload", {"station_id": "ZONA-001", "result_id": "abc"}, actor="operador-001")
    append_log("query", {"result_id": "abc"}, actor="operador-001")
    print("Chain válida:", verify_chain())
