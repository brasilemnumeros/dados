# Metodologia — Selic

## selic-meta

- **Definição:** meta da taxa Selic definida pelo Copom, **ao ano** — o nível em vigor no
  **último dia do mês**. `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: nivel`,
  granularidade `mensal`.
- **Fonte e código:** Banco Central do Brasil, SGS **432** (meta Selic definida pelo Copom,
  % a.a., diária, desde 05/03/1999). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json`, consultado em janelas
  de 10 anos (limite do SGS para série diária). O `urlFonte` publicado é a página estável do
  histórico de taxas de juros (`https://www.bcb.gov.br/controleinflacao/historicotaxasjuros`),
  que abre e permite auditar o número; o endpoint sem janela responde HTTP 406.
- **Fórmula:** nenhuma. A meta do mês é a última leitura diária do mês (`valores[-1]`), isto é,
  o nível em vigor no último dia; o mês corrente é descartado. A média das leituras diárias não
  é usada: ela se afasta do nível de fim de mês sempre que o Copom se move dentro do mês, e o
  desvio chega a 4,85 p.p. (abr/1999: média de 36,85% contra 32,00% em vigor no último dia).
- **Cobertura:** desde 1999-03 até o último mês fechado — **332 pontos na edição atual**, sem
  lacuna.
- **Conferência:** jul/2016 = 14,25% ao ano (meta constante no período); out/2025 = 15,00%;
  mar/1999 = 42,00% (primeiro mês da fonte, a partir de 05/03; a média daria 44,22%). Todos os
  valores são múltiplos de 0,25 p.p.
- **Limitações:** é a meta anualizada, não a taxa efetiva nem o acumulado de aperto monetário.
  Acumulá-la exigiria convertê-la em taxa mensal equivalente e recompor — um construto que só
  coincide com a meta quando ela fica parada 12 meses (dez/2003: meta de 16,50% no último dia,
  construto de 23,03%).
- **Verificação independente:** a Agência Brasil de 18/06/2025
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2025-06/copom-eleva-juros-basicos-da-economia-para-15-ao-ano`)
  publica 15,00% a.a.; a de 16/09/2026
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-09/bc-reduz-juros-basicos-para-1375-ao-ano`)
  publica 13,75%; o Poder360 de 18/03/2026
  (`https://www.poder360.com.br/poder-economia/copom-reduz-selic-para-1475-inicia-ciclo-de-corte/`)
  registra a passagem de 15,00% para 14,75%. Todas citam o BCB; **não há segunda medição**.
  Busca feita em 05/11/2026.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## selic-over-acum-12m

- **Definição:** taxa efetiva Selic (over) acumulada nos 12 meses de calendário encerrados no
  mês de referência. `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: acumulado-12m`,
  granularidade `mensal`.
- **Fonte e código:** Banco Central do Brasil, SGS **11** (Selic % a.d., diária, desde 1986-06);
  a SGS 4390 serve de conferência. O `urlFonte` publicado é a página estável
  `https://www.bcb.gov.br/estatisticas/txjuros`; o endpoint sem `dataInicial` responde HTTP 406,
  porque a série é diária e o SGS exige janela de no máximo 10 anos.
- **Fórmula:** `V_t = (∏_{k=t−11}^{t} ∏_{d∈m_k}(1+i_d/100) − 1) × 100`, com o fator mensal
  `F_m = ∏_{d∈m}(1+i_d/100)` e a janela de 12 meses fechados — o mês corrente não entra.
- **Cobertura:** desde 1995-12 até o último mês fechado — **371 pontos na edição atual**, sem
  lacuna.
- **Conferência:** o fator mensal da 11 reproduz a 4390 em todos os meses comuns, com desvio
  máximo de 0,005 p.p. Choques: 2002-12 19,17%; 2008-12 12,48%; 2015-12 13,27%; 2020-12 2,76%.
  O valor é arredondado a 2 casas, a mesma precisão da série.
- **Verificação independente:** o Brasil Indicadores, página “Taxa Selic”, atualizada em
  04/11/2026 (`https://brasilindicadores.com.br/selic/`), traz a coluna “Acumulada em 12 meses”:
  os 22 meses de 2025-01 a 2026-10 batem exatamente com a série, incluindo 2025-10 = 13,71%,
  2025-12 = 14,32% e 2026-10 = 14,24%. A publicação cita o BCB; **não há segunda medição**.
  Busca feita em 05/11/2026.
- **Limitações:** é a taxa efetiva acumulada, não a meta nem a Selic de um dia; o acumulado de
  12 meses não é o rendimento de um investimento específico, que depende de impostos e prazos.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
