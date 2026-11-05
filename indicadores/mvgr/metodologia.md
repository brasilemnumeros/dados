# Metodologia — MVG-R

## mvgr-nominal

- **Definição:** **MVG-R** (Mediana dos Valores de Garantia de Imóveis Residenciais Financiados):
  mediana dos valores de **avaliação** dos imóveis residenciais dados em garantia a
  financiamentos imobiliários de pessoas físicas (alienação fiduciária e hipoteca residencial),
  informados ao SCR — janela móvel de 3 meses, cobertura nacional, operações com valor
  contratado acima de 13,3 salários mínimos mensais. É nível de **valor de garantia** mediano em
  reais, não preço de mercado, índice de preços ou massa agregada. `moeda` (`R$`, 0 casas),
  `eixo: reais`, `medida: nivel`, `mensal`.
- **Fonte e código:** Banco Central do Brasil (SCR), SGS **25419**. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.25419/dados?formato=json`. Definição em
  `https://www.bcb.gov.br/content/estatisticas/mercadoimobiliario_docs/Metodologia.pdf`.
- **Fórmula:** nenhuma. A série é publicada tal como o BCB a divulga e é recalculada inteira a
  cada execução — é a única forma de acompanhar as revisões do SCR.
- **Cobertura:** 2004-03 a 2026-08, **270 pontos**, sem lacuna. 2004-03 é o limite da fonte. O
  BCB divulga com ~90 dias corridos após o mês de referência; por isso a série termina em M−3.
- **Conferência:** 2009-03 R$ 78.500; out/2020 R$ 198.000; 2025-07 R$ 260.000; 2026-08
  R$ 290.000.
- **Verificação independente:** o Poder360 de 01/06/2017 publica mediana de R$ 160 mil no
  1º trimestre de 2017, igual ao ponto de 2017-03; a UOL Economia, reproduzida pelo
  Seconci-Rio em 29/10/2021
  (`https://www.abecip.org.br/imprensa/noticias/na-pandemia-brasileiro-paga-20-a-mais-para-financiar-casa-propria`),
  lista fev/2020 R$ 185 mil, mai/2020 R$ 180 mil, ago/2020 R$ 185 mil, nov/2020 R$ 200 mil,
  fev/2021 R$ 213 mil, mai/2021 R$ 217 mil e ago/2021 R$ 220 mil; os três primeiros e nov/2020
  coincidem, e a divergência cresce até 2,3% em ago/2021 por revisão do SCR. As duas
  publicações citam o BCB; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** o valor é o de avaliação para garantia, não o preço de venda; a composição da
  amostra muda ao longo do tempo, então a série não mede a valorização de um mesmo imóvel nem é
  um índice de preços constante-quality. O piso de 13,3 salários mínimos é baixo e não é um
  corte de alta renda.
- **Revisão:** o SCR revisa a série; reexecutar o notebook segue a revisão. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.

## mvgr-real

- **Definição:** **MVG-R deflacionado pelo IPCA**, em reais constantes de **março de 2004**
  (mês-base = primeiro mês da série). É o nominal dividido pela **média geométrica de 3 meses do
  IPCA** (a mesma janela da mediana móvel); não é um índice de preços nem a valorização de um
  mesmo imóvel. `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `mensal`.
- **Fonte e código:** BCB/SGS 25419 deflacionada pela média geométrica de 3 meses do IPCA, SGS
  **433**. O BCB não publica MVG-R real; o IVG-R (21340) é índice de preços, não valor em reais.
- **Fórmula:** `nominal(t) / ∏(1 + i_avg(s)/100)`, com
  `i_avg(s) = [(1+i_{s-2})(1+i_{s-1})(1+i_s)]^(1/3) − 1`, base fixa em 2004-03. A janela de 3
  meses é a mesma do MVG-R nominal; a média geométrica é a taxa que, composta, reproduz a
  inflação da janela (a média aritmética das taxas daria 85.619,95 no último ponto, contra
  85.662,08 da geométrica). A base fixa evita reescalar o histórico a cada execução. O IGP-M é
  descartado por ser índice de atacado e reajuste contratual, não custo de vida. O cálculo exato
  seria deflacionar cada uma das três observações e tomar a mediana, mas o BCB publica só a
  mediana da janela; a média da janela é a melhor aproximação com o dado disponível.
- **Cobertura:** 2004-03 a 2026-08, **270 pontos**, sem lacuna. O BCB divulga o MVG-R nominal
  com ~90 dias corridos após o mês de referência; a série real herda a defasagem e termina em M−3.
- **Conferência:** a cadeia do 433 reproduz o número-índice do IPCA do IBGE (SIDRA 1737, variável
  2266) com desvio relativo máximo de 2,1×10⁻⁵. A razão `real/nominal` é exatamente
  `1/deflator` em todos os 270 meses. Base 2004-03 = R$ 44.419,00 (deflator 1); 2022-08 =
  R$ 79.890,58; 2026-08 = R$ 85.662,08.
- **Verificação independente:** a ABECIP de 28/10/2021
  (`https://www.abecip.org.br/imprensa/noticias/na-pandemia-brasileiro-paga-20-a-mais-para-financiar-casa-propria`)
  lista sete pontos do MVG-R nominal: fev/2020 R$ 185 mil (igual), mai/2020 R$ 180 mil (igual),
  ago/2020 R$ 185 mil (publicado 186 mil, +0,5%), nov/2020 R$ 200 mil (igual), fev/2021
  R$ 213 mil (215 mil, +0,9%), mai/2021 R$ 217 mil (219.110, +1,0%) e ago/2021 R$ 220 mil
  (225 mil, +2,3%). O gradiente é revisão do SCR, não erro de janela. A publicação confere o
  insumo nominal; **não há segunda medição do MVG-R real**, que é derivação do site. Busca
  feita em 05/11/2026.
- **Limitações:** é um nível deflacionado, não um índice de preços constante-quality nem a
  valorização do mesmo imóvel; a composição da amostra do MVG-R muda. O número em reais de
  mar/2004 não é preço de hoje.
- **Revisão:** reexecutar o notebook não muda valor além da revisão das fontes (SCR e IPCA).
  Mudança de valor é revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
