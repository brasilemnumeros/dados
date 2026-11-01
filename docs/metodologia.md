# Metodologia dos indicadores

Revisão da definição e da fórmula de cada indicador, conferida contra a fonte
e contra a matemática do próprio indicador — nunca contra o código atual.

> **Escopo do piloto:** apenas o IPCA foi revisado nesta rodada, por decisão
> explícita. As demais séries estão listadas em [Pendentes](#pendentes) e
> serão revisadas nas próximas rodadas.

## ipca-acum-12m

- **Definição:** variação percentual do IPCA acumulada nos últimos 12 meses
  (taxa efetiva do período), unidade `percentage` (`%`, 2 casas decimais),
  granularidade `monthly`.
- **Fonte e código:** IBGE, via API de Dados Abertos do Banco Central (SGS),
  série **13522** (IPCA, variação acumulada em 12 meses, %). É a série primária
  e única usada para o dado publicado. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados?formato=json`.
  A série 433 (variação mensal) **não** é usada para gerar a saída.
- **Fórmula atual:** `df['IPCA (%)'].rolling(12).sum()` sobre a série 433 —
  soma aritmética das 12 variações mensais; incorreta porque soma taxas em vez
  de usar a série acumulada oficial.
- **Fórmula proposta:** nenhuma. A série é lida direto da 13522 e publicada tal
  qual o BCB/IBGE a divulga. O notebook só busca, filtra os meses fechados e
  formata — o cálculo fica definido pela fonte, o que é intencional.
- **Evidência:**
  - A 13522 é a série oficial do SGS para “IPCA — variação acumulada em 12
    meses”; publicá-la direto elimina qualquer erro de acumulação local.
  - Conferência numérica (janela jul/2024 a jun/2025): a soma das variações
    mensais da 433 dá **5,23%** (valor publicado hoje), enquanto a 13522
    registra **5,35%** para 2025-06 — a soma diverge do oficial.
  - Mesma conferência em inflação alta: dez/2002 — soma **11,90%** vs. 13522
    **12,53%**; fev/2003 — soma **14,84%** vs. 13522 **15,85%**.
  - A 13522 já tem valores desde antes de 1995 (pré-Plano Real); o pipeline
    coleta desde **1995-01-01**, então a série publicada começa em 1995-01-01.
- **Veredito:** corrigir.
- **Impacto esperado:** os valores passam a ser os da série oficial 13522
  (mudam de `soma` para `oficial` em todos os pontos). Como a coleta começa em
  1995-01-01, a série publicada ganha os 11 pontos de 1995-01 a 1995-11 antes
  do atual início em 1995-12, e passa a se estender até o último mês fechado.
- **Decisão pendente:** não — aprovada pelo usuário; implementação na Task 4.

## Pendentes

Revisão não iniciada (próximas rodadas):

- `selic-meta-acum-12m`
- `selic-over-acum-12m`
- `igpm-acum-12m`
- `pib-real-anual`
- `mvgr-nominal`
- `mvgr-real`
- `caged-total-mensal`
- `populacao-total-anual`
- `populacao-variacao-anual`
- `homicidios-anual`
- `homicidios-armas-fogo-anual`
- `proporcao-homicidios-armas-fogo-anual`
