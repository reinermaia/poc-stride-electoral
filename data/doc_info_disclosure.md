## Cenário 5 — Information Disclosure (I1/I3): Pre-signed URL Leak

### Descrição
Uma URL pré-assinada com TTL longo vaza via log ou resposta de erro.
Um atacante a captura e reutiliza para acessar arquivos de resultado
antes da publicação oficial ou múltiplas vezes sem autorização.

### Ativo afetado
Pre-signed URL / arquivo de resultados no storage (ref. Tabela 7 do catálogo STRIDE)

### Método de simulação
- Baseline: URL com TTL=3600s sem binding de actor e sem one-time use
- Com controles: TTL=10s + binding de actor + revogação após uso
- 5 vetores testados: reutilização, actor errado, token revogado, TTL expirado

### Resultados

| Vetor | Baseline | Com Controles |
|---|---|---|
| Reutilização do token | ACEITO | BLOQUEADO |
| Múltiplas reutilizações | ACEITO | BLOQUEADO |
| Actor diferente | N/A | BLOQUEADO |
| Token revogado (one-time) | N/A | BLOQUEADO |
| TTL expirado | N/A | BLOQUEADO |
| Detection Rate | 0% | 100% |

### Achado científico
TTL longo sem binding de actor permite reutilização irrestrita do token,
expondo arquivos de resultado a qualquer portador da URL. A combinação
TTL curto + binding de actor + one-time use elimina completamente
esse vetor de Information Disclosure.

### Controles validados
- TTL curto (10s) nas URLs pré-assinadas
- Binding de actor — token válido apenas para o operador emissor
- One-time use — token revogado automaticamente após primeiro uso

### Conclusão
Os três controles combinados bloquearam 100% dos vetores de Information
Disclosure testados, sem impacto operacional relevante para o fluxo
legítimo de transmissão.
