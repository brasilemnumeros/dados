# Metodologia dos indicadores

Revisão da definição e da fórmula de cada indicador, conferida contra a fonte
e contra a matemática do próprio indicador — nunca contra o código atual.

> **Escopo:** as 12 séries foram revisadas e publicadas em 2026-11-01. O IPCA foi o piloto
> (`ipca-acum-12m`); o IGP-M veio em seguida; as outras seis famílias fecharam a rodada.

## ipca-acum-12m

- **Definição:** variação percentual do IPCA acumulada nos últimos 12 meses
  (taxa efetiva do período), unidade `percentage` (`%`, 2 casas decimais),
  granularidade `monthly`.
- **Fonte e código:** IBGE, via API de Dados Abertos do Banco Central (SGS),
  série **13522** (IPCA, variação acumulada em 12 meses, %). É a série primária
  e única usada para o dado publicado. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados?formato=json`.
  A série 433 (variação mensal) **não** é usada para gerar a saída.
- **Fórmula atual:** `df['IPCA (%)'].rolling(12).sum()` sobre a série 433 —
  soma aritmética das 12 variações mensais; incorreta porque soma taxas em vez
  de usar a série acumulada oficial.
- **Fórmula proposta:** nenhuma. A série é lida direto da 13522 e publicada tal
  qual o BCB/IBGE a divulga. O notebook só busca, filtra os meses fechados e
  formata — o cálculo fica definido pela fonte, o que é intencional.
- **Evidência:**
  - A 13522 é a série oficial do SGS para “IPCA — variação acumulada em 12
    meses”; publicá-la direto elimina qualquer erro de acumulação local.
  - Conferência numérica (janela jul/2024 a jun/2025): a soma das variações
    mensais da 433 dá **5,23%** (valor publicado hoje), enquanto a 13522
    registra **5,35%** para 2025-06 — a soma diverge do oficial.
  - Mesma conferência em inflação alta: dez/2002 — soma **11,90%** vs. 13522
    **12,53%**; fev/2003 — soma **14,84%** vs. 13522 **15,85%**.
  - A 13522 já tem valores desde antes de 1995 (pré-Plano Real); o pipeline
    coleta desde **1995-01-01**, então a série publicada começa em 1995-01-01.
- **Veredito:** corrigir.
- **Impacto esperado:** os valores passam a ser os da série oficial 13522
  (mudam de `soma` para `oficial` em todos os pontos). O notebook já coletava
  desde 1995-01-01, então a cobertura não mudou — a previsão de "ganhar os 11
  pontos de 1995-01 a 1995-11" não se confirmou: a série já começava em 1995-01,
  com 381 pontos, e continua com 381.
- **Decisão pendente:** não — aprovada e publicada. O notebook foi migrado para o
  contrato `versao`/`unidade`/`dados` em 2026-11-01 (antes ele ainda escrevia o
  envelope antigo), e o arquivo ganhou `urlFonte`.

## igpm-acum-12m

- **Definição:** variação percentual do IGP-M acumulada nos últimos 12 meses (taxa
  efetiva do período), unidade `percentual` (`%`, 2 casas decimais),
  `medida: acumulado-12m`, granularidade `mensal`.
- **Fonte e código:** FGV, via API de Dados Abertos do Banco Central (SGS), série
  **28655** — variação mensal do IGP-M calculada sobre os números-índices da FGV,
  a mesma série que o BCB usa na Calculadora do Cidadão para correção pelo IGP-M
  desde 12/04/2021. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.28655/dados?formato=json`.
  O IGP-M **não tem** série pronta de acumulado em 12 meses no SGS: o catálogo de
  séries do IGP-M (`https://www4.bcb.gov.br/pec/series/port/metadados/mg40Bp.htm`)
  lista apenas 0189 (variação mensal), 7448/7449 (1º e 2º decêndios) e 7450–7458
  (componentes IPA-M, IPC-M, INCC-M). A 0189 (variação mensal publicada, 2 casas) é
  buscada só para conferência; a 28655, de precisão estendida, gera a saída.
