import json
import hashlib
import uuid
from datetime import datetime, timezone

def generate_result(station_id: str, candidates: dict) -> dict:
    result = {
        "id": str(uuid.uuid4()),
        "station_id": station_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidates": candidates,
    }
    content = json.dumps(result, sort_keys=True)
    result["hash"] = hashlib.sha256(content.encode()).hexdigest()
    return result

if __name__ == "__main__":
    result = generate_result(
        station_id="ZONA-001-SECAO-042",
        candidates={"candidato_A": 120, "candidato_B": 98, "candidato_C": 45}
    )
    print(json.dumps(result, indent=2))
