# Metodologia dos indicadores

Revisão da definição e da fórmula de cada indicador, conferida contra a fonte
e contra a matemática do próprio indicador — nunca contra o código atual.

> **Escopo:** as 13 séries foram revisadas e publicadas em 2026-11-01. O IPCA foi o piloto
> (`ipca-acum-12m`); o IGP-M veio em seguida; as outras seis famílias fecharam a rodada.
> As três séries da PNAD Contínua (`pnad-*`) foram publicadas em 2026-11-03 e têm seção
> própria abaixo; elas não fazem parte da contagem das 13.

## ipca-acum-12m

- **Definição:** variação percentual do IPCA acumulada nos últimos 12 meses
  (taxa efetiva do período), unidade `percentual` (`%`, 2 casas decimais),
  granularidade `mensal`.
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

- **Definição:** meta da taxa Selic definida pelo Copom, **ao ano** — o nível em vigor no
  **último dia do mês**. `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: nivel`,
  `mensal`.
- **Fonte e código:** Banco Central do Brasil, SGS **432** (meta Selic definida pelo Copom,
  % a.a., diária, desde 05/03/1999). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados?formato=json`, consultado em janelas
  de 10 anos (limite do SGS para série diária).
- **Fórmula atual:** nenhuma. A meta do mês é a **última leitura diária do mês**
  (`valores[-1]`), isto é, o nível em vigor no último dia do mês. O mês corrente é descartado.
- **Fórmula proposta:** nenhuma. A meta é o que o Copom decide; repetir o nível é reproduzir a
  fonte, não calcular.
- **Correção de 2026-11-02:** a versão anterior publicava a **média** das leituras diárias do
  mês (`sum(valores) / len(valores)`), alegando que ela só lidava com mudança de meta no meio
  do mês e teria "efeito máximo de ~0,03 p.p.". A alegação era falsa: a média se afasta do
  nível de fim de mês sempre que o Copom se move dentro do mês, e o desvio chega a **4,85 p.p.**
  (abr/1999: 36,85% publicado contra **32,00%** em vigor no último dia). A série passou a
  publicar `valores[-1]`; o descarte do mês corrente e a checagem de meses contínuos foram
  mantidos.
- **Evidência:** jul/2016 = 14,25% ao ano (meta constante no período); out/2025 = 15,00%;
  mar/1999 = **42,00%** (primeiro mês da fonte, a partir de 05/03; a média dava 44,22%). Na
  correção, **148 dos 332 valores** publicados mudam; o maior desvio é 4,85 p.p. (abr/1999) e
  todos os valores novos são múltiplos de 0,25 p.p. Exemplos recentes: dez/2024 **11,90 →
  12,25**; jun/2025 **14,85 → 15,00**; set/2026 **13,88 → 13,75**. Não existe série oficial de
  "meta acumulada em 12 meses" porque a meta é anualizada — acumulá-la exigiria convertê-la em
  taxa mensal equivalente e recompor, um construto que só coincide com a meta quando ela fica
  parada 12 meses. Em dez/2003 a meta em vigor no último dia era **16,50%** e esse construto
  daria **23,03%** (com a média antiga, 17,05%, dava 23,48%).
- **Veredito:** corrigir (a série publicava a média diária; passa a publicar o nível de fim de
  mês). A migração anterior, de construto acumulado para nível, já estava aprovada em
  2026-11-01.
- **Impacto esperado:** 332 pontos mantidos (`1999-03`–`2026-10`); **148 valores mudam**; maior
  desvio 4,85 p.p. (abr/1999); o primeiro ponto passa de 44,22% para **42,00%** e o último
  (out/2026) continua **13,75%**. `id`, `unidade`, `eixo`, `medida` e cobertura não mudam.
- **Decisão pendente:** não — correção de agregação aplicada em 2026-11-02; a definição da meta
  como nível (e não acumulado) segue a decisão de 2026-11-01.

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

## pib-per-capita-nominal

- **Definição:** PIB por habitante a preços correntes, em reais do próprio ano, ano civil.
  `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`.
- **Fonte e código:** IBGE, Contas Nacionais Anuais, tabela SIDRA **6784**, variável **9812**
  ("PIB per capita - valores correntes"), Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6784/n1/all/v/all/p/all?formato=json` (o notebook lê
  a tabela inteira e usa as variáveis 9811, 9812, 9813 e 9814).