- **Fórmula atual:** `df_igpm_combined.rolling(12).sum()` sobre as variações mensais
  da 0189 — soma aritmética das 12 taxas; incorreta porque soma percentuais que
  deveriam ser capitalizados, e subestima o acumulado em todo período com taxas
  relevantes.
- **Fórmula proposta:** composição geométrica das 12 variações mensais,
  `(∏(1 + i/100) − 1) × 100`, sobre a 28655. A fonte do dado mensal não muda (é a
  mesma série da FGV); o que muda é a agregação, de soma para capitalização.
- **Evidência:**
  - Não existe série oficial acumulada em 12 meses para o IGP-M (ver catálogo
    acima), ao contrário do IPCA (SGS 13522). Por isso o acumulado é calculado — mas
    a partir da série mensal oficial, não de taxas somadas.
  - A 28655 é a série de precisão estendida derivada dos números-índices da FGV:
    coincide com a 0189 até a 2ª casa nos 449 meses da história (única diferença,
    jul/1989: 35,9051% contra 35,90%).
  - Conferência contra a tabela de 12 meses publicada pela FGV
    (`https://portal.fgv.br/noticias/igp-m-2025`), 14 meses de nov/2024 a dez/2025:
    a composição da 28655 reproduz **os 14 valores**; a da 0189 reproduz 8. Em
    set/2024 e out/2024, que só consegui conferir em fonte secundária, a composição
    da 28655 fica 0,01 p.p. acima do publicado — o tamanho do arredondamento de 2
    casas.
  - Out/2026: a FGV publica **5,24%** em 12 meses (portal IBRE). A composição da
    28655 dá 5,2369% (arredonda para 5,24%); a da 0189 dá 5,2465% (5,25%).
  - Choque de 2002–2003, soma → composição: dez/2002 **22,92% → 25,31%**
    (+2,39 p.p.); fev/2003 **27,11% → 30,60%** (+3,49 p.p.); jun/2003
    **25,28% → 28,23%** (+2,95 p.p.).
  - Recente: jun/2025 **4,35% → 4,39%**; jul/2025 **2,97% → 2,96%**; dez/2025
    **−1,02% (soma) → −1,05%**, igual ao valor publicado pela FGV.
  - Onde a soma erra mais, no trecho comum: mai/2021 — **32,00% → 37,04%**
    (+5,04 p.p.).
  - No trecho comum (349 pontos), **331 valores mudam** e 18 coincidem ao centésimo
    (meses de inflação baixa); diferença média absoluta de 0,47 p.p.
- **Veredito:** corrigir.
- **Impacto esperado:** a série publicada passa de 349 para **382 pontos**, de
  `1996-07-01`–`2025-07-01` para `1995-01-01`–`2026-10-01`. Ganha 18 pontos antes do
  início atual (1995-01 a 1996-06) e 15 depois do fim atual (2025-08 a 2026-10). A
  fonte tem janela de 12 meses fechada desde `1990-05` (o IGP-M começa em jun/1989);
  o recorte em 1995-01 alinha a série ao `ipca-acum-12m` e deixa de fora a cauda de
  hiperinflação — o primeiro ponto publicado é 603,74% (jan/1995), comparável ao
  631,54% do IPCA no mesmo mês. Último ponto: **5,24%** (out/2026).
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01. O notebook
  reescreve `indicadores/igp-m/igpm-acum-12m.json` inteiro a cada execução, com a
  série de 382 pontos publicada nesta rodada.

## selic-meta

- **Definição:** meta da taxa Selic definida pelo Copom, **ao ano** — o nível em vigor no mês.
  `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: nivel`, `mensal`.
