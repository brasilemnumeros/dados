# Metodologia — PNAD Contínua

## pnad-desocupacao

- **Definição:** percentual das pessoas de 14 anos ou mais **na força de trabalho** que estavam
  desocupadas no trimestre móvel de três meses encerrado no mês da data. `percentual` (`%`,
  1 casa), `eixo: percentual`, `medida: nivel`, `granularidade: mensal`. O ponto `2026-09-01`
  cobre jul–ago–set/2026; não é a taxa do mês de setembro isolado.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6381**, variável **4099**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6381/n1/all/v/4099/p/all?formato=json`. O IBGE
  divulga o trimestre móvel cerca de um mês após o encerramento (o de jul–set saiu em
  30/10/2026); a série publicada fica sempre ~1 mês atrás do calendário. A pesquisa é
  republicada por inteiro a cada divulgação, e a reponderação de 31/07/2025 reexpressou as
  estimativas na nova base populacional — revisão da fonte entra no ciclo seguinte.
- **Fórmula:** nenhuma — a taxa é publicada pelo IBGE. O notebook busca, recorta o último
  trimestre fechado e formata. Não há emenda com a PME (2002–2012): a PME tinha outra
  metodologia e cobria só 6 regiões metropolitanas.
- **Cobertura:** 2012-03 a 2026-09, **175 trimestres móveis**, sem lacuna. 2012-03 é o primeiro
  trimestre móvel da PNAD Contínua mensal.
- **Conferência:** primeiro `8,0%` (jan–fev–mar/2012); último `5,2%` (jul–ago–set/2026); máximo
  `14,9%` (jul–ago–set/2020); mínimo `5,1%` (out–dez/2025). Contra o mesmo trimestre do ano
  anterior, `5,6% → 5,2%` em set/2026.
- **Verificação independente:** o Estadão de 30/10/2026
  (`https://www.estadao.com.br/economia/ibge-pnad-desemprego-setembro-2026/`) publica 5,2%
  para jul–set/2026, 5,4% para abr–jun e 5,6% para jul–set/2025; a Folha
  (`https://www1.folha.uol.com.br/mercado/2026/10/desemprego-fica-em-52-e-tem-menor-taxa-ate-setembro-na-serie-historica.shtml`)
  e O Globo
  (`https://oglobo.globo.com/economia/noticia/2026/10/30/desemprego-cai-para-52percent-e-chega-ao-menor-nivel-ja-registrado-em-setembro.ghtml`)
  repetem 5,2%; o informativo da SPE/Fazenda
  (`https://www.gov.br/fazenda/pt-br/central-de-conteudo/publicacoes/conjuntura-economica/emprego-e-renda/2026/informativo-pnad-set2026.html`)
  também. As publicações citam o IBGE; **não há segunda medição**. A divulgação do próprio IBGE
  de 30/10/2026 traz 5,2% para jul–set/2026
  (`https://biblioteca.ibge.gov.br/visualizacao/periodicos/3086/pnacm_2026_set.pdf`), mas é o
  produtor e não conta como publicação externa. Busca feita em 05/11/2026.
- **Limitações:** o trimestre móvel é lido como mês de encerramento; não deve ser comparado com a
  PME nem com os anos 1990; não é o estoque do Caged. A taxa pode cair por saída da força de
  trabalho — a leitura conjunta com a participação é obrigatória. Refere-se a pessoas de 14 anos
  ou mais, no Brasil, sem recorte regional nem ajuste sazonal. A reponderação de 31/07/2025
  reexpressou a série na nova base populacional; os pontos anteriores a jul/2025 não são
  diretamente comparáveis com publicações da base antiga.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pnad-participacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam na força de trabalho
  (ocupadas ou desocupadas) no trimestre móvel encerrado no mês. `percentual` (`%`, 1 casa),
  `eixo: percentual`, `medida: nivel`, `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **5944**, variável **4096**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/5944/n1/all/v/4096/p/all?formato=json`.
