# Metodologia — Fiscal

## divida-liquida-pib

- **Definição:** razão entre a dívida líquida do setor público consolidado no fim do mês —
  dívida do setor público (União, INSS, estados, municípios, estatais, exceto Petrobras e
  Eletrobras, e Banco Central) descontados os ativos financeiros, inclusive as reservas
  internacionais — e o PIB nominal acumulado nos 12 meses encerrados naquele mês, em %.
  `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`, granularidade `mensal`.
- **Fonte e código:** Banco Central do Brasil — Estatísticas Fiscais, SGS **4513** (“Dívida
  líquida do setor público consolidado, % do PIB”). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.4513/dados?formato=json`. O SGS entrega `data`
  em `DD/MM/AAAA` e `valor` como texto; o notebook converte para `float` e não arredonda. O mês
  corrente é descartado.
- **Fórmula:** nenhuma. A série é oficial e já calculada; o notebook busca, corta o mês aberto e
  normaliza a data para o primeiro dia do mês (C15). Não é emendada com o IPEADATA
  (`PAN12_DTSPY12`, desde 1991), que é a mesma série transcrita por outro canal e exigiria uma
  emenda de safra.
- **Cobertura:** 2001-12 a 2026-09, **298 pontos**, sem lacuna. A série começa em dez/2001 no
  SGS.
- **Conferência:** primeiro ponto `2001-12 = 51,49%`; último `2026-09 = 69,98%`. Os valores
  conferem com a Tabela 4 das Estatísticas Fiscais do BCB. O denominador é o PIB corrente de 12
  meses estimado pelo BCB; quando o IBGE revisa as Contas Nacionais, a série inteira pode mudar
  — é revisão da fonte, não erro de fórmula. Meses recentes são preliminares.
- **Verificação independente:** a Agência Brasil publicou em 29/10/2026 que a dívida líquida
  ficou em **70% do PIB** em setembro, alta de **0,7 p.p.** no mês e de **4,7 p.p.** no ano
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-10/divida-publica-fica-em-829-do-pib-e-deficit-soma-r-55-bilhoes`);
  a série dá 69,98%, +0,71 p.p. e +4,74 p.p. — diferença de arredondamento. O Poder360
  (`https://www.poder360.com.br/poder-economia/divida-bruta-fica-em-829-do-pib-diz-banco-central/`)
  e a UOL conferem agosto/setembro. Não há segunda medição: a imprensa cita o BCB.
- **Limitações:** a DLSP inclui o Banco Central e as estatais (exceto Petrobras e Eletrobras) e
  desconta ativos; não é a dívida bruta do governo geral (DBGG), que tem outro universo, nem a
  dívida pública federal do Tesouro. A variação mensal é dominada por juros, câmbio e PIB
  nominal, não só pelo resultado primário; uma queda pode refletir valorização cambial ou
  crescimento nominal, não austeridade.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.

## resultado-primario-pib

- **Definição:** resultado primário do setor público consolidado — União, INSS, estados,
  municípios e estatais (exceto Petrobras e Eletrobras) e Banco Central — acumulado nos 12 meses
  encerrados no mês, em % do PIB corrente dos mesmos 12 meses. É receita menos despesa **sem**
  os juros da dívida; o resultado nominal é o primário mais os juros nominais. `percentual`
  (`%`, 2 casas), `eixo: percentual`, `medida: acumulado-12m`, granularidade `mensal` (C15).
- **Fórmula:** nenhuma de nível. O valor publicado é o **negativo** do valor da fonte:
  `publicado = −NFSP primária`. O SGS publica a necessidade de financiamento do setor público
  (NFSP), em que valor positivo é déficit; a série usa a convenção de “resultado primário”
  (positivo = superávit), a mesma do BCB na nota de divulgação e da imprensa. A inversão de
  sinal é feita uma vez, na célula de filtragem, e conferida ponto a ponto na validação.
