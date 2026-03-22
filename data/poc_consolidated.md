# Experimental Evaluation — POC STRIDE Electoral Transmission

## 5.1 Experimental Setup

A proof-of-concept (POC) was implemented to empirically validate the STRIDE
threat catalog proposed for the results transmission phase in electronic elections.
The environment was deliberately designed at medium fidelity — sufficient to
validate threat classes and control effectiveness without requiring production
infrastructure.

### Environment
- OS: Ubuntu 24.04 LTS (WSL2 on Windows 11)
- Language: Python 3.12.3
- API Framework: FastAPI 0.135.1 + Uvicorn 0.42.0
- Auth: python-jose 3.5.0 (JWT/HS256)
- Crypto: cryptography (RSA-2048)
- Rate Limiting: slowapi
- Storage (simulated): in-memory + append-only audit log
- Queue (simulated): Redis 7 (Docker)
- Object Storage (simulated): MinIO (Docker)
- Database (simulated): PostgreSQL 16 (Docker)

### Architecture
The POC implements a simplified version of the reference architecture
described in Section 4, with three explicit trust boundaries:
- TB-1: ResultGenerator → TransmissionClient (local/source environment)
- TB-2: TransmissionClient → API Gateway (network crossing)
- TB-3: API Gateway → Cloud Services (managed services boundary)

### Methodology
Each scenario was executed in two modes:
- Baseline: pipeline without security controls
- With controls: pipeline with controls active (feature flags)
Attack scripts were executed against both modes and results compared.
Latency measurements used 30 executions per scenario (p50/p95/p99/mean).

---

## 5.2 Attack Scenarios and Results

### Scenario 1 — Spoofing (S1/S2): Token Forgery

| Condition | No Token | Forged Token | Detection Rate |
|---|---|---|---|
| Baseline | ACCEPTED | ACCEPTED | 0% |
| With controls | 401 Blocked | 401 Blocked | 100% |

Controls applied: JWT validation (aud/scope/exp), signature verification (HS256).

### Scenario 2 — Tampering (T1/T3): File Modification

| Condition | Invalid Hash | Recalculated Hash | Detection Rate |
|---|---|---|---|
| Baseline | ACCEPTED | ACCEPTED | 0% |
| Hash only | BLOCKED | ACCEPTED | 33% |
| Hash + RSA-2048 | BLOCKED | BLOCKED | 100% |

Scientific finding: SHA-256 hash alone is insufficient. An attacker who knows
the algorithm can recompute the hash after tampering. RSA-2048 digital
signature closes this gap, as the attacker does not possess the private key.

Controls applied: SHA-256 hash verification + RSA-2048 digital signature.

### Scenario 3 — Denial of Service (D1/D2): Pipeline Flooding

| Condition | Availability | Latency mean (ms) | Degradation |
|---|---|---|---|
| No attack | 100% | 2.89 | — |
| Under DoS (20 workers) | 100% | 16.02 | +454.5% |

Scientific finding: DoS does not crash the API but degrades latency by 454.5%,
directly impacting the electoral transmission window.

Controls applied: Rate limiting (60/minute on /upload), JWT as pre-filter.

### Scenario 4 — Repudiation (R1/R3): Audit Trail Tampering

| Condition | Tampering Detected | Detection Rate |
|---|---|---|
| Baseline (no chain) | NO | 0% |
| With chained hash | YES | 100% |

Controls applied: Append-only audit log with SHA-256 chained hash,
actor/timestamp/prev_hash per entry.

### Scenario 5 — Information Disclosure (I1/I3): Pre-signed URL Leak

| Vector | Baseline | With Controls |
|---|---|---|
| Token reuse | ACCEPTED | BLOCKED |
| Multiple reuses | ACCEPTED | BLOCKED |
| Different actor | N/A | BLOCKED |
| Revoked token | N/A | BLOCKED |
| Expired TTL | N/A | BLOCKED |
| Detection Rate | 0% | 100% |

Controls applied: TTL=10s, actor binding, one-time use revocation.

---

## 5.3 Performance Evaluation

### Latency overhead per scenario (30 executions)

| Scenario | Baseline mean (ms) | Secure mean (ms) | Overhead (ms) | Overhead (%) |
|---|---|---|---|---|
| Spoofing | 1.38 | 2.06 | +0.68 | +49% |
| Tampering | 2.18 | 2.29 | +0.11 | +5% |
| DoS (no attack) | 2.89 | — | — | — |
| DoS (under attack) | — | 16.02 | +13.13 | +454% |

All latency overheads introduced by security controls (Spoofing: +0.68ms,
Tampering: +0.11ms) remain well within acceptable bounds for electoral
transmission windows, which typically operate on minute-scale deadlines.

---

## 5.4 Threat Coverage Analysis

| STRIDE Category | Asset (ref. Table 7) | Scenario | Detection Rate | Control |
|---|---|---|---|---|
| Spoofing (S) | Credentials/tokens | Token Forgery | 100% | JWT + HS256 |
| Tampering (T) | Results media | File Modification | 100% | SHA-256 + RSA-2048 |
| Repudiation (R) | Audit trails | Log Tampering | 100% | Chained hash log |
| Information Disclosure (I) | Pre-signed URL | URL Leak | 100% | TTL + binding + one-time |
| Denial of Service (D) | API Gateway | Flooding | — | Rate limiting |
| Elevation of Privilege (E) | IAM/Roles | — | — | (architectural control) |

STRIDE coverage: 5 out of 6 categories exercised (83%).
Elevation of Privilege was addressed architecturally (RBAC/least-privilege)
and is recommended as future empirical validation.

---

## 5.5 Limitations

- Medium-fidelity environment: threats and controls represent classes of risk,
  not an assessment of a specific deployed infrastructure.
- No quantitative risk scoring or formal penetration testing.
- Elevation of Privilege not empirically tested (architectural control only).
- RSA key pair generated in memory at startup — production requires HSM
  or Secrets Manager integration.
- DoS scenario demonstrates latency degradation but not full service
  disruption, which may occur at higher attack volumes.

---

## 5.6 Summary

The experimental results demonstrate that the proposed STRIDE catalog is
not only descriptively valid but operationally actionable: all five tested
STRIDE categories were exercised, controls achieved detection rates of 100%
across scenarios S, T, R, and I, and performance overhead remained below
1ms for authentication and integrity controls — well within acceptable bounds
for electoral transmission windows.

The key scientific finding is that SHA-256 hash alone is insufficient for
integrity protection: an attacker who knows the algorithm can recompute
the hash after tampering. RSA-2048 digital signature is required to close
this gap. This transforms the catalog from a theoretical artifact into an
empirically grounded tool for requirements engineering, audit planning,
and test design in real-world electoral systems.
