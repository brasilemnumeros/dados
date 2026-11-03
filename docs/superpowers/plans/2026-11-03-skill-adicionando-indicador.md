# Skill adicionando-indicador Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Criar a skill `.agents/skills/adicionando-indicador/` que conduz um agente a criar um indicador novo com definição, fonte, verificação independente, atribuição correta, JSON no contrato (C1…C15), catálogo e workflow recorrente.

**Architecture:** A skill é um `SKILL.md` com três gates (definição, fonte, verificação), apoiado por quatro referências operacionais e um asset de caller de workflow. O contrato continua no repo `sitio`; o validador continua sendo a prova executável. A skill é validada por cenários com subagentes: baseline sem skill, aplicação com skill e um teste de mecânica sem rede.

**Tech Stack:** Agent Skills (Markdown), Python 3.12, `scripts/validar.py`, `pytest`, GitHub Actions YAML, subagentes para teste de comportamento.

**Spec:** `docs/superpowers/specs/2026-11-02-skill-adicionando-indicador-design.md`

> **Execução (2026-11-03):** tarefas 1–6 executadas no worktree `dados-skill`; o PR não foi aberto — integração pendente. O commit de C15 inclui o alinhamento de vocabulário em `docs/metodologia.md` (`percentage`→`percentual`, `monthly`→`mensal`), parte da mesma revisão de contrato.

## Base e pré-requisitos

- **Não implementar no `main` local divergente.** O `main` local está 4 commits à frente e 9 atrás de `origin/main`; os 4 commits locais são de dado (Selic, homicídios, MVG-R) e não entram no branch da skill. Criar um worktree/branch a partir de `origin/main` (usar `superpowers:using-git-worktrees` no momento da execução).
- **C15 é pré-requisito.** As mudanças de C15 estão no working tree dos dois repos. Elas precisam ser commitadas e mescladas antes do teste da skill: contrato/validador em `sitio`, contrato/validador/corpus em `dados`. O worktree da skill deve partir de uma base que já tenha C15.
- **Não misturar trabalho alheio.** O working tree de `sitio` também tem mudanças não relacionadas (`app/src/chart/adapter.js`, `app/src/domain/marcadores.js`); não incluí-las no commit de C15.
- **Skill isolada.** A skill, suas referências e o asset são a única entrega deste plano. Nenhum valor de `indicadores/` muda.

## Global Constraints

- Skill em `.agents/skills/adicionando-indicador/`; ID `adicionando-indicador`; `SKILL.md` com frontmatter `name: Adicionando indicador` e `description` em português começando por “Use quando…”.
- A `description` diz **quando** usar, não resume o fluxo.
- Contrato `C1…C15` e catálogo `K1…K8`; fonte de verdade `../sitio/docs/contrato-de-indicadores.md`. Não copiar o contrato inteiro.
- C15: mensal `AAAA-MM-01`, anual `AAAA-01-01`, diária com a data real.
- Atribuição: `fonte` é a linha legível da ficha; `urlFonte` é a URL exata do recorte; todas as URLs/códigos vão para `docs/metodologia.md`; produtor ≠ agregador; cálculo próprio é declarado.
- Workflow: um caller por família; a família entra na allowlist do `atualizar-familia.yml`; não reescrever o reutilizável; se ele não existir no checkout, sincronizar a branch.
- Cadência divergente da família: parar e perguntar; não mudar o cron da família sozinha.
- Testes com subagentes: **o teste de mecânica não usa rede**; os cenários de baseline e GREEN
  podem pesquisar a fonte. Nenhum teste altera `indicadores/`.
- Commits em Conventional Commits, em português, escopo `dados` (`docs(dados): ...`).
- Nenhum arquivo de `scripts/`, `tests/` ou `indicadores/` é alterado por este plano; C15 já é um commit anterior.

## Review Focus

- **Agente pula o gate de definição** e começa pelo notebook/JSON sem saber o que o número mede, o período, nominal/real, per capita, sazonalidade ou caveat.
- **Agente atribui ao agregador** (BCB SGS) como se fosse o produtor (IBGE/FGV/Ipea) ou omite a segunda fonte de uma emenda.
- **Agente usa a mesma fonte como verificação independente** ou declara “conferido” sem comparar com terceiro.
- **Agente cria família nova sem allowlist** ou ignora cadência incompatível com o caller existente.
- **Agente grava data fora de C15** (mensal no dia 15, anual em fevereiro) ou escreve JSON à mão em vez de gerar pelo notebook.