- **Fonte e código:** Banco Central do Brasil, SGS **432** (meta Selic definida pelo Copom,
  % a.a., diária, desde 05/03/1999). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json`, consultado em janelas
  de 5 anos (limite do SGS para série diária).
- **Fórmula atual:** nenhuma. A meta do mês é o valor em vigor (a média das leituras diárias do
  mês só lida com mudança de meta no meio do mês — efeito máximo de ~0,03 p.p.). O mês corrente
  é descartado.
- **Fórmula proposta:** nenhuma. A meta é o que o Copom decide; repetir o nível é reproduzir a
  fonte, não calcular.
- **Evidência:** jul/2016 = 14,25% ao ano (meta constante no período); out/2025 = 15,00%;
  mar/1999 = 44,22% (primeiro mês da fonte, a partir de 05/03). Não existe série oficial de
  "meta acumulada em 12 meses" porque a meta é anualizada — acumulá-la exigiria convertê-la em
  taxa mensal equivalente e recompor, um construto que só coincide com a meta quando ela fica
  parada 12 meses. Em dez/2003 a meta em vigor era **17,05%** e esse construto daria **23,48%**.
- **Veredito:** corrigir (a série publicava um construto acumulado; passa a publicar o nível).
- **Impacto esperado:** 320 → **332 pontos**; `2000-03`–`2026-10` → **`1999-03`–`2026-10`**; os
  valores voltam ao nível (out/2025 = 15,00%, dez/2003 = 17,05%) e o `id` muda de
  `selic-meta-acum-12m` para **`selic-meta`**.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01: a meta é nível; a série
  acumulada é a do over.

## selic-over-acum-12m

- **Definição:** taxa efetiva Selic (over) acumulada nos 12 meses de calendário encerrados no
  mês de referência. Unidade `percentual` (`%`, 2 casas), `eixo: percentual`,
  `medida: acumulado-12m`, `mensal`.
- **Fonte e código:** BCB, SGS **11** (Selic % a.d., diária, desde 1986-06); a SGS 4390 serve de
  conferência.
- **Fórmula atual:** duas em paralelo. A que gerou o JSON era `F_m = ∏_{d∈m}(1+i_d/100)` com
  `rolling(12)` sobre os fatores mensais — janela correta, mas incluindo o mês corrente aberto.
  A segunda, `rolling(365)` sobre **linhas** diárias ("rough approximation"), nunca chegou ao
  JSON (a célula que a consumiria é markdown); se tivesse, erraria ~6 p.p. (365 dias de
  publicação ≈ 1,45 ano).
- **Fórmula proposta:** a mesma da primeira, como caminho único e com mês fechado:
  `V_t = (∏_{k=t−11}^{t} ∏_{d∈m_k}(1+i_d/100) − 1) × 100`.
- **Evidência:** o fator mensal da 11 reproduz a 4390 em todos os 382 meses comuns (desvio máximo
  0,005 p.p.). Choques: 2002-12 19,17%; 2008-12 12,48%; 2015-12 13,27%; 2020-12 2,76% — todos
  idênticos ao publicado. Único desvio: **2025-10, 12,77 → 13,71** (+0,94 p.p., mês aberto).
- **Veredito:** corrigir (fórmula mantida; corrige mês aberto, cobertura e o segundo pipeline).
- **Impacto esperado:** 359 → 371 pontos; `1995-12`–`2025-10` → `1995-12`–`2026-10`; 1 valor muda;
  os demais 358 mudam só na representação (arredondamento a 2 casas).
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## pib-real-anual

- **Definição:** variação percentual do PIB real (volume) do ano civil contra o anterior, a
  preços de mercado, série encadeada. `percentual` (`%`, 2 casas), `eixo: percentual`,
  `medida: variacao-anual`, `anual`, data no início do ano.
- **Fonte e código:** IBGE, Contas Nacionais, lida na SGS **7326** (2 casas). Conferência no
  SIDRA v3: tabela 5932 (taxa acumulada no ano, 4º tri) e índice de volume da 1620.
- **Fórmula atual:** nenhuma — o notebook lia a mesma SGS 7326 via `python-bcb` em blocos de
  3.650 dias. O conceito estava certo; o defeito era de pipeline: saída em `/content`, campo
  `rate`, sem contrato, sem conferência e parado em 2024 com o valor de 2024 desatualizado
  (3,40 contra 3,42).
- **Fórmula proposta:** nenhuma. A taxa é definida pelo IBGE; o notebook busca, recorta anos
  fechados, formata e confere cada ponto contra duas publicações do IBGE.
- **Evidência:** as tabelas do IBGE (6784 anual e 5932 trimestral) publicam a mesma taxa com 1
  casa; a SGS 7326 traz 2 casas e cobre até 2025. Ela é idêntica ao centésimo à taxa recomposta
  do índice 1620 em 29 de 29 anos e fica a ≤0,05 p.p. da 5932 em 30 de 30. A tabela 6784 **não**
  é usada: em 2018 e 2019 traz 1,7 e 1,3 contra 1,8 e 1,2 das tabelas de nível (inconsistência
  interna do IBGE; a soma dos dois anos é a mesma). Choques conferidos: 2003 1,14; 2009 −0,13;
  2015 −3,55; 2016 −3,28; 2020 −3,28; 2021 4,76. Única diferença contra o publicado: 2024
  **3,40 → 3,42**; 2025 entra com 2,29.
- **Veredito:** manter (fonte e valores) + corrigir (pipeline e cobertura).
- **Impacto esperado:** 30 → 31 pontos, `1995`–`2024` → `1995`–`2025`; 1 valor muda; maior
  desvio 0,02 p.p. O corte em 1995 é editorial (a SGS vai a 1963, mas antes de 1995 os números
  vêm da base de volume anterior). 1995 é o único ponto sem conferência possível — o IBGE só
  publica taxa a partir de 1996.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## mvgr-nominal

- **Definição:** mediana dos valores de avaliação dos imóveis residenciais dados em garantia a
  financiamentos imobiliários de pessoas físicas, informados ao SCR — janela móvel de 3 meses,
  cobertura nacional, financiamentos acima de 13,3 salários mínimos. É nível de preço mediano
  em reais, não massa agregada. `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `mensal`.
