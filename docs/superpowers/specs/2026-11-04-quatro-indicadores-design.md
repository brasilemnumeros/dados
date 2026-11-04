# Quatro indicadores complementares — design

- **Data:** 2026-11-04
- **Estado:** proposto (aguardando aval)
- **Escopo:** quatro séries novas — dívida líquida, renda domiciliar per capita, desmatamento e câmbio — com as famílias, catálogo, workflows e metodologia correspondentes.
- **Fora de escopo:** mudar valor de série existente, mudar o contrato (`C1…C15`), criar o eixo `taxa`, publicar a estimativa de desmatamento de 2026, emendar PNAD antiga, calcular câmbio real efetivo.

## Intenção

O catálogo tem 19 séries em 7 grupos, com quatro grupos econômicos (monetário, inflação,
crescimento, trabalho), um imobiliário, e o social reduzido a demografia e segurança pública.
Faltam três perguntas que o cidadão faz de um governo: **para onde vai o dinheiro público**,
**como vive a população** e **o que acontece com o meio ambiente**. O câmbio fecha o triângulo
macroeconômico com a Selic e a inflação.

A régua usada: responder a uma pergunta que o site ainda não responde, ter série oficial longa,
não repetir grupo existente e caber no contrato atual (`percentual`, `reais`, `contagem`,
`por-100-mil`).

## O que entra

| # | Série | Grupo | Família | Fonte | Cobertura | Unidade / eixo / medida | Granularidade |
|---|---|---|---|---|---|---|---|
| 1 | `divida-liquida-pib` | `fiscal` (novo) | `fiscal` (nova) | BCB SGS **4513** | dez/2001–set/2026 | `percentual` / `percentual` / `nivel` | mensal |
| 2 | `pnad-renda-domiciliar-per-capita-real` | `trabalho` | `pnad` (existente) | IBGE PNAD Contínua, SIDRA **7533**, variável **10816** | 2012–2025 | `moeda` / `reais` / `nivel` | anual |
| 3 | `desmatamento-amazonia-legal-anual` | `meio-ambiente` (novo) | `meio-ambiente` (nova) | INPE/PRODES via TerraBrasilis, taxa consolidada | 1988–2025 | `numero` / `contagem` / `nivel` | anual |
| 4 | `cambio-media-mensal` | `monetario` | `cambio` (nova) | BCB SGS **3698** (PTAX venda, média mensal) | jan/1995–out/2026 | `moeda` / `reais` / `nivel` | mensal |

## Decisões de produto (confirmar)

### 1. Dívida líquida: SGS 4513, de dez/2001

**Recomendação:** publicar a série do SGS, de **dez/2001** a **set/2026** (298 pontos, sem
lacuna). É a série oficial do BCB, mensal, machine-readable, atualizada pelo mesmo tipo de
pipeline das outras famílias. O pico de 2002 já está na janela.

**Alternativa rejeitada:** emendar com o IPEADATA `PAN12_DTSPY12`, que começa em 1991. Nos 298
meses comuns as duas séries são idênticas (3 diferenças de 0,01 por arredondamento), mas o
trecho 1991–2001 troca de canal e de safra metodológica. O ganho é o pré-Real; o custo é uma
emenda que precisa ser conferida em toda execução. O catálogo já tem séries que começam depois
de 1995 por limite de fonte (`selic-meta` 1999, `populacao` 2000, `pnad` 2012).

**O que o número é:** estoque da dívida líquida do setor público consolidado no fim do mês,
descontados os ativos financeiros (inclusive reservas), em % do PIB acumulado em 12 meses.
Não é a dívida bruta (DBGG), que é maior porque não desconta ativos. Meses recentes são
preliminares; o histórico muda quando o IBGE revisa o PIB.

**Metadados:** `unidade: {tipo: percentual, simbolo: "%", casas: 1}`, `eixo: percentual`,
`medida: nivel` (é uma razão, não um total — `estoque` no app significa "total no período"),
`granularidade: mensal`, `fonte: "Banco Central do Brasil — Estatísticas Fiscais (SGS 4513)"`,
`urlFonte: "https://api.bcb.gov.br/dados/serie/bcdata.sgs.4513/dados?formato=json"`.

### 2. Renda domiciliar: PNAD Contínua 2012–2025, já real

**Recomendação:** publicar a série oficial da **SIDRA 7533, variável 10816**, anual,
**2012–2025** (14 pontos). O valor já é **real**, deflacionado pelo IPCA a preços médios do
último ano da série; a cada divulgação o IBGE reexpressa a série inteira na nova base. O
notebook gera o `fonte` com o ano-base vigente, e a `descricao` do catálogo **não** fixa o ano.