---

### Task 1: Baseline sem skill (RED)

**Files:**
- Nenhum arquivo do repo. Evidência em `/tmp/skill-adicionando-indicador/`.

**Interfaces:**
- Produces: transcrição do baseline e lista de falhas verbatim, usada para escrever o `SKILL.md`.

- [x] **Step 1: Criar a pasta de evidência**

```bash
mkdir -p /tmp/skill-adicionando-indicador
```

- [x] **Step 2: Rodar o cenário sem a skill**

Despache um subagente generalista com este prompt, sem mencionar a skill e sem permitir alterações:

```text
Você está no repo `dados` (brasilemnumeros). Quero adicionar ao site a taxa de
desocupação mensal do Brasil, da PNAD Contínua (IBGE), de 2012 até o último
período fechado. Como você faria? Não altere arquivos nem publique nada;
responda com o plano que seguiria, incluindo as decisões de fonte, cobertura,
verificação e atribuição.

Não leia `docs/superpowers/specs/2026-11-02-skill-adicionando-indicador-design.md`
nem `docs/superpowers/plans/2026-11-03-skill-adicionando-indicador.md`: eles
descrevem o comportamento esperado e contaminariam este baseline.
```

- [x] **Step 3: Salvar e avaliar a resposta**

Salve a resposta em `/tmp/skill-adicionando-indicador/baseline.md` e marque cada
critério:

| Critério | O que conta como cumprido |
|---|---|
| Definição | perguntou o que o número mede, unidade, período, nominal/real, per capita, sazonalidade, geografia, estoque/fluxo |
| Leitor/caveat | disse quais perguntas o leitor faria e o que tornaria o indicador enganoso |
| Fonte | comparou produtor e agregador e preferiu série oficial já calculada |
| Horizonte | verificou 2012–último período fechado e tratou emenda/lacuna |
| Verificação | propôs fonte independente, não a mesma usada |
| Atribuição | nomeou todas as fontes e disse o que é cálculo próprio |
| C15/granularidade | escolheu a granularidade mínima e a data correta |

- [x] **Step 4: Registrar as falhas**

Anote, verbatim, as frases em que o agente pulou um gate. Essas frases são o
alvo do `SKILL.md`; não invente falhas que não apareceram. Não há commit nesta
task.

---

### Task 2: Escrever o `SKILL.md`

**Files:**
- Create: `.agents/skills/adicionando-indicador/SKILL.md`

**Interfaces:**
- Produces: skill descoberta pelo ID `adicionando-indicador`, com os três gates e o fluxo de 10 passos.
- Consumes: falhas do baseline; contrato `C1…C15`; design aprovado.

- [x] **Step 1: Criar o frontmatter e a estrutura**

O arquivo começa exatamente com:

```markdown
---
name: Adicionando indicador
description: Use quando for criar ou publicar um indicador novo no repo dados — nova série, novo JSON, entrada no catálogo, notebook de coleta/cálculo ou workflow de atualização.
---
```

O corpo tem, nesta ordem: **Overview**, **Quando usar / quando não usar**,
**Gate de definição**, **Gate de fonte**, **Gate de verificação**, **Fluxo**,
**Tabela de decisão do contrato**, **Catálogo**, **C15**, **Workflow recorrente**,
**Atribuição de fonte(s)**, **Validação**, **Erros comuns / red flags** e
**Referências**.

- [x] **Step 2: Escrever os três gates**

O gate de definição pergunta, no mínimo: o que o número mede; unidade e período
de referência; nominal/real; total/per capita; sazonalidade; geografia; estoque
vs fluxo; as três perguntas do leitor; o que tornaria o indicador enganoso; a
comparação natural; a granularidade mínima; se já existe indicador redundante.

O gate de fonte exige, nesta ordem: série oficial já calculada → componentes
oficiais com fórmula publicada → cálculo próprio documentado e conferido.
Registra produtor vs agregador, código/tabela, endpoint, cobertura até o último
período fechado, frequência, defasagem, revisão, ajuste sazonal, deflator,
estabilidade da API e licença.

O gate de verificação exige fonte independente que já publicou o indicador,
comparação de níveis e variações, divergência quantificada e explicada; se não
houver fonte independente, a limitação é declarada.