- **Fórmula:** nenhuma — série oficial. Cobertura e recorte iguais aos da desocupação.
- **Cobertura:** 2012-03 a 2026-09, **175 pontos**, sem lacuna.
- **Conferência:** primeiro `62,3%`; último `62,2%`; máximo `63,6%` (abr–jun/2019); mínimo
  `56,5%` (mai–jul/2020). A identidade
  `nível de ocupação = participação × (1 − desocupação/100)` é conferida ponto a ponto no
  notebook, com tolerância de 0,15 p.p. (resíduo máximo medido: 0,1125 p.p. em 2019-02, efeito do
  arredondamento de 1 casa).
- **Verificação independente:** o Dadobruto (17/10/2026,
  `https://dadobruto.com/analises/mercado-de-trabalho`) traz 62,2% para jun–ago/2026 (ponto
  `2026-08`) e a série da tabela bate em 62,3% (mar/2012), 62,4% (dez/2013), 63,4% (dez/2019),
  56,8% (ago/2020) e 62,3% (ago/2025). A divulgação do IBGE de 30/10/2026 traz 62,2% para
  jul–set/2026, mas é o produtor e não conta como publicação externa. As publicações citam o
  IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** é o denominador que explica por que a taxa de desocupação pode cair sem
  aumento de emprego; herda o recorte de 14 anos ou mais, Brasil, sem ajuste sazonal e a
  reponderação de 31/07/2025.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pnad-nivel-ocupacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam ocupadas no trimestre
  móvel encerrado no mês. `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`,
  `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6379**, variável **4097**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6379/n1/all/v/4097/p/all?formato=json`.
- **Fórmula:** nenhuma — série oficial. Cobertura e recorte iguais aos da desocupação.
- **Cobertura:** 2012-03 a 2026-09, **175 pontos**, sem lacuna.
- **Conferência:** primeiro `57,3%`; último `59,0%`; mínimo `48,4%` (jun–ago/2020); máximo
  `59,0%` (set–out–nov/2025 e jul–ago–set/2026). É o produto da participação pela fração de
  ocupados na força de trabalho; a identidade usa a mesma tolerância de 0,15 p.p.
- **Verificação independente:** o Dadobruto (out/2026,
  `https://dadobruto.com/analises/mercado-de-trabalho`) cita `59,0%` em nov/2025 e `58,9%` em
  jun–ago/2026, iguais aos pontos `2025-11` e `2026-08`; o informativo da SPE/Fazenda de
  out/2026 traz o mesmo 59,0%. A divulgação do IBGE de 30/10/2026 também traz `59,0%`, mas é o
  produtor e não conta como publicação externa. As publicações citam o IBGE; **não há segunda
  medição**. Busca feita em 05/11/2026.
- **Limitações:** não substitui a leitura das três séries do mercado de trabalho, porque cada uma
  isola uma margem diferente; herda o recorte de 14 anos ou mais, Brasil, sem ajuste sazonal e a
  reponderação de 31/07/2025.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pnad-rendimento-real

- **Definição:** rendimento médio mensal real das pessoas de 14 anos ou mais ocupadas na semana
  de referência com rendimento de trabalho, **habitualmente recebido em todos os trabalhos**, no
  trimestre móvel encerrado no mês. `moeda` (`R$`, 0 casas), `eixo: reais`, `medida: nivel`,
  `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6390**, variável **5933**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6390/n1/all/v/5933/p/all?formato=json`.
- **Fórmula:** nenhuma — a série já vem deflacionada pelo IBGE (INPC): o valor está em reais de
  poder de compra, não em reais correntes. Não é a série efetivamente recebida (tabela 6387): a
  habitual é a manchete da divulgação mensal e é a que as publicações externas citam. A base de
  preços acompanha o trimestre mais recente e o IBGE **reexpressa a série inteira a cada
  divulgação**: o nível muda, a variação interanual não. Por isso os níveis absolutos não são
  comparáveis entre edições (o mesmo trimestre teve R$ 3.762 numa publicação de agosto e
  R$ 3.767 hoje).
- **Cobertura:** 2012-03 a 2026-09, **175 pontos**, sem lacuna. O trimestre móvel é divulgado
  cerca de um mês após o encerramento; a série publicada está sempre ~1 mês atrás do calendário.
- **Conferência:** primeiro `3.179`; último `3.790`; mínimo `3.074` (out–nov–dez/2021); máximo
  `3.811` (jan–fev–mar/2026), leitura da edição de 30/10/2026. No último trimestre, `3.790` está
  abaixo do pico de 2026-03, e o piso da série é a pandemia.