**Alternativa rejeitada:** emendar a PNAD antiga (1995–2015) com a PNAD Contínua. São
questionários e conceitos de renda diferentes; a skill manda começar depois a emendar sem
declarar a quebra. A série Contínua já é a mesma família dos outros quatro `pnad-*`.

**O que o número é:** média, por morador, do rendimento mensal do domicílio — rendimento
habitual do trabalho das pessoas de 14+ anos mais outras fontes — dividido pelo total de
moradores, média dos quatro trimestres do ano, em reais constantes. Não é o rendimento
individual de quem trabalha (`pnad-rendimento-real`), nem o número nominal do FPE/TCU que a
imprensa publica em fevereiro.

**Metadados:** `unidade: {tipo: moeda, simbolo: "R$", casas: 0}`, `eixo: reais`,
`medida: nivel`, `granularidade: anual`,
`fonte: "IBGE (PNAD Contínua — Rendimento de todas as fontes, SIDRA 7533, variável 10816; a preços médios de <ano>)"`,
`urlFonte: "https://apisidra.ibge.gov.br/values/t/7533/n1/all/v/10816/p/all/c1019/49243?formato=json"`.

**Armadilha:** a tabela **7395** (variável 4196) tem nome parecido, é do módulo TIC, começa em
2016, não tem 2020 e dá valores ~1% diferentes. A metodologia deve dizer que ela foi
descartada.

### 3. Desmatamento: Amazônia Legal, 1988–2025, taxa consolidada

**Recomendação:** publicar a taxa **consolidada** do PRODES para a **Amazônia Legal**,
**1988–2025** (38 pontos), em km², soma dos 9 estados calculada pelo site. A série nacional
não existe: os biomas têm inícios e métodos diferentes (Amazônia 1988, Cerrado 2001, três
biomas só em 2024). Publicar “Brasil” produziria 2–3 pontos ou uma emenda invisível.

**O que o número é:** área de vegetação nativa suprimida por corte raso na Amazônia Legal no
**ano Prodes** (1º de agosto a 31 de julho), em km². É fluxo anual, não estoque acumulado. Não
é ano-calendário, não é o Brasil inteiro, não é o DETER (alertas mensais) e não é queimada.

**Corte de segurança:** o arquivo da fonte (`rates<ano>.json`) mistura a estimativa do ano
corrente com as taxas consolidadas, sem marcador. O notebook corta em **ano civil corrente − 1**
e o workflow roda em **abril e outubro**; a estimativa de 2026 (3.335 km²) não entra. O nome do
arquivo gira todo ano (`rates2025.json` já dá 404); o notebook resolve o nome pelo bundle do
TerraBrasilis, com fallback para `rates<ano>.json` e `rates<ano−1>.json`.

**Metadados:** `unidade: {tipo: numero, simbolo: "km²", casas: 0}`, `eixo: contagem`,
`medida: nivel`, `granularidade: anual`,
`fonte: "INPE — PRODES/BiomasBR (TerraBrasilis), taxa consolidada da Amazônia Legal, soma dos 9 estados calculada pelo site"`,
`urlFonte: "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates"`.

**Licença:** CC BY-SA 4.0; atribuição ao INPE/TerraBrasilis na metodologia.

### 4. Câmbio: PTAX venda, média mensal, 1995–2026

**Recomendação:** SGS **3698** — PTAX venda, **média aritmética das cotações diárias** do mês,
**jan/1995–out/2026** (382 pontos, sem lacuna). É série oficial já agregada (hierarquia 1 da
skill), sem cálculo próprio, e a média representa o mês; o fechamento é um único dia e chega a
ficar 32% acima da média em jan/1999.

**Alternativa rejeitada:** SGS 3696 (fim de período). O `id` mudaria para `cambio-fim-mes` e a
leitura seria “o dólar fechou o mês em…”. Fica para outra decisão de produto.

**O que o número é:** taxa de câmbio **nominal** do dólar americano, mercado livre/comercial,
cotação de venda (PTAX), em reais por dólar, média do mês. Não é câmbio real efetivo, não é
competitividade e não é o dólar à vista. A série nominal sobe ~6× em 31 anos; sem esse caveat
na descrição, o gráfico vira afirmação falsa por omissão.

**Metadados:** `unidade: {tipo: moeda, simbolo: "R$/US$", casas: 4}`, `eixo: reais`,
`medida: nivel`, `granularidade: mensal`,
`fonte: "Banco Central do Brasil (SGS 3698 — PTAX venda, média mensal)"`,
`urlFonte: "https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json"`.

**Nota de contrato:** não existe `eixo: taxa`; `reais` é a única combinação legal. O app separa
por amplitude (razão > 50) e avisa, então não há gráfico errado, mas a semântica do eixo fica
frouxa. Um `eixo: taxa` é candidato a uma próxima versão do contrato, não deste PR.

## Grupos, famílias e workflows