- [x] **Step 3: Escrever o fluxo de 10 passos e a tabela de decisão**

O fluxo é o do desenho: definição → fonte → classificação (família existente,
família nova, família sem caller) → notebook → JSON → catálogo → workflow →
metodologia → verificação → PR.

A tabela de decisão fixa:

| `eixo` | `unidade.tipo` |
|---|---|
| `percentual` | `percentual` |
| `reais` | `moeda` |
| `contagem` | `numero` |
| `por-100-mil` | `numero` |

E lista `medida` (`nivel`, `acumulado-12m`, `variacao-anual`, `estoque`,
`participacao`), `granularidade` (`diaria`, `mensal`, `anual`) e C15.

- [x] **Step 4: Escrever workflow, atribuição, validação e erros comuns**

Workflow: família com caller não ganha outro; família sem caller ganha caller +
linha na allowlist + linha no `AGENTS.md`; reutilizável ausente → sincronizar a
branch; cadência divergente → parar e perguntar.

Atribuição: `fonte` legível com todas as fontes/papéis; `urlFonte` principal;
metodologia com todas as URLs; produtor ≠ agregador; cálculo próprio declarado.

Validação: os comandos de `validar.py`, `pytest`, parse de JSON/YAML e
`git diff --check`, mais a execução do notebook em ensaio.

Erros comuns: pular definição, usar agregador como produtor, verificar com a
mesma fonte, criar família sem allowlist, gravar data fora de C15, escrever JSON
à mão.

- [x] **Step 5: Conferir frontmatter e ID**

```bash
python3 - <<'PY'
from pathlib import Path
import re
texto = Path('.agents/skills/adicionando-indicador/SKILL.md').read_text(encoding='utf-8')
assert texto.startswith('---\n')
front, corpo = texto[4:].split('\n---\n', 1)
assert re.search(r'^name: .+$', front, re.M)
assert re.search(r'^description: Use quando .+$', front, re.M)
assert 'Gate de definição' in corpo
assert 'Gate de fonte' in corpo
assert 'Gate de verificação' in corpo
print('skill ok')
PY
```

Expected: `skill ok`.

- [x] **Step 6: Commit**

```bash
git add .agents/skills/adicionando-indicador/SKILL.md
git commit -m "docs(dados): adiciona skill de indicador novo"
```

---

### Task 3: Referências operacionais

**Files:**
- Create: `.agents/skills/adicionando-indicador/references/contrato-resumo.md`
- Create: `.agents/skills/adicionando-indicador/references/notebook-padrao.md`
- Create: `.agents/skills/adicionando-indicador/references/qualidade-e-fontes.md`
- Create: `.agents/skills/adicionando-indicador/references/workflow-recorrente.md`

**Interfaces:**
- Consumes: `SKILL.md` da Task 2.
- Produces: detalhes carregados sob demanda; nenhum arquivo repete o contrato inteiro.

- [x] **Step 1: Escrever `contrato-resumo.md`**

Conteúdo: caminho do arquivo; chaves de topo; `unidade`; tabela `eixo` ↔
`unidade.tipo`; `medida`; `granularidade`; ponto `{data, valor}`; C11, C12, C13,
C15; catálogo `K1…K8`; link para `../sitio/docs/contrato-de-indicadores.md` como
fonte de verdade. Limite: ~120 linhas. Não copiar C1–C15 inteiro.

- [x] **Step 2: Escrever `notebook-padrao.md`**

Conteúdo: células obrigatórias (markdown de fonte/definição/fórmula; raiz
`DADOS_RAIZ`; `<FAMILIA>_SAIDA`; coleta completa; cálculo visível; filtro de
período fechado; escrita do JSON inteiro; validação inline). Apontar
`indicadores/ipca/IPCA.ipynb` como exemplo real. Dizer explicitamente que não há
template para preencher.

- [x] **Step 3: Escrever `qualidade-e-fontes.md`**

Conteúdo: os três gates em detalhe; hierarquia de fontes; produtor vs agregador;
cobertura 1995/last closed; emenda e sobreposição; verificação independente;
armadilhas de API (BCB SGS 10 anos/diária, 502, timeout, 200 com HTML); regras
de atribuição e licença. Este é o arquivo mais longo; pode passar de 120 linhas.

- [x] **Step 4: Escrever `workflow-recorrente.md`**

