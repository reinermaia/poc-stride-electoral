## Cenário 4 — Repudiation (R1/R3): Audit Trail Tampering

### Descrição
Um operador realiza upload de resultado e posteriormente tenta negar a ação
adulterando o audit log. Sem hash encadeado, a adulteração passa despercebida.
Com o controle ativo, qualquer modificação no log é detectada.

### Ativo afetado
Logs e trilha de auditoria (ref. Tabela 7 do catálogo STRIDE)

### Método de simulação
- Operador realiza upload legítimo (registrado no log)
- Atacante modifica diretamente o campo "actor" da entrada no log
- Sistema verifica integridade da chain antes e após adulteração

### Resultados

| Condição | Adulteração detectada | Detection Rate |
|---|---|---|
| Baseline (sem hash encadeado) | NÃO | 0% |
| Com hash encadeado SHA-256 | SIM | 100% |

### Achado científico
O hash encadeado garante que qualquer modificação em uma entrada do log
invalida o hash de todas as entradas subsequentes, tornando a adulteração
detectável mesmo por um atacante com acesso direto ao arquivo.

### Controles validados
- Audit log append-only com hash encadeado SHA-256
- Registro de eventos com actor, timestamp, prev_hash e entry_hash
- Verificação de integridade da chain completa

### Conclusão
O controle de hash encadeado detectou 100% das tentativas de adulteração
do audit log, garantindo não-repúdio e rastreabilidade forense das ações
dos operadores no pipeline de transmissão.
