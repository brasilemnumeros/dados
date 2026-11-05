# Metodologia — Saneamento

## esgoto-rede-coletora-total

- **Definição:** percentual da população residente do Brasil atendida por rede coletora de esgoto,
  urbana e rural somadas. `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`,
  `anual` (C15: `AAAA-01-01`). Não é esgoto tratado: mede quem tem coleta, não quem tem
  tratamento.
- **Fonte e código:** SNIS — Série Histórica, base municipal consolidada, informação **ES001** (população
  total atendida com esgotamento sanitário), 1995–2022; e Sinisa — planilhas do módulo
  Esgotamento Sanitário, `GTE0001 + GTE0002` da linha `TOTAL NACIONAL` (ou `Brasil`) do
  consolidado UF/MR/Brasil, para 2023. O SNIS fez a última coleta em 2023 (dados de 2022); o
  Sinisa começou em 2023. O notebook descobre o arquivo do Sinisa nas páginas de resultados do
  programa e imprime o nome do arquivo usado.
- **`urlFonte`:** `https://app4.cidades.gov.br/serieHistorica/`, a página da Série Histórica do
  SNIS, que cobre 28 dos 29 pontos (1995–2022) e é o endereço estável da fonte principal. O
  Sinisa não tem URL única de série: o notebook descobre o arquivo do ano nas páginas de
  resultados.
- **Fórmula:** `100 × população total atendida ÷ população residente do Brasil (IBGE)`. O
  denominador é a informação **POP_TOT** da Série Histórica somada sobre todos os municípios
  (reproduz 169.799.170 em 2000 e 190.755.799 em 2010; em 2022, 203.080.756 é a estimativa do
  ano, 0,009% acima do Censo de 203.062.512).
- **Cobertura:** 1995–2023, **29 pontos** anuais. Primeiro ponto 5,57% (1995); último 54,83%
  (2023).
- **Quem não reporta entra como não atendido.** O numerador soma apenas a população que os
  prestadores declararam atender; município sem declaração não entra. A série é um **piso**.
- **Começo da série (1995–1999).** A alta de 5,57% para 28,95% (5,5× até 2000, com +13,85 p.p.
  só de 1995 para 1996) é a **rampa de entrada de municípios na amostra do SNIS**, não
  crescimento de cobertura. O denominador é o país inteiro, mas o numerador só conta quem
  declarou; ler o começo como “obras” superestima o avanço.
- **Emenda SNIS → Sinisa.** Não há ano de sobreposição: o SNIS termina em 2022 e o Sinisa começa
  em 2023. O critério de 0,1 p.p. vale para o mesmo ano medido pelas duas fontes e **não se
  aplica**; a emenda entra com a quebra declarada. O degrau 2022 → 2023 com o mesmo denominador é
  **−0,71 p.p.** (55,54% → 54,83%) e é **diagnóstico**, não gate: mistura troca de sistema,
  movimento do ano e mudança de amostra (o Sinisa 2023 cobre 186,5 milhões de habitantes, contra
  201,4 milhões na base de água do SNIS 2022).
- **2024 fica fora.** O IBGE muda a base populacional em 2024 (212,58 milhões contra 203,08
  milhões em 2022), um degrau de ~4,6% no denominador. A série entra em 2024 quando houver
  população nacional comparável. Enquanto isso, o notebook avisa na saída quando o Sinisa publica
  ano mais novo que o fim da série.
- **2023 usa a população de 2022.** O IBGE não publicou estimativa de 2023 na base do Censo (a
  publicação do DOU de 2023 trouxe 2022; a revisão de 2024 muda de base). Usar 203.080.756 em
  2023 **superestima** a taxa em cerca de **0,25–0,3 p.p.**, o crescimento populacional de 2022
  para 2023. Não é 0,005 p.p.: esse é outro efeito, a diferença entre a estimativa de 2022 e o
  Censo de 2022, que afeta o ponto de 2022.
- **Diferença para o índice oficial.** O SNIS 2022 publica IN056 = 56,0% e o Sinisa 2023 publica
  IES0001 = 59,7%. Os dois usam como denominador a população dos municípios que declararam; esta
  série divide a mesma população atendida pelo país inteiro (203,1 milhões em 2023), o que dá
  54,83% — 4,9 p.p. abaixo do índice da amostra.
- **Verificação independente:** SNIS, *Diagnóstico Temático Água e Esgoto — Visão Geral, SNIS
  2023* (dados de 2022), p. 70–71: 112,8 milhões atendidos e IN056 = 56,0% — o notebook
  reproduz 112.795.436 e 56,00%. Sinisa, *Relatório dos Serviços de Esgotamento Sanitário, SINISA
  2024* (referência 2023): IES0001 = 59,7% (111,3 milhões) — o notebook reproduz 111.344.129 e
  59,70% da planilha. Trata Brasil, *Ranking do Saneamento 2024* (base 2022): cerca de 90 milhões
  sem coleta (203,1 − 112,8 = 90,3 milhões). Consulta em 2026-11-05. As três publicações citam o
  SNIS/Sinisa; não há segunda medição.
- **Revisão:** o SNIS revisa a base e o IBGE revisa a população. Reexecutar o notebook só muda
  valor se a fonte revisar; nesse caso as âncoras do notebook falham e a revisão precisa ser
  registrada neste arquivo antes de publicar.
