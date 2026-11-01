# Pipeline de indicadores Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer cada notebook ser a explicação executável e o único motor de coleta, cálculo e publicação dos indicadores, revisando a metodologia contra a fonte e respeitando exclusivamente o contrato consumido pelo `sitio`.

**Architecture:** Toda execução recalcula a série inteira desde `1995-01-01`, publica apenas períodos encerrados e escreve o JSON canônico diretamente, com `value` e sem `rate`. O GitHub Actions executa os notebooks, valida os arquivos e abre/atualiza um PR quando `git diff` acusa mudança. `scripts/` contém somente validação, nunca lógica de indicador nem classificação de diff.

**Tech Stack:** Python 3.12, Jupyter/nbconvert, pandas, `python-bcb`, `ipeadatapy`, requests, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md`

## Global Constraints

- Python 3.12.
- Contrato de dados: `sitio/app/src/data/validate.js`, `sitio/docs/plans/01-contrato-de-dados.md` e `sitio/docs/plans/11-migracao-do-repo-dados.md`.
- Publicar somente `value`; `rate` não faz parte do contrato final.
- `schema === 1`; `id == nome do arquivo`; `unit.type` em `percentage`/`number`/`currency`; `unit.symbol` não vazio; `unit.decimals` inteiro ≥ 0; `granularity` em `daily`/`monthly`/`annual`; `source` não vazio.
- `date` em `YYYY-MM-DD` e `value` numérico finito.
- Nenhum mês repetido na mesma série.
- O contrato **não** exige dia 01, ordem ascendente nem período fechado. Não validar essas regras como se fossem contrato.
- Toda série coleta desde `1995-01-01`; a publicação começa no primeiro ponto calculável.
- O pipeline publica apenas períodos encerrados, por decisão própria, não por exigência do contrato.
- Preservar a convenção de data já usada em cada série para evitar diffs desnecessários.
- Não existem modos `update`/`rebuild`; toda execução recalcula tudo.
- Um notebook pode publicar vários JSONs; séries derivadas são calculadas no próprio notebook, a partir das fontes brutas.
- A lógica dos indicadores será revisada. Correção que altere valores publicados exige justificativa, fonte e aval humano antes de ser implementada.
- `scripts/` não pode buscar nem calcular indicador.
- `governos/` não é tocado por este plano.
- Commit messages: Conventional Commits em português, escopo `dados`.

## Review Focus

- Ponto sem `value` ou com `value` não finito: deve falhar, mesmo que tenha `rate`.
- `rate` extra: deve ser tolerado e ignorado; não é campo do contrato.
- Data como `1999-03-31`: deve passar; dia 01 não é exigência.
- Data fora de ordem: deve passar; a ordenação é responsabilidade do app/pipeline, não do contrato.
- Mês repetido: deve falhar, porque o teste de integração do `sitio` exige ausência de duplicatas.
- Correção metodológica: deve aparecer no diff com justificativa e não pode ser confundida com atualização rotineira.
- Série derivada: deve ser recalculada da fonte bruta, sem ler o JSON publicado de outra pasta.

---

## File Structure

- `requirements.txt`: dependências fixadas do CI e do ambiente local.
- `scripts/__init__.py`: permite importar os scripts nos testes.
- `scripts/validar.py`: contrato do JSON publicado; não corrige nada.
- `tests/test_validar.py`: testes do validador.
- `docs/metodologia.md`: revisão da definição e da fórmula de cada indicador.
- `.github/workflows/atualizar-dados.yml`: execução diária, validação e PR.
- `<pasta>/*.ipynb`: notebooks migrados, um por pasta, publicando N JSONs.
- `<pasta>/*.json`: dados publicados.

### Contrato de migração de notebook

Todo notebook migrado deve:

1. Abrir com markdown declarando fonte, URL/endpoint, códigos das séries, unidade, granularidade, período coberto, definição do indicador e fórmula usada.
2. Resolver a raiz uma vez:
   ```python
   from pathlib import Path
   import os
   RAIZ = Path(os.environ.get("DADOS_RAIZ", Path.cwd()))
   ```
3. Buscar a fonte completa desde `1995-01-01`, sem ler JSON publicado e sem trecho de atualização incremental.
4. Calcular em células visíveis, com a fórmula aprovada em `docs/metodologia.md`.
5. Filtrar períodos abertos antes de montar os pontos.
6. Preservar a convenção de data da série (dia 01 na maioria; dia 15 em `homicidios-armas-fogo-anual`).
7. Montar os pontos como `{"date": "YYYY-MM-DD", "value": valor}`, sem `rate`.
8. Escrever todos os JSONs da pasta com `json.dump(..., ensure_ascii=False, indent=2)`.
9. Terminar com uma célula de validação inline que falha se houver duplicata de mês, `value` ausente/não finito ou metadado inválido, e com as conferências de cálculo da revisão metodológica.
10. Não conter `/content`, `indicatorName`, `rate` na escrita final nem leitura de arquivo existente para decidir o que buscar.

---

### Task 1: Validador do contrato

**Files:**
- Create: `requirements.txt`
- Create: `scripts/__init__.py`
- Create: `scripts/validar.py`
- Test: `tests/test_validar.py`

**Interfaces:**
- Produces: `validar_serie(serie: dict, caminho: Path) -> list[str]`
- Produces: `validar_arquivo(caminho: Path) -> list[str]`
- Produces: `validar_todos(raiz: Path) -> dict[Path, list[str]]`
- Produces CLI: `python3 scripts/validar.py [arquivos...]`, exit `0` se tudo válido, `1` caso contrário.

- [ ] **Step 1: Criar `requirements.txt` com as dependências**

```text
pandas
python-bcb
ipeadatapy
requests
matplotlib
seaborn
plotly
nbconvert
ipykernel
pytest
PyYAML
```

Depois de instalar, fixe as versões exatas com `pip freeze` e substitua as linhas acima por `pacote==versao`.

- [ ] **Step 2: Escrever os testes do validador**

Crie `tests/test_validar.py`:

```python
from pathlib import Path

from scripts.validar import validar_serie

CAMINHO = Path("ipca/ipca-acum-12m.json")


def serie(**over):
    base = {
        "schema": 1,
        "id": "ipca-acum-12m",
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "IBGE",
        "data": [{"date": "2026-09-30", "value": 5.0}],
    }
    base.update(over)
    return base


def test_serie_valida():
    assert validar_serie(serie(), CAMINHO) == []


def test_aceita_rate_extra():
    s = serie(data=[{"date": "2026-09-30", "rate": 5.0, "value": 5.0}])
    assert validar_serie(s, CAMINHO) == []


def test_recusa_ponto_sem_value():
    s = serie(data=[{"date": "2026-09-30", "rate": 5.0}])
    assert any("value" in e for e in validar_serie(s, CAMINHO))


def test_recusa_schema_desconhecido():
    assert any("schema" in e for e in validar_serie(serie(schema=2), CAMINHO))


def test_recusa_id_divergente():
    assert any("id" in e for e in validar_serie(serie(id="outro"), CAMINHO))


def test_recusa_tipo_de_unidade():
    s = serie(unit={"type": "peso", "symbol": "kg", "decimals": 1})
    assert any("unit.type" in e for e in validar_serie(s, CAMINHO))


def test_recusa_simbolo_vazio():
    s = serie(unit={"type": "number", "symbol": "", "decimals": 0})
    assert any("symbol" in e for e in validar_serie(s, CAMINHO))


def test_recusa_decimals_invalido():
    s = serie(unit={"type": "number", "symbol": "x", "decimals": -1})
    assert any("decimals" in e for e in validar_serie(s, CAMINHO))


def test_recusa_granularidade():
    assert any("granularity" in e for e in validar_serie(serie(granularity="semanal"), CAMINHO))


def test_recusa_source_vazio():
    assert any("source" in e for e in validar_serie(serie(source=""), CAMINHO))


def test_recusa_data_fora_do_formato():
    s = serie(data=[{"date": "31/03/1999", "value": 1.0}])
    assert any("YYYY-MM-DD" in e for e in validar_serie(s, CAMINHO))


def test_recusa_valor_nao_finito():
    s = serie(data=[{"date": "2026-09-30", "value": float("nan")}])
    assert any("finito" in e for e in validar_serie(s, CAMINHO))


def test_recusa_mes_repetido():
    s = serie(data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-31", "value": 6.0},
    ])
    assert any("repetido" in e for e in validar_serie(s, CAMINHO))


def test_aceita_data_fora_do_dia_01():
    s = serie(data=[{"date": "1999-03-31", "value": 44.22}])
    assert validar_serie(s, CAMINHO) == []


def test_aceita_fora_de_ordem():
    s = serie(data=[
        {"date": "2026-09-01", "value": 5.0},
        {"date": "2026-08-01", "value": 4.0},
    ])
    assert validar_serie(s, CAMINHO) == []


def test_aceita_periodo_aberto():
    s = serie(data=[{"date": "2026-11-01", "value": 5.0}])
    assert validar_serie(s, CAMINHO) == []
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

Run: `python3 -m pytest tests/test_validar.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.validar'`.

- [ ] **Step 4: Implementar `scripts/validar.py`**

Implemente as três funções com as assinaturas acima. Regras:

- `validar_arquivo` lê JSON; erro de parse vira item de erro.
- `validar_serie` valida exatamente o contrato descrito em Global Constraints.
- `data` deve ser lista não vazia; cada ponto exige `date` ISO e `value` numérico finito. Campos extras, inclusive `rate`, são ignorados.
- Duplicata é por `YYYY-MM`.
- Não validar ordem, dia 01, período aberto, `rate` nem `rate == value`.
- `validar_todos` percorre `raiz.glob("*/*.json")`, ignora a pasta `governos` e retorna um dict com chave `Path` e valor `list[str]` apenas para arquivos com erro.
- Mensagens em português, incluindo caminho e, quando aplicável, o índice do ponto.

