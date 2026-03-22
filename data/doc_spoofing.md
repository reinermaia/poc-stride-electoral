## Cenário 1 — Spoofing (S1/S2): Token Forgery

### Descrição
Um atacante tenta fazer upload de um arquivo de resultado falso sem token de
autenticação ou com um token JWT forjado, visando inserir dados fraudulentos
no pipeline de transmissão.

### Ativo afetado
Credenciais e tokens JWT (ref. Tabela 7 do catálogo STRIDE)

### Método de simulação
- Ataque 1: requisição POST /upload sem header Authorization
- Ataque 2: requisição POST /upload com token JWT com assinatura inválida

### Resultados

| Condição | Ataque 1 (sem token) | Ataque 2 (token forjado) | Detection Rate |
|---|---|---|---|
| Baseline (sem controles) | ACEITO | ACEITO | 0% |
| Com controles | BLOQUEADO (401) | BLOQUEADO (401) | 100% |

### Latência (30 execuções)

| Métrica | Sem token (ms) | Com token válido (ms) | Overhead |
|---|---|---|---|
| p50 | 1.07 | 1.55 | +44% |
| p95 | 2.25 | 2.56 | +13% |
| p99 | 5.82 | 16.31 | +180% |
| mean | 1.38 | 2.06 | +49% |

### Overhead médio
0.68ms — aceitável para janelas de transmissão eleitoral.

### Controles validados
- JWT validation (aud/scope/exp)
- Rejeição de requisições sem token
- Verificação de assinatura criptográfica (HS256)

### Conclusão
O controle de validação JWT bloqueou 100% dos ataques de spoofing simulados,
com overhead médio de 0.68ms, demonstrando eficácia sem impacto operacional
relevante no pipeline de transmissão.
