# Quatro indicadores sociais — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** publicar quatro séries novas — mortalidade infantil, esgotamento sanitário, Ideb e mortes no trânsito — depois de emendar o contrato com `eixo: por-mil` e `granularidade: bienal`.

**Architecture:** a emenda do contrato entra primeiro, nos dois repositórios (`dados` e `sitio`), porque o app valida a série ao carregar. Depois, quatro pipelines independentes geram um JSON cada, com notebook próprio, família própria e caller próprio. A integração de catálogo, grupos, metodologia e workflows é serial; cada série passa pelo gate de revisão da skill `adicionando-indicador`.

**Tech Stack:** Python 3.12, pandas, requests, nbconvert; Jupyter/Colab; GitHub Actions; `uv`; Svelte 5 + Vitest no `sitio`.

**Spec:** `docs/superpowers/specs/2026-11-04-quatro-indicadores-sociais-design.md`

## Global Constraints

- Contrato `../sitio/docs/contrato-de-indicadores.md` (`C1…C15`); catálogo `K1…K9`.
- `versao: 1` não muda. Nenhum valor de série existente muda.
- C15: anual e bienal `AAAA-01-01`; mensal `AAAA-MM-01`.
- Lacuna é ausência de ponto; nunca `null`, zero ou interpolação.
- Notebook: primeira célula é o selo Open in Colab; nenhum caminho absoluto da máquina (`/Users/`, `/home/`, `/root/`, `C:\`, `file://`) em célula ou saída; `relativo()` em todo print de caminho.
- Notebook busca a fonte e recalcula a série inteira; não lê o JSON publicado. Ensaio com `DADOS_RAIZ` e `<FAMILIA>_SAIDA`.
- Série + catálogo no mesmo PR (K1/K2); `urlNotebook` aponta para o notebook que gera a série.
- A emenda do `sitio` (Tasks 1–3) tem de estar mergeada **antes** de a primeira série ser publicada; senão a home abre em `SchemaError`.
- Grupos novos, na ordem: `saude` (🩺 Saúde), `saneamento` (🚰 Saneamento), `educacao` (🎓 Educação), `mobilidade` (🚗 Mobilidade), entre `trabalho` e `demografia`.
- Commits em português, Conventional Commits com escopo `dados` (e `app` no `sitio`).
- Toda série passa pelo gate de revisão independente da skill; o revisor não edita.

## Review Focus

- **Denominador trocado:** taxa por mil/100 mil com denominador de amostra, de outro ano ou de outra fonte (mortalidade, trânsito, esgoto).
- **Data de publicação usada como referência (C15):** ano do arquivo do Inep, ano do relatório do SNIS, ano de coleta do SIM.
- **Emenda escondida:** juntar SNIS e Sinisa, ou SIM e Sinasc, sem declarar a quebra e sem conferir a sobreposição.
- **Bienal sem paridade:** série com anos consecutivos passa e o painel de mandatos calcula expectativa errada.
- **Descrição que promete o que o número não é:** "esgoto tratado" para rede coletora, "aprendizado" para Ideb, "mortes no trânsito" para acidentes de transporte.
- **Rótulo da ficha:** unidade `numero` exibida como "contagem" e granularidade `bienal` em branco.

---

### Task 1: Emenda `por-mil` + `bienal` no validador do `dados`

**Files:**
- Modify: `scripts/validar.py:39-47,78-93,150-230`
- Modify: `tests/test_validar.py`
- Create: `tests/contrato/validos/canonica-por-mil.json`
- Create: `tests/contrato/validos/canonica-bienal.json`
- Create: `tests/contrato/invalidos/C4-por-mil-com-percentual.json`
- Create: `tests/contrato/invalidos/C6-bienal-paridade.json`
- Create: `tests/contrato/invalidos/C15-bienal-mes-02.json`
- Modify: `AGENTS.md` (resumo do contrato: listas de `eixo` e `granularidade`)
- Modify: `.agents/skills/adicionando-indicador/SKILL.md` (tabela de decisão e lista de granularidade)
- Modify: `.agents/skills/adicionando-indicador/references/contrato-resumo.md` (enums, se listar)

**Interfaces:**
- Consumes: `validar_serie(serie, caminho, checar_nome=True)` existente.
- Produces: `por-mil` aceito como `eixo` com `unidade.tipo: numero`; `bienal` aceito como `granularidade`, com paridade obrigatória; corpus que o `validate.js` do `sitio` também roda.

- [ ] **Step 1: Escrever os testes que falham em `tests/test_validar.py`**

```python
def test_aceita_eixo_por_mil():
    s = serie(eixo="por-mil", unidade={"tipo": "numero", "simbolo": "por mil", "casas": 1})
    assert erros(s) == []

def test_recusa_por_mil_com_unidade_percentual():
    s = serie(eixo="por-mil", unidade={"tipo": "percentual", "simbolo": "%", "casas": 1})
    assert any(e.split(": ")[1] == "C4" for e in erros(s))

def test_aceita_bienal_com_lacuna():
    s = serie(
        granularidade="bienal",
        dados=[
            {"data": "2005-01-01", "valor": 3.8},
            {"data": "2009-01-01", "valor": 4.6},
        ],
    )
    assert erros(s) == []

def test_recusa_bienal_fora_de_paridade():
    s = serie(
        granularidade="bienal",
        dados=[
            {"data": "2005-01-01", "valor": 3.8},
            {"data": "2006-01-01", "valor": 4.2},
        ],
    )
    assert any("paridade" in e for e in erros(s))

def test_recusa_bienal_fora_do_inicio_do_ano():
    s = serie(granularidade="bienal", dados=[{"data": "2006-02-01", "valor": 4.2}])
    assert any(e.split(": ")[1] == "C15" for e in erros(s))
```

- [ ] **Step 2: Criar os casos do corpus**

`validos/canonica-por-mil.json`: `id` `canonica-por-mil`, `unidade` `{tipo:"numero", simbolo:"por mil", casas:1}`, `eixo:"por-mil"`, `medida:"nivel"`, `granularidade:"anual"`, dois pontos (1996, 1997).

`validos/canonica-bienal.json`: `id` `canonica-bienal`, `unidade` `{tipo:"numero", simbolo:"índice", casas:1}`, `eixo:"contagem"`, `medida:"nivel"`, `granularidade:"bienal"`, pontos 2005, 2007 e 2011 (lacuna de 4 anos permitida).

`invalidos/C4-por-mil-com-percentual.json`: mesmo formato do válido, com `eixo:"por-mil"` e `unidade.tipo:"percentual"`.

`invalidos/C6-bienal-paridade.json`: `granularidade:"bienal"`, pontos 2005 e 2006.

`invalidos/C15-bienal-mes-02.json`: `granularidade:"bienal"`, um ponto em `2006-02-01`.

- [ ] **Step 3: Rodar e confirmar que falham**

Run: `uv run --frozen --group ci pytest tests/test_validar.py -q`
Expected: os testes novos falham (`eixo` desconhecido / `granularidade` inválida) e os casos válidos do corpus reprovam.

- [ ] **Step 4: Implementar em `scripts/validar.py`**

- `GRANULARIDADES = ("diaria", "mensal", "anual", "bienal")`.
- `EIXOS = ("percentual", "reais", "contagem", "por-100-mil", "por-mil")`.
- `TIPO_DO_EIXO["por-mil"] = "numero"`.
- `_chave_periodo`: `bienal` entra no ramo do ano (`data[:4]`).
- `_inicio_do_periodo`: `bienal` entra no ramo `data[5:] == "01-01"`.
- No laço dos pontos, depois do C15: guardar a paridade do primeiro ano e, se um ano seguinte tiver paridade diferente, `erro("C6", f"ponto {indice}: ano {data[:4]!r} quebra a paridade bienal ...")`.
- Mensagens de enum listam `...|bienal` e `...|por-mil`.

- [ ] **Step 5: Rodar e confirmar que passam**

Run: `uv run --frozen --group ci pytest tests/test_validar.py -q`
Expected: PASS, incluindo `test_casos_validos_do_corpus_passam` e `test_casos_invalidos_do_corpus_falham_com_o_codigo_do_nome`.

- [ ] **Step 6: Atualizar `AGENTS.md` e a skill**

`AGENTS.md`: `eixo` passa a listar `por-mil`; `granularidade` passa a listar `bienal`. Na skill, a tabela de decisão ganha `por-mil → numero` e a lista de granularidade ganha `bienal`; `references/contrato-resumo.md` idem, se listar enums.

- [ ] **Step 7: Commitar**

```bash
git add scripts/validar.py tests/test_validar.py tests/contrato AGENTS.md .agents/skills/adicionando-indicador
git commit -m "feat(dados): emenda o contrato com eixo por-mil e granularidade bienal"
```

### Task 2: Emenda no validador do `sitio`

**Files:**
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/data/validate.js:20-30,85-100`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/data/validate.test.js`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/docs/contrato-de-indicadores.md`

**Interfaces:**
- Consumes: o corpus criado na Task 1 (`dados/tests/contrato/`), que os testes do `sitio` leem.
- Produces: `validateSeries` aceita `por-mil` e `bienal` com a mesma regra de paridade do Python.

- [ ] **Step 1: Escrever os testes que falham em `validate.test.js`**

Casos: aceita `por-mil` com `numero`; recusa `por-mil` com `percentual` (C4); aceita `bienal` com lacuna; recusa `bienal` com anos consecutivos (C6); recusa `bienal` com data fora de `01-01` (C15).

- [ ] **Step 2: Rodar e confirmar que falham**

Run: `cd app && NODE_ENV=development npm test -- validate`
Expected: FAIL nos casos novos.

- [ ] **Step 3: Implementar em `validate.js`**

- `GRANULARIDADES` ganha `bienal`; `EIXOS` ganha `por-mil`; `TIPO_DO_EIXO` ganha `'por-mil': 'numero'`.
- `chaveDoPeriodo` e `inicioDoPeriodo` tratam `bienal` no ramo do ano.
- No laço dos pontos, a mesma checagem de paridade da Task 1, com erro `C6`.

- [ ] **Step 4: Rodar o corpus e os testes**

Run: `cd app && NODE_ENV=development npm test -- validate`
Expected: PASS. Rodar também o teste de integração que lê `dados/tests/contrato/` (mesmo comando, suíte completa).

- [ ] **Step 5: Atualizar o contrato**

`docs/contrato-de-indicadores.md`: linha `por-mil` na tabela do C4; `bienal` no C6; menção a `bienal` no C11 e no C15; frase única sobre paridade obrigatória.

- [ ] **Step 6: Commitar no `sitio`**

```bash
git add app/src/data/validate.js app/src/data/validate.test.js docs/contrato-de-indicadores.md
git commit -m "feat(app): aceita eixo por-mil e granularidade bienal no contrato"
```

### Task 3: Comparação por mandato e rótulos da ficha

**Files:**
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/domain/mandates.js:33-100`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/domain/mandates.test.js`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/domain/format.js`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/domain/format.test.js`
- Modify: `/Users/lucas/Workspace/personal/brasilemnumeros/sitio/app/src/components/Ficha.svelte:70-71,136-146`

**Interfaces:**
- `pontosEsperados(granularidade, mandato, fase = null): number|null` — `fase` é o ano do primeiro ponto, obrigatório para `bienal`.
- `rotuloDaUnidade(eixo, tipo): string` e `rotuloDaGranularidade(granularidade): string`.

- [ ] **Step 1: Escrever os testes que falham em `mandates.test.js`**

```js
const IDEB = {
  id: 'ideb-anos-iniciais',
  granularidade: 'bienal',
  dados: [
    { data: '2005-01-01', valor: 3.8 },
    { data: '2007-01-01', valor: 4.2 },
    { data: '2019-01-01', valor: 5.9 },
    { data: '2021-01-01', valor: 5.8 },
  ],
};
const BOLSONARO = { id: 'federal-2019-bolsonaro', inicio: '2019-01-01', fim: '2022-12-31' };
const TEMER = { id: 'federal-2016-temer', inicio: '2016-05-12', fim: '2018-12-31' };
const LULA_I = { id: 'federal-2003-lula', inicio: '2003-01-01', fim: '2006-12-31' };

it('bienal espera 2 pontos num mandato de 4 anos e 1 num de 2', () => {
  expect(pontosEsperados('bienal', BOLSONARO, 2005)).toBe(2);
  expect(pontosEsperados('bienal', TEMER, 2005)).toBe(1);
  expect(pontosEsperados('bienal', LULA_I, 2005)).toBe(1);
});

it('bienal completo é calculável e o delta é último − primeiro', () => {
  const c = deltaNoMandato(IDEB, BOLSONARO);
  expect(c.estado).toBe(COBERTURA.CALCULAVEL);
  expect(c.delta).toBeCloseTo(5.8 - 5.9, 6);
});

it('janela entre duas medições diz que não há medição no período', () => {
  const c = deltaNoMandato(IDEB, TEMER);
  expect(c.estado).toBe(COBERTURA.SEM);
  expect(c.motivo).toMatch(/sem medição no período/);
});
```

`format.test.js`: `rotuloDaUnidade('por-mil', 'numero') === 'taxa por mil'`, `rotuloDaUnidade('por-100-mil', 'numero') === 'taxa por 100 mil'`, `rotuloDaUnidade('contagem', 'numero') === 'contagem'`, `rotuloDaGranularidade('bienal') === 'bienal'`.

- [ ] **Step 2: Rodar e confirmar que falham**

Run: `cd app && NODE_ENV=development npm test -- mandates format`
Expected: FAIL (`pontosEsperados` não aceita `fase`, funções de rótulo não existem).

- [ ] **Step 3: Implementar `mandates.js`**

- `pontosEsperados(granularidade, mandato, fase = null)`: `bienal` conta os anos de `inicio` a `fim` com a mesma paridade de `fase`; sem `fase`, devolve `null`.
- `deltaNoMandato` passa `Number(series.dados[0].data.slice(0, 4))` como `fase`.
- `motivoDaAusencia`: se houver ponto antes de `inicio` **e** ponto depois de `fim`, devolve `sem medição no período`; senão mantém os textos atuais.

- [ ] **Step 4: Implementar os rótulos em `format.js` e usar na `Ficha.svelte`**

`rotuloDaUnidade` mapeia por `eixo` (`percentual`, `reais`→`moeda`, `contagem`, `por-100-mil`→`taxa por 100 mil`, `por-mil`→`taxa por mil`), com fallback para `tipo`. `rotuloDaGranularidade` cobre `diaria`, `mensal`, `anual`, `bienal`. A ficha troca `TIPO[...]` e `GRANULARIDADE[...]` por essas funções.

- [ ] **Step 5: Rodar os testes**

Run: `cd app && NODE_ENV=development npm test`
Expected: PASS.

- [ ] **Step 6: Commitar no `sitio`**

```bash
git add app/src/domain/mandates.js app/src/domain/mandates.test.js app/src/domain/format.js app/src/domain/format.test.js app/src/components/Ficha.svelte
git commit -m "feat(app): cobre bienal no painel de mandatos e rotula taxa na ficha"
```

### Task 4: Mortalidade infantil (por mil nascidos vivos)

**Files:**
- Create: `indicadores/saude/MortalidadeInfantil.ipynb`
- Create: `indicadores/saude/mortalidade-infantil-anual.json`

**Interfaces:**
- Consumes: MS/SIM + Sinasc via Datasus (taxa pronta do TabNet ou cálculo próprio; o gate de fonte decide e registra o endpoint).
- Produces: série `mortalidade-infantil-anual`, anual, 1996–último ano fechado, `eixo: por-mil`.

- [ ] **Step 1: Gate de fonte**

Registrar no relatório da tarefa: endpoint/código (TabNet `sim/cnv/inf10uf.def` ou microdados SIM `DOINF` + Sinasc `DN`), cobertura 1996+, último ano fechado, política de revisão, e uma publicação externa candidata (imprensa/instituto/relatório). Se o TabNet não for scriptável, o notebook calcula `1000 × óbitos <1 ano ÷ nascidos vivos` com a fórmula visível.

- [ ] **Step 2: Criar o notebook** com as células obrigatórias da skill; `DESTINO = SAUDE_SAIDA`; retry na coleta; corte do ano corrente incompleto; validação inline (C15, ordem, duplicata, paridade não se aplica).

- [ ] **Step 3: Metadados exatos** — `unidade: {tipo:"numero", simbolo:"por mil", casas:1}`, `eixo:"por-mil"`, `medida:"nivel"`, `granularidade:"anual"`, `fonte` nomeando SIM/Sinasc e o que é cálculo próprio, `urlFonte` do recorte.

- [ ] **Step 4: Rodar em ensaio duas vezes** com `DADOS_RAIZ="$PWD" SAUDE_SAIDA=<tmp>`; comparar byte a byte; conferir primeiro ponto 1996, último ano fechado, contagem e C15. Conferir 2000–2016 contra a série CD100 do IBGE (2016 = 13,3) e o último ano contra a publicação do MS; divergência > 0,3 por mil investigar antes de publicar.

- [ ] **Step 5: Gerar o JSON publicado** em `indicadores/saude/`; sem caminho absoluto na saída.

- [ ] **Step 6: Entregar relatório** com status, arquivos, comandos/resultados, fonte, verificação externa e proposta de `descricao` + seção de metodologia (não editar arquivos compartilhados).

### Task 5: Esgotamento sanitário (rede coletora)

**Files:**
- Create: `indicadores/saneamento/Esgoto.ipynb`
- Create: `indicadores/saneamento/esgoto-rede-coletora-total.json`

**Interfaces:**
- Consumes: SNIS (1995–2023) e Sinisa (2024), população atendida com rede coletora; denominador = população residente do Brasil (IBGE).
- Produces: série `esgoto-rede-coletora-total`, anual, 1995–2024, `eixo: percentual`.

- [ ] **Step 1: Gate de fonte**

Registrar: arquivo/URL da Série Histórica do SNIS e do relatório do Sinisa; variável de população atendida (total, não só urbana); denominador IBGE; último ano fechado; publicação externa candidata (relatório do Sinisa/Trata Brasil). Confirmar que o denominador nacional é o do design.

- [ ] **Step 2: Criar o notebook** com as células obrigatórias; `DESTINO = SANEAMENTO_SAIDA`; retry; corte do ano corrente; validação inline.

- [ ] **Step 3: Metadados exatos** — `unidade: {tipo:"percentual", simbolo:"%", casas:1}`, `eixo:"percentual"`, `medida:"nivel"`, `granularidade:"anual"`, `fonte` nomeando SNIS/Sinisa e o cálculo do denominador, `urlFonte` do recorte.

- [ ] **Step 4: Emenda SNIS → Sinisa**

Calcular 2023 pelas duas fontes com o mesmo denominador. Se `|diferença| ≤ 0,1 p.p.`, publicar 2024 e registrar a diferença na metodologia; se maior, parar em 2023 e registrar o motivo. Não ajustar número para colar.

- [ ] **Step 5: Rodar em ensaio duas vezes**, comparar byte a byte, conferir primeiro ponto 1995, último ano, contagem, C15 e que 2023 fica na faixa de 55–62% (o número oficial de amostra é 59,7%; a diferença para o nacional é esperada e explicada).

- [ ] **Step 6: Gerar o JSON publicado** em `indicadores/saneamento/` e entregar o relatório com a proposta de catálogo + metodologia.

### Task 6: Ideb — anos iniciais

**Files:**
- Create: `indicadores/educacao/IDEB.ipynb`
- Create: `indicadores/educacao/ideb-anos-iniciais.json`

**Interfaces:**
- Consumes: Inep/Ideb, Brasil, anos iniciais, rede total; XLSX da edição vigente (resolver o nome do arquivo, falhar se não achar).
- Produces: série `ideb-anos-iniciais`, bienal, 2005–2025, 11 pontos, `granularidade: bienal`.

- [ ] **Step 1: Gate de fonte**

Registrar: URL do XLSX de Brasil (anos iniciais, total), cobertura 2005–2025, periodicidade bienal, e publicação externa (flyer do Inep reproduzido por veículo/instituição).

- [ ] **Step 2: Criar o notebook** com as células obrigatórias; `DESTINO = EDUCACAO_SAIDA`; ler o XLSX com `pandas`; selecionar Brasil/anos iniciais/total; corte do ano corrente se a edição não estiver fechada; validação inline incluindo paridade.

- [ ] **Step 3: Metadados exatos** — `unidade: {tipo:"numero", simbolo:"índice", casas:1}`, `eixo:"contagem"`, `medida:"nivel"`, `granularidade:"bienal"`, `fonte: "Inep — Ideb, anos iniciais do ensino fundamental, rede total (Brasil)"`, `urlFonte` da página de resultados.

- [ ] **Step 4: Rodar em ensaio duas vezes** e conferir os 11 pontos: 2005 3,8; 2007 4,2; 2009 4,6; 2011 5,0; 2013 5,2; 2015 5,5; 2017 5,8; 2019 5,9; 2021 5,8; 2023 6,0; 2025 6,3. Conferir paridade ímpar, C15 e ausência de anos pares.

- [ ] **Step 5: Gerar o JSON publicado** em `indicadores/educacao/` e entregar o relatório com a proposta de catálogo + metodologia (índice 0–10, Saeb + Censo Escolar, bienal, não é percentual).

### Task 7: Mortes no trânsito (por 100 mil)

**Files:**
- Create: `indicadores/mobilidade/Transito.ipynb`
- Create: `indicadores/mobilidade/mortes-transito-anual.json`

**Interfaces:**
- Consumes: SIM/Datasus, CID-10 V01–V99 (óbitos), e a mesma população residente de `homicidios` (`AVIOL12_VIOLPOP`).
- Produces: série `mortes-transito-anual`, anual, 1996–último ano fechado, `eixo: por-100-mil`.

- [ ] **Step 1: Gate de fonte**

Registrar: arquivo do SIM (`DOEXT<AA>.dbc` ou TabNet com a categoria de transporte), cobertura 1996+, último ano fechado, e publicação externa (ONSV, Ministério da Saúde, artigo). Se o `.dbc` exigir dependência nova, adicionar a versão exata em `[project].dependencies` e rodar `uv lock` no mesmo commit.

- [ ] **Step 2: Criar o notebook** com as células obrigatórias; `DESTINO = MOBILIDADE_SAIDA`; retry; filtrar `CAUSABAS` V01–V99; cortar o ano corrente incompleto; validação inline.

- [ ] **Step 3: Metadados exatos** — `unidade: {tipo:"numero", simbolo:"por 100 mil", casas:2}`, `eixo:"por-100-mil"`, `medida:"nivel"`, `granularidade:"anual"`, `fonte: "Ministério da Saúde — SIM/Datasus (CID-10 V01–V99); taxa por 100 mil calculada pelo site"`, `urlFonte` do recorte.

- [ ] **Step 4: Rodar em ensaio duas vezes**; conferir 1996, último ano, contagem, C15 e a taxa contra a publicação externa (nível e variação em janela sobreposta).

- [ ] **Step 5: Gerar o JSON publicado** em `indicadores/mobilidade/` e entregar o relatório com a proposta de catálogo + metodologia (acidentes de transporte, não sinistros nem feridos; denominador único).

### Task 8: Integração — catálogo, grupos, metodologia e workflows

**Files:**
- Modify: `indicadores/catalogo.json`
- Modify: `docs/metodologia.md`
- Modify: `AGENTS.md`
- Modify: `.github/workflows/atualizar-familia.yml:46`
- Create: `.github/workflows/atualizar-saude.yml`
- Create: `.github/workflows/atualizar-saneamento.yml`
- Create: `.github/workflows/atualizar-educacao.yml`
- Create: `.github/workflows/atualizar-mobilidade.yml`

**Interfaces:**
- Consumes: os quatro JSONs e notebooks das Tasks 4–7.
- Produces: catálogo com 27 séries e 13 grupos; quatro callers; metodologia com quatro seções.

- [ ] **Step 1: Catálogo — entradas**

Inserir, sem reordenar as existentes:

```json
{
  "id": "mortalidade-infantil-anual",
  "nome": "Mortalidade Infantil (por mil nascidos vivos)",
  "grupo": "saude",
  "arquivo": "saude/mortalidade-infantil-anual.json",
  "escala": "numero",
  "descricao": "Óbitos de crianças com menos de 1 ano por mil nascidos vivos no ano, Brasil. Depende da captação de óbitos e nascidos vivos: nos anos e regiões de pior cobertura, o número é menor que o real. Não é a taxa corrigida por métodos demográficos do IBGE.",
  "urlNotebook": "https://github.com/brasilemnumeros/dados/blob/main/indicadores/saude/MortalidadeInfantil.ipynb"
}
```

```json
{
  "id": "esgoto-rede-coletora-total",
  "nome": "Esgoto — população atendida com rede coletora (%)",
  "grupo": "saneamento",
  "arquivo": "saneamento/esgoto-rede-coletora-total.json",
  "escala": "percentual",
  "descricao": "Percentual da população residente do Brasil atendida por rede coletora de esgoto. Não é esgoto tratado: o município pode coletar e lançar sem tratamento. Quem não reporta entra como não atendido, então a série é um piso.",
  "urlNotebook": "https://github.com/brasilemnumeros/dados/blob/main/indicadores/saneamento/Esgoto.ipynb"
}
```

```json
{
  "id": "ideb-anos-iniciais",
  "nome": "Ideb — anos iniciais do ensino fundamental (0–10)",
  "grupo": "educacao",
  "arquivo": "educacao/ideb-anos-iniciais.json",
  "escala": "numero",
  "descricao": "Índice de 0 a 10 que combina a proficiência no Saeb com a taxa de aprovação do Censo Escolar, para os anos iniciais, rede total. É bienal e não é percentual de aprendizado nem nota de escola.",
  "urlNotebook": "https://github.com/brasilemnumeros/dados/blob/main/indicadores/educacao/IDEB.ipynb"
}
```

```json
{
  "id": "mortes-transito-anual",
  "nome": "Mortes no Trânsito (por 100 mil)",
  "grupo": "mobilidade",
  "arquivo": "mobilidade/mortes-transito-anual.json",
  "escala": "numero",
  "descricao": "Mortes por acidentes de transporte (CID-10 V01–V99) por 100 mil habitantes, Brasil, incluindo pedestres, motociclistas, ocupantes e ciclistas. Não é número de sinistros, de feridos nem de mortes em rodovias federais.",
  "urlNotebook": "https://github.com/brasilemnumeros/dados/blob/main/indicadores/mobilidade/Transito.ipynb"
}
```

- [ ] **Step 2: Catálogo — grupos**

Inserir entre `trabalho` e `demografia`, nesta ordem:

```json
"saude": { "nome": "🩺 Saúde" },
"saneamento": { "nome": "🚰 Saneamento" },
"educacao": { "nome": "🎓 Educação" },
"mobilidade": { "nome": "🚗 Mobilidade" },
```

- [ ] **Step 3: Metodologia**

Quatro seções em `docs/metodologia.md`, cada uma com definição, fonte/código, fórmula, cobertura, revisão, caveats e o parágrafo **“Verificação independente”** (nome, data, valores, URL, ou a busca feita e por que não serviu). Incluir a emenda SNIS→Sinisa e a paridade do Ideb.

- [ ] **Step 4: `AGENTS.md`**

Quatro linhas na tabela de cadência: `saude` `0 15 10 6 *`, `saneamento` `0 15 10 4 *`, `educacao` `0 15 10 9 *`, `mobilidade` `0 15 10 6 *` (ajustar se a janela de divulgação da fonte for outra). Acrescentar `SAUDE_SAIDA`, `SANEAMENTO_SAIDA`, `EDUCACAO_SAIDA` e `MOBILIDADE_SAIDA` à lista de variáveis e as famílias novas à prosa.

- [ ] **Step 5: Workflows**

Quatro callers copiados de `atualizar-selic.yml`, com `familia: saude` etc.; allowlist de `atualizar-familia.yml` ganha `saude|saneamento|educacao|mobilidade`. `tests/test_workflows.py` descobre as famílias pelo disco e deve passar sem edição.

- [ ] **Step 6: Commitar** as quatro séries + integração (commits por família + um de integração), sem push.

### Task 9: Gate final e PR

- [ ] **Step 1: Validar** `uv run --frozen --group ci python scripts/validar.py`.
- [ ] **Step 2: Testar** `uv run --frozen --group ci pytest -q`.
- [ ] **Step 3: Parse** `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"`.
- [ ] **Step 4: Diff** `git diff --check` e revisão do diff numérico; confirmar que as 23 séries existentes não mudaram.
- [ ] **Step 5: Revisão final** — subagente fresco com o diff completo, o design e o contrato; corrigir `Critical`/`Important` e re-revisar o diff de correção. Conferir na ficha do app: `por-mil` como “taxa por mil”, `bienal` como “bienal”, Ideb com paridade e painel de mandatos sem “parcial” falso.
- [ ] **Step 6: PR** — abrir o PR no `dados` com resumo, fontes e verificações; o PR do `sitio` (Tasks 2–3) mergeia antes da publicação das séries. O CI é o gate.