| Grupo | Nome proposto | Posição | Séries |
|---|---|---|---|
| `fiscal` | **🏛️ Fiscal** | depois de `crescimento` | dívida líquida |
| `meio-ambiente` | **🌳 Meio Ambiente** | último | desmatamento |

- `cambio` é **família nova** (`indicadores/cambio/`), mas entra no grupo existente
  `monetario`: pôr o câmbio em `selic/` faria o caminho do catálogo mentir, e um grupo
  “Câmbio” de uma série só polui a navegação.
- `pnad` é família existente; a renda entra em **notebook novo** (`RendaDomiciliar.ipynb`),
  porque o `PNAD.ipynb` amarra as quatro séries à cobertura mensal. O caller `atualizar-pnad.yml`
  já roda todos os `.ipynb` da pasta e o cron `0 15 5,28 * *` cobre a divulgação anual de maio.

**Callers novos:**

| Família | Arquivo | Cron (UTC) | Variável de ensaio |
|---|---|---|---|
| `fiscal` | `atualizar-fiscal.yml` | `0 15 4,20 * *` | `FISCAL_SAIDA` |
| `meio-ambiente` | `atualizar-meio-ambiente.yml` | `0 15 15 4,10 * *` | `MEIO_AMBIENTE_SAIDA` |
| `cambio` | `atualizar-cambio.yml` | `0 15 3 * *` | `CAMBIO_SAIDA` |
| `pnad` | já existe | — | `PNAD_SAIDA` |

- Allowlist de `atualizar-familia.yml`: acrescentar `fiscal`, `meio-ambiente` e `cambio` à
  linha do `case`. Sem isso, `tests/test_workflows.py` reprova.
- `AGENTS.md`: três linhas novas na tabela de cadência, as três variáveis na lista e a menção
  às famílias novas.
- `tests/test_workflows.py`: não muda; ele descobre as famílias pelo disco.

## Mapa de fontes e verificação externa

### Dívida líquida (SGS 4513)

- **Produtor:** BCB, Estatísticas Fiscais. **Canal:** SGS. **Cobertura:** 298 pontos,
  dez/2001–set/2026. **Defasagem:** fim do mês seguinte. **Revisão:** sim — estoques e PIB
  corrente de 12 meses; meses recentes preliminares. **Sazonalidade:** nenhuma. **Licença:**
  dados abertos do BCB com atribuição.
- **Verificação:** Agência Brasil (29/10/2026) publica 70% e +0,7 p.p. no mês; a série dá
  69,98% e +0,71 p.p. Poder360 e UOL conferem ago/jul. Divergências antigas são revisão do
  denominador (PIB), não erro de unidade. **Não há segunda medição**; a imprensa cita o BCB.

### Renda domiciliar (SIDRA 7533/10816)

- **Produtor:** IBGE, PNAD Contínua — Rendimento de todas as fontes. **Cobertura:** 2012–2025,
  14 pontos. **Defasagem:** anual, maio do ano seguinte. **Revisão:** reexpressa a série inteira
  a cada edição (nova base de preços + reponderação). **Deflator:** IPCA médio anual.
- **Verificação:** FGV IBRE (15/06/2026), Metrópoles e O Informante publicam R$ 2.264 em 2025
  e as variações; a série confere. O número nominal do FPE/TCU (R$ 2.316, fevereiro) é outro
  produto — universo e preço diferentes; a descrição precisa negar a confusão. **Não há segunda
  medição.**

### Desmatamento (PRODES/TerraBrasilis)

- **Produtor:** INPE, PRODES/BiomasBR. **Cobertura:** 1988–2025, 38 pontos. **Defasagem:**
  estimativa em outubro, consolidada no 1º semestre seguinte. **Revisão:** estimativa →
  consolidada; a série inteira é reescrita, sem changelog. **Licença:** CC BY-SA 4.0.
- **Verificação:** Agência Brasil (16/10/2026), Geocracia (25/08/2026) e PNB Online
  (18/08/2026) publicam 5.731 km² em 2025 e −12,07% sobre 6.518; confere. A imprensa às vezes
  troca a estimativa (5.796) pela consolidada; a descrição precisa separar. **Não há segunda
  medição** — o MapBiomas Alerta é outro método e o próprio relatório declara incomparabilidade.

### Câmbio (SGS 3698)

- **Produtor:** BCB. **Cobertura:** 382 meses, jan/1995–out/2026. **Defasagem:** depois do
  fechamento do mês. **Revisão:** sem revisão sistemática. **Licença:** ODbL, atribuição ao BCB.
- **Verificação:** FAESP/SENAR-SP (out/2026) publica R$ 5,14 em setembro e R$ 5,15 em agosto;
  a série dá 5,1447 e 5,1532. ValorFinal, MeusRepresentantes e O Cafezinho conferem níveis e
  fechamentos. O Apurômetro publica 5,09 porque mediu outubro até 27/10 (mês aberto) — é o erro
  que o corte de período fechado impede. **Não há segunda medição.**

