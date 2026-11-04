# Quatro indicadores complementares — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** publicar quatro séries novas — dívida líquida, renda domiciliar per capita, desmatamento da Amazônia Legal e câmbio — com notebook, JSON, catálogo, metodologia e atualização agendada.

**Architecture:** um notebook por família (ou um notebook novo na família `pnad`) gera o JSON inteiro a cada execução; o catálogo descreve a apresentação; o workflow reutilizável roda todos os `.ipynb` da família. Quatro pipelines independentes em paralelo; a integração de catálogo, metodologia, `AGENTS.md` e workflows é serial; revisão por subagente independente em cada pipeline e uma revisão final do PR inteiro.

**Tech Stack:** Python 3.12, pandas, requests, nbconvert; Jupyter/Colab; GitHub Actions; `uv`.

**Spec:** `docs/superpowers/specs/2026-11-04-quatro-indicadores-design.md`

## Global Constraints

- Contrato `../sitio/docs/contrato-de-indicadores.md` (`C1…C15`); catálogo `K1…K9`.
- Cada ponto tem exatamente `{"data": "YYYY-MM-DD", "valor": número finito}`.
- Datas ascendentes, um ponto por período; C15: mensal `AAAA-MM-01`, anual `AAAA-01-01`.
- Lacuna é ausência de ponto; nunca `null`, zero ou interpolação.
- Notebook: primeira célula é o selo Open in Colab; nenhum caminho absoluto da máquina (`/Users/`, `/home/`, `/root/`, `C:\`, `file://`) em célula ou saída.
- Notebook público: use `relativo()` em todo print de caminho; `DADOS_RAIZ` e `<FAMILIA>_SAIDA` para ensaio.
- O notebook busca a fonte e recalcula a série inteira; não lê o JSON publicado.
- Não alterar valores de séries existentes; não tocar em `cases` fora do escopo.
- Não mexer no contrato nem no validador.
- Não publicar a estimativa de desmatamento de 2026.
- Um PR único com série + catálogo no mesmo PR (K1/K2).
- Commits em português, Conventional Commits com escopo `dados`.

## Review Focus

- Fonte errada ou agregador chamado de produtor: o número pode estar certo e a atribuição errada.
- Data de publicação usada como data de referência (C15).
- Período aberto publicado (mês/ano corrente incompleto).
- Unidade/eixo/medida/granularidade que não descrevem o número.
- `descricao` do catálogo divergindo da metodologia ou do `fonte` gerado.
- Caminho absoluto da máquina no notebook ou na saída.
- `urlNotebook` apontando para notebook que não gera a série.
- Diff numérico acidental em série existente.
- Rebase/revisão da fonte confundida com erro de fórmula.

---

### Task 1: Dívida líquida do setor público (% do PIB)

**Files:**
- Create: `indicadores/fiscal/Divida-Liquida.ipynb`
- Create: `indicadores/fiscal/divida-liquida-pib.json`

**Interfaces:**
- Consumes: BCB SGS 4513, `https://api.bcb.gov.br/dados/serie/bcdata.sgs.4513/dados?formato=json`.
- Produces: série `divida-liquida-pib`, mensal, dez/2001–último mês fechado.

- [ ] **Step 1: Criar o notebook** com as células obrigatórias da skill: selo do Colab em `indicadores/fiscal/Divida-Liquida.ipynb`; markdown de abertura com fonte, código, definição, cobertura e arquivo gerado; setup com `RAIZ`, `PASTA`, `DESTINO = FISCAL_SAIDA` e `relativo()`; coleta com retry; corte do mês corrente; escrita; validação inline.
- [ ] **Step 2: Metadados exatos** — `unidade: {tipo: "percentual", simbolo: "%", casas: 1}`, `eixo: "percentual"`, `medida: "nivel"`, `granularidade: "mensal"`, `fonte: "Banco Central do Brasil — Estatísticas Fiscais (SGS 4513)"`, `urlFonte` do endpoint.
- [ ] **Step 3: Rodar em ensaio duas vezes** com `DADOS_RAIZ="$PWD" FISCAL_SAIDA=<tmp>`; comparar os dois JSONs byte a byte; conferir primeiro ponto (2001-12 = 51.49), último fechado (2026-09 = 69.98 na data de hoje), contagem (298), ordem e C15.
- [ ] **Step 4: Gerar o JSON publicado** na pasta `indicadores/fiscal/`; sem caminho absoluto na saída.
- [ ] **Step 5: Entregar relatório** com status, arquivos, comandos/resultados, contagem, primeiro/último ponto e a proposta de entrada de catálogo + seção de metodologia (não editar os arquivos compartilhados).

### Task 2: Renda domiciliar per capita real (PNAD Contínua)

**Files:**
- Create: `indicadores/pnad/RendaDomiciliar.ipynb`
- Create: `indicadores/pnad/pnad-renda-domiciliar-per-capita-real.json`

**Interfaces:**
- Consumes: IBGE SIDRA 7533, variável 10816, `c1019/49243`, `https://apisidra.ibge.gov.br/values/t/7533/n1/all/v/10816/p/all/c1019/49243?formato=json`.
- Produces: série anual 2012–2025.

- [ ] **Step 1: Criar o notebook** com as células obrigatórias; `DESTINO = PNAD_SAIDA`; `DADOS_RAIZ` aponta para `indicadores/pnad`; não alterar `PNAD.ipynb` nem os quatro JSONs existentes.
- [ ] **Step 2: Metadados exatos** — `unidade: {tipo: "moeda", simbolo: "R$", casas: 0}`, `eixo: "reais"`, `medida: "nivel"`, `granularidade: "anual"`; `fonte` gerado com o ano-base vigente (ex.: “... a preços médios de 2025”); `urlFonte` acima.
- [ ] **Step 3: Rodar em ensaio duas vezes** com `DADOS_RAIZ="$PWD" PNAD_SAIDA=<tmp>`; comparar; conferir 14 pontos (2012–2025), 2020 = 1820, 2021 = 1692, 2025 = 2264, ordem e C15 (`AAAA-01-01`).
- [ ] **Step 4: Gerar o JSON publicado** em `indicadores/pnad/`; sem caminho absoluto.
- [ ] **Step 5: Entregar relatório** com status, evidências, proposta de catálogo + metodologia (incluindo o aviso sobre a tabela 7395 e o número nominal do FPE/TCU).

### Task 3: Desmatamento da Amazônia Legal (km²)

**Files:**
- Create: `indicadores/meio-ambiente/Desmatamento.ipynb`
- Create: `indicadores/meio-ambiente/desmatamento-amazonia-legal-anual.json`

**Interfaces:**
- Consumes: INPE/PRODES via TerraBrasilis; arquivo `rates<ano>.json` rotativo, resolvido pelo bundle/página; soma dos 9 estados por período.
- Produces: série anual 1988–2025, taxa consolidada.

- [ ] **Step 1: Criar o notebook** com as células obrigatórias; `DESTINO = MEIO_AMBIENTE_SAIDA`; resolver o nome do arquivo (bundle → fallback `rates<ano>.json` → `rates<ano−1>.json`); retry; cortar em `ano civil corrente − 1`; nunca publicar 2026.
- [ ] **Step 2: Metadados exatos** — `unidade: {tipo: "numero", simbolo: "km²", casas: 0}`, `eixo: "contagem"`, `medida: "nivel"`, `granularidade: "anual"`, `fonte: "INPE — PRODES/BiomasBR (TerraBrasilis), taxa consolidada da Amazônia Legal, soma dos 9 estados calculada pelo site"`, `urlFonte: "https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates"`.
- [ ] **Step 3: Rodar em ensaio duas vezes** com `DADOS_RAIZ="$PWD" MEIO_AMBIENTE_SAIDA=<tmp>`; comparar; conferir 38 pontos, 1988 = 21050, 2004 = 27772, 2012 = 4571, 2024 = 6518, 2025 = 5731, ausência de 2026, 1993 = 1994 = 14896.
- [ ] **Step 4: Gerar o JSON publicado** em `indicadores/meio-ambiente/`; sem caminho absoluto.
- [ ] **Step 5: Entregar relatório** com status, evidências, proposta de catálogo + metodologia (Amazônia Legal, ano Prodes, estimativa × consolidado, licença CC BY-SA 4.0).

### Task 4: Câmbio (R$/US$) — média mensal

**Files:**
- Create: `indicadores/cambio/Cambio.ipynb`
- Create: `indicadores/cambio/cambio-media-mensal.json`

**Interfaces:**
- Consumes: BCB SGS 3698, `https://api.bcb.gov.br/dados/serie/bcdata.sgs.3698/dados?formato=json`.
- Produces: série mensal jan/1995–out/2026.

- [ ] **Step 1: Criar o notebook** com as células obrigatórias; `DESTINO = CAMBIO_SAIDA`; retry; cortar o mês corrente; C15.
- [ ] **Step 2: Metadados exatos** — `unidade: {tipo: "moeda", simbolo: "R$/US$", casas: 4}`, `eixo: "reais"`, `medida: "nivel"`, `granularidade: "mensal"`, `fonte: "Banco Central do Brasil (SGS 3698 — PTAX venda, média mensal)"`, `urlFonte` do endpoint.
- [ ] **Step 3: Rodar em ensaio duas vezes** com `DADOS_RAIZ="$PWD" CAMBIO_SAIDA=<tmp>`; comparar; conferir 382 pontos, primeiro 1995-01 = 0.8471, último 2026-10 = 5.1294 na data de hoje, ordem e C15.
- [ ] **Step 4: Gerar o JSON publicado** em `indicadores/cambio/`; sem caminho absoluto.
- [ ] **Step 5: Entregar relatório** com status, evidências, proposta de catálogo + metodologia (nominal, média mensal, PTAX venda, não é câmbio real efetivo).

### Task 5: Integração dos arquivos compartilhados

**Files:**
- Modify: `indicadores/catalogo.json`
- Modify: `docs/metodologia.md`
- Modify: `AGENTS.md`
- Modify: `.github/workflows/atualizar-familia.yml`
- Create: `.github/workflows/atualizar-fiscal.yml`
- Create: `.github/workflows/atualizar-meio-ambiente.yml`
- Create: `.github/workflows/atualizar-cambio.yml`

- [ ] **Step 1: Catálogo** — inserir as quatro entradas sem reordenar as existentes; criar `fiscal` (depois de `crescimento`) e `meio-ambiente` (último) em `grupos`; `escala` = `unidade.tipo`; `urlNotebook` para o notebook que gera cada série.
- [ ] **Step 2: Metodologia** — quatro seções com definição, fonte/código, fórmula, evidência, veredito, impacto, caveats e o parágrafo “Verificação independente” de cada uma.
- [ ] **Step 3: AGENTS.md** — três linhas na tabela de cadência (`fiscal`, `meio-ambiente`, `cambio`), as três variáveis de ensaio e a menção às famílias novas; manter a tabela em ordem de fonte.
- [ ] **Step 4: Workflows** — três callers copiados do padrão `atualizar-selic.yml`; allowlist com `fiscal|meio-ambiente|cambio`.
- [ ] **Step 5: Commitar** os quatro pipelines + integração em um commit (ou commits por família + um de integração), sem push.

### Task 6: Gate final e revisão do PR

- [ ] **Step 1: Validar** `uv run --frozen --group ci python scripts/validar.py`.
- [ ] **Step 2: Testar** `uv run --frozen --group ci pytest -q`.
- [ ] **Step 3: Parse** `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"`.
- [ ] **Step 4: Diff** `git diff --check` e revisão do diff numérico; confirmar que séries existentes não mudaram.
- [ ] **Step 5: Revisão final** — subagente fresco com o diff completo, o design e o contrato; corrigir Critical/Important e re-revisar o diff de correção.
- [ ] **Step 6: PR** — abrir o PR com o resumo, as fontes e as verificações; o CI é o gate.

### Task 7: Atualizar a skill `adicionando-indicador` (depois do PR de dados)

**Files:**
- Modify: `.agents/skills/adicionando-indicador/SKILL.md`
- Create: `.agents/skills/adicionando-indicador/references/revisor.md`

- [ ] **Step 1: Baseline** — registrar o que o revisor efetivamente pegou neste lote que o CI não pegou.
- [ ] **Step 2: Adicionar o `Gate de revisão`** depois do `Gate de verificação`, com papéis, pacote de revisão, veredito e loop de correção.
- [ ] **Step 3: Adicionar `references/revisor.md`** com o prompt e o checklist (contrato, catálogo, fonte, cobertura, C15, caminho absoluto, determinismo, amostra contra a fonte).
- [ ] **Step 4: Atualizar `Fluxo`, `Erros comuns` e a tabela de racionalizações** com o gate.
- [ ] **Step 5: Testar** com um cenário de pressão (implementador sem revisor × com revisor) e registrar o resultado no PR da skill.