- **Verificação independente:** a Folha de S.Paulo de 30/10/2026 cita “renda média do trabalho em
  R$ 3.790 por mês no trimestre até setembro”
  (`https://www1.folha.uol.com.br/mercado/2026/10/desemprego-fica-em-52-e-tem-menor-taxa-ate-setembro-na-serie-historica.shtml`);
  o UOL
  (`https://economia.uol.com.br/noticias/estadao-conteudo/2026/10/30/taxa-de-desemprego-no-brasil-cai-para-52-no-trimestre-ate-setembro-mostra-ibge.htm`)
  e O Globo citam o mesmo `R$ 3.790` para jul–ago–set/2026, igual ao ponto `2026-09`. As três
  citam o IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** é rendimento do trabalho das pessoas ocupadas **com rendimento**, não renda
  domiciliar per capita; é habitual, não efetivamente recebido; é média (não mediana) e não tem
  recorte regional nem ajuste sazonal; o trimestre móvel é lido como mês de encerramento. A base
  móvel e a reexpressão a cada divulgação explicam por que o nível de um trimestre muda entre
  edições; a reponderação de 31/07/2025 também alcança esta série.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pnad-renda-domiciliar-per-capita-real

- **Definição:** média, por morador, do rendimento mensal do domicílio — rendimento habitual do
  trabalho das pessoas de 14 anos ou mais mais as outras fontes —, média dos quatro trimestres do
  ano, em reais constantes. `moeda` (`R$`, 0 casas), `eixo: reais`, `medida: nivel`,
  `granularidade: anual` (C15: `AAAA-01-01`). É a renda de todos os moradores, não o rendimento
  individual de quem trabalha.
- **Fonte e código:** IBGE, PNAD Contínua — Rendimento de todas as fontes, SIDRA **7533**,
  variável **10816**, classificação **1019 = 49243** (`Total`), Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/7533/n1/all/v/10816/p/all/c1019/49243?formato=json`.
  A tabela **7395** (variável 4196) é descartada: apesar do nome parecido, é do módulo TIC,
  começa em 2016, não tem 2020 e dá valores diferentes conforme o ano.
- **Fórmula:** nenhuma — a série é publicada pelo IBGE já **real**, deflacionada pelo IPCA e
  reexpressa a preços médios do último ano. O notebook não deflaciona de novo; o ano-base do
  campo `fonte` sai do último ano da série, nunca fixo no código. A cada divulgação o IBGE
  reexpressa a série inteira na nova base; a `descricao` do catálogo não fixa o ano.
- **Cobertura:** 2012–2025, **14 pontos**, sem lacuna. A PNAD Contínua anual começa em 2012; a
  PNAD antiga (1995–2015) não é emendada, por ter questionário e conceito de renda diferentes.
- **Conferência:** 2012 R$ 1.782; 2025 R$ 2.264 (máximo); mínimo R$ 1.692 (2021); 2020
  R$ 1.820; 2024 R$ 2.118; 2025 cresce 6,9% sobre 2024. O IBGE reexpressou a série inteira em
  2025 (nova base de preços e reponderação).
- **Verificação independente:** o Blog do IBRE/FGV publicou em 15/06/2026 que a renda domiciliar
  per capita de 2025 foi **R$ 2.264**, +6,9%, com a série 2012–2025
  (`https://blogdoibre.fgv.br/posts/renda-cresce-e-pobreza-cai-mas-brasil-segue-marcado-por-desigualdades-regionais`);
  Metrópoles (08/05/2026) e O Informante (08/05/2026) publicam o mesmo nível. O número nominal do
  FPE/TCU divulgado em fevereiro (R$ 2.316 em 2025) é **outro produto**: nominal, universo do
  FPE/TCU (inclui pensionistas e empregados domésticos) e rendimento efetivo; a diferença de 2,3%
  é de conceito. Não há segunda medição: o IBRE/FGV analisa os microdados do IBGE.
- **Limitações:** é renda domiciliar per capita, não rendimento individual; é real (IPCA, base
  móvel), não nominal; a média não é mediana; em 2020–2022 a coleta usou quintas visitas
  (pandemia) e a edição de 2025 trouxe reponderação — quebras de comparabilidade declaradas.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
