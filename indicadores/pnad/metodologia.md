# Metodologia — PNAD Contínua

As taxas gravam 1 casa e os valores em reais gravam 0 casas, a precisão da fonte; `unidade.casas`
é só exibição.

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
  `14,9%`, empatado em jul–ago–set/2020 e jan–fev–mar/2021; mínimo `5,1%` (out–dez/2025).
  Contra o mesmo trimestre do ano anterior, `5,6% → 5,2%` em set/2026.
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
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso sujeito aos termos de uso do IBGE.

## pnad-participacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam na força de trabalho
  (ocupadas ou desocupadas) no trimestre móvel encerrado no mês. `percentual` (`%`, 1 casa),
  `eixo: percentual`, `medida: nivel`, `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **5944**, variável **4096**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/5944/n1/all/v/4096/p/all?formato=json`. O trimestre
  móvel é divulgado cerca de um mês após o encerramento; a pesquisa é republicada por inteiro a
  cada divulgação, e a reponderação de 31/07/2025 reexpressou as estimativas na nova base
  populacional.
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
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso sujeito aos termos de uso do IBGE.

## pnad-nivel-ocupacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam ocupadas no trimestre
  móvel encerrado no mês. `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`,
  `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6379**, variável **4097**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6379/n1/all/v/4097/p/all?formato=json`.
- **Fórmula:** nenhuma — série oficial. Cobertura e recorte iguais aos da desocupação.
- **Cobertura:** 2012-03 a 2026-09, **175 pontos**, sem lacuna. O trimestre móvel é divulgado
  cerca de um mês após o encerramento; a série publicada está sempre ~1 mês atrás do calendário.
- **Conferência:** primeiro `57,3%`; último `59,0%`; mínimo `48,4%` (jun–ago/2020); máximo
  `59,0%` (set–out–nov/2025 e jul–ago–set/2026). É o produto da participação pela fração de
  ocupados na força de trabalho; a identidade usa a mesma tolerância de 0,15 p.p.; o resíduo
  máximo medido é 0,1125 p.p. em 2019-02.
- **Verificação independente:** o Dadobruto (out/2026,
  `https://dadobruto.com/analises/mercado-de-trabalho`) cita `59,0%` em nov/2025 e `58,9%` em
  jun–ago/2026, iguais aos pontos `2025-11` e `2026-08`; o informativo da SPE/Fazenda de
  out/2026 traz o mesmo 59,0%. A divulgação do IBGE de 30/10/2026 também traz `59,0%`
  (`https://biblioteca.ibge.gov.br/visualizacao/periodicos/3086/pnacm_2026_set.pdf`), mas é o
  produtor e não conta como publicação externa. As publicações citam o IBGE; **não há segunda
  medição**. Busca feita em 05/11/2026.
- **Limitações:** não substitui a leitura das três séries do mercado de trabalho, porque cada uma
  isola uma margem diferente; herda o recorte de 14 anos ou mais, Brasil, sem ajuste sazonal e a
  reponderação de 31/07/2025.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso
  sujeito aos termos de uso do IBGE.

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
  abaixo do pico de 2026-03; o piso é out–nov–dez/2021, no auge da perda de poder de compra,
  não o pico da pandemia.
- **Verificação independente:** a Folha de S.Paulo de 30/10/2026 cita “renda média do trabalho em
  R$ 3.790 por mês no trimestre até setembro”
  (`https://www1.folha.uol.com.br/mercado/2026/10/desemprego-fica-em-52-e-tem-menor-taxa-ate-setembro-na-serie-historica.shtml`);
  o UOL
  (`https://economia.uol.com.br/noticias/estadao-conteudo/2026/10/30/taxa-de-desemprego-no-brasil-cai-para-52-no-trimestre-ate-setembro-mostra-ibge.htm`)
  e o G1/O Globo
  (`https://g1.globo.com/jornal-nacional/noticia/2026/10/30/terceiro-trimestre-de-2026-tem-o-menor-numero-de-desempregados-para-o-periodo-desde-2012.ghtml`)
  citam o mesmo `R$ 3.790` para jul–ago–set/2026, igual ao ponto `2026-09`. As três citam o
  IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** é rendimento do trabalho das pessoas ocupadas **com rendimento**, não renda
  domiciliar per capita; é habitual, não efetivamente recebido; é média (não mediana) e não tem
  recorte regional nem ajuste sazonal; o trimestre móvel é lido como mês de encerramento. A base
  móvel e a reexpressão a cada divulgação explicam por que o nível de um trimestre muda entre
  edições; a reponderação de 31/07/2025 também alcança esta série.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso
  sujeito aos termos de uso do IBGE.

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
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso
  sujeito aos termos de uso do IBGE.

