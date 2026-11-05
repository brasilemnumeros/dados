# Metodologia — Homicídios

## homicidios-anual

- **Definição:** taxa anual de homicídios por 100 mil habitantes, por local de residência.
  `numero` (`por 100 mil`, 2 casas), `eixo: por-100-mil`, `medida: nivel`, `anual`.
- **Fonte e código:** MS/SVS/CGIAE — SIM, compilado pelo IPEA/Atlas da Violência; numerador na
  série 328 do Atlas e denominador na série Ipeadata `AVIOL12_VIOLPOP` (população residente,
  estimativa/TCU ajustada). Endpoints: `https://www.ipea.gov.br/dados-api/series-values/328/1` e
  `https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='AVIOL12_VIOLPOP')`.
- **Fórmula:** `100.000 × homicídios ÷ população`, com o numerador do Atlas e a população
  `AVIOL12_VIOLPOP` do mesmo ano; nenhuma taxa herdada. A taxa pronta do Atlas (série 20) não é
  usada porque mistura populações de vintages diferentes (Contagem em 1996, Estimativas TCU em
  1997–2003 e 2016, IBGE/Diretoria de Pesquisas em 2004–2015), o que produz um patchwork de
  denominadores.
- **Cobertura:** 1995–2024, **30 pontos**, sem lacuna. O corte em 1995 é editorial: alinha a
  série às demais famílias; a série 328 tem 1989–1994, mas esse trecho usa a definição CID-9/SIM
  da década de 1990 e não é emendado ao bloco CID-10.
- **Conferência:** 2007 `48.219 ÷ 189.462.739 × 100.000 = 25,45`, igual à taxa pronta atual;
  2012 `57.045 ÷ 199.239.473 = 28,63` contra 28,86 da taxa pronta (denominador implícito de
  197,7 milhões); 2020 23,55 contra 23,84 da taxa pronta (−0,29; denominador implícito de
  209,2 milhões). 2003 28,53; 2017 31,72; 2022 21,81; 2023 21,52; 2024 20,04.
- **Verificação independente:** o G1 de 26/05/2026
  (`https://g1.globo.com/politica/noticia/2026/05/26/sete-em-cada-dez-homicidios-no-brasil-foram-cometidos-com-arma-de-fogo-em-2024-diz-atlas-da-violencia.ghtml`)
  publica 42.590 homicídios em 2024 e 29.870 por arma de fogo, 70,1% do total e queda de 8,8%
  nas armas. O total de 42.590 é exatamente o da série; a taxa de 20,04 por 100 mil é cálculo
  do site com a `AVIOL12_VIOLPOP`, não um número publicado pelo G1. A publicação cita o Atlas,
  não é segunda medição; a conferência da série 20 é do próprio produtor. Busca feita em
  05/11/2026.
- **Limitações:** 2022 e 2023 usam interpolação exponencial entre 2021 e 2024 na
  `AVIOL12_VIOLPOP`. O erro do denominador é de 0,9% em dois anos (a projeção 2024 do IBGE dá
  210,9 milhões para 2022 contra 212,8 milhões da VIOLPOP), sem gerar degrau na série. Trocar a
  fonte para as Projeções 2024 começaria em 2000 e truncaria 1995–1999 ou reintroduziria dois
  denominadores.
- **Condição de revisão:** refazer o cálculo quando o IPEA/IBGE publicarem população consolidada
  para 2022 e 2023.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## homicidios-armas-fogo-anual

- **Definição:** taxa anual de homicídios por armas de fogo por 100 mil habitantes, por local de
  residência. `numero` (`por 100 mil`, 2 casas), `eixo: por-100-mil`, `medida: nivel`, `anual`.
- **Fonte e código:** SIM, compilado pelo Atlas da Violência. Numerador: série 31 do Ipea para
  1995–2013; 2014–2024: Atlas da Violência 2026 (FBSP/Ipea), Tabela 11.1, publicado em PDF
  (`https://forumseguranca.org.br/wp-content/uploads/2026/05/atlas-violencia-2026-relatorio-completo.pdf`).
  Denominador: `AVIOL12_VIOLPOP`, a mesma população de `homicidios-anual`.
- **Fórmula:** `100.000 × homicídios_armas ÷ população`, com a contagem da série 31 (1995–2013) ou
  do Atlas 2026 (2014–2024) e a mesma população do ano; datas no dia 01 (C9). A taxa pronta da
  série 35 não é usada: usa população mista e para em 2022; a rota `/valores-series/35/1` da API
  do Atlas devolve 404 e trazia a data de publicação (`YYYY-01-15`) como referência.