Crie `scripts/__init__.py` vazio.

- [ ] **Step 5: Rodar os testes e confirmar que passam**

Run: `python3 -m pytest tests/test_validar.py -q`
Expected: PASS.

- [ ] **Step 6: Validar as séries reais**

Run: `python3 scripts/validar.py`
Expected: exit `0`. Se algum arquivo tiver `rate` sem `value`, ele deve falhar; os 13 publicados hoje têm `value`.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt scripts/__init__.py scripts/validar.py tests/test_validar.py
git commit -m "feat(dados): valida o contrato consumido pelo sitio"
```

---

### Task 2: Revisão metodológica dos indicadores

**Files:**
- Create: `docs/metodologia.md`

**Interfaces:**
- Consumes: fontes públicas já usadas por cada notebook.
- Produces: uma seção por série, com definição, fórmula e veredito `manter` ou `corrigir`.

- [ ] **Step 1: Criar o documento com o template**

```markdown
# Metodologia dos indicadores

## <id>

- **Definição:** uma frase, com unidade e granularidade.
- **Fonte e código:** órgão, série e URL/endpoint.
- **Fórmula atual:** como o notebook calcula hoje.
- **Fórmula proposta:** a que deveria ser usada.
- **Evidência:** documentação da fonte, definição matemática ou conferência numérica.
- **Veredito:** manter | corrigir.
- **Impacto esperado:** nenhum | quais valores/intervalos mudam.
- **Decisão pendente:** sim | não.
```

- [ ] **Step 2: Preencher as 13 séries**

Cubra todas as séries das 8 pastas: `selic-meta-acum-12m`, `selic-over-acum-12m`, `ipca-acum-12m`, `igpm-acum-12m`, `pib-real-anual`, `mvgr-nominal`, `mvgr-real`, `caged-total-mensal`, `populacao-total-anual`, `populacao-variacao-anual`, `homicidios-anual`, `homicidios-armas-fogo-anual`, `proporcao-homicidios-armas-fogo-anual`.

Investigue explicitamente:

- IPCA e IGP-M acumulados em 12 meses: soma rolante vs. composição.
- Selic Meta: o `id` diz “acum-12m”, mas o notebook publica média mensal da meta.
- Selic Over: anualização da taxa diária e janela de 12 meses.
- MVG-R real: deflator, data-base e fonte da série nominal.
- Homicídios: anos cobertos diferentes e uso de taxas vs. contagens.
- População: base populacional e anos de estimativa vs. censo.
- PIB e CAGED: confirmar que não há cálculo além da leitura da fonte.

- [ ] **Step 3: Fechar os vereditos**

Para cada série, escreva a fórmula proposta e a evidência. Onde a fórmula atual estiver correta, diga isso explicitamente; não invente correção.

- [ ] **Step 4: Checkpoint humano para mudanças de valor**

Se qualquer veredito for `corrigir` e a correção alterar valores publicados, pare e apresente ao usuário:

- a série afetada;
- a fórmula atual e a proposta;
- a fonte que sustenta a mudança;
- o impacto esperado.

Não implemente essas correções até receber aval.

- [ ] **Step 5: Commit**

```bash
git add docs/metodologia.md
git commit -m "docs(dados): registra a revisao metodologica dos indicadores"
```

---

### Task 3: Migrar o notebook piloto do PIB

**Files:**
- Modify: `pib/PIB.ipynb`
- Modify: `pib/pib-real-anual.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e decisão do PIB em `docs/metodologia.md`.
- Produces: primeiro notebook no contrato, sem cálculo próprio; serve de referência para os demais.
- Produces: `pib/pib-real-anual.json` com `unit` `percentage`/`%`/`2`, `granularity` `annual`, `source` `IBGE`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "indicatorName" pib/PIB.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Busque SGS 7326 desde `1995-01-01`.
- Exclua o ano corrente.
- Preserve a convenção de data existente.
- Escreva `pib/pib-real-anual.json` no contrato: `{date, value}`, sem `rate`.

