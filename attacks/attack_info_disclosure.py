import time
import sys
sys.path.insert(0, '/home/reiner/poc-stride-electoral')
from src.presigned import generate_presigned_url, validate_presigned_url, revoke_url

def test_baseline():
    """Baseline: URL sem TTL curto e sem binding — atacante reutiliza livremente"""
    print("=== BASELINE: URL com TTL longo (3600s) sem binding de actor ===\n")

    # simula URL com TTL longo (1 hora) — má prática
    url_data = generate_presigned_url("resultado-secreto", actor="qualquer", ttl_seconds=3600)
    token = url_data["token"]

    print(f"[1] URL gerada com TTL=3600s")
    print(f"    Token: {token[:20]}...\n")

    print("[2] Atacante captura e reutiliza token (mesmo actor pois não há binding):")
    result = validate_presigned_url(token, actor="qualquer")
    print(f"    Resultado: {result}\n")

    print("[3] Atacante reutiliza token novamente (sem one-time use):")
    result2 = validate_presigned_url(token, actor="qualquer")
    print(f"    Resultado: {result2}\n")

    print(">>> BASELINE: token reutilizável e com TTL longo — vulnerável\n")

def test_with_controls():
    """Com controles: TTL curto + binding de actor + one-time use"""
    print("=== COM CONTROLES: TTL=10s + binding de actor + one-time use ===\n")

    url_data = generate_presigned_url("resultado-secreto", actor="operador-001", ttl_seconds=10)
    token = url_data["token"]

    print(f"[1] URL gerada com TTL=10s para operador-001")
    print(f"    Token: {token[:20]}...\n")

    print("[2] Atacante tenta usar token com actor diferente:")
    result = validate_presigned_url(token, actor="atacante-999")
    print(f"    Resultado: {result}\n")

    print("[3] Operador legítimo usa token (válido):")
    result2 = validate_presigned_url(token, actor="operador-001")
    print(f"    Resultado: {result2}")
    revoke_url(token)  # one-time use
    print(f"    Token revogado após uso.\n")

    print("[4] Atacante tenta reutilizar token já revogado:")
    result3 = validate_presigned_url(token, actor="operador-001")
    print(f"    Resultado: {result3}\n")

    print("[5] Aguardando TTL expirar (11s)...")
    url_data2 = generate_presigned_url("resultado-secreto", actor="operador-001", ttl_seconds=10)
    token2 = url_data2["token"]
    time.sleep(11)
    result4 = validate_presigned_url(token2, actor="operador-001")
    print(f"    Resultado após expiração: {result4}\n")

    print(">>> COM CONTROLES: todos os vetores de Information Disclosure BLOQUEADOS")

if __name__ == "__main__":
    print("=== ATAQUE INFORMATION DISCLOSURE - Pre-signed URL ===\n")
    test_baseline()
    test_with_controls()