Conteúdo: anatomía do caller; cron UTC/15:00; `workflow_dispatch` com `seco`;
`permissions: contents: read`; `concurrency`; `uses`; regra de allowlist;
família com/sem caller; cadência divergente; reutilizável ausente → sincronizar;
tabela de cadência do `AGENTS.md`.

- [x] **Step 5: Conferir caminhos e links**

```bash
python3 - <<'PY'
from pathlib import Path
raiz = Path('.agents/skills/adicionando-indicador')
for nome in ['contrato-resumo.md','notebook-padrao.md','qualidade-e-fontes.md','workflow-recorrente.md']:
    assert (raiz/'references'/nome).is_file(), nome
print('references ok')
PY
```

Expected: `references ok`.

- [x] **Step 6: Commit**

```bash
git add .agents/skills/adicionando-indicador/references
git commit -m "docs(dados): adiciona referencias da skill de indicador"
```

---

### Task 4: Asset do caller de workflow

**Files:**
- Create: `.agents/skills/adicionando-indicador/assets/atualizar-familia-caller.yml`

**Interfaces:**
- Consumes: contrato do caller em `origin/main:.github/workflows/atualizar-ipca.yml`.
- Produces: YAML copiável com placeholders `__FAMILIA__` e `__CRON__`.

- [x] **Step 1: Criar o caller com placeholders**

```yaml
# Workflow da família __FAMILIA__; o notebook e os dados vivem em indicadores/__FAMILIA__/.
name: atualizar __FAMILIA__
on:
  schedule:
    - cron: '__CRON__'
  workflow_dispatch:
    inputs:
      seco:
        description: Executar sem publicar
        type: boolean
        default: true
permissions:
  contents: read
concurrency:
  group: atualizar-__FAMILIA__
  cancel-in-progress: false
jobs:
  atualizar:
    uses: ./.github/workflows/atualizar-familia.yml
    with:
      familia: __FAMILIA__
      seco: ${{ inputs.seco == true }}
    secrets:
      token: ${{ secrets.DADOS_BOT_TOKEN }}
```

- [x] **Step 2: Conferir o YAML e as regras**

```bash
python3 - <<'PY'
from pathlib import Path
import yaml
texto = Path('.agents/skills/adicionando-indicador/assets/atualizar-familia-caller.yml').read_text(encoding='utf-8')
assert '__FAMILIA__' in texto and '__CRON__' in texto
assert 'pull_request_target' not in texto
assert 'gh pr merge' not in texto
yaml.safe_load(texto)
print('caller ok')
PY
```

Expected: `caller ok`.

- [x] **Step 3: Commit**

```bash
git add .agents/skills/adicionando-indicador/assets/atualizar-familia-caller.yml
git commit -m "docs(dados): adiciona caller modelo da skill"
```

---

### Task 5: Teste com a skill (GREEN)

**Files:**
- Nenhum arquivo de dado. Evidência em `/tmp/skill-adicionando-indicador/`.
- Modify se o teste revelar lacuna: `.agents/skills/adicionando-indicador/SKILL.md` e referências.

**Interfaces:**
- Consumes: skill das Tasks 2–4; baseline da Task 1.
- Produces: evidência de que a skill fecha as falhas do baseline.

- [x] **Step 1: Rodar o mesmo cenário com a skill**

Despache um subagente novo com o mesmo prompt da Task 1, precedido de:

```text
Leia e siga `.agents/skills/adicionando-indicador/SKILL.md`.
```

Salve em `/tmp/skill-adicionando-indicador/com-skill.md`.

- [x] **Step 2: Comparar com o baseline**

A resposta com skill precisa cumprir a tabela da Task 1 **e**:

- não começar o notebook antes do brief de definição;
- distinguir produtor de agregador;
- preferir série oficial já calculada;
- propor verificação independente (não a mesma fonte);
- atribuir todas as fontes e declarar cálculo próprio;
- usar C15 e granularidade mínima;
- se for família nova, incluir allowlist, caller e linha no `AGENTS.md`.

Registre cada falha restante e a frase do baseline que ela reabre.

- [x] **Step 3: Rodar o teste de mecânica sem rede**

Despache outro subagente com:

```text
Sem acessar a rede e sem alterar arquivos, liste os arquivos e comandos que você
criaria/alteraria para adicionar uma série mensal nova (a) numa família existente
e (b) numa família nova, incluindo catálogo, C15, allowlist e caller.
```