- [ ] **Step 3: Executar e validar**

Run:
```bash
mkdir -p /tmp/nbexec
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec pib/PIB.ipynb
python3 scripts/validar.py pib/pib-real-anual.json
```
Expected: exit `0`.

- [ ] **Step 4: Comparar com o publicado**

Run: `git diff -- pib/pib-real-anual.json`
Expected: nenhuma alteração de valor; apenas remoção de `rate` e anos fechados novos, se houver. Se um valor existente mudar, pare e investigue.

- [ ] **Step 5: Confirmar que o notebook não tem legado**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
nb = json.loads(Path("pib/PIB.ipynb").read_text(encoding="utf-8"))
fonte = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
for proibido in ["/content", "indicatorName"]:
    assert proibido not in fonte, proibido
assert "1995-01-01" in fonte
print("ok: notebook migrado")
PY
```
Expected: `ok: notebook migrado`.

- [ ] **Step 6: Commit**

```bash
git add pib/PIB.ipynb pib/pib-real-anual.json
git commit -m "refactor(dados): migra pib para o pipeline auditavel"
```

---

### Task 4: Revisar e migrar o IPCA

**Files:**
- Modify: `ipca/IPCA.ipynb`
- Modify: `ipca/ipca-acum-12m.json`

**Interfaces:**
- Consumes: contrato de migração e decisão do IPCA em `docs/metodologia.md`.
- Produces: `ipca/ipca-acum-12m.json` no contrato, com `percentage`/`%`/`2`, `monthly`, `IBGE`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "indicatorName" ipca/IPCA.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Aplicar a decisão metodológica aprovada**

A decisão registrada em `docs/metodologia.md` é **usar a SGS 13522 diretamente**, sem recalcular a composição a partir da SGS 433.

- Busque SGS 13522 (IPCA acumulado em 12 meses, série oficial) desde `1995-01-01`.
- Não use a SGS 433 para gerar os valores publicados.
- Documente no markdown do notebook que o cálculo é definido pela fonte e que o notebook apenas busca, filtra e formata.
- Registre que a série passa a começar em `1995-01-01`, adicionando os 11 pontos anteriores a `1995-12`.

- [ ] **Step 3: Migrar o pipeline**

- A fonte do notebook passa a ser a SGS 13522; remova a lógica de `rolling(12).sum()` e a dependência da SGS 433 para o resultado.
- Exclua o mês corrente.
- Preserve a convenção de data existente.
- Escreva `ipca/ipca-acum-12m.json` com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec ipca/IPCA.ipynb
python3 scripts/validar.py ipca/ipca-acum-12m.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- ipca/ipca-acum-12m.json`
Expected: remoção de `rate`; valores passam a ser os oficiais da SGS 13522; entram os 11 pontos de `1995-01` a `1995-11`; meses fechados novos podem ser adicionados. Qualquer outro tipo de mudança deve ser investigado.

