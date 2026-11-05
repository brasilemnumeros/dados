# Metodologia — Câmbio

## cambio-media-mensal

- **Definição:** taxa de câmbio **nominal** do dólar americano, mercado livre/comercial,
  cotação de **venda** (PTAX), em reais por dólar, **média aritmética das cotações diárias** do
  mês. `moeda` (`R$/US$`, 4 casas), `eixo: reais`, `medida: nivel`, granularidade `mensal`
  (C15: `AAAA-MM-01`).
- **Fonte e código:** Banco Central do Brasil, SGS **3698** — “Taxa de câmbio livre - Dólar
  americano (venda) - média de período - mensal” (PTAX venda), série oficial já agregada.
  Endpoint: `https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json`. O notebook
  busca a série inteira, corta em `1995-01-01`, descarta o mês corrente (aberto) e grava o valor
  sem arredondamento novo; `casas: 4` é só exibição.
- **Fórmula:** nenhuma — o BCB publica a média já calculada.
- **Cobertura:** 1995-01 a 2026-10, **382 meses**, sem lacuna. A fonte tem 885 leituras desde
  fev/1953 e, antes de jul/1994, atravessa cruzeiro, cruzado, cruzado novo, cruzeiro e cruzeiro
  real, com saltos de unidade entre jul/1993 e ago/1993 e entre jun/1994 e jul/1994. Publicar
  antes de 1995 misturaria moedas e regimes cambiais; o recorte começa em jan/1995, a mesma
  janela de IPCA e IGP-M.
- **Conferência:** primeiro `1995-01 = 0,8471`; último `2026-10 = 5,1294`; máximo nominal
  `2024-12 = 6,0970`; mínimo `1995-02 = 0,8408`. A média mensal difere do fechamento: em
  jan/1999, o fechamento (1,9832) fica 32% acima da média (1,5019); em out/2026, a média é
  5,1294 e o fechamento, 5,4212. Não é o dólar à vista.
- **Verificação independente:** a FAESP/SENAR-SP (Radar Macroeconômico nº 32, out/2026,
  `https://faespsenar.com.br/wp-content/uploads/2026/10/2026.10-Radar-Macroeconomico.pdf`)
  publica R$ 5,14 em setembro e R$ 5,15 em agosto; a série dá 5,1447 e 5,1532. O ValorFinal e o
  MeusRepresentantes publicam a média de outubro em R$ 5,13 e citam a SGS 3698. O Apurômetro
  publica 5,09 porque mediu outubro até 27/10 (mês aberto), não o mês fechado. Não há segunda
  medição: as publicações citam o BCB.
- **Limitações:** é nominal; a alta da série mistura inflação brasileira e não mede
  competitividade. O câmbio real efetivo é outro indicador (índice, com deflatores e cestas de
  parceiros) e não é obtido dividindo esta série pelo IPCA. A PTAX é a referência do mercado
  interbancário; não é dólar paralelo nem turismo.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
