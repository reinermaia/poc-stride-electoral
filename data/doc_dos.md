## Cenário 3 — Denial of Service (D1/D2): Pipeline Flooding

### Descrição
Durante a janela de transmissão, um atacante inunda a API com requisições
em alta frequência, visando degradar a disponibilidade e aumentar a latência
das transmissões legítimas além da janela operacional aceitável.

### Ativo afetado
API Gateway + pipeline de transmissão (ref. Tabela 7 do catálogo STRIDE)

### Método de simulação
- 20 workers simultâneos de flooding contra o endpoint /health
- 3 workers de transmissões legítimas em paralelo
- Duração: 10 segundos por cenário
- Métrica principal: latência e disponibilidade das requisições legítimas

### Resultados

| Condição | Disponibilidade | Latência p50 (ms) | Latência mean (ms) | Degradação |
|---|---|---|---|---|
| Sem ataque | 100% | 2.43 | 2.89 | — |
| Sob ataque DoS | 100% | 15.35 | 16.02 | +454.5% |

### Achado científico
O ataque DoS não derruba completamente a API, mas degrada a latência em
454.5% — de 2.89ms para 16.02ms. Em contexto eleitoral, essa degradação
representa risco direto ao cumprimento da janela operacional de transmissão,
podendo atrasar a divulgação de resultados e gerar questionamentos sobre
a integridade do processo.

### Controles validados
- Rate limiting (60/minute) no endpoint crítico /upload
- JWT validation como barreira prévia ao rate limiter
- Separação de endpoints críticos e não-críticos

### Conclusão
O cenário demonstra que ataques DoS de baixa sofisticação produzem impacto
operacional mensurável mesmo sem derrubar o serviço. Controles de rate
limiting e separação de endpoints são essenciais para proteger a janela
de transmissão eleitoral.