- [ ] **Step 6: Commit**

```bash
git add ipca/IPCA.ipynb ipca/ipca-acum-12m.json
git commit -m "refactor(dados): revisa e migra ipca para o pipeline auditavel"
```

---

### Task 5: Revisar e migrar a Selic

**Files:**
- Modify: `selic/Selic.ipynb`
- Modify: `selic/selic-meta-acum-12m.json`, `selic/selic-over-acum-12m.json`

**Interfaces:**
- Consumes: contrato de migração e decisões de Selic em `docs/metodologia.md`.
- Produces: os dois JSONs no contrato, `percentage`/`%`/`2`, `monthly`, `Banco Central do Brasil`.

- [ ] **Step 1: Confirmar o legado**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
nb = json.loads(Path("selic/Selic.ipynb").read_text(encoding="utf-8"))
fonte = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
assert "indicatorName" in fonte
assert "last_indicator_date" in fonte
print("ok: notebook legado")
PY
```
Expected: `ok: notebook legado`.

- [ ] **Step 2: Aplicar as decisões metodológicas**

- Meta: seguir a decisão de `docs/metodologia.md` (média mensal da meta vs. acumulado). Se o `id` continuar `selic-meta-acum-12m`, não renomeie: o contrato e o `sitio` dependem desse id.
- Over: seguir a decisão sobre composição da taxa diária e janela de 12 meses.
- Documente no notebook a definição e a fórmula final.

- [ ] **Step 3: Migrar o pipeline**

- Remova todas as células de atualização incremental que leem JSON e calculam a partir da última data.
- Busque SGS 432 (meta diária) e SGS 11 (over diário) desde `1995-01-01`.
- Exclua o mês corrente.
- Escreva os dois JSONs com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec selic/Selic.ipynb
python3 scripts/validar.py selic/selic-meta-acum-12m.json selic/selic-over-acum-12m.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- selic/`
Expected: remoção de `rate`; mudanças de valor apenas se a revisão metodológica tiver aprovado. Investigue qualquer outra.

