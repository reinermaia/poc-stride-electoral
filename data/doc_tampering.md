## Cenário 2 — Tampering (T1/T3): File Modification + Hash Recalculation

### Descrição
Um atacante intercepta o arquivo de resultados em trânsito e modifica os votos,
tentando burlar a verificação de integridade. Dois vetores foram simulados:
adulteração sem recomputar o hash e adulteração com hash recalculado pelo atacante.

### Ativo afetado
Arquivo de resultados + metadados de chain of custody (ref. Tabela 7 do catálogo STRIDE)

### Método de simulação
- Ataque 1: upload com chave assimétrica do atacante (chave errada)
- Ataque 2: votos adulterados com hash inválido e sem assinatura
- Ataque 3: votos adulterados com hash recalculado e assinatura do atacante

### Achado científico
Hash SHA-256 sozinho é insuficiente: um atacante que conhece o algoritmo
consegue recalcular o hash após adulteração. A assinatura digital RSA-2048
com chave assimétrica fecha essa lacuna, pois o atacante não possui a chave
privada legítima.

### Resultados

| Condição | Ataque 1 | Ataque 2 | Ataque 3 | Detection Rate |
|---|---|---|---|---|
| Baseline (sem controles) | ACEITO | ACEITO | ACEITO | 0% |
| Apenas hash SHA-256 | ACEITO | BLOQUEADO | ACEITO | 33% |
| Hash + Assinatura RSA-2048 | BLOQUEADO | BLOQUEADO | BLOQUEADO | 100% |

### Latência (30 execuções)

| Métrica | Sem assinatura (ms) | Com assinatura válida (ms) | Overhead |
|---|---|---|---|
| p50 | 2.06 | 2.28 | +10% |
| p95 | 2.52 | 2.85 | +13% |
| p99 | 5.10 | 3.02 | -40% |
| mean | 2.18 | 2.29 | +5% |

### Overhead médio
0.11ms — imperceptível para janelas de transmissão eleitoral.

### Controles validados
- Verificação de hash SHA-256
- Assinatura digital RSA-2048 com chave assimétrica
- Rejeição de payload sem assinatura

### Conclusão
A combinação hash SHA-256 + assinatura RSA-2048 bloqueou 100% dos ataques
de tampering simulados, incluindo o vetor mais sofisticado onde o atacante
recalcula o hash. O overhead médio de 0.11ms é operacionalmente irrelevante.
