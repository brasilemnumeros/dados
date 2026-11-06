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

## divida-bruta-pib

- **Definição:** razão entre a Dívida Bruta do Governo Geral (DBGG) no fim do mês — governo
  federal, INSS, governos estaduais e municipais — e o PIB nominal acumulado nos 12 meses
  encerrados naquele mês, em %. `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`,
  granularidade `mensal`. É dívida bruta: não desconta ativos financeiros.
- **Fonte e código:** Banco Central do Brasil — Estatísticas Fiscais, SGS **13762** (“Dívida
  bruta do governo geral (% PIB) — metodologia utilizada a partir de 2008”). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.13762/dados?formato=json`. O SGS entrega `data`
  em `DD/MM/AAAA` e `valor` como texto; o notebook converte para `float` e não arredonda. O mês
  corrente é descartado.
- **Fórmula:** nenhuma. A série é oficial e já calculada; o notebook busca, corta o mês aberto e
  normaliza a data para o primeiro dia do mês (C15).
- **Cobertura:** 2006-12 a 2026-09, **238 pontos**, sem lacuna. A diretriz de cobrir desde 1995
  foi verificada: a série oficial da DBGG no SGS começa em dez/2006, início do recálculo
  retroativo da metodologia atual (rotulada pelo SGS como “metodologia utilizada a partir de
  2008”); a DLSP, que começa em 2001, é outra medida e não substitui a bruta.
- **Conferência:** primeiro ponto `2006-12 = 55,48%`; último `2026-09 = 82,93%`; mínimo
  `51,27%` (2011-12); máximo `87,66%` (2020-10). Em dez/2022 a série dá `71,68%`, e o acumulado
  de 2026 até setembro é `+4,29 p.p.` (78,64% em dez/2025). Agosto/2026 = `82,87%`; setembro
  ficou estável. O denominador é o PIB corrente de 12 meses estimado pelo BCB; quando o IBGE
  revisa as Contas Nacionais, a série inteira pode mudar.
- **Verificação independente:** a Agência Brasil de 29/10/2026
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-10/divida-publica-fica-em-829-do-pib-e-deficit-soma-r-55-bilhoes`)
  publica **82,9% do PIB** em setembro de 2026, estável em relação a agosto, **+4,3 p.p.** no ano
  e **71,7%** no fim de 2022; a série dá 82,93%, 82,87% em agosto, +4,29 p.p. e 71,68% — a
  diferença é de arredondamento. O Poder360
  (`https://www.poder360.com.br/poder-economia/divida-bruta-fica-em-829-do-pib-diz-banco-central/`)
  publica o mesmo 82,9%. Não há segunda medição: a imprensa cita o BCB. Busca feita em 06/11/2026.
- **Limitações:** a DBGG cobre o governo geral (federal, INSS, estados e municípios) e não
  inclui o Banco Central nem as estatais; não desconta ativos, então não é a DLSP; não é a
  dívida pública federal do Tesouro. A variação mensal é dominada por juros nominais, câmbio e
  PIB nominal, não só pelo resultado primário. Meses recentes são preliminares e revisões do
  PIB podem alterar o denominador e o histórico.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** Dados abertos do Banco Central do Brasil (SGS); atribuição ao BCB.
