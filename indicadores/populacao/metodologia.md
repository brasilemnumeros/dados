# Metodologia — População

## populacao-total-anual

- **Definição:** população residente total do Brasil, em habitantes, estimada para 1º de julho de
  cada ano. `numero` (`hab.`, 0 casas), `eixo: contagem`, `medida: estoque`, `anual`.
- **Fonte e código:** IBGE, Projeções da População — Revisão 2024, tabela 4 (Indicadores
  Implícitos), variável `POP_T`:
  `https://ftp.ibge.gov.br/Projecao_da_Populacao/Projecao_da_Populacao_2024/projecoes_2024_tab4_indicadores.xlsx`.
  Conferência na SIDRA 6579 (variável 9324), que republica as estimativas anuais: 2024–2026
  coincidem dígito a dígito. Se o endpoint de metadados do SIDRA
  (`servicodados.ibge.gov.br/api/v3/agregados/6579/periodos`) não responder de dentro do GitHub
  Actions, o notebook confere apenas o último ano, com aviso; os valores continuam vindo da
  planilha de projeção.
- **Fórmula:** nenhuma. A série lê `POP_T` — população conciliada a 1º de julho da revisão
  vigente. Não é usada a `DEPIS_POP` do IPEADATA, construída por interpolação spline entre
  Censos e Contagens: ela produz uma queda artificial de população em 2020–2022, que não é
  demografia. A SIDRA 6579 como série contínua também é descartada: 2001–2021 misturam safras
  de anos diferentes (degrau de 2013: 193,9 → 201,0 milhões num ano) e faltam 2007, 2010, 2022 e
  2023.
- **Cobertura:** 2000–2026, **27 pontos**. A revisão não tem série conciliada antes de 2000, por
  isso o começo é 2000. O fim é a última estimativa anual publicada no DOU (SIDRA 6579,
  divulgação de agosto); os anos seguintes da planilha (até 2070) são projeção, não estimativa
  publicada, e ficam fora. A defasagem é de agosto: a série é atualizada na execução seguinte.
- **Conferência:** 2000 = 174.695.935; 2010 = 194.749.329; 2020 = 209.164.889; 2022 =
  210.862.983; 2024 = 212.583.750; 2026 = 214.211.951. O Censo 2022 (203.080.756 em 1º/8) não é
  revisado; a revisão 2024 trabalha com população **conciliada** (210.862.983 em 1º/7, ajuste
  PPE), aplicada retroativamente a 2000 (+3,0%) e 2010 (+2,2%) — por isso não há degrau em 2022.
- **Verificação independente:** o G1 de 28/08/2026
  (`https://g1.globo.com/economia/noticia/2026/08/28/brasil-tem-2142-milhoes-de-habitantes-diz-ibge.ghtml`)
  publica 214.211.951 habitantes em 1º/7/2026, alta de 0,37% sobre 2025; o Jornal de Brasília /
  Folhapress de 22/08/2024
  (`https://jornaldebrasilia.com.br/noticias/brasil/ibge-estima-populacao-de-2109-milhoes-no-brasil-39-maior-que-a-apontada-no-censo-2022`)
  publica 210.862.983 para 2022 e o ajuste de +3,9% sobre o Censo. Os pontos de 2022, 2024 e
  2026 batem. As publicações citam o IBGE; **não há segunda medição** para os anos
  intermediários (2001–2023), cuja conferência é a própria planilha do produtor. Busca feita em
  05/11/2026.
- **Limitações:** é projeção, não contagem censitária; a data publicada é `AAAA-01-01` (início do
  ano, como C9 manda) e o valor é de 1º de julho; a revisão do IBGE reescreve o histórico.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.

## populacao-variacao-anual

- **Definição:** variação percentual da população residente total contra o ano anterior (1º de
  julho contra 1º de julho). `percentual` (`%`, 2 casas), `eixo: percentual`,
  `medida: variacao-anual`, `anual`.
- **Fonte e código:** IBGE, Revisão 2024, tabela 4, variável `TCG_T` (taxa de crescimento
  geométrico anual) — o IBGE publica a variação pronta.
- **Fórmula:** nenhuma. `TCG_T` é exatamente `(P_t/P_{t−1} − 1) × 100`; a identidade é conferida
  nos 26 pontos, com resíduo máximo de 4,2×10⁻¹⁵ p.p. O primeiro ponto é 2001, porque 2000 é
  denominador.
- **Cobertura:** 2001–2026, **26 pontos**, todos positivos. Herda a regra de corte da população
  total: termina na última estimativa publicada no DOU (SIDRA 6579, divulgação de agosto); os
  anos seguintes da projeção ficam fora.
- **Conferência:** 2001 1,3210; 2010 0,8155; 2020 0,6084; 2022 0,3614; 2024 0,4198; 2026
  0,3706.
- **Verificação independente:** a Agência Brasil de 28/08/2026
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-08/crescimento-populacional-caiu-para-037-em-2026-estima-ibge`)
  publica 214,2 milhões em 1º/7/2026, +0,37% no ano e +0,39% em 2024/2025; a InfoMoney/Estadão
  Conteúdo da mesma data
  (`https://www.infomoney.com.br/brasil/ibge-populacao-brasileira-cresce-037-e-chega-a-2142-milhoes-em-2026/`)
  repete os três números. Os pontos `2026` (0,3706) e `2025` (0,3939) batem no arredondamento.
  As publicações citam o IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** deriva da mesma projeção da população total e herda a conciliação da Revisão
  2024; não é a taxa de crescimento entre Censos.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