- **Fonte e código:** Banco Central do Brasil — Estatísticas Fiscais, SGS **5793** (“NFSP sem
  desvalorização cambial (% PIB) — fluxo acumulado em 12 meses — resultado primário — total —
  setor público consolidado”). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.5793/dados?formato=json`. O SGS entrega `data`
  em `DD/MM/AAAA` e `valor` como texto; o notebook converte para `float` e não arredonda. O mês
  corrente é descartado. O BCB divulga o mês fechado no fim do mês seguinte (junto com a dívida
  líquida e a bruta); por isso o último ponto publicado é o último mês **divulgado**, não o
  último mês calendário.
- **Cobertura:** 2002-11 a 2026-09, **287 pontos**, sem lacuna. A série do total consolidado
  começa em nov/2002 no SGS; o fluxo mensal equivalente (SGS 4649) começa em dez/2001 e o
  acumulado de 12 meses em % do PIB exige 12 meses de fluxo. A diretriz de cobrir desde 1995 foi
  verificada: as séries de componentes começam antes — SGS 5786 (estados e municípios somados)
  em 1991-12, e 5787 (estaduais) e 5788 (municipais) em 1998-12 —, mas o **total** consolidado
  não tem série compatível antes de dez/2001. A transcrição do IPEADATA para a mesma definição
  (`BM12_NFSPPYS12`) tem 287 meses com valor, começando em 2002-11 e idêntica à SGS 5793: não é
  uma predecessora mais longa. Emendar componentes antigos com o total novo somaria universos
  diferentes, não safras. Busca feita em 06/11/2026.
- **Conferência:** primeiro ponto `2002-11 = +3,31%` (superávit); mínimo `2020-12 = −9,24%`
  (pico do déficit da pandemia); máximo `2005-04 = +4,08%`; último `2026-09 = −0,52%`. A
  identidade `NFSP primária + juros nominais = NFSP nominal` é conferida mês a mês contra as SGS
  **5727** (resultado nominal, % do PIB, 12 meses) e **5760** (juros nominais, % do PIB, 12
  meses), com tolerância de 0,02 p.p. (arredondamento de três séries com 2 casas); o desvio
  máximo observado é 0,01 p.p. O denominador é o PIB corrente de 12 meses do BCB: quando o IBGE
  revisa as Contas Nacionais, a razão inteira pode mudar — é revisão da fonte, não erro de
  fórmula. Meses recentes são preliminares.
- **Verificação independente:** a Agência Brasil publicou em 29/10/2026 que o setor público
  consolidado registrou, nos 12 meses até setembro, **déficit primário de R$ 70,1 bilhões,
  equivalente a 0,52% do PIB**, e que em agosto o indicador era **0,62%**
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-10/divida-publica-fica-em-829-do-pib-e-deficit-soma-r-55-bilhoes`);
  a série dá −0,52% em setembro e −0,62% em agosto. A mesma reportagem registra juros de 8,99%
  e nominal de 9,51% do PIB, que fecham a identidade com o primário. Para 2025, a CNN Brasil de
  30/01/2026 publica **déficit de R$ 55 bilhões, 0,43% do PIB**
  (`https://www.cnnbrasil.com.br/economia/money/macroeconomia/setor-publico-tem-deficit-de-r-55-bilhoes-em-2025-diz-banco-central/`);
  a série dá −0,43% em dezembro. As duas publicações citam o BCB; não há segunda medição.
- **Limitações:** é um fluxo acumulado em 12 meses, não um estoque — não mede a dívida. Exclui
  os juros: um primário positivo pode conviver com nominal muito negativo. É o setor público
  consolidado, não o governo central nem o governo geral. O denominador muda com a revisão do
  PIB. 2020 é atípico pelo gasto emergencial; 2021 e 2022 têm superávit inflado por receitas
  extraordinárias e inflação alta; a leitura de tendência atravessa esses choques. A estatística
  do BCB é “abaixo da linha” (variação do endividamento), diferente da execução orçamentária do
  Tesouro para o governo central.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** dados abertos do Banco Central do Brasil; atribuição ao BCB.
