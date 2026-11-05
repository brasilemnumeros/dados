# Metodologia — PIB

## pib-real-anual

- **Definição:** variação percentual do PIB real (volume) do ano civil contra o anterior, a
  preços de mercado, série encadeada. `percentual` (`%`, 2 casas), `eixo: percentual`,
  `medida: variacao-anual`, granularidade `anual`, data no início do ano.
- **Fonte e código:** IBGE, Contas Nacionais, lida na SGS **7326** (2 casas). Conferência no
  SIDRA v3: tabela 5932 (taxa acumulada no ano, 4º tri) e índice de volume da 1620.
- **Fórmula:** nenhuma. A taxa é definida pelo IBGE; o notebook busca, recorta anos fechados,
  formata e confere cada ponto contra duas publicações do IBGE. A tabela 6784 não é usada: em
  2018 e 2019 traz 1,7 e 1,3 contra 1,8 e 1,2 das tabelas de nível (inconsistência interna do
  IBGE; a soma dos dois anos é a mesma), enquanto a 7326 mantém 2 casas e a série completa.
- **Cobertura:** desde 1995 até o último ano fechado — **31 pontos na edição atual**. O corte em
  1995 é editorial: a SGS vai a 1963, mas
  antes de 1995 os números vêm da base de volume anterior. 1995 é o único ponto sem conferência
  possível, porque o IBGE só publica taxa a partir de 1996.
- **Conferência:** a 7326 fica a menos de 0,01 p.p. (máximo 0,006) da taxa recomposta do índice
  1620 em 29 de 29 anos e a ≤0,05 p.p. da 5932 em 30 de 30. Choques: 2003 1,14; 2009 −0,13;
  2015 −3,55;
  2016 −3,28; 2020 −3,28; 2021 4,76; 2024 3,42; 2025 2,29.
- **Verificação independente:** o G1 de 03/03/2026
  (`https://g1.globo.com/economia/noticia/2026/03/03/pib-do-brasil-cresce-23percent-em-2025-diz-ibge.ghtml`)
  e a Agência Brasil da mesma data
  (`https://agenciabrasil.ebc.com.br/educacao/noticia/2026-03/economia-brasileira-cresce-23-em-2025-revela-ibge`)
  publicam 2,3% para 2025; a Folha de 07/03/2025
  (`https://www1.folha.uol.com.br/mercado/2025/03/pib-fecha-2024-com-alta-de-34-no-brasil.shtml`)
  publica 3,4% para 2024. As três citam o IBGE; **não há segunda medição**. Busca feita em
  05/11/2026.
- **Limitações:** é a variação real do volume, não o nível do PIB nem o PIB per capita; anos
  sujeitos a revisão das Contas Nacionais.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pib-per-capita-nominal

- **Definição:** PIB por habitante a preços correntes, em reais do próprio ano, ano civil.
  `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`.
- **Fonte e código:** IBGE. 1996–2023: Contas Nacionais Anuais, tabela SIDRA **6784**,
  variável **9812** (“PIB per capita - valores correntes”), Brasil (N1), endpoint
  `https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/all/p/all?formato=json`; 2024–2025:
  caderno das Contas Nacionais Trimestrais, 4º trimestre
  (`https://ftp.ibge.gov.br/Contas_Nacionais/Contas_Nacionais_Trimestrais/Fasciculo_Indicadores_IBGE/{ano}/pib-vol-val_{ano}04caderno.pdf`),
  que publica o nível corrente do PIB per capita no fechamento anual. O notebook lê a 6784
  inteira (variáveis 9811, 9812, 9813 e 9814) e extrai 2024–2025 do PDF. A série **não tem
  `urlFonte` único** — nenhuma das duas publicações cobre o período inteiro —, por isso o campo
  é omitido e as duas URLs ficam aqui.
- **Fórmula:** nenhuma — o IBGE publica o nível. A emenda 2023/2024 é declarada: a 6784 para em
  2023 e o caderno trimestral publica 2024 = R$ 55.247,45 e 2025 = R$ 59.687,49.
- **Cobertura:** 1996–2025, **30 pontos**. 2024–2025 vêm do fechamento anual das Contas
  Trimestrais porque a tabela anual 6784 ainda não os publicou. A tabela anual tem defasagem de
  ~2 anos; o caderno trimestral fecha o ano seguinte e é a fonte dos pontos novos.
- **Conferência:** 1996 R$ 5.219,36; 2023 R$ 51.693,92; 2024 R$ 55.247,45; 2025 R$ 59.687,49;
  mínimo R$ 5.219,36 (1996); crescimento nominal de **1.043,6%** no período 1996–2025 (890,4%
  no recorte 1996–2023).