- **Fórmula:** nenhuma — o IBGE publica o nível. Cobertura `1996`–`2023` (28 pontos), os anos
  fechados das Contas Nacionais Anuais nesta edição.
- **Evidência:** `1996` R$ 5.219,36; `2023` R$ 51.693,92; mínimo R$ 5.219,36 (1996); máximo
  R$ 51.693,92 (2023). Crescimento nominal de **890,4%** no período.
- **Verificação independente:** a Carta Capital de 06/11/2025 cita "PIB per capita de 2023
  foi equivalente a 51.693,92 reais"
  (`https://www.cartacapital.com.br/economia/ibge-confirma-crescimento-de-32-da-economia-em-2023/`);
  o DComércio cita o mesmo valor
  (`https://dcomercio.com.br/publicacao/s/pib-cresce-3-2-em-2023-e-soma-r-10-9-tri-mostram-dados-definitivos-do-ibge`).
  As duas citam o IBGE; não há segunda medição.
- **Caveats:** é nominal — o crescimento ao longo do tempo mistura inflação e não mede poder
  de compra; anual; para 2024 e 2025 não há nível per capita publicado.

## pib-per-capita-real

- **Definição:** PIB por habitante em reais constantes de **2023**, ano civil. `moeda`
  (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `granularidade: anual`, data em
  `AAAA-01-01`. Série derivada, não publicada pelo IBGE.
- **Fonte e código:** IBGE, Contas Nacionais Anuais, tabela SIDRA **6784**, variáveis **9812**
  (PIB per capita corrente) e **9814** (PIB per capita — variação em volume); cálculo do
  site. Endpoint: o mesmo da tabela 6784.
- **Fórmula:** `L_2023 = 9812_2023`; para cada ano anterior,
  `L_t = L_{t+1} / (1 + 9814_{t+1}/100)`. O ano-base 2023 é o último ano fechado; a base é
  fixa e não é rebaseada automaticamente.
- **Evidência:** 28 pontos, `1996`–`2023`; `1996` R$ 37.261,36; `2023` R$ 51.693,92;
  crescimento real de **38,7%** contra **890,4%** do nominal. O deflator implícito do PIB
  acumulou **7,12×** no período.
- **Conferência do cálculo:** o notebook reconstrói a série por três rotas independentes da
  mesma tabela — a variação em volume oficial (9814, rota publicada), o deflator implícito
  encadeado (9811) e o PIB per capita a preços do ano anterior encadeado (9813). O desvio
  máximo medido entre elas é de **0,30%** (R$ 140 em 2008), compatível com o arredondamento
  de 1–2 casas da fonte; a tolerância do notebook é 0,5%.
- **Verificação independente:** não há publicação de terceiro com esta série em reais de
  2023 — a busca encontrou apenas o nível nominal (Carta Capital, DComércio, acima) e séries
  internacionais de PIB per capita em US$ (Banco Mundial/FMI), que usam outra moeda, outra
  base e, às vezes, PPP. A conferência é interna, contra as três variáveis oficiais da 6784.
- **Caveats:** é uma série **derivada** (o número em R$ de 2023 não é o que o IBGE divulga);
  o ano-base é escolha de apresentação; a cobertura para em 2023; não deve ser comparada
  numericamente com PIB per capita em US$ de organismos internacionais.

## mvgr-nominal

- **Definição:** **MVG-R** (Mediana dos Valores de Garantia de Imóveis Residenciais
  Financiados): mediana dos valores de **avaliação** dos imóveis residenciais dados em garantia
  a financiamentos imobiliários de pessoas físicas (alienação fiduciária e hipoteca
  residencial), informados ao SCR — janela móvel de 3 meses, cobertura nacional, operações com
  valor contratado acima de 13,3 salários mínimos mensais (um salário mínimo anual; piso baixo,
  não corte de alta renda). É nível de **valor de garantia** mediano em reais, não preço de
  mercado, índice de preços ou massa agregada. `moeda` (`R$`, 0 casas), `eixo: reais`,
  `medida: nivel`, `mensal`.
- **Fonte e código:** BCB (SCR), SGS **25419**. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.25419/dados?formato=json`. Definição em
  `https://www.bcb.gov.br/content/estatisticas/mercadoimobiliario_docs/Metodologia.pdf`.
- **Fórmula atual:** nenhum cálculo — o notebook lia a 25419 em blocos de 10 anos. A aritmética
  estava limpa, mas o JSON nunca foi regerado: parou em 2025-07 e guarda valores de uma extração
  anterior.
- **Fórmula proposta:** nenhuma. A série é publicada tal qual o BCB a divulga, recalculada
  inteira a cada execução — é a única forma de acompanhar as revisões do SCR.
- **Correção de 2026-11-02 (apresentação):** o nome "Valor mediano do imóvel em garantia"
  sugeria preço de mercado; passa a "MVG-R — valor mediano de garantia (R$ correntes)". A
  descrição do catálogo explicita PF, modalidades, janela de 3 meses, cobertura nacional e o
  piso de 13,3 salários mínimos. `casas` passa de 2 para 0 (a 25419 publica reais inteiros) e
  o `fonte` vira "Banco Central do Brasil (SGS 25419)". Nenhum valor muda. O post do `sitio`
  ainda chama o MVG-R de "valor médio", "preço de etiqueta" e "valor real dos imóveis" —
  corrigir no repo `sitio`.
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

- **Definição:** **MVG-R deflacionado pelo IPCA**, em reais constantes de **março de 2004**
  (mês-base = primeiro mês da série). É o nominal dividido pela **média geométrica de 3 meses do
  IPCA** (a mesma janela da mediana móvel); não é um índice de preços nem a valorização de um
  mesmo imóvel. `moeda` (`R$`, 2 casas), `eixo: reais`, `medida: nivel`, `mensal`.
- **Fonte e código:** BCB/SGS 25419 deflacionada pela média geométrica de 3 meses do IPCA, SGS
  **433**. O BCB não publica MVG-R real; o IVG-R (21340) é índice de preços, não valor em reais.
- **Fórmula atual:** `nominal(t) / ∏(1 + IPCA_s/100)`, base 2004-03 — conceitualmente correta,
  mas o deflator implícito aplica a variação do IPCA **duas vezes** em `2005-10` (fator 1,5056%
  contra 0,75%) e `2015-10` (1,6467% contra 0,82%), além de herdar o nominal desatualizado.
- **Fórmula proposta:** `nominal(t) / ∏(1 + i_avg(s)/100)`, com
  `i_avg(s) = [(1+i_{s-2})(1+i_{s-1})(1+i_s)]^(1/3) − 1`, base fixa em 2004-03 (para o
  histórico não ser reescalado a cada execução). A janela de 3 meses é a mesma do MVG-R
  nominal; a média geométrica é a taxa média que, composta, reproduz a inflação da janela (a
  média aritmética das taxas daria 85.619,95 no último ponto, contra 85.662,08 da geométrica —
  diferença de segunda ordem). IGP-M descartado: é atacado e reajuste contratual, não custo de
  vida; o catálogo do app declara IPCA. O exato seria deflacionar cada uma das três observações
  e tomar a mediana, mas o BCB publica só a mediana da janela; a média da janela é a melhor
  aproximação com o dado disponível. A série continua sendo um nível deflacionado, não um
  índice de preços constante-quality.
- **Evidência:** a cadeia do 433 reproduz o número-índice do IPCA do IBGE (SIDRA 1737, variável
  2266) com desvio relativo máximo 2,1×10⁻⁵. Dupla contagem provada pelo fator implícito
  `nominal/real`: 2005-10 = 1,015056 = (1,0075)² e 2015-10 = 1,016467 = (1,0082)²; nos outros
  254 meses o fator é exatamente `1 + IPCA/100`. Efeito acumulado: o real publicado fica 0,75%
  abaixo do correto depois de out/2005 e 1,55% depois de out/2015. 2025-07 **76.833,66 →
  80.522,29** (+4,80%, maior desvio); 2026-08 novo, 86.268,70. `real/nominal = 1/deflator` em
  todos os 270 meses. (Valores desta Evidência são da revisão de 2026-11-01; a média da janela
  de 2026-11-02 muda o último para 85.662,08 — ver abaixo.)
- **Correção de 2026-11-02 (média da janela):** o deflator do mês `t` deixou de ser o IPCA de
  `t` e passou a ser a média geométrica dos fatores de `t-2`, `t-1` e `t`, a mesma janela da
  mediana móvel. Todos os 269 pontos depois da base mudam; o último (2026-08) passa de
  **86.268,70** para **85.662,08** e o maior desvio é 2022-08 (**80.679,93 → 79.890,58**,
  −789,35). A base 2004-03 continua 44.419,00 (deflator = 1). A validação inline confere que o
  fator mensal é exatamente `1 + média da janela/100` e que a média entra uma única vez.
- **Veredito:** corrigir.
- **Impacto esperado:** 270 pontos mantidos, `2004-03`–`2026-08`; 269 dos 270 valores mudam
  (só a base não muda); maior desvio R$ 789,35 em 2022-08; último 86.268,70 → 85.662,08.
- **Decisão pendente:** não — aprovada pelo usuário em 2026-11-01; nomenclatura e média da
  janela aplicadas em 2026-11-02. O nome é "MVG-R deflacionado pelo IPCA (R$ de mar/2004)"; a
  descrição explica a base e a janela; o `fonte` credita o IPCA/IBGE (SGS 433). O símbolo da
  unidade continua "R$" (a base aparece no nome/descrição). O que a série real **não** mede:
  valorização do mesmo imóvel, preço de mercado ou "patrimônio" — a composição da amostra muda.

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
- **Fonte e código:** SIM compilado pelo Atlas. Numerador: série 31 do Ipea até 2013;
  2014–2024: Atlas da Violência 2026 (FBSP/Ipea), Tabela 11.1, publicado em PDF
  (`https://forumseguranca.org.br/wp-content/uploads/2026/05/atlas-violencia-2026-relatorio-completo.pdf`).
  Denominador: `AVIOL12_VIOLPOP`.
- **Fórmula atual:** lia a taxa pronta da série 35 pela API antiga do Atlas (`/valores-series/35/1`,
  hoje 404) e usava o `periodo` como data — a API devolve `YYYY-01-15`, e daí vinha **o dia 15**
  desta série, sozinho no repo. Não calculava denominador; a taxa 35 usa população mista e para
  em 2022.
- **Fórmula proposta:** `100.000 × homicídios_armas ÷ população`, com a contagem 31 (1995–2013)
  ou a contagem do Atlas 2026 (2014–2024) e a mesma população do ano. Datas no dia 01, como
  manda C9.
- **Evidência:** 2007 `34.147 ÷ 189.462.739 = 18,02` (antigo 18,56; implica 184,0 mi); 2012
  `40.077 ÷ 199.239.473 = 20,11` (antigo 20,66); 2019 `30.206 ÷ 210.131.314 = 14,37` (safra
  antiga, 1995–2013; o antigo 14,67 implica 30.826 homicídios por arma, 620 acima da contagem
  publicada). O bloco 2014–2024 muda 10 dos 11 anos em relação à safra antiga (só 2022 é
  idêntico); nesta emenda, em relação ao HEAD anterior, mudam 2014–2021 (2022–2024 já estavam
  desde 977e8cb). Contagem, taxa e proporção, safra antiga → safra 2026:

  | ano | contagem | taxa | proporção |
  |---:|---:|---:|---:|
  | 2014 | 42.755 → 43.397 | 21,09 → 21,40 | 70,70 → 71,76 |
  | 2015 | 41.817 → 42.656 | 20,45 → 20,86 | 70,78 → 72,20 |
  | 2016 | 44.475 → 45.616 | 21,58 → 22,13 | 71,14 → 72,97 |
  | 2017 | 47.510 → 49.085 | 22,98 → 23,74 | 72,42 → 74,82 |
  | 2018 | 41.179 → 42.908 | 19,75 → 20,58 | 71,05 → 74,04 |
  | 2019 | 30.206 → 32.091 | 14,37 → 15,27 | 66,38 → 70,53 |
  | 2020 | 33.994 → 35.828 | 16,05 → 16,92 | 68,17 → 71,85 |
  | 2021 | 33.039 → 35.070 | 15,49 → 16,44 | 69,05 → 73,30 |
  | 2022 | 33.580 → 33.580 | 15,78 → 15,78 | 72,36 → 72,36 |
  | 2023 | 30.789 → 32.749 | 14,48 → 15,41 | 67,30 → 71,59 |
  | 2024 | — → 29.870 | — → 14,05 | — → 70,13 |

  A variação 2013→2014 é **+7,50%** na contagem (40.369 → 43.397) e **+6,58%** na taxa
  (20,08 → 21,40). A safra 2026 tem 2013 = 40.870 (Tabela 11.1 de 2025); se ele fosse usado,
  a variação seria +6,18%. O resíduo de +1,32 p.p. é a revisão de 2013 que não foi aplicada.
  Maior desvio de taxa no bloco: 2021, +0,95 (15,49 → 16,44); maior desvio de proporção:
  2023, +4,29 p.p. (67,30 → 71,59).
- **Veredito:** corrigir.
- **Impacto esperado:** 30 pontos (1995–2024; a cobertura não muda nesta emenda). Em relação à
  revisão original de 2026-11-01, 28 → 30 pontos. 2014–2021 mudam nesta emenda; 2022–2024 já
  estavam desde 977e8cb (2022 é idêntico à safra antiga).
- **Decisão pendente:** não — bloco completo 2014–2024 aprovado pelo usuário em 2026-11-02.
- **Complemento 2014–2024 (Atlas da Violência 2026).** A série 31 da API do Ipea cobre
  1995–2013 na safra antiga e termina em 2023 com 30.789 — valor que já não é o da safra
  revisada —, sem 2024. O Atlas 2026 publica a safra revisada na Tabela 11.1 (p. 151):
  **2014 = 43.397**, **2015 = 42.656**, **2016 = 45.616**, **2017 = 49.085**, **2018 = 42.908**,
  **2019 = 32.091**, **2020 = 35.828**, **2021 = 35.070**, **2022 = 33.580**, **2023 = 32.749**
  e **2024 = 29.870**, com a mesma definição (CID-10 X93–X95 + Y35.0, Brasil, por residência,
  contagem). O bloco 2014–2024 é contíguo; 2022 = 33.580 coincide nas duas safras, então não
  há degrau em 2022. A emenda é 2013/2014: 2013 continua na série 31 (40.369) e 2014 entra
  pelo Atlas (43.397), +7,50% na contagem. A safra nova tem 2013 = 40.870 (Tabela 11.1 de
  2025), o que daria +6,18%; a diferença é o resíduo de 2013, que fica para uma revisão com
  aval. A fonte é PDF porque não há publicação machine-readable da safra 2026: a API do Ipea
  não foi atualizada, o site do FBSP só oferece o relatório e os microdados do SIM/DATASUS
  não estão tabulados para 2024 neste ambiente. A transcrição é explícita no notebook e
  conferida contra a Tabela 11.3 (70,1% em 2024).
  **Safra mista:** 1995–2013 continuam na série 31 (safra antiga) e 2014–2024 vêm do Atlas
  2026. A Tabela 11.1 de 2025 já revisa 2013 (40.369 → 40.870); esse único ano não foi trocado
  porque a emenda 2013/2014 é o limite do bloco aprovado. O valor de 2022 coincide nas duas
  safras (33.580), então a emenda em 2022 não tem degrau de nível.

## proporcao-homicidios-armas-fogo-anual

- **Definição:** participação percentual dos homicídios por armas de fogo no total de homicídios.
  `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: participacao`, `anual`.
- **Fonte e código:** derivada das contagens de armas (série 31 até 2013; Atlas da Violência
  2026, Tabela 11.1, em 2014–2024) e do total (série 328).
- **Fórmula atual:** `100 × taxa_armas ÷ taxa_total`. Só é igual a `100 × armas ÷ total` quando
  as duas taxas usam o mesmo denominador — o que não acontece em vários anos.
- **Fórmula proposta:** `100 × homicídios_armas ÷ homicídios_total`, direto das contagens, nos
  anos em que ambas existem.
- **Evidência:** nos anos 1995–2013, a proporção publicada é exatamente `100 × série 31 ÷
  série 328` (diferença 0,00 no 2º decimal). 2019 **67,76% → 66,38%** (−1,38 p.p., o maior
  desvio da revisão de 2026-11-01); fora 2019 todos os desvios são ≤0,03 p.p. (arredondamento).
  O bloco 2014–2024 usa as contagens do Atlas 2026; a proporção muda em 10 dos 11 anos (2022
  é idêntico): 2014 70,70 → 71,76; 2015 70,78 → 72,20; 2016 71,14 → 72,97; 2017 72,42 →
  74,82; 2018 71,05 → 74,04; 2019 66,38 → 70,53; 2020 68,17 → 71,85; 2021 69,05 → 73,30;
  2022 72,36 = 72,36; 2023 67,30 → 71,59; 2024 — → 70,13. O Atlas publica 70,1% em 2024.
- **Veredito:** corrigir.
- **Impacto esperado:** 30 pontos; a cobertura não muda. Em relação à revisão original de
  2026-11-01, 28 → 30 pontos. 2014–2021 mudam nesta emenda; 2022–2024 já estavam (2022 é
  idêntico). Maior desvio: 2023, +4,29 p.p. (67,30 → 71,59); depois 2021, +4,25 p.p. e 2019,
  +4,15 p.p.
- **Decisão pendente:** não — bloco completo 2014–2024 aprovado pelo usuário em 2026-11-02.
- **Safra mista:** a mesma do bloco de `homicidios-armas-fogo-anual`. Como o total (série 328)
  já é a safra 2026, a proporção de 1995–2013 mistura o numerador antigo com o denominador
  atual. Em 2013, a proporção publicada é **70,33%** (40.369 ÷ 57.396); com a contagem revisada
  de 2013 (40.870, Tabela 11.1 de 2025) seria **71,21%**. A emenda 2013/2014 na proporção é
  70,33 → 71,76 (+1,43 p.p.); com o 2013 revisado, 71,21 → 71,76 (+0,55 p.p.). O resíduo é a
  revisão de 2013, que depende de aval.

## pnad-desocupacao

- **Definição:** percentual da força de trabalho (pessoas de 14 anos ou mais) que estava
  desocupada no trimestre móvel de três meses encerrado no mês da data. `percentual` (`%`,
  1 casa), `eixo: percentual`, `medida: nivel`, `granularidade: mensal`. O ponto
  `2026-09-01` cobre jul–ago–set/2026; não é a taxa do mês de setembro isolado.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6381**, variável **4099**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6381/n1/all/v/4099/p/all?formato=json`.
- **Fórmula:** nenhuma — a taxa é publicada pelo IBGE. O notebook busca, recorta o último
  trimestre fechado e formata. A série começa em `2012-03` (primeiro trimestre móvel da
  PNAD Contínua mensal). Não há emenda com a PME (2002–2012): a PME tinha outra metodologia
  e cobria só 6 regiões metropolitanas.
- **Evidência:** 175 trimestres móveis, `2012-03` a `2026-09`, sem lacuna. Primeiro `8,0%`
  (jan–fev–mar/2012); último `5,2%` (jul–ago–set/2026); máximo `14,9%` (jul–ago–set/2020);
  mínimo `5,1%` (out–dez/2025). Contra o mesmo trimestre do ano anterior, `5,6% → 5,2%`
  em set/2026.
- **Verificação independente:** ad hoc. A divulgação do IBGE de 30/10/2026 (trimestre
  jul–set/2026) traz `5,2%`, igual ao ponto `2026-09`; a de 29/09/2026 (jun–ago/2026)
  traz `5,3%`, igual ao ponto `2026-08`
  (`https://biblioteca.ibge.gov.br/visualizacao/periodicos/3086/pnacm_2026_set.pdf`).
  Publicações externas de 30/10/2026 (Estadão, UOL, O Globo, Folha, InfoMoney) citam
  `5,2%` para jul–set/2026, `5,4%` para abr–jun e `5,6%` para jul–set/2025 — os três pontos
  batem (Estadão: `https://www.estadao.com.br/economia/ibge-pnad-desemprego-setembro-2026/`;
  O Globo: `https://oglobo.globo.com/economia/noticia/2026/10/30/desemprego-cai-para-52percent-e-chega-ao-menor-nivel-ja-registrado-em-setembro.ghtml`).
  As publicações citam o IBGE, não são uma segunda medição; a limitação fica declarada.
- **Caveats:** trimestre móvel lido como mês; comparação com a PME ou com os anos 1990;
  confusão com o estoque do Caged; queda da taxa por saída da força de trabalho (ver a
  série de participação). A taxa se refere a pessoas de 14 anos ou mais, no Brasil, sem
  recorte regional nem ajuste sazonal.

## pnad-participacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam na força de trabalho
  (ocupadas ou desocupadas) no trimestre móvel encerrado no mês. `percentual` (`%`, 1 casa),
  `eixo: percentual`, `medida: nivel`, `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **5944**, variável **4096**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/5944/n1/all/v/4096/p/all?formato=json`.
- **Fórmula:** nenhuma — série oficial. Cobertura e recorte iguais aos da desocupação.
- **Evidência:** 175 pontos, `2012-03` a `2026-09`; primeiro `62,3%`; último `62,2%`;
  máximo `63,6%` (abr–jun/2019); mínimo `56,5%` (mai–jul/2020).
- **Papel na leitura:** é o denominador que explica por que a taxa de desocupação pode cair
  sem aumento de emprego. A identidade `nível de ocupação = participação ×
  (1 − desocupação/100)` é conferida ponto a ponto no notebook, com tolerância de 0,15 p.p.
  (o resíduo máximo medido é 0,1125 p.p. em 2019-02, efeito do arredondamento de 1 casa).
- **Verificação independente:** a mesma limitação da desocupação; a divulgação de
  30/10/2026 traz `62,2%` e o Dadobruto (out/2026,
  `https://dadobruto.com/analises/mercado-de-trabalho`) também cita `62,2%` para
  jul–set/2026, igual ao ponto `2026-09`.

## pnad-nivel-ocupacao

- **Definição:** percentual das pessoas de 14 anos ou mais que estavam ocupadas no trimestre
  móvel encerrado no mês. `percentual` (`%`, 1 casa), `eixo: percentual`, `medida: nivel`,
  `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6379**, variável **4097**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6379/n1/all/v/4097/p/all?formato=json`.
- **Fórmula:** nenhuma — série oficial. Cobertura e recorte iguais aos da desocupação.
- **Evidência:** 175 pontos, `2012-03` a `2026-09`; primeiro `57,3%`; último `59,0%`;
  mínimo `48,4%` (jun–ago/2020); máximo `59,0%` (out–dez/2025 e jul–ago–set/2026).
- **Relação com as outras duas:** é o produto da participação pela fração de ocupados na
  força de trabalho. A identidade é a mesma conferida no notebook; ela não substitui a
  leitura das três séries, porque cada uma isola uma margem diferente.
- **Verificação independente:** a mesma limitação da desocupação; a divulgação de
  30/10/2026 traz `59,0%` e o Dadobruto (out/2026,
  `https://dadobruto.com/analises/mercado-de-trabalho`) cita `59,0%` em nov/2025 e `58,9%`
  em jun–ago/2026, iguais aos pontos `2025-11` e `2026-08`.

## pnad-rendimento-real

- **Definição:** rendimento médio mensal real das pessoas de 14 anos ou mais ocupadas na
  semana de referência com rendimento de trabalho, **habitualmente recebido em todos os
  trabalhos**, no trimestre móvel encerrado no mês. `moeda` (`R$`, 0 casas), `eixo: reais`,
  `medida: nivel`, `granularidade: mensal`.
- **Fonte e código:** IBGE, PNAD Contínua mensal, tabela SIDRA **6390**, variável **5933**,
  Brasil (N1). Endpoint:
  `https://apisidra.ibge.gov.br/values/t/6390/n1/all/v/5933/p/all?formato=json`.
- **Fórmula:** nenhuma — a série já vem deflacionada pelo IBGE (INPC): o valor está em reais
  de poder de compra, não em reais correntes. O notebook só busca, recorta o último trimestre
  fechado e formata. Não é a
  série efetivamente recebida (tabela 6387): a habitual é a manchete da divulgação mensal e
  é a que as publicações externas citam.
- **Evidência:** 175 pontos, `2012-03` a `2026-09`; primeiro `3.179`; último `3.790`; mínimo
  `3.074` (out–nov–dez/2021); máximo `3.811` (jan–fev–mar/2026). No último trimestre,
  `3.790` está abaixo do pico de 2026-03, e o piso da série é a pandemia.
- **Verificação independente:** a Folha de S.Paulo de 30/10/2026 cita "renda média do
  trabalho em R$ 3.790 por mês no trimestre até setembro"
  (`https://www1.folha.uol.com.br/mercado/2026/10/desemprego-fica-em-52-e-tem-menor-taxa-ate-setembro-na-serie-historica.shtml`);
  o UOL
  (`https://economia.uol.com.br/noticias/estadao-conteudo/2026/10/30/taxa-de-desemprego-no-brasil-cai-para-52-no-trimestre-ate-setembro-mostra-ibge.htm`)
  e O Globo citam o mesmo `R$ 3.790` para jul–ago–set/2026, igual ao ponto `2026-09`. As
  três citam o IBGE; não há segunda medição.
- **Caveats:** é rendimento do trabalho das pessoas ocupadas **com rendimento**, não renda
  domiciliar per capita; é habitual, não efetivamente recebido; é média (não mediana) e não
  tem recorte regional nem ajuste sazonal; o trimestre móvel é lido como mês de encerramento.

## Pendentes

Revisão concluída para as 13 séries em 2026-11-01. **Não há pendência de dado nem de forma.**
As quatro séries da PNAD (`pnad-*`) têm seção própria acima — três publicadas em 2026-11-03 e
o rendimento em 2026-11-04 —, assim como as duas de PIB per capita; elas não fazem parte da
contagem das 13.

Fora deste repo, o post do `sitio` sobre o MVG-R foi alinhado ao catálogo em 2026-11-03: não
fala mais em "valor médio", "preço de etiqueta" nem "valor real dos imóveis", e os números do
texto passaram a ser os do deflator da janela (R$ 290.000 nominal e R$ 85.662,08 real).

As decisões de apresentação que estavam abertas foram fechadas no catálogo deste repo
(`indicadores/catalogo.json`), que o app do `sitio` lê em runtime:

- `mvgr-real` chama-se "MVG-R deflacionado pelo IPCA (R$ de mar/2004)" e a descrição diz
  que são reais constantes de março de 2004 — o número não é preço de hoje; `mvgr-nominal` é
  "MVG-R — valor mediano de garantia (R$ correntes)", não preço de mercado;
- `populacao-*` diz que é projeção de 2024 do IBGE, população conciliada ao Censo 2022, com
  referência em 1º de julho;
- o carimbo `AAAA-01-01` nas séries anuais é convenção de C9 (início do período) e foi mantido.

Três **condições de revisão** ficam registradas — não são pendências, são gatilhos:

- **Homicídios:** o denominador de 2022–2023 é interpolação do IPEA, com erro limitado a 0,9%
  (ver o bloco de `homicidios-anual`). Refazer quando IPEA/IBGE publicarem população consolidada
  para esses anos.
- **Homicídios por armas de fogo:** 2014–2024 vêm do Atlas 2026 em PDF e 1995–2013 vêm da série
  31 (safra antiga). Quando o Ipea publicar a safra 2026 na API (série 31 com 2024), remover o
  complemento do notebook e conferir o bloco 2014–2024 contra a API. A Tabela 11.1 de 2025 já
  traz 2013 = 40.870, mas **não** é aplicada sozinha: trocar só esse ano criaria uma ilha de
  safra entre 1995–2012 (API antiga) e 2014–2024 (Atlas 2026), sem saber o tamanho da revisão
  de 2012. A emenda 2013/2014 fica em +7,50% (40.369 → 43.397) até a API publicar a safra
  revisada, quando o bloco 1995–2013 inteiro é trocado de uma vez. O gatilho é a API deixar de
  devolver 2023 = 30.789 ou passar a devolver 2024.
- **Séries anuais:** se o instante da medida (1º de julho, no caso da população) passar a
  importar mais que o alinhamento entre séries anuais, muda-se C9 para as seis séries anuais no
  mesmo commit — não série a série.