- [ ] **Step 6: Commit**

```bash
git add selic/Selic.ipynb selic/selic-meta-acum-12m.json selic/selic-over-acum-12m.json
git commit -m "refactor(dados): revisa e migra selic para o pipeline auditavel"
```

---

### Task 6: Revisar e migrar o IGP-M

**Files:**
- Modify: `igp-m/IGP-M.ipynb`
- Modify: `igp-m/igpm-acum-12m.json`

**Interfaces:**
- Consumes: contrato de migração e decisão do IGP-M em `docs/metodologia.md`.
- Produces: `igp-m/igpm-acum-12m.json` no contrato, `percentage`/`%`/`2`, `monthly`, `FGV`.

- [ ] **Step 1: Confirmar a janela móvel e o legado**

Run:
```bash
grep -c "30 \* 365" igp-m/IGP-M.ipynb
grep -c "indicatorName" igp-m/IGP-M.ipynb
```
Expected: ambos maiores que `0`.

- [ ] **Step 2: Aplicar a decisão metodológica**

- Substitua a janela móvel de 30 anos por `1995-01-01`.
- Se a revisão mandar compor em vez de somar, implemente a composição; senão, preserve a fórmula.
- Documente a decisão no notebook.

- [ ] **Step 3: Migrar o pipeline**

- Busque SGS 189 desde `1995-01-01`.
- Exclua o mês corrente.
- Preserve a convenção de data existente.
- Escreva `igp-m/igpm-acum-12m.json` com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec igp-m/IGP-M.ipynb
python3 scripts/validar.py igp-m/igpm-acum-12m.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- igp-m/igpm-acum-12m.json`
Expected: remoção de `rate`; pontos anteriores ao início atual podem ser adicionados; mudanças de valor apenas se a revisão tiver aprovado.

- [ ] **Step 6: Commit**

```bash
git add igp-m/IGP-M.ipynb igp-m/igpm-acum-12m.json
git commit -m "refactor(dados): revisa e migra igp-m para o pipeline auditavel"
```

---

### Task 7: Migrar o CAGED

**Files:**
- Modify: `caged/CAGED.ipynb`
- Modify: `caged/caged-total-mensal.json`

**Interfaces:**
- Consumes: contrato de migração e decisão do CAGED em `docs/metodologia.md`.
- Produces: `caged/caged-total-mensal.json` no contrato, `number`/`vínculos`/`0`, `monthly`, `Ministério do Trabalho`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "indicatorName" caged/CAGED.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Revisar e migrar**

- Confirme em `docs/metodologia.md` que o CAGED é leitura direta do estoque, sem cálculo.
- Busque SGS 28763 desde `1995-01-01`.
- Exclua o mês corrente.
- Preserve inteiros e a convenção de data.
- Escreva o JSON com `{date, value}`, sem `rate`.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec caged/CAGED.ipynb
python3 scripts/validar.py caged/caged-total-mensal.json
```
Expected: exit `0`.

- [ ] **Step 4: Comparar com o publicado**