- **Verificação independente:** a Carta Capital de 06/11/2025 cita “PIB per capita de 2023 foi
  equivalente a 51.693,92 reais”
  (`https://www.cartacapital.com.br/economia/ibge-confirma-crescimento-de-32-da-economia-em-2023/`);
  o DComércio cita o mesmo valor
  (`https://dcomercio.com.br/publicacao/s/pib-cresce-3-2-em-2023-e-soma-r-10-9-tri-mostram-dados-definitivos-do-ibge`);
  o Valor de 07/03/2025 publica R$ 55.247,45 para 2024
  (`https://valor.globo.com/brasil/noticia/2025/03/07/pib-per-capita-de-2024-foi-recorde-diz-ibge.ghtml`);
  a Agência Brasil de 03/03/2026
  (`https://agenciabrasil.ebc.com.br/educacao/noticia/2026-03/economia-brasileira-cresce-23-em-2025-revela-ibge`)
  publica R$ 59.687 (arredondado) e 1,9% para 2025, e o valor exato de R$ 59.687,49 está no
  caderno do IBGE
  (`https://agenciadenoticias.ibge.gov.br/agencia-noticias/2012-agencia-de-noticias/noticias/45969-pib-cresce-2-3-em-2025`).
  Todas citam o IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** é nominal — o crescimento ao longo do tempo mistura inflação e não mede poder
  de compra; é anual; a tabela 6784 para em 2023 e 2024–2025 são lidos do fechamento anual das
  Contas Trimestrais. O valor é arredondado a 2 casas, a mesma precisão da fonte.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar. O nível de 2024–2025 é a primeira
  estimativa anual do caderno do 4º tri; uma revisão entra quando a 6784 publicar o ano.

## pib-per-capita-real

- **Definição:** PIB por habitante em reais constantes de **2023**, ano civil. `moeda`
  (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`. Série derivada, não publicada pelo IBGE.
- **Fonte e código:** IBGE. 1996–2023: Contas Nacionais Anuais, tabela SIDRA **6784**,
  variáveis **9812** (PIB per capita corrente) e **9814** (PIB per capita — variação em
  volume); 2024–2025: caderno das Contas Nacionais Trimestrais, 4º trimestre, que publica o
  nível corrente e a variação real do ano. Cálculo do site. A série **não tem `urlFonte` único**
  — a 6784 cobre 1996–2023 e o caderno cobre os anos seguintes —, por isso o campo é omitido e
  as duas URLs ficam aqui.
- **Fórmula:** `L_2023 = 9812_2023`; para cada ano anterior,
  `L_t = L_{t+1} / (1 + 9814_{t+1}/100)`; para cada ano posterior,
  `L_{t+1} = L_t × (1 + variação_real_{t+1}/100)`. O ano-base 2023 é fixo e não é rebaseado
  automaticamente, para o histórico não ser reescalado a cada execução.
- **Cobertura:** 1996–2025, **30 pontos**.
- **Conferência:** 1996 R$ 37.261,36; 2023 R$ 51.693,92; 2024 R$ 53.244,74; 2025 R$ 54.256,39;
  crescimento real de **45,6%** no período 1996–2025 (38,7% no recorte 1996–2023) contra
  **1.043,6%** do nominal (890,4% no recorte). O notebook reconstrói 1996–2023 por três rotas
  independentes da mesma tabela — a variação em volume oficial (9814), o deflator implícito
  encadeado (9811) e o PIB per capita a preços do ano anterior encadeado (9813) —; o desvio
  máximo entre elas é de **0,30%** (R$ 140 em 2008), compatível com o arredondamento de 1–2
  casas da fonte. A tolerância do notebook é 0,5%. Para 2024–2025 não há segunda rota: o nível
  corrente e a variação real (3,0% e 1,9%) são lidos do caderno trimestral e encadeados ao
  nível de 2023; a checagem do notebook é só de consistência do encadeamento.
- **Verificação independente:** não há publicação de terceiro com esta série em reais de 2023 —
  a busca encontrou apenas o nível nominal e séries internacionais de PIB per capita em US$
  (Banco Mundial/FMI), que usam outra moeda, outra base e, às vezes, PPP. A **variação** de
  +38,7% no recorte 1996–2023 é corroborada pela Fundação Perseu Abramo, *29 anos de economia
  brasileira 1995/2023* (nov/2025, p. 70,
  `https://fpabramo.org.br/editora/wp-content/uploads/sites/17/2025/11/29-anos-anos-de-economia-brasileira-1995-2023.pdf`):
  o índice do PIB a preços de 2010 (1994=100) vai de 106,53 em 1996 a 190,96 em 2023 (1,7925×),
  e dividido pelo crescimento populacional da 6784 dá 1,3867 → +38,7%. Não há segunda medição
  nem nível de terceiro em R$ de 2023. A conferência interna é contra as três variáveis
  oficiais da 6784. Busca feita em 05/11/2026.
- **Limitações:** é uma série **derivada** (o número em R$ de 2023 não é o que o IBGE divulga);
  o ano-base é escolha de apresentação; 2024–2025 usam a variação real do caderno trimestral,
  não a variável 9814 (que ainda para em 2023); o nível é o per capita oficial da 6784, com o
  denominador da projeção do IBGE (211,70 milhões em 2023), não o do Censo 2022 (203,08
  milhões) — por isso pode diferir de publicações de contas regionais. O deflator citado como
  7,12× é a cadeia da 9811; a razão entre as duas séries publicadas dá ≈7,1×. O valor é
  arredondado a 2 casas, a mesma precisão da fonte. Não deve ser comparada numericamente com PIB
  per capita em US$ de organismos internacionais. A próxima edição das Contas Nacionais vem na
  base 2021 e reescreve a série inteira.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar. O nível de 2024–2025 é a primeira
  estimativa anual do caderno do 4º tri; uma revisão entra quando a 6784 publicar o ano.