- **Cobertura:** 1995–2024, **30 pontos**, sem lacuna.
- **Conferência:** 2007 `34.147 ÷ 189.462.739 = 18,02`; 2012 `40.077 ÷ 199.239.473 = 20,11`;
  2013 `40.369 ÷ 201.029.717 = 20,08`; 2019 `32.091 ÷ 210.131.314 = 15,27`. Bloco 2014–2024:

  | ano | homicídios por arma | taxa |
  |---:|---:|---:|
  | 2014 | 43.397 | 21,40 |
  | 2015 | 42.656 | 20,86 |
  | 2016 | 45.616 | 22,13 |
  | 2017 | 49.085 | 23,74 |
  | 2018 | 42.908 | 20,58 |
  | 2019 | 32.091 | 15,27 |
  | 2020 | 35.828 | 16,92 |
  | 2021 | 35.070 | 16,44 |
  | 2022 | 33.580 | 15,78 |
  | 2023 | 32.749 | 15,41 |
  | 2024 | 29.870 | 14,05 |

  A Tabela 11.3 do Atlas registra 70,1% de participação em 2024, compatível com a contagem.
- **Verificação independente:** o G1 de 26/05/2026
  (`https://g1.globo.com/politica/noticia/2026/05/26/sete-em-cada-dez-homicidios-no-brasil-foram-cometidos-com-arma-de-fogo-em-2024-diz-atlas-da-violencia.ghtml`)
  publica 29.870 homicídios por arma de fogo em 2024, 70,1% dos 42.590 homicídios e queda de
  8,8% sobre 2023; a contagem é a mesma da série. A taxa de 14,05 por 100 mil é cálculo do site
  com a `AVIOL12_VIOLPOP`, não um número publicado pelo G1. A publicação cita o Atlas, não é
  segunda medição. Para 1995–2013 não há segunda medição localizada; a
  conferência de 2014–2024 contra a Tabela 11.3 é do próprio produtor. Busca feita em
  05/11/2026.
- **Limitações:** a série é mista por necessidade: 1995–2013 vêm da série 31 e 2014–2024 do Atlas
  2026. A edição de 2025 do Atlas (Tabela 11.1) traz 2013 = 40.870, mas o ponto publicado usa
  40.369 (série 31); a emenda 2013/2014 fica em **+7,50%** na contagem (40.369 → 43.397), contra
  +6,18% se o 2013 revisado fosse usado. O valor de 2022 coincide nas duas safras (33.580), então
  não há degrau de nível em 2022. A fonte 2014–2024 é PDF porque a API do Ipea não publica essa
  safra e os microdados do SIM/DATASUS não estão tabulados para 2024.
- **Condição de revisão:** quando o Ipea publicar a safra 2026 na API (série 31 com 2024),
  remover o complemento em PDF e conferir o bloco 2014–2024 contra a API; trocar 1995–2013 de
  uma vez, não ano a ano, para não criar uma ilha de safras. O gatilho é a API deixar de devolver
  2023 = 30.789 ou passar a devolver 2024.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## proporcao-homicidios-armas-fogo-anual

- **Definição:** participação percentual dos homicídios por armas de fogo no total de homicídios.
  `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: participacao`, `anual`.
- **Fonte e código:** derivada das contagens de armas (série 31 até 2013; Atlas da Violência 2026,
  Tabela 11.1, em 2014–2024) e do total (série 328). O `urlFonte` do JSON aponta para o PDF do
  Atlas, que cobre o bloco de armas a partir de 2014; os pontos de 1995–2013 vêm da API do Ipea
  (séries 31 e 328), cujos endpoints estão na seção `homicidios-armas-fogo-anual`.
- **Fórmula:** `100 × homicídios_armas ÷ homicídios_total`, direto das contagens, nos anos em que
  ambas existem. A razão entre as duas taxas só é igual a isso quando as duas usam o mesmo
  denominador — o que não acontece em vários anos.
- **Cobertura:** 1995–2024, **30 pontos**, sem lacuna.
- **Conferência:** em 1995–2013 a proporção é exatamente `100 × série 31 ÷ série 328` (diferença
  0,00 no 2º decimal). 2013 = 70,33%; 2014 = 71,76%; 2024 = 70,13%, igual aos 70,1% publicados
  pelo Atlas.
- **Verificação independente:** o G1 de 26/05/2026
  (`https://g1.globo.com/politica/noticia/2026/05/26/sete-em-cada-dez-homicidios-no-brasil-foram-cometidos-com-arma-de-fogo-em-2024-diz-atlas-da-violencia.ghtml`)
  publica 29.870 de 42.590 homicídios em 2024, 70,1%, a menor proporção desde 2014 — igual ao
  ponto `2024-01-01` (70,13%). A publicação cita o Atlas, não é segunda medição; para
  1995–2013 não há segunda medição localizada. Busca feita em 05/11/2026.
- **Limitações:** em 1995–2013 o numerador é a contagem da série 31 e o denominador é o total da
  safra 2026, então a proporção desse trecho mistura safras. Com o 2013 revisado (40.870), a
  proporção de 2013 seria 71,21% em vez de 70,33%; a emenda 2013/2014 fica em +1,43 p.p. na
  proporção (70,33 → 71,76) e cairia para +0,55 p.p. com o 2013 revisado.
- **Condição de revisão:** a mesma de `homicidios-armas-fogo-anual` — quando a API do Ipea
  publicar a safra 2026, trocar o bloco 1995–2013 inteiro.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