Run: `git diff -- caged/caged-total-mensal.json`
Expected: remoção de `rate`; nenhuma alteração de valor existente; apenas meses fechados novos, se houver.

- [ ] **Step 5: Commit**

```bash
git add caged/CAGED.ipynb caged/caged-total-mensal.json
git commit -m "refactor(dados): migra caged para o pipeline auditavel"
```

---

### Task 8: Revisar e migrar o MVG-R

**Files:**
- Modify: `mvgr/MVG-R.ipynb`
- Modify: `mvgr/mvgr-nominal.json`, `mvgr/mvgr-real.json`

**Interfaces:**
- Consumes: contrato de migração e decisões de MVG-R em `docs/metodologia.md`.
- Produces: os dois JSONs no contrato, `currency`/`R$`/`2`, `monthly`, com `source` conferido contra a fonte real.

- [ ] **Step 1: Confirmar o legado**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
nb = json.loads(Path("mvgr/MVG-R.ipynb").read_text(encoding="utf-8"))
fonte = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
assert "indicatorName" in fonte
assert "start_date_ipca = datetime(2004, 3, 1)" in fonte
print("ok: notebook legado")
PY
```
Expected: `ok: notebook legado`.

- [ ] **Step 2: Aplicar as decisões metodológicas**

- Confira a definição da série 25419 e a fonte correta (`Banco Central do Brasil` ou `IPEAdata`, conforme a evidência).
- Revise o deflator, a data-base e a normalização do IPCA.
- Documente no notebook a fórmula final e a fonte.

- [ ] **Step 3: Migrar o pipeline**

- Busque SGS 25419 (MVG-R nominal) e SGS 433 (IPCA) desde `1995-01-01`.
- Exclua o mês corrente.
- Preserve a primeira data disponível da fonte para o nominal.
- Escreva os dois JSONs com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec mvgr/MVG-R.ipynb
python3 scripts/validar.py mvgr/mvgr-nominal.json mvgr/mvgr-real.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- mvgr/`
Expected: remoção de `rate`; mudanças de valor apenas se a revisão tiver aprovado. O primeiro ponto continua sendo a primeira data válida da fonte.

- [ ] **Step 6: Commit**

```bash
git add mvgr/MVG-R.ipynb mvgr/mvgr-nominal.json mvgr/mvgr-real.json
git commit -m "refactor(dados): revisa e migra mvg-r para o pipeline auditavel"
```

---

### Task 9: Revisar e migrar a População

**Files:**
- Modify: `populacao/População.ipynb`
- Modify: `populacao/populacao-total-anual.json`, `populacao/populacao-variacao-anual.json`

**Interfaces:**
- Consumes: contrato de migração e decisão de População em `docs/metodologia.md`.
- Produces: os dois JSONs no contrato; total `number`/`hab.`/`0`; variação `percentage`/`%`/`2`; `annual`, `IBGE`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "output_dir = \"/content\"" populacao/População.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Aplicar a decisão metodológica**

- Confirme a definição da população (estimativa vs. censo) e a fórmula da variação.
- Documente no notebook a decisão e a fonte.

- [ ] **Step 3: Migrar o pipeline**