A resposta precisa mencionar: JSON no contrato, entrada no catálogo, C15,
`validar.py`, `pytest`, caller + allowlist + `AGENTS.md` para família nova,
metodologia e atribuição. Salve em `/tmp/skill-adicionando-indicador/mecanica.md`.

- [x] **Step 4: Corrigir os buracos e re-testar**

Se o agente pulou um gate, acrescente ao `SKILL.md` um **red flag** explícito e,
se necessário, um critério no gate correspondente. Rode o cenário de novo. Não
adicione conteúdo para falhas que não apareceram.

- [x] **Step 5: Commit das correções**

```bash
git add .agents/skills/adicionando-indicador
git commit -m "docs(dados): fecha lacunas da skill de indicador"
```

---

### Task 6: Verificação final e PR

**Files:**
- Modify: `docs/superpowers/specs/2026-11-02-skill-adicionando-indicador-design.md` (status já aprovado)
- Create: `docs/superpowers/plans/2026-11-03-skill-adicionando-indicador.md` (este plano)

**Interfaces:**
- Consumes: todas as tasks anteriores.
- Produces: branch pronta para PR, sem mudança de dado.

- [x] **Step 1: Rodar os gates do repo**

```bash
python3 scripts/validar.py
python3 -m pytest -q
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"
python3 - <<'PY'
from pathlib import Path
import yaml
for caminho in Path('.agents/skills/adicionando-indicador').rglob('*.yml'):
    yaml.safe_load(caminho.read_text(encoding='utf-8'))
print('yaml ok')
PY
git diff --check
```

Expected: `validar.py` exit 0; `pytest` verde; parse ok; `yaml ok`.

- [x] **Step 2: Confirmar que nenhum dado mudou**

```bash
git diff --name-only origin/main...HEAD -- indicadores scripts tests
```

Expected: vazio, exceto se o commit de C15 estiver no mesmo branch. Se C15 for
um PR separado, este comando precisa sair vazio.

- [x] **Step 3: Confirmar a descoberta da skill**

```bash
test -f .agents/skills/adicionando-indicador/SKILL.md
find .agents/skills/adicionando-indicador -type f | sort
```

Expected: `SKILL.md`, quatro referências e o asset.

Em uma sessão/subagente novo, carregue a skill pelo ID `adicionando-indicador`
(ou `@adicionando-indicador`). Expected: o `SKILL.md` é carregado. Se não
aparecer, confira o caminho `.agents/skills/...` e o frontmatter; o ID é o nome
da pasta.

- [x] **Step 4: Revisar a evidência do baseline e do GREEN**

Confirme que `/tmp/skill-adicionando-indicador/baseline.md` e `com-skill.md`
existem e que a diferença é a esperada. O corpo do PR cita as falhas fechadas.

- [ ] **Step 5: Commit final e PR**

```bash
git add .agents/skills/adicionando-indicador \
  docs/superpowers/specs/2026-11-02-skill-adicionando-indicador-design.md \
  docs/superpowers/plans/2026-11-03-skill-adicionando-indicador.md
git commit -m "docs(dados): detalha a skill de indicador novo"
```

Abra o PR contra `main` com: objetivo, arquivos da skill, evidência
baseline/GREEN, resultado dos gates e a nota de que nenhum dado mudou. Se C15
ainda não estiver na `main`, abra/mescle o PR de C15 primeiro e rebaseie este.

---

## Self-Review

- **Cobertura do spec:** gates (Tasks 2–3), fluxo e decisões (Task 2), referências
  (Task 3), workflow (Tasks 3–4), atribuição (Tasks 2–3), baseline/GREEN
  (Tasks 1 e 5), gates finais e PR (Task 6).
- **Base divergente:** tratada nos pré-requisitos; o plano não mistura os 4
  commits locais de dado nem o trabalho não relacionado de `sitio`.
- **C15:** é pré-requisito explícito, não tarefa deste plano.
- **Review Focus:** cada um dos cinco modos de falha tem critério no baseline
  (Task 1), no `SKILL.md` (Task 2) e no teste GREEN (Task 5).
- **Proporção:** o plano fixa decisões e roteiros de teste; o texto final da
  skill e das referências é escrito nas tasks, sem transcrever o contrato.
