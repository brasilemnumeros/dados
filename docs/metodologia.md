# Metodologia dos indicadores

Revisão da definição e da fórmula de cada indicador, conferida contra a fonte
e contra a matemática do próprio indicador — nunca contra o código atual.

> **Escopo do piloto:** apenas o IPCA foi revisado nesta rodada, por decisão
> explícita. O IGP-M entrou na rodada seguinte (`igpm-acum-12m`, decisão
> pendente de aval). As demais séries estão listadas em
> [Pendentes](#pendentes) e serão revisadas nas próximas rodadas.

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

## igpm-acum-12m

- **Definição:** variação percentual do IGP-M acumulada nos últimos 12 meses (taxa
  efetiva do período), unidade `percentual` (`%`, 2 casas decimais),
  `medida: acumulado-12m`, granularidade `mensal`.
- **Fonte e código:** FGV, via API de Dados Abertos do Banco Central (SGS), série
  **28655** — variação mensal do IGP-M calculada sobre os números-índices da FGV,
  a mesma série que o BCB usa na Calculadora do Cidadão para correção pelo IGP-M
  desde 12/04/2021. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.28655/dados?formato=json`.
  O IGP-M **não tem** série pronta de acumulado em 12 meses no SGS: o catálogo de
  séries do IGP-M (`https://www4.bcb.gov.br/pec/series/port/metadados/mg40Bp.htm`)
  lista apenas 0189 (variação mensal), 7448/7449 (1º e 2º decêndios) e 7450–7458
  (componentes IPA-M, IPC-M, INCC-M). A 0189 (variação mensal publicada, 2 casas) é
  buscada só para conferência; a 28655, de precisão estendida, gera a saída.
- **Fórmula atual:** `df_igpm_combined.rolling(12).sum()` sobre as variações mensais
  da 0189 — soma aritmética das 12 taxas; incorreta porque soma percentuais que
  deveriam ser capitalizados, e subestima o acumulado em todo período com taxas
  relevantes.
- **Fórmula proposta:** composição geométrica das 12 variações mensais,
  `(∏(1 + i/100) − 1) × 100`, sobre a 28655. A fonte do dado mensal não muda (é a
  mesma série da FGV); o que muda é a agregação, de soma para capitalização.
- **Evidência:**
  - Não existe série oficial acumulada em 12 meses para o IGP-M (ver catálogo
    acima), ao contrário do IPCA (SGS 13522). Por isso o acumulado é calculado — mas
    a partir da série mensal oficial, não de taxas somadas.
  - A 28655 é a série de precisão estendida derivada dos números-índices da FGV:
    coincide com a 0189 até a 2ª casa nos 449 meses da história (única diferença,
    jul/1989: 35,9051% contra 35,90%).
  - Conferência contra a tabela de 12 meses publicada pela FGV
    (`https://portal.fgv.br/noticias/igp-m-2025`), 14 meses de nov/2024 a dez/2025:
    a composição da 28655 reproduz **os 14 valores**; a da 0189 reproduz 8. Em
    set/2024 e out/2024, que só consegui conferir em fonte secundária, a composição
    da 28655 fica 0,01 p.p. acima do publicado — o tamanho do arredondamento de 2
    casas.
  - Out/2026: a FGV publica **5,24%** em 12 meses (portal IBRE). A composição da
    28655 dá 5,2369% (arredonda para 5,24%); a da 0189 dá 5,2465% (5,25%).
  - Choque de 2002–2003, soma → composição: dez/2002 **22,92% → 25,31%**
    (+2,39 p.p.); fev/2003 **27,11% → 30,60%** (+3,49 p.p.); jun/2003
    **25,28% → 28,23%** (+2,95 p.p.).
  - Recente: jun/2025 **4,35% → 4,39%**; jul/2025 **2,97% → 2,96%**; dez/2025
    **−1,02% (soma) → −1,05%**, igual ao valor publicado pela FGV.
  - Onde a soma erra mais, no trecho comum: mai/2021 — **32,00% → 37,04%**
    (+5,04 p.p.).
  - No trecho comum (349 pontos), **331 valores mudam** e 18 coincidem ao centésimo
    (meses de inflação baixa); diferença média absoluta de 0,47 p.p.
- **Veredito:** corrigir.
- **Impacto esperado:** a série publicada passa de 349 para **382 pontos**, de
  `1996-07-01`–`2025-07-01` para `1995-01-01`–`2026-10-01`. Ganha 18 pontos antes do
  início atual (1995-01 a 1996-06) e 15 depois do fim atual (2025-08 a 2026-10). A
  fonte tem janela de 12 meses fechada desde `1990-05` (o IGP-M começa em jun/1989);
  o recorte em 1995-01 alinha a série ao `ipca-acum-12m` e deixa de fora a cauda de
  hiperinflação — o primeiro ponto publicado é 603,74% (jan/1995), comparável ao
  631,54% do IPCA no mesmo mês. Último ponto: **5,24%** (out/2026).
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01. O notebook
  reescreve `indicadores/igp-m/igpm-acum-12m.json` inteiro a cada execução, com a
  série de 382 pontos publicada nesta rodada.

## Pendentes

Revisão não iniciada (próximas rodadas):

- `selic-meta-acum-12m`
- `selic-over-acum-12m`
- `pib-real-anual`
- `mvgr-nominal`
- `mvgr-real`
- `caged-total-mensal`
- `populacao-total-anual`
- `populacao-variacao-anual`
- `homicidios-anual`
- `homicidios-armas-fogo-anual`
- `proporcao-homicidios-armas-fogo-anual`
