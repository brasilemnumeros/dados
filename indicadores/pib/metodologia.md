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
- **Cobertura:** 1995–2025, **31 pontos**. O corte em 1995 é editorial: a SGS vai a 1963, mas
  antes de 1995 os números vêm da base de volume anterior. 1995 é o único ponto sem conferência
  possível, porque o IBGE só publica taxa a partir de 1996.
- **Conferência:** a 7326 é idêntica ao centésimo à taxa recomposta do índice 1620 em 29 de 29
  anos e fica a ≤0,05 p.p. da 5932 em 30 de 30. Choques: 2003 1,14; 2009 −0,13; 2015 −3,55;
  2016 −3,28; 2020 −3,28; 2021 4,76; 2024 3,42; 2025 2,29.
- **Limitações:** é a variação real do volume, não o nível do PIB nem o PIB per capita; anos
  sujeitos a revisão das Contas Nacionais.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## pib-per-capita-nominal

- **Definição:** PIB por habitante a preços correntes, em reais do próprio ano, ano civil.
  `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`.
- **Fonte e código:** IBGE, Contas Nacionais Anuais, tabela SIDRA **6784**, variável **9812**
  (“PIB per capita - valores correntes”), Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/all/p/all?formato=json` — o notebook lê
  a tabela inteira e usa as variáveis 9811, 9812, 9813 e 9814.
- **Fórmula:** nenhuma — o IBGE publica o nível.
- **Cobertura:** 1996–2023, **28 pontos**, os anos fechados das Contas Nacionais Anuais.
- **Conferência:** 1996 R$ 5.219,36; 2023 R$ 51.693,92 (máximo); mínimo R$ 5.219,36 (1996);
  crescimento nominal de **890,4%** no período.
- **Verificação independente:** a Carta Capital de 06/11/2025 cita “PIB per capita de 2023 foi
  equivalente a 51.693,92 reais”
  (`https://www.cartacapital.com.br/economia/ibge-confirma-crescimento-de-32-da-economia-em-2023/`);
  o DComércio cita o mesmo valor
  (`https://dcomercio.com.br/publicacao/s/pib-cresce-3-2-em-2023-e-soma-r-10-9-tri-mostram-dados-definitivos-do-ibge`).
  As duas citam o IBGE; não há segunda medição.
- **Limitações:** é nominal — o crescimento ao longo do tempo mistura inflação e não mede poder
  de compra; é anual; para 2024 e 2025 não há nível per capita publicado.

## pib-per-capita-real

- **Definição:** PIB por habitante em reais constantes de **2023**, ano civil. `moeda`
  (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`. Série derivada, não publicada pelo IBGE.
- **Fonte e código:** IBGE, Contas Nacionais Anuais, tabela SIDRA **6784**, variáveis **9812**
  (PIB per capita corrente) e **9814** (PIB per capita — variação em volume); cálculo do site.
  Endpoint: o mesmo da tabela 6784.
- **Fórmula:** `L_2023 = 9812_2023`; para cada ano anterior,
  `L_t = L_{t+1} / (1 + 9814_{t+1}/100)`. O ano-base 2023 é o último ano fechado; a base é
  fixa e não é rebaseada automaticamente, para o histórico não ser reescalado a cada execução.
- **Cobertura:** 1996–2023, **28 pontos**.
- **Conferência:** 1996 R$ 37.261,36; 2023 R$ 51.693,92; crescimento real de **38,7%** contra
  **890,4%** do nominal; o deflator implícito do PIB acumulou **7,12×** no período. O notebook
  reconstrói a série por três rotas independentes da mesma tabela — a variação em volume oficial
  (9814), o deflator implícito encadeado (9811) e o PIB per capita a preços do ano anterior
  encadeado (9813) —; o desvio máximo entre elas é de **0,30%** (R$ 140 em 2008), compatível
  com o arredondamento de 1–2 casas da fonte. A tolerância do notebook é 0,5%.
- **Verificação independente:** não há publicação de terceiro com esta série em reais de 2023 —
  a busca encontrou apenas o nível nominal e séries internacionais de PIB per capita em US$
  (Banco Mundial/FMI), que usam outra moeda, outra base e, às vezes, PPP. A conferência é
  interna, contra as três variáveis oficiais da 6784.
- **Limitações:** é uma série **derivada** (o número em R$ de 2023 não é o que o IBGE divulga);
  o ano-base é escolha de apresentação; a cobertura para em 2023; não deve ser comparada
  numericamente com PIB per capita em US$ de organismos internacionais.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