## pnad-gini-renda-domiciliar-per-capita

- **Definição:** índice de Gini da distribuição do rendimento domiciliar per capita — soma dos
  rendimentos de todas as fontes dos moradores, dividida pelo número de moradores —, calculado
  sobre os dados acumulados dos quatro trimestres do ano, a preços médios do ano. `numero`
  (`índice`, 3 casas), `eixo: contagem`, `medida: nivel`, `granularidade: anual` (C15:
  `AAAA-01-01`). 0 = igualdade total;
  1 = concentração máxima. É um índice, não percentual nem fração da renda.
- **Fonte e código:** IBGE, PNAD Contínua — Rendimento de todas as fontes, SIDRA **7435**,
  variável **10681**, Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/7435/n1/all/v/10681/p/all?formato=json`. A cada
  divulgação a pesquisa é reexpressa a preços médios do último ano; a edição corrente (dados de
  2025, divulgada em 08/05/2026) usa a base populacional do Censo 2022 e reexpressa os anos
  anteriores. Revisões da fonte podem mudar o nível entre edições, então a comparação válida é
  dentro da edição corrente.
- **Fórmula:** nenhuma — o IBGE publica o índice. O notebook busca, recorta o Brasil, descarta o
  ano corrente (incompleto) e grava. Não há emenda com a PNAD antiga: a pesquisa anterior tem
  questionário, período de referência e cobertura diferentes, e converter seus níveis para a
  escala da PNAD Contínua exigiria um fator de calibração — uma escolha nossa, não da fonte —
  que fabricaria comparabilidade. A série começa em 2012.
- **Cobertura:** 2012–2025, **14 pontos**, sem lacuna. A diretriz de cobrir desde 1995 foi
  verificada: a PNAD antiga é a fonte predecessora, mas não é compatível em nível com a PNAD
  Contínua; a sobreposição 2012–2015 não foi usada para calibrar a série. Busca pela fonte
  predecessora feita em 06/11/2026.
- **Conferência:** primeiro `0,540` (2012); último `0,511` (2025); mínimo `0,504` (2024);
  máximo `0,545` (2018); 2025 é o segundo menor da série, 1,4% acima de 2024. A trajetória
  recente é 0,543 (2019), 0,523 (2020), 0,543 (2021), 0,517 (2022), 0,517 (2023), 0,504 (2024).
- **Verificação independente:** a Folha de S.Paulo de 08/05/2026
  (`https://www1.folha.uol.com.br/mercado/2026/05/desigualdade-sobe-em-2025-mas-e-a-2a-menor-da-serie-no-brasil-renda-cresce-mais-para-ricos.shtml`)
  publica `0,511` em 2025 e `0,504` em 2024, aponta `0,545` como o máximo de 2018 e diz que a
  série começa em 2012; o Jornal da UFG
  (`https://jornal.ufg.br/n/200968-crescimento-da-renda-expansao-do-emprego-e-aumento-da-desigualdade`)
  repete `0,504 → 0,511`. O Ipeadata reproduz a mesma série (`0,540` a `0,511`), mas é agregador
  da PNAD; **não há segunda medição**. A divulgação do IBGE de 08/05/2026
  (`https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/46579-rendimento-medio-da-populacao-brasileira-atinge-r-3-367-em-2025`)
  traz os mesmos valores, mas é o produtor e não conta como publicação externa. Busca feita em
  06/11/2026.
- **Limitações:** mede a desigualdade da distribuição, não o nível de renda, e não diz onde na
  distribuição a mudança ocorreu; a captação dos rendimentos do topo é limitada (juros,
  dividendos e ganhos de capital), o que pode subestimar a concentração; é renda domiciliar per
  capita, não individual; é o acumulado de quatro trimestres, não um mês isolado; é Brasil, sem
  recorte regional; não é compatível com a PNAD antiga nem com o Gini do Banco Mundial ou do
  Ipea sem conferir o conceito de renda; a reponderação na base do Censo 2022 e as visitas da
  pandemia afetam a comparabilidade ao longo da série.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** Dados abertos do IBGE (PNAD Contínua); atribuição ao IBGE. Uso
  sujeito aos termos de uso do IBGE.
