# Metodologia dos indicadores

Revisão da definição e da fórmula de cada indicador, conferida contra a fonte
e contra a matemática do próprio indicador — nunca contra o código atual.

> **Escopo do piloto:** apenas o IPCA foi revisado nesta rodada, por decisão
> explícita. As demais séries estão listadas em [Pendentes](#pendentes) e
> serão revisadas nas próximas rodadas.

## ipca-acum-12m

- **Definição:** variação percentual do IPCA acumulada nos últimos 12 meses
  (taxa efetiva do período, composta por encadeamento), unidade `percentage`
  (`%`, 2 casas decimais), granularidade `monthly`.
- **Fonte e código:** IBGE, lida pela API de Dados Abertos do Banco Central
  (SGS). Série de trabalho: **433** (IPCA, variação mensal, % a.m.). Série de
  conferência: **13522** (IPCA, variação acumulada em 12 meses, %).
  Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json`.
- **Fórmula atual:** `df['IPCA (%)'].rolling(12).sum()` — soma aritmética das
  12 variações mensais.
- **Fórmula proposta:** composição (encadeamento) das 12 variações mensais:
  `(∏(1 + r_i/100) − 1) × 100`, com `i` de `t−11` a `t`.
  Equivalentemente, ler direto a série oficial 13522.
- **Evidência:**
  - Definição matemática: inflação acumulada em um período é o produto dos
    fatores mensais `(1 + r_i/100)`, não a soma das taxas. O IBGE, na página
    “Inflação” (`ibge.gov.br/explica/inflacao.php`), descreve o IPCA como
    índice mensal cujo acumulado é obtido por encadeamento.
  - Conferência numérica contra a série oficial 13522 (SGS, janela jul/2024 a
    jun/2025): a soma das variações mensais dá **5,23%** (valor publicado),
    a composição dá **5,35%** e a série 13522 registra **5,35%** para 2025-06.
  - Mesma conferência em períodos de inflação alta: dez/2002 — soma publicada
    **11,90%** vs. 13522 **12,53%**; fev/2003 — soma publicada **14,84%** vs.
    13522 **15,85%**.
- **Veredito:** corrigir.
- **Impacto esperado:** a série publicada subestima a inflação acumulada em
  todos os pontos, porque `composto > soma` para taxas positivas. A diferença
  cresce com o nível da inflação: ~0,1 p.p. ao redor de 5% a.a. (diferença
  relativa ~2%) e ~0,6–1,0 p.p. em 2002–2003 (12–16% a.a.). A correção altera
  todos os valores já publicados — é revisão histórica, não atualização.
- **Decisão pendente:** sim.

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