- **Fonte e código:** BCB (SCR), SGS **25419**. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.25419/dados?formato=json`. Definição em
  `https://www.bcb.gov.br/content/estatisticas/mercadoimobiliario_docs/Metodologia.pdf`.
- **Fórmula atual:** nenhum cálculo — o notebook lia a 25419 em blocos de 10 anos. A aritmética
  estava limpa, mas o JSON nunca foi regerado: parou em 2025-07 e guarda valores de uma extração
  anterior.
- **Fórmula proposta:** nenhuma. A série é publicada tal qual o BCB a divulga, recalculada
  inteira a cada execução — é a única forma de acompanhar as revisões do SCR.
- **Evidência:** 270 leituras na fonte, `2004-03`–`2026-08`, sem lacuna. Contra o publicado
  (257 pontos): 132 idênticos, **125 divergentes**, desvio máximo **3,17%** em 2025-07
  (252.000 → 260.000); 93 valores publicados não existem em nenhuma data da série atual —
  assinatura de revisão, não de cálculo. 2009-03 78.771 → 78.500; out/2020 196.000 → 198.000.
  O início em 2004-03 é limite da fonte.
- **Veredito:** corrigir (regerar da fonte; sem mudança de fórmula).
- **Impacto esperado:** 257 → 270 pontos, `2004-03`–`2025-07` → `2004-03`–`2026-08`; 125 dos 257
  valores comuns mudam; maior desvio −3,17%.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## mvgr-real

- **Definição:** MVG-R nominal deflacionado pelo IPCA, em reais constantes de **março de 2004**
  (mês-base = primeiro mês da série). `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`,
  `mensal`.
- **Fonte e código:** BCB/SGS 25419 deflacionada pelo IPCA mensal, SGS **433**. O BCB não publica
  MVG-R real; o IVG-R (21340) é índice de preços, não valor em reais.
- **Fórmula atual:** `nominal(t) / ∏(1 + IPCA_s/100)`, base 2004-03 — conceitualmente correta,
  mas o deflator implícito aplica a variação do IPCA **duas vezes** em `2005-10` (fator 1,5056%
  contra 0,75%) e `2015-10` (1,6467% contra 0,82%), além de herdar o nominal desatualizado.
