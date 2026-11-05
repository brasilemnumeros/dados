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
  isso o começo é 2000.
- **Conferência:** 2000 = 174.695.935; 2010 = 194.749.329; 2020 = 209.164.889; 2022 =
  210.862.983; 2024 = 212.583.750; 2026 = 214.211.951. O Censo 2022 (203.080.756 em 1º/8) não é
  revisado; a revisão 2024 trabalha com população **conciliada** (210.862.983 em 1º/7, ajuste
  PPE), aplicada retroativamente a 2000 (+3,0%) e 2010 (+2,2%) — por isso não há degrau em 2022.
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
- **Cobertura:** 2001–2026, **26 pontos**, todos positivos.
- **Conferência:** 2001 1,3210; 2010 0,8155; 2020 0,6084; 2022 0,3614; 2024 0,4198; 2026
  0,3706.
- **Limitações:** deriva da mesma projeção da população total e herda a conciliação da Revisão
  2024; não é a taxa de crescimento entre Censos.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