- Mantenha `ipeadatapy.timeseries("DEPIS_POP")`.
- Filtre a partir de `1995-01-01`.
- Calcule a variação anual com `pct_change() * 100`, se essa for a decisão.
- Exclua o ano corrente.
- Escreva os dois JSONs com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec "populacao/População.ipynb"
python3 scripts/validar.py populacao/populacao-total-anual.json populacao/populacao-variacao-anual.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- populacao/`
Expected: remoção de `rate`; mudanças de valor apenas se a revisão tiver aprovado.

- [ ] **Step 6: Commit**

```bash
git add "populacao/População.ipynb" populacao/populacao-total-anual.json populacao/populacao-variacao-anual.json
git commit -m "refactor(dados): revisa e migra populacao para o pipeline auditavel"
```

---

### Task 10: Revisar e migrar os Homicídios

**Files:**
- Modify: `homicidios/Homicidios.ipynb`
- Modify: `homicidios/homicidios-anual.json`, `homicidios/homicidios-armas-fogo-anual.json`, `homicidios/proporcao-homicidios-armas-fogo-anual.json`

**Interfaces:**
- Consumes: contrato de migração e decisões de Homicídios em `docs/metodologia.md`.
- Produces: os três JSONs no contrato, `annual`, `IPEA/Atlas da Violência`; taxas com `number`/`por 100 mil`/`2`; proporção com `percentage`/`%`/`2`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "output_dir = \"/content\"" homicidios/Homicidios.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Aplicar as decisões metodológicas**

- Confirme a definição das três séries e os anos cobertos.
- Verifique se a proporção usa a razão entre as taxas e se o intervalo é 0–100.
- Documente no notebook a decisão e a fonte.

- [ ] **Step 3: Migrar o pipeline**

- Mantenha as fontes e transformações aprovadas.
- Exclua o ano corrente.
- Preserve a convenção de data de cada série, inclusive o dia 15 de `homicidios-armas-fogo-anual`.
- Escreva os três JSONs com `{date, value}`, sem `rate`.

- [ ] **Step 4: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec homicidios/Homicidios.ipynb
python3 scripts/validar.py homicidios/homicidios-anual.json homicidios/homicidios-armas-fogo-anual.json homicidios/proporcao-homicidios-armas-fogo-anual.json
```
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- homicidios/`
Expected: remoção de `rate`; datas preservadas; mudanças de valor apenas se a revisão tiver aprovado.

- [ ] **Step 6: Commit**

```bash
git add homicidios/Homicidios.ipynb homicidios/homicidios-anual.json homicidios/homicidios-armas-fogo-anual.json homicidios/proporcao-homicidios-armas-fogo-anual.json
git commit -m "refactor(dados): revisa e migra homicidios para o pipeline auditavel"
```

---

### Task 11: Workflow de atualização e PR

**Files:**
- Create: `.github/workflows/atualizar-dados.yml`
- Modify: `requirements.txt` (se faltar alguma dependência de CI)

**Interfaces:**
- Consumes: `scripts/validar.py`.
- Produces: execução diária e manual que abre/atualiza o PR `dados/atualizacao` quando `git diff` acusa mudança.

- [ ] **Step 1: Validar a sintaxe antes de escrever**

Crie um arquivo temporário com a estrutura abaixo e rode `python3 -c "import yaml; yaml.safe_load(open('/tmp/workflow.yml'))"` para confirmar a sintaxe.

Estrutura obrigatória:

- `name: Atualizar dados`
- `on: schedule` com `cron: "0 11 * * *"` e `workflow_dispatch`
- `permissions: contents: write` e `pull-requests: write`
- `concurrency: group: atualizar-dados, cancel-in-progress: false`
- job `atualizar` em `ubuntu-latest`, `timeout-minutes: 30`
- steps: checkout, setup-python 3.12 com cache pip, `pip install -r requirements.txt`, `pytest -q`, loop de `jupyter nbconvert --execute` para `*/*.ipynb`, `python3 scripts/validar.py`, detecção de diff, upload de artifact de `/tmp/nbexec`, criação do PR.

- [ ] **Step 2: Implementar o workflow**

Regras:

- Detectar mudança com um step com `id: diff`:
  ```bash
  if git diff --quiet; then
    echo "mudou=false" >> "$GITHUB_OUTPUT"
  else
    echo "mudou=true" >> "$GITHUB_OUTPUT"
  fi
  ```
- Todos os steps de publicação usam `if: steps.diff.outputs.mudou == 'true'`.
- Configurar `user.name` e `user.email` do bot.
- `git checkout -B dados/atualizacao`.
- Adicionar apenas séries: `git add -- '*/*.json' ':!governos/*'`.
- Commit fixo: `dados: atualizacao`.
- `git push --force origin dados/atualizacao`.
- Gerar o corpo do PR com:
  ```bash
  {
    echo "## Alterações"
    echo
    echo "O diff é a fonte de verdade. Revise antes de mergear."
    echo
    echo "- [ ] Nenhum valor de data já publicada foi alterado (apenas acréscimos)."
    echo "- [ ] Se houver valor antigo alterado, a mudança foi conferida na fonte."
    echo
    echo '```text'
    git diff --stat
    echo '```'
  } > /tmp/pr.md
  ```
- Se o PR existir, `gh pr edit`; senão, `gh pr create --base main --head dados/atualizacao`.
- Usar `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.
- `actions/upload-artifact@v4` com `if: always()` e `path: /tmp/nbexec`.
- Não usar `pull_request_target`.
- Não fazer merge automático.
- Não criar labels nem classificar o diff.

- [ ] **Step 3: Verificar o workflow localmente**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-dados.yml'))"
python3 scripts/validar.py
git diff --quiet; echo "git-diff-exit=$?"
```
Expected: YAML carrega, validador exit `0`, `git-diff-exit=0` (sem mudanças).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/atualizar-dados.yml requirements.txt
git commit -m "ci(dados): executa notebooks e abre pr de atualizacao"
```

---

### Task 12: Remover `rate` e validar o ciclo completo

**Files:**
- Modify: todos os JSONs publicados que ainda tiverem `rate` (o IPCA já está sem)
- Modify: `AGENTS.md`

**Interfaces:**
- Consumes: todas as tasks anteriores.
- Produces: repositório sem `rate`, com validação e PR como únicas ferramentas de contrato.

- [ ] **Step 1: Confirmar que o conversor já saiu**

Run:
```bash
test ! -e converter-schema-canonico.py && echo "ok: conversor ausente"
grep -R "converter-schema-canonico" --exclude-dir=.git --exclude-dir=docs . || true
```
Expected: `ok: conversor ausente` e nenhuma referência fora de `docs/` e do histórico. O conversor foi removido no piloto do IPCA.

- [ ] **Step 2: Remover `rate` dos JSONs que ainda tiverem**

Run:
```bash
python3 - <<'PY'
import glob, json
from pathlib import Path

for caminho in sorted(glob.glob("*/*.json")):
    p = Path(caminho)
    d = json.loads(p.read_text(encoding="utf-8"))
    for ponto in d["data"]:
        ponto.pop("rate", None)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