- **Fórmula proposta:** a mesma, executada uma única vez por mês, base fixa em 2004-03 (para o
  histórico não ser reescalado a cada execução). IGP-M descartado: é atacado e reajuste
  contratual, não custo de vida; o catálogo do app declara IPCA.
- **Evidência:** a cadeia do 433 reproduz o número-índice do IPCA do IBGE (SIDRA 1737, variável
  2266) com desvio relativo máximo 2,1×10⁻⁵. Dupla contagem provada pelo fator implícito
  `nominal/real`: 2005-10 = 1,015056 = (1,0075)² e 2015-10 = 1,016467 = (1,0082)²; nos outros
  254 meses o fator é exatamente `1 + IPCA/100`. Efeito acumulado: o real publicado fica 0,75%
  abaixo do correto depois de out/2005 e 1,55% depois de out/2015. 2025-07 **76.833,66 →
  80.522,29** (+4,80%, maior desvio); 2026-08 novo, 86.268,70. `real/nominal = 1/deflator` em
  todos os 270 meses.
- **Veredito:** corrigir.
- **Impacto esperado:** 257 → 270 pontos, `2004-03`–`2026-08`; 247 dos 257 valores comuns mudam;
  maior desvio R$ 3.688,62 (+4,80%) em 2025-07.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01. Fica registrado que o produto
  não comunica a base (reais de mar/2004): é pendência de apresentação, não de dado.

## caged-total-mensal

- **Definição:** número de vínculos formais ativos no último dia do mês de competência
  (celetistas; inclui aprendizes, intermitentes e temporários; exclui estatutários). É
  **estoque**, não fluxo. `numero` (`vínculos`, 0 casas), `eixo: contagem`, `medida: estoque`,
  `mensal`.