## Implementação

### Fase A — pesquisa (concluída)

Quatro subagentes em paralelo, um por indicador, produziram brief, mapa de fontes e verificação
externa. Nada foi escrito em disco.

### Fase B — quatro pipelines em paralelo

Cada subagente trabalha em **arquivos exclusivos da sua família** e **não toca** em
`catalogo.json`, `metodologia.md`, `AGENTS.md`, allowlist ou workflows. Entrega notebook + JSON
gerado + texto da seção de metodologia e da entrada de catálogo.

| Pipeline | Arquivos exclusivos |
|---|---|
| Fiscal | `indicadores/fiscal/Divida-Liquida.ipynb`, `indicadores/fiscal/divida-liquida-pib.json` |
| PNAD | `indicadores/pnad/RendaDomiciliar.ipynb`, `indicadores/pnad/pnad-renda-domiciliar-per-capita-real.json` |
| Meio Ambiente | `indicadores/meio-ambiente/Desmatamento.ipynb`, `indicadores/meio-ambiente/desmatamento-amazonia-legal-anual.json` |
| Câmbio | `indicadores/cambio/Cambio.ipynb`, `indicadores/cambio/cambio-media-mensal.json` |

Cada notebook segue o padrão da skill: selo do Colab na primeira célula, `relativo()`, coleta
com retry, corte de período fechado, escrita do JSON inteiro e validação inline. Nenhum caminho
absoluto da máquina.

### Fase C — integração serial (eu)

1. Inserir as quatro entradas no `catalogo.json`, sem reordenar as existentes; criar os grupos
   `fiscal` e `meio-ambiente` na posição decidida.
2. Acrescentar as quatro seções em `docs/metodologia.md`, com fonte, fórmula, cobertura,
   caveats e o parágrafo “Verificação independente”.
3. Criar os três callers, a linha da allowlist, as linhas do `AGENTS.md` e as variáveis.
4. Rodar `scripts/validar.py`, `pytest -q`, o parse de todos os JSONs e `git diff --check`.
5. Rodar cada notebook duas vezes em ensaio (`<FAMILIA>_SAIDA`), comparar os JSONs e conferir
   primeiro/último ponto, lacunas, ordem e C15.
6. Revisar o diff numérico e abrir **um PR** com os quatro indicadores — o par série + catálogo
   no mesmo PR é o que K1/K2 exigem.

## Não-objetivos

- Não alterar valores de séries existentes.
- Não mudar o contrato nem o validador.
- Não publicar a estimativa de desmatamento de 2026.
- Não emendar PNAD antiga (1995–2015) nem IPEADATA (1991–2001).
- Não calcular câmbio real efetivo nem deflacionar a renda por conta própria.
- Não criar grupo “Câmbio” nem mover `cambio` para `selic/`.

## Anti-objetivos

- Gráfico de dívida tratado como “qualidade de gestão” ou como dívida bruta.
- Renda confundida com o rendimento individual ou com o número nominal do FPE.
- Desmatamento lido como Brasil inteiro, ano-calendário ou DETER.
- Câmbio nominal lido como competitividade ou como dólar à vista.
- Série com lacuna preenchida com zero, interpolação ou estimativa não consolidada.

## Riscos

- **Dívida:** revisão do PIB muda o histórico e abre PR; a metodologia precisa dizer que é
  revisão da fonte, não erro de fórmula.
- **Renda:** a re-base anual reescreve os 14 pontos; a `descricao` não pode fixar o ano-base.
- **Desmatamento:** o arquivo da fonte gira e mistura estimativa com consolidado; o corte e o
  cron precisam andar juntos.
- **Câmbio:** `eixo: reais` declara comparabilidade frouxa com MVG-R/PIB per capita; o app
  separa por amplitude, mas a semântica fica para uma futura versão do contrato.
- **Famílias novas:** sem caller/allowlist, a série existe e nunca atualiza; o teste cobre o
  caller, não a documentação.
- **Um PR grande:** quatro séries + catálogo + metodologia + workflows. O diff numérico precisa
  ser revisado com atenção; o CI é o mesmo gate.

## Decisões pendentes

1. Confirma **dívida 4513 (2001+)** em vez de IPEADATA (1991+)?
2. Confirma **renda 2012+** em vez de emendar a PNAD antiga?
3. Confirma **desmatamento da Amazônia Legal** em vez de “Brasil”?
4. Confirma **câmbio média mensal** em vez de fim de mês?
5. Confirma os nomes/posições **🏛️ Fiscal** (depois de Crescimento) e **🌳 Meio Ambiente**
   (último)?

Com o aval, a Fase B começa.