PY
```

- [ ] **Step 3: Confirmar que só `rate` saiu**

Run:
```bash
python3 - <<'PY'
import glob, json, subprocess

for caminho in sorted(glob.glob("*/*.json")):
    antes = json.loads(subprocess.check_output(["git", "show", f"HEAD:{caminho}"], text=True))
    depois = json.loads(open(caminho, encoding="utf-8").read())
    a = [(p["date"], p["value"]) for p in antes["data"]]
    b = [(p["date"], p["value"]) for p in depois["data"]]
    assert a == b, caminho
print("ok: valores preservados")
PY
```
Expected: `ok: valores preservados`.

- [ ] **Step 4: Rodar todos os testes e o validador**

Run:
```bash
python3 -m pytest -q
python3 scripts/validar.py
```
Expected: PASS e exit `0`.

- [ ] **Step 5: Executar todos os notebooks**

Run:
```bash
mkdir -p /tmp/nbexec-todos
for nb in */*.ipynb; do
  jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec-todos "$nb" || exit 1
done
python3 scripts/validar.py
```
Expected: todos executam e o validador passa. Se a fonte estiver fora do ar, registre a falha e não commite dados parciais.

- [ ] **Step 6: Conferir que não há alteração inesperada**

Run: `git status --short && git diff --stat`
Expected: nenhum valor alterado além das correções metodológicas já aprovadas; nenhum `/tmp` versionado.

- [ ] **Step 7: Atualizar `AGENTS.md`**

Remova qualquer menção a `rate == value` e documente o estado final:

```text
- O contrato de dados é o validado em `sitio/app/src/data/validate.js`.
- Os JSONs publicam `{date, value}`; `rate` não faz parte do contrato.
- `python3 scripts/validar.py` valida o contrato de todas as séries.
- Toda execução recalcula a série inteira; não há modo incremental.
- Notebooks publicam apenas períodos encerrados.
- Revisões históricas e correções metodológicas aparecem no diff do PR e exigem revisão humana.
```

- [ ] **Step 8: Commit**

```bash
git add AGENTS.md
git add -- '*/*.json'
git commit -m "chore(dados): publica somente value em todas as series"
```

---

## Self-Review

- **Cobertura do spec:** contrato do `sitio` (Task 1), revisão metodológica (Task 2), piloto sem cálculo (Task 3), lógica e migração de cada pasta (Tasks 4–10), workflow/PR (Task 11), remoção de `rate` e documentação (Task 12). O conversor foi removido no piloto.
- **Tipos e nomes:** `validar_serie`, `validar_arquivo` e `validar_todos` são usados com as mesmas assinaturas nas tasks seguintes.
- **Contrato:** nenhum teste exige dia 01, ordem, período fechado ou `rate`; todos exigem `value`.
- **Proporção:** as tasks de migração referenciam o contrato e a decisão metodológica em vez de repetir o código.