- **Fonte e código:** MTE (Caged / Novo Caged), via SGS **28763** ("Estoque de empregos formais —
  Total", unidade "Unidades"). Descartadas: microdados FTP do MTE (indisponível/403), página
  mensal do MTE (só o mês corrente), SGS 28526 (índice, inativa desde 2019-12), IBGE (não produz
  CAGED), IPEA (espelho).
- **Fórmula atual:** nenhuma — já lia a série oficial de estoque. O defeito era de proveniência e
  cobertura: `fonte` genérica, sem `urlFonte`, inicio em 1995-01 (limite administrativo), fim em
  2025-08 (12 meses desatualizado) e vintage de out/2025, anterior à revisão de base.
- **Fórmula proposta:** nenhuma. Busca, recorte dos meses fechados e formatação.
- **Evidência:** **estoque, não fluxo** — nível 19,6M–48,2M e maior movimento mensal de toda a
  série −981.331 (2020-04, 2,6% do nível); Δestoque de ago/2026 = 165.827, exatamente o saldo
  oficial do mês (2.294.563 admissões − 2.128.736 desligamentos). Choques: 2008-12 −695.361;
  2015-12 −614.393; 2020-04 −981.331; 2020-02→06 −1,79M. **Revisão de base:** o JSON publicado
  estava exatamente **+1.301.949** acima do vintage atual em todos os 300 meses de 1995-01 a
  2019-12, com variações mensais idênticas — deslocamento de base, não revisão de fluxo;
  2025-12 = 47.110.663 é o "estoque RAIS 2025" usado como base pelo MTE. A emenda Caged → Novo
  Caged (jan/2020) é invisível por construção (2019-12 = 38.152.770 → 2020-01 = 38.267.044),
  mas o BCB registra "diferenças metodológicas relevantes" entre os trechos.
- **Veredito:** manter (`medida: estoque` confirmada) + corrigir proveniência, cobertura e vintage.
- **Impacto esperado:** 368 → 380 pontos; `1995-01`–`2025-08` → `1995-01`–`2026-08`; os 368 pontos
  comuns mudam todos; diferença +1.301.949 constante até 2019-12, entre +1.295.014 e +1.357.641
  de 2020 em diante; maior desvio absoluto +1.357.641 (2020-03). O recorte em 1995-01 **foi
  mantido** apesar de a fonte começar em 1992: o gráfico só exibe a partir de 1995, e estender
  não acrescentaria nada visível.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01 (manter 1995; a alternativa
  RAIS Mensal mudaria `id`, semântica e histórico, e ficou de fora).

## populacao-total-anual

- **Definição:** população residente total do Brasil, em habitantes, estimada para 1º de julho de
  cada ano. `numero` (`hab.`, 0 casas), `eixo: contagem`, `medida: estoque`, `anual`.
- **Fonte e código:** IBGE, Projeções da População — Revisão 2024, tabela 4 (Indicadores
  Implícitos), variável `POP_T`:
  `https://ftp.ibge.gov.br/Projecao_da_Populacao/Projecao_da_Populacao_2024/projecoes_2024_tab4_indicadores.xlsx`.
  Conferência na SIDRA 6579 (variável 9324), que republica as estimativas anuais: 2024–2026
  coincidem dígito a dígito. Se o endpoint de metadados do SIDRA
  (`servicodados.ibge.gov.br/api/v3/agregados/6579/periodos`) não responder de dentro do
  GitHub Actions, o notebook confere apenas o último ano, com aviso; os valores continuam
  vindo da planilha de projeção.
- **Fórmula atual:** nenhuma — mas a série **não era do IBGE**: era `DEPIS_POP` do IPEADATA,
  construída por interpolação spline cúbica entre Censos e Contagens, com extrapolação em
  2023–2024. Os 30 pontos publicados são idênticos à DEPIS_POP, e a "queda" de 2020–2022
  (204,08 → 203,79 → 203,08 milhões) é artefato do spline, não demografia.
- **Fórmula proposta:** nenhuma. Leitura de `POP_T` — população conciliada a 1º de julho da
  revisão vigente.
- **Evidência:** 2000 **169.799.170 → 174.695.935** (+2,88%); 2010 **190.755.799 → 194.749.329**
  (+2,09%); 2020 **204.080.793 → 209.164.889** (+2,49%); 2022 (Censo) **203.080.756 →
  210.862.983** (+3,83%, maior desvio); 2024 **204.861.525 → 212.583.750**. 25 de 25 anos comuns
  mudam. O Censo 2022 (203.080.756 em 1º/8) não é revisado; a revisão 2024 trabalha com
  população **conciliada** (210.862.983 em 1º/7, ajuste PPE), aplicada retroativamente a 2000
  (+3,0%) e 2010 (+2,2%) — por isso não há degrau em 2022. A SIDRA 6579 como série contínua foi
  descartada: 2001–2021 são safras antigas (degrau de 2013: 193,9 → 201,0 milhões num ano) e
  faltam 2007, 2010, 2022 e 2023.
- **Veredito:** adotar-fonte-oficial.
- **Impacto esperado:** 30 → 27 pontos; `1995`–`2024` → `2000`–`2026`; 25 valores comuns, todos
  mudam; maior desvio +7.782.227 hab. (2022). Perde 1995–1999 porque a revisão não tem série
  conciliada antes de 2000 — trecho que, na prática, era o interpolado.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01, inclusive a perda de
  1995–1999. Fica registrado que a data publicada é `AAAA-01-01` (início do ano, como C9 manda)
  e o valor é de 1º de julho; mudar o carimbo para `07-01` seria mudança de convenção do
  contrato, não desta série.

## populacao-variacao-anual

- **Definição:** variação percentual da população residente total contra o ano anterior (1º de
  julho contra 1º de julho). `percentual` (`%`, 2 casas), `eixo: percentual`,
  `medida: variacao-anual`, `anual`.
- **Fonte e código:** IBGE, Revisão 2024, tabela 4, variável `TCG_T` (taxa de crescimento
  geométrico anual) — o IBGE **publica a variação pronta**.
- **Fórmula atual:** `pct_change() * 100` sobre a DEPIS_POP. A derivação estava certa em si, mas
  incidia sobre série interpolada — e publicava **queda** de população em 2021 (−0,1447%) e 2022
  (−0,3458%).
- **Fórmula proposta:** nenhuma — publica-se `TCG_T`, que é exatamente
  `(P_t/P_{t−1} − 1) × 100`. A identidade foi conferida nos 26 pontos (resíduo máximo 4,2×10⁻¹⁵
  p.p.). O primeiro ponto é 2001, porque 2000 é denominador.
- **Evidência:** 2001 1,5652 → 1,3210; 2010 1,2283 → 0,8155; 2020 0,0427 → 0,6084; 2022
  **−0,3458 → +0,3614** (+0,7072 p.p., maior desvio); 2024 0,4236 → 0,4198. 24 de 24 pontos
  comuns mudam; a série nova é positiva em todos os 26 pontos.
- **Veredito:** adotar-fonte-oficial.
- **Impacto esperado:** 29 → 26 pontos; `1996`–`2024` → `2001`–`2026`; maior desvio +0,7072 p.p.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## homicidios-anual

- **Definição:** taxa anual de homicídios por 100 mil habitantes, por local de residência.
  `numero` (`por 100 mil`, 2 casas), `eixo: por-100-mil`, `medida: nivel`, `anual`.
- **Fonte e código:** MS/SVS/CGIAE — SIM, compilado pelo IPEA/Atlas da Violência; numerador na
  série 328 do Atlas e denominador na série Ipeadata `AVIOL12_VIOLPOP` (população residente,
  estimativa/TCU ajustada). Endpoints: `https://www.ipea.gov.br/dados-api/series-values/328/1` e
  `https://www.ipeadata.gov.br/api/odata4/ValoresSerie(SERCODIGO='AVIOL12_VIOLPOP')`.
- **Fórmula atual:** nenhuma — lia `THOMIC` (taxa pronta, série que saiu do catálogo do Ipeadata)
  e publicava. A taxa pronta mistura populações de vintages diferentes (Contagem em 1996,
  Estimativas TCU em 1997–2003 e 2016, IBGE/Diretoria de Pesquisas em 2004–2015), e o JSON
  publicado é um patchwork: 1995–2013 do `THOMIC`, 2014–2021 de contagem ÷ VIOLPOP, 2017/2022/2023
  com outras populações. O 2023 publicado (21,218263) equivale a `45.747 ÷ 215.602.000`,
  denominador que não existe em nenhuma série atual.
- **Fórmula proposta:** `100.000 × homicídios ÷ população`, com o numerador do Atlas e a
  população `AVIOL12_VIOLPOP` do mesmo ano. Nenhuma taxa herdada. A série de população declara
  que 2022 e 2023 são interpolações exponenciais entre 2021 e 2024 — limitação conhecida e
  **limitada**: a projeção 2024 do IBGE dá 210,9 mi para 2022 contra 212,8 mi da `VIOLPOP`, ou
  seja, o erro do denominador é de 0,9% em dois anos, sem gerar degrau na série. Trocar a fonte
  para resolver isso custaria mais: as Projeções 2024 começam em 2000, e usá-las truncaria
  1995–1999 ou reintroduziria dois denominadores — o defeito que esta revisão eliminou.
- **Evidência:** 2007 `48.219 ÷ 189.462.739 × 100.000 = 25,45` (o antigo 26,20 implica 184,0 mi);
  2012 `57.045 ÷ 199.239.473 = 28,63` (o antigo 29,41 implica 194,0 mi); 2020 23,55 contra 23,54
  (aqui a população já era a mesma). 2003 29,14 → 28,53; 2017 31,59 → 31,72; 2022 21,67 → 21,81;
  2023 21,22 → 21,52; 2024 novo, 20,04. Maior desvio 2012, −0,78.
- **Veredito:** corrigir.
- **Impacto esperado:** 29 → 30 pontos; `1995`–`2023` → `1995`–`2024`; 17 dos 29 valores comuns
  mudam; maior desvio 0,78 p.p. A alternativa de publicar a taxa oficial do Atlas (série 20),
  que mantém o denominador misto, foi descartada.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## homicidios-armas-fogo-anual

- **Definição:** taxa anual de homicídios por armas de fogo por 100 mil habitantes, por
  residência. `numero` (`por 100 mil`, 2 casas), `eixo: por-100-mil`, `medida: nivel`, `anual`.
- **Fonte e código:** SIM compilado pelo Atlas, numerador na série 31 e denominador na
  `AVIOL12_VIOLPOP`.
- **Fórmula atual:** lia a taxa pronta da série 35 pela API antiga do Atlas (`/valores-series/35/1`,
  hoje 404) e usava o `periodo` como data — a API devolve `YYYY-01-15`, e daí vinha **o dia 15**
  desta série, sozinho no repo. Não calculava denominador; a taxa 35 usa população mista e para
  em 2022.
- **Fórmula proposta:** `100.000 × homicídios_armas ÷ população`, com a contagem 31 e a mesma
  população do ano. Datas no dia 01, como manda C9.
- **Evidência:** 2007 `34.147 ÷ 189.462.739 = 18,02` (antigo 18,56; implica 184,0 mi); 2012
  `40.077 ÷ 199.239.473 = 20,11` (antigo 20,66); 2019 `30.206 ÷ 210.131.314 = 14,37` (o antigo
  14,67 implica 30.826 homicídios por arma, 620 acima da contagem publicada). 2003 20,42 → 20,00;
  2017 22,88 → 22,98; 2022 15,68 → 15,78; 2023 novo, 14,48. Maior desvio 2012, −0,55.
- **Veredito:** corrigir.
- **Impacto esperado:** 28 → 29 pontos; `1995-01-15`–`2022-01-15` → `1995-01-01`–`2023-01-01`.
  **As 28 datas mudam** (dia 15 → 01) e 16 dos 28 valores mudam; maior desvio 0,55.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01, inclusive a normalização do
  dia 15.

## proporcao-homicidios-armas-fogo-anual

- **Definição:** participação percentual dos homicídios por armas de fogo no total de homicídios.
  `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: participacao`, `anual`.
- **Fonte e código:** derivada das contagens 31 (armas) e 328 (total) do SIM/Atlas.
- **Fórmula atual:** `100 × taxa_armas ÷ taxa_total`. Só é igual a `100 × armas ÷ total` quando
  as duas taxas usam o mesmo denominador — o que não acontece em vários anos.
- **Fórmula proposta:** `100 × homicídios_armas ÷ homicídios_total`, direto das contagens, nos
  anos em que ambas existem.
- **Evidência:** a proporção proposta é exatamente `100 × série 31 ÷ série 328` nos 29 anos
  (diferença 0,00 no 2º decimal). 2019 **67,76% → 66,38%** (−1,38 p.p., o maior desvio); fora
  2019 todos os desvios são ≤0,03 p.p. (arredondamento). 2023 novo, 67,30.
- **Veredito:** corrigir.
- **Impacto esperado:** 28 → 29 pontos; `1995`–`2022` → `1995`–`2023`; 28 valores mudam no 2º
  decimal, só 2019 de forma substantiva.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01.

## Pendentes

Revisão concluída para as 12 séries em 2026-11-01. **Não há pendência de dado nem de forma.**

As decisões de apresentação que estavam abertas foram fechadas no catálogo do `sitio`
(`app/src/data/indicadores.json`), que é o que a ficha do app exibe:

- `mvgr-real` chama-se "Valor mediano do imóvel em garantia (R$ de mar/2004)" e a descrição diz
  que são reais constantes de março de 2004 — o número não é preço de hoje;
- `populacao-*` diz que é projeção de 2024 do IBGE, população conciliada ao Censo 2022, com
  referência em 1º de julho;
- o carimbo `AAAA-01-01` nas séries anuais é convenção de C9 (início do período) e foi mantido.

Duas **condições de revisão** ficam registradas — não são pendências, são gatilhos:

- **Homicídios:** o denominador de 2022–2023 é interpolação do IPEA, com erro limitado a 0,9%
  (ver o bloco de `homicidios-anual`). Refazer quando IPEA/IBGE publicarem população consolidada
  para esses anos.
- **Séries anuais:** se o instante da medida (1º de julho, no caso da população) passar a
  importar mais que o alinhamento entre séries anuais, muda-se C9 para as seis séries anuais no
  mesmo commit — não série a série.
