# Pipeline de indicadores Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fazer cada notebook ser a explicação executável e o único motor de coleta/cálculo dos indicadores, com publicação via PR, validação automática e detecção explícita de revisões históricas.

**Architecture:** Toda execução recalcula a série inteira desde `1995-01-01`, publica apenas períodos encerrados e escreve o JSON canônico diretamente. O GitHub Actions executa os notebooks, valida os arquivos, classifica o diff e abre/atualiza um PR. `scripts/` contém somente validação e classificação de diff, nunca lógica de indicador.

**Tech Stack:** Python 3.12, Jupyter/nbconvert, pandas, `python-bcb`, `ipeadatapy`, requests, pytest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md`

## Global Constraints

- Python 3.12.
- Toda série coleta desde `1995-01-01`; a publicação começa no primeiro ponto calculável.
- Somente períodos encerrados são publicados: mês anterior ao atual, ano anterior ao atual.
- Datas no formato `YYYY-MM-01`.
- No máximo um ponto por mês/ano; ordem ascendente; sem duplicatas.
- `rate === value` em todos os pontos.
- Schema: `schema: 1`, `id`, `unit`, `granularity`, `source`, `data`.
- Não existem modos `update`/`rebuild`; toda execução recalcula tudo.
- Um notebook pode publicar vários JSONs.
- Séries derivadas são calculadas no próprio notebook, a partir das fontes brutas.
- `scripts/` não pode buscar nem calcular indicador.
- `governos/` não é tocado por este plano.
- Valores existentes não podem mudar sem justificativa e revisão; datas podem ser normalizadas para o dia 01.
- Commit messages: Conventional Commits em português, escopo `dados`.

## Review Focus

- Série mensal cujo último ponto é o mês corrente: deve ser excluído, não publicado.
- Série anual cujo último ponto é o ano corrente: deve ser excluído, não publicado.
- Série acumulada de 12 meses: o primeiro ponto só existe após 12 meses de aquecimento, sem `NaN`.
- Arquivo novo, ainda ausente no `HEAD`: o diff deve classificá-lo como `novo`, não quebrar.
- Revisão de metadado (`source`, `unit`, `granularity`, `schema`) ou remoção de ponto: deve virar `revisao`, nunca `acrescimo`.
- Série derivada: deve ser recalculada da fonte bruta, sem ler o JSON publicado de outra pasta.

---

## File Structure

- `requirements.txt`: dependências fixadas do CI e do ambiente local.
- `scripts/__init__.py`: permite importar os scripts nos testes.
- `scripts/validar.py`: contrato do JSON publicado; não corrige nada.
- `scripts/diff_series.py`: compara `HEAD` com a árvore e classifica o diff.
- `tests/test_validar.py`: testes do validador.
- `tests/test_diff_series.py`: testes da classificação.
- `.github/workflows/atualizar-dados.yml`: execução diária, validação e PR.
- `<pasta>/*.ipynb`: notebooks migrados, um por pasta, publicando N JSONs.
- `<pasta>/*.json`: dados publicados.

### Contrato de migração de notebook

Todo notebook migrado deve:

1. Abrir com markdown declarando fonte, URL/endpoint, códigos das séries, unidade, granularidade e período coberto.
2. Resolver a raiz uma vez:
   ```python
   from pathlib import Path
   import os
   RAIZ = Path(os.environ.get("DADOS_RAIZ", Path.cwd()))
   ```
3. Buscar a fonte completa desde `1995-01-01`, sem ler JSON publicado e sem trecho de atualização incremental.
4. Manter as transformações e fórmulas existentes; a migração não é uma reescrita metodológica.
5. Filtrar períodos abertos antes de montar os pontos.
6. Montar os pontos como `{"date": "YYYY-MM-01", "rate": valor, "value": valor}`.
7. Escrever todos os JSONs da pasta com `json.dump(..., ensure_ascii=False, indent=2)`.
8. Terminar com uma célula de validação inline que falha se houver data fora do dia 01, duplicata, desordem, `rate != value` ou valor não finito.
9. Não conter `/content`, `indicatorName` nem leitura de arquivo existente para decidir o que buscar.

---

### Task 1: Validador do contrato

**Files:**
- Create: `requirements.txt`
- Create: `scripts/__init__.py`
- Create: `scripts/validar.py`
- Test: `tests/test_validar.py`

**Interfaces:**
- Produces: `validar_serie(serie: dict, caminho: Path, hoje: date | None = None) -> list[str]`
- Produces: `validar_arquivo(caminho: Path, hoje: date | None = None) -> list[str]`
- Produces: `validar_todos(raiz: Path, hoje: date | None = None) -> dict[Path, list[str]]`
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
from datetime import date
from pathlib import Path

from scripts.validar import validar_serie

HOJE = date(2026, 11, 1)
CAMINHO = Path("ipca/ipca-acum-12m.json")


def serie(**over):
    base = {
        "schema": 1,
        "id": "ipca-acum-12m",
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "IBGE",
        "data": [{"date": "2026-09-01", "rate": 5.0, "value": 5.0}],
    }
    base.update(over)
    return base


def test_serie_valida():
    assert validar_serie(serie(), CAMINHO, hoje=HOJE) == []


def test_id_divergente():
    erros = validar_serie(serie(id="outro"), CAMINHO, hoje=HOJE)
    assert any("id" in e for e in erros)


def test_data_fora_do_dia_01():
    s = serie(data=[{"date": "2026-09-15", "rate": 5.0, "value": 5.0}])
    assert any("dia 01" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_mes_repetido():
    s = serie(data=[
        {"date": "2026-08-01", "rate": 5.0, "value": 5.0},
        {"date": "2026-08-01", "rate": 6.0, "value": 6.0},
    ])
    assert any("repetido" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_fora_de_ordem():
    s = serie(data=[
        {"date": "2026-09-01", "rate": 5.0, "value": 5.0},
        {"date": "2026-08-01", "rate": 4.0, "value": 4.0},
    ])
    assert any("ordem" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_rate_diferente_de_value():
    s = serie(data=[{"date": "2026-09-01", "rate": 5.0, "value": 5.1}])
    assert any("rate" in e and "value" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_mes_em_curso():
    s = serie(data=[{"date": "2026-11-01", "rate": 5.0, "value": 5.0}])
    assert any("em curso" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_ano_em_curso():
    s = serie(
        granularity="annual",
        data=[{"date": "2026-01-01", "rate": 2.0, "value": 2.0}],
    )
    assert any("em curso" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))


def test_valor_nao_finito():
    s = serie(data=[{"date": "2026-09-01", "rate": float("nan"), "value": float("nan")}])
    assert any("finito" in e for e in validar_serie(s, CAMINHO, hoje=HOJE))
```

- [ ] **Step 3: Rodar os testes e confirmar que falham**

Run: `python3 -m pytest tests/test_validar.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.validar'`.

- [ ] **Step 4: Implementar `scripts/validar.py`**

Implemente as três funções com as assinaturas acima. Regras:

- `validar_arquivo` lê JSON; erro de parse vira item de erro.
- `validar_serie` valida schema, campos, `id == caminho.stem`, tipos, datas ISO no dia 01, ordem, duplicata por `YYYY-MM`, `rate == value`, números finitos e período aberto em relação a `hoje`.
- Verifique finitude antes de comparar `rate` e `value`, para que `NaN` produza a mensagem de “valor não finito”.
- Período aberto: mensal se `(d.year, d.month) >= (hoje.year, hoje.month)`; anual se `d.year >= hoje.year`.
- `validar_todos` percorre `raiz.glob("*/*.json")`, ignora a pasta `governos` e retorna um dict com chave `Path` e valor `list[str]` apenas para arquivos com erro.
- Mensagens em português, incluindo caminho e data quando aplicável.

Crie `scripts/__init__.py` vazio.

- [ ] **Step 5: Rodar os testes e confirmar que passam**

Run: `python3 -m pytest tests/test_validar.py -q`
Expected: PASS.

- [ ] **Step 6: Validar uma série real**

Run: `python3 scripts/validar.py ipca/ipca-acum-12m.json`
Expected: exit `0` e mensagem de sucesso.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt scripts/__init__.py scripts/validar.py tests/test_validar.py
git commit -m "feat(dados): adiciona validador do contrato das séries"
```

---

### Task 2: Classificador de diff

**Files:**
- Create: `scripts/diff_series.py`
- Test: `tests/test_diff_series.py`

**Interfaces:**
- Consumes: schema das séries da Task 1.
- Produces: `comparar(antes: dict | None, depois: dict | None) -> dict`
- Produces: `classificar(antes: dict | None, depois: dict | None) -> str`
- Produces: `comparar_raiz(raiz: Path) -> dict`
- Produces CLI: `python3 scripts/diff_series.py [--json | --markdown]`

`comparar` retorna exatamente:

```python
{
    "classificacao": "novo" | "acrescimo" | "revisao" | "sem_mudanca",
    "adicionadas": ["YYYY-MM-DD"],
    "alteradas": ["YYYY-MM-DD"],
    "removidas": ["YYYY-MM-DD"],
    "metadados_alterados": ["source", "unit"],
}
```

`comparar_raiz` retorna exatamente:

```python
{
    "series": [{"caminho": "ipca/ipca-acum-12m.json", **resultado_de_comparar}],
    "tem_mudanca": True,
    "tem_revisao": False,
}
```

- [ ] **Step 1: Escrever os testes do classificador**

Crie `tests/test_diff_series.py`:

```python
from scripts.diff_series import classificar, comparar

META = {
    "schema": 1,
    "id": "serie",
    "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
    "granularity": "monthly",
    "source": "IBGE",
}


def serie(*pontos, **over):
    base = {**META, "data": [{"date": d, "rate": v, "value": v} for d, v in pontos]}
    base.update(over)
    return base


def test_arquivo_novo():
    assert classificar(None, serie(("2026-09-01", 5.0))) == "novo"


def test_acrescimo():
    antes = serie(("2026-08-01", 4.0))
    depois = serie(("2026-08-01", 4.0), ("2026-09-01", 5.0))
    assert classificar(antes, depois) == "acrescimo"


def test_revisao_de_valor():
    antes = serie(("2026-08-01", 4.0))
    depois = serie(("2026-08-01", 4.1))
    assert classificar(antes, depois) == "revisao"


def test_revisao_de_metadado():
    antes = serie(("2026-08-01", 4.0))
    depois = serie(("2026-08-01", 4.0), source="FGV")
    assert classificar(antes, depois) == "revisao"


def test_remocao_de_ponto():
    antes = serie(("2026-08-01", 4.0), ("2026-09-01", 5.0))
    depois = serie(("2026-09-01", 5.0))
    assert classificar(antes, depois) == "revisao"


def test_sem_mudanca():
    antes = serie(("2026-08-01", 4.0))
    assert classificar(antes, serie(("2026-08-01", 4.0))) == "sem_mudanca"


def test_detalhe_do_diff():
    antes = serie(("2026-08-01", 4.0), ("2026-09-01", 5.0))
    depois = serie(("2026-08-01", 4.1), ("2026-10-01", 6.0))
    r = comparar(antes, depois)
    assert r["alteradas"] == ["2026-08-01"]
    assert r["removidas"] == ["2026-09-01"]
    assert r["adicionadas"] == ["2026-10-01"]
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `python3 -m pytest tests/test_diff_series.py -q`
Expected: FAIL com `ModuleNotFoundError: No module named 'scripts.diff_series'`.

- [ ] **Step 3: Implementar `scripts/diff_series.py`**

Regras de classificação:

- `antes is None` e `depois` presente: `novo`.
- `depois is None`: `revisao`.
- Metadados comparados: `schema`, `id`, `unit`, `granularity`, `source`; qualquer diferença: `revisao`.
- Ponto comparado pelo par `(rate, value)` na mesma data.
- Data removida ou valor alterado: `revisao`.
- Só datas novas: `acrescimo`.
- Nada mudou: `sem_mudanca`.

`comparar_raiz`:

- Lê os arquivos atuais de `raiz.glob("*/*.json")`, ignorando `governos`.
- Lê a versão de `HEAD` com `git show HEAD:<caminho-relativo>`; arquivo ausente vira `None`.
- Inclui também arquivos que existiam no `HEAD` e desapareceram.
- `--json` imprime o resumo; `--markdown` imprime um corpo de PR com uma seção por série; sem flag, imprime resumo legível.
- Exit `0` mesmo sem mudanças; exit `2` apenas para erro de Git ou JSON.

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `python3 -m pytest tests/test_diff_series.py -q`
Expected: PASS.

- [ ] **Step 5: Conferir o diff real do repositório**

Run: `python3 scripts/diff_series.py --json`
Expected: todas as séries como `sem_mudanca`, `tem_mudanca: false`.

- [ ] **Step 6: Commit**

```bash
git add scripts/diff_series.py tests/test_diff_series.py
git commit -m "feat(dados): classifica acrescimos e revisoes historicas"
```

---

### Task 3: Normalizar datas de homicídios por armas de fogo

**Files:**
- Modify: `homicidios/homicidios-armas-fogo-anual.json`

**Interfaces:**
- Consumes: `scripts/validar.py` da Task 1.
- Produces: série com todas as datas no dia 01, pronta para o validador global passar.

- [ ] **Step 1: Confirmar o estado atual**

Run:
```bash
python3 - <<'PY'
import json
d = json.load(open("homicidios/homicidios-armas-fogo-anual.json"))
assert {p["date"][8:10] for p in d["data"]} == {"15"}
print("ok: todas as datas no dia 15")
PY
```
Expected: `ok: todas as datas no dia 15`.

- [ ] **Step 2: Normalizar as datas sem tocar nos valores**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
p = Path("homicidios/homicidios-armas-fogo-anual.json")
d = json.loads(p.read_text(encoding="utf-8"))
for ponto in d["data"]:
    ponto["date"] = ponto["date"][:8] + "01"
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
PY
```

- [ ] **Step 3: Validar todas as séries**

Run: `python3 scripts/validar.py`
Expected: exit `0`, sem arquivos com erro.

- [ ] **Step 4: Conferir que só as datas mudaram**

Run: `git diff --stat -- homicidios/homicidios-armas-fogo-anual.json && git diff --word-diff -- homicidios/homicidios-armas-fogo-anual.json`
Expected: apenas `15` → `01` nas datas; nenhum `rate`/`value` alterado.

- [ ] **Step 5: Commit**

```bash
git add homicidios/homicidios-armas-fogo-anual.json
git commit -m "fix(dados): normaliza datas anuais para o dia 01"
```

---

### Task 4: Migrar o notebook piloto do IPCA

**Files:**
- Modify: `ipca/IPCA.ipynb`
- Modify: `ipca/ipca-acum-12m.json` (somente se houver ponto novo legítimo)

**Interfaces:**
- Consumes: contrato de migração de notebook deste plano.
- Produces: primeiro notebook no contrato; serve de referência para as Tasks 5–11.
- Produces: `ipca/ipca-acum-12m.json` canônico, mensal, `unit.type = percentage`, `symbol = %`, `decimals = 2`, `source = IBGE`.

- [ ] **Step 1: Confirmar que o notebook ainda está no formato antigo**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
nb = json.loads(Path("ipca/IPCA.ipynb").read_text(encoding="utf-8"))
fonte = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
assert "indicatorName" in fonte
assert "1995-01-01" in fonte
print("ok: notebook legado")
PY
```
Expected: `ok: notebook legado`.

- [ ] **Step 2: Migrar o notebook**

Substitua as células de coleta, cálculo e escrita para:

- buscar SGS 433 com `start="1995-01-01"` e `end` igual a hoje;
- calcular `rolling(12).sum()` sobre a série mensal e remover `NaN`;
- excluir o mês corrente de `date.today()`;
- escrever `ipca/ipca-acum-12m.json` com o schema canônico.

Use este padrão na célula final, adaptando nomes:

```python
from pathlib import Path
import json
import math
import os
from datetime import date

RAIZ = Path(os.environ.get("DADOS_RAIZ", Path.cwd()))
ARQUIVO = RAIZ / "ipca" / "ipca-acum-12m.json"
hoje = date.today()

pontos = [
    {"date": indice.strftime("%Y-%m-01"), "rate": float(valor), "value": float(valor)}
    for indice, valor in serie_12m.items()
    if valor == valor and (indice.year, indice.month) < (hoje.year, hoje.month)
]
pontos.sort(key=lambda p: p["date"])

serie = {
    "schema": 1,
    "id": "ipca-acum-12m",
    "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
    "granularity": "monthly",
    "source": "IBGE",
    "data": pontos,
}

assert pontos, "série vazia"
assert [p["date"] for p in pontos] == sorted(p["date"] for p in pontos)
assert len({p["date"][:7] for p in pontos}) == len(pontos)
assert all(p["date"].endswith("-01") for p in pontos)
assert all(math.isfinite(p["rate"]) and p["rate"] == p["value"] for p in pontos)

ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
ARQUIVO.write_text(json.dumps(serie, ensure_ascii=False, indent=2), encoding="utf-8")
```

- [ ] **Step 3: Executar o notebook com kernel novo**

Run:
```bash
mkdir -p /tmp/nbexec
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec ipca/IPCA.ipynb
```
Expected: exit `0`, sem exceção.

- [ ] **Step 4: Validar o JSON gerado**

Run: `python3 scripts/validar.py ipca/ipca-acum-12m.json`
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- ipca/ipca-acum-12m.json`
Expected: nenhuma mudança de valor; apenas acréscimos legítimos se a fonte tiver publicado meses novos. Qualquer alteração de valor existente deve ser investigada antes de seguir.

- [ ] **Step 6: Confirmar que o notebook não tem legado**

Run:
```bash
python3 - <<'PY'
import json
from pathlib import Path
nb = json.loads(Path("ipca/IPCA.ipynb").read_text(encoding="utf-8"))
fonte = "\n".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")
for proibido in ["/content", "indicatorName"]:
    assert proibido not in fonte, proibido
assert "1995-01-01" in fonte
print("ok: notebook migrado")
PY
```
Expected: `ok: notebook migrado`.

- [ ] **Step 7: Commit**

```bash
git add ipca/IPCA.ipynb ipca/ipca-acum-12m.json
git commit -m "refactor(dados): migra ipca para o pipeline auditavel"
```

---

### Task 5: Migrar o notebook da Selic

**Files:**
- Modify: `selic/Selic.ipynb`
- Modify: `selic/selic-meta-acum-12m.json`, `selic/selic-over-acum-12m.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: `selic-meta-acum-12m.json` e `selic-over-acum-12m.json` canônicos, mensais, `percentage`, `%`, `decimals = 2`, `source = Banco Central do Brasil`.

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

- [ ] **Step 2: Migrar o notebook**

- Remova todas as células de atualização incremental que leem `selic-*.json` e calculam a partir da última data.
- Busque SGS 432 (meta diária) e SGS 11 (over diário) desde `1995-01-01`.
- Preserve as fórmulas existentes: meta = média mensal da série diária; over = produto mensal dos fatores diários e produto rolante de 12 meses, convertido para porcentagem.
- Exclua o mês corrente.
- Escreva os dois JSONs canônicos com o padrão da Task 4.

- [ ] **Step 3: Executar o notebook**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec selic/Selic.ipynb
```
Expected: exit `0`.

- [ ] **Step 4: Validar os dois JSONs**

Run: `python3 scripts/validar.py selic/selic-meta-acum-12m.json selic/selic-over-acum-12m.json`
Expected: exit `0`.

- [ ] **Step 5: Comparar com o publicado**

Run: `git diff -- selic/`
Expected: nenhuma alteração de valor existente; apenas acréscimos de meses fechados, se houver.

- [ ] **Step 6: Commit**

```bash
git add selic/Selic.ipynb selic/selic-meta-acum-12m.json selic/selic-over-acum-12m.json
git commit -m "refactor(dados): migra selic para o pipeline auditavel"
```

---

### Task 6: Migrar o notebook do IGP-M

**Files:**
- Modify: `igp-m/IGP-M.ipynb`
- Modify: `igp-m/igpm-acum-12m.json` (esperado: acréscimo de pontos anteriores a 1996-07)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: `igp-m/igpm-acum-12m.json` canônico, mensal, `percentage`, `%`, `decimals = 2`, `source = FGV`.

- [ ] **Step 1: Confirmar a janela móvel**

Run:
```bash
grep -c "30 \* 365" igp-m/IGP-M.ipynb
```
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Substitua a janela móvel de 30 anos por `1995-01-01`.
- Busque SGS 189 desde essa data.
- Preserve o cálculo de soma rolante de 12 meses.
- Exclua o mês corrente.
- Escreva `igp-m/igpm-acum-12m.json` no schema canônico.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec igp-m/IGP-M.ipynb
python3 scripts/validar.py igp-m/igpm-acum-12m.json
```
Expected: exit `0` nos dois comandos.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- igp-m/igpm-acum-12m.json`
Expected: pontos anteriores a `1996-07-01` podem ser adicionados; nenhum valor existente pode mudar. Se houver remoção, pare e investigue.

- [ ] **Step 5: Commit**

```bash
git add igp-m/IGP-M.ipynb igp-m/igpm-acum-12m.json
git commit -m "refactor(dados): migra igp-m para o pipeline auditavel"
```

---

### Task 7: Migrar o notebook do PIB

**Files:**
- Modify: `pib/PIB.ipynb`
- Modify: `pib/pib-real-anual.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: `pib/pib-real-anual.json` canônico, anual, `percentage`, `%`, `decimals = 2`, `source = IBGE`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "indicatorName" pib/PIB.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Busque SGS 7326 desde `1995-01-01`.
- Exclua o ano corrente.
- Preserve o valor anual publicado.
- Escreva `pib/pib-real-anual.json` no schema canônico.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec pib/PIB.ipynb
python3 scripts/validar.py pib/pib-real-anual.json
```
Expected: exit `0`.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- pib/pib-real-anual.json`
Expected: nenhuma alteração de valor; apenas anos novos encerrados, se houver.

- [ ] **Step 5: Commit**

```bash
git add pib/PIB.ipynb pib/pib-real-anual.json
git commit -m "refactor(dados): migra pib para o pipeline auditavel"
```

---

### Task 8: Migrar o notebook do CAGED

**Files:**
- Modify: `caged/CAGED.ipynb`
- Modify: `caged/caged-total-mensal.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: `caged/caged-total-mensal.json` canônico, mensal, `number`, `vínculos`, `decimals = 0`, `source = Ministério do Trabalho`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "indicatorName" caged/CAGED.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Busque SGS 28763 desde `1995-01-01`.
- Preserve o estoque mensal como inteiro.
- Exclua o mês corrente.
- Escreva `caged/caged-total-mensal.json` no schema canônico.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec caged/CAGED.ipynb
python3 scripts/validar.py caged/caged-total-mensal.json
```
Expected: exit `0`.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- caged/caged-total-mensal.json`
Expected: nenhuma alteração de valor existente; apenas meses fechados novos, se houver.

- [ ] **Step 5: Commit**

```bash
git add caged/CAGED.ipynb caged/caged-total-mensal.json
git commit -m "refactor(dados): migra caged para o pipeline auditavel"
```

---

### Task 9: Migrar o notebook do MVG-R

**Files:**
- Modify: `mvgr/MVG-R.ipynb`
- Modify: `mvgr/mvgr-nominal.json`, `mvgr/mvgr-real.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: `mvgr/mvgr-nominal.json` e `mvgr/mvgr-real.json` canônicos, mensais, `currency`, `R$`, `decimals = 2`, `source = Banco Central do Brasil`.

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

- [ ] **Step 2: Migrar o notebook**

- Busque SGS 25419 (MVG-R nominal) e SGS 433 (IPCA) desde `1995-01-01`.
- Preserve a fórmula de MVG-R real: fator de IPCA, índice acumulado, normalização pela primeira data válida do MVG-R e divisão do nominal pelo índice normalizado.
- Exclua o mês corrente dos dois JSONs.
- Escreva os dois JSONs canônicos no padrão da Task 4.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec mvgr/MVG-R.ipynb
python3 scripts/validar.py mvgr/mvgr-nominal.json mvgr/mvgr-real.json
```
Expected: exit `0`.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- mvgr/`
Expected: nenhuma alteração de valor existente; apenas meses fechados novos, se houver. O primeiro ponto do MVG-R continua sendo a primeira data disponível na fonte, mesmo com coleta desde 1995.

- [ ] **Step 5: Commit**

```bash
git add mvgr/MVG-R.ipynb mvgr/mvgr-nominal.json mvgr/mvgr-real.json
git commit -m "refactor(dados): migra mvg-r para o pipeline auditavel"
```

---

### Task 10: Migrar o notebook da População

**Files:**
- Modify: `populacao/População.ipynb`
- Modify: `populacao/populacao-total-anual.json`, `populacao/populacao-variacao-anual.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: os dois JSONs canônicos, anuais; total com `number`, `hab.`, `decimals = 0`; variação com `percentage`, `%`, `decimals = 2`; `source = IBGE`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "output_dir = \"/content\"" populacao/População.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Mantenha a fonte `ipeadatapy.timeseries("DEPIS_POP")`.
- Filtre a partir de `1995-01-01`.
- Calcule a variação anual com `pct_change() * 100`.
- Exclua o ano corrente dos dois JSONs.
- Escreva os dois JSONs canônicos.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec "populacao/População.ipynb"
python3 scripts/validar.py populacao/populacao-total-anual.json populacao/populacao-variacao-anual.json
```
Expected: exit `0`.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- populacao/`
Expected: nenhuma alteração de valor existente; apenas anos fechados novos, se houver.

- [ ] **Step 5: Commit**

```bash
git add "populacao/População.ipynb" populacao/populacao-total-anual.json populacao/populacao-variacao-anual.json
git commit -m "refactor(dados): migra populacao para o pipeline auditavel"
```

---

### Task 11: Migrar o notebook de Homicídios

**Files:**
- Modify: `homicidios/Homicidios.ipynb`
- Modify: `homicidios/homicidios-anual.json`, `homicidios/homicidios-armas-fogo-anual.json`, `homicidios/proporcao-homicidios-armas-fogo-anual.json` (somente acréscimos legítimos)

**Interfaces:**
- Consumes: contrato de migração de notebook e padrão da Task 4.
- Produces: os três JSONs canônicos, anuais, `number`/`por 100 mil` para as taxas e `percentage`/`%` para a proporção, `source = IPEA/Atlas da Violência`.

- [ ] **Step 1: Confirmar o legado**

Run: `grep -c "output_dir = \"/content\"" homicidios/Homicidios.ipynb`
Expected: valor maior que `0`.

- [ ] **Step 2: Migrar o notebook**

- Mantenha as fontes e transformações existentes da API do Atlas da Violência.
- Calcule a proporção a partir das duas séries no próprio notebook.
- Exclua o ano corrente dos três JSONs.
- Force todas as datas para `YYYY-01-01`, inclusive a série de armas de fogo.
- Escreva os três JSONs canônicos.

- [ ] **Step 3: Executar e validar**

Run:
```bash
jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec homicidios/Homicidios.ipynb
python3 scripts/validar.py homicidios/homicidios-anual.json homicidios/homicidios-armas-fogo-anual.json homicidios/proporcao-homicidios-armas-fogo-anual.json
```
Expected: exit `0`.

- [ ] **Step 4: Revisar o diff**

Run: `git diff -- homicidios/`
Expected: `homicidios-armas-fogo-anual.json` mantém as datas já normalizadas na Task 3; nenhum valor existente muda.

- [ ] **Step 5: Commit**

```bash
git add homicidios/Homicidios.ipynb homicidios/homicidios-anual.json homicidios/homicidios-armas-fogo-anual.json homicidios/proporcao-homicidios-armas-fogo-anual.json
git commit -m "refactor(dados): migra homicidios para o pipeline auditavel"
```

---

### Task 12: Workflow de atualização e PR

**Files:**
- Create: `.github/workflows/atualizar-dados.yml`
- Modify: `requirements.txt` (se faltar alguma dependência de CI)

**Interfaces:**
- Consumes: `scripts/validar.py` e `scripts/diff_series.py`.
- Produces: execução diária e manual que abre/atualiza o PR `dados/atualizacao`.

- [ ] **Step 1: Validar o YAML antes de escrever**

Crie um arquivo temporário com a estrutura abaixo e rode `python3 -c "import yaml; yaml.safe_load(open('/tmp/workflow.yml'))"` para confirmar a sintaxe.

Estrutura obrigatória:

- `name: Atualizar dados`
- `on: schedule` com `cron: "0 11 * * *"` e `workflow_dispatch`
- `permissions: contents: write` e `pull-requests: write`
- `concurrency: group: atualizar-dados, cancel-in-progress: false`
- job `atualizar` em `ubuntu-latest`, `timeout-minutes: 30`
- steps: checkout, setup-python 3.12 com cache pip, `pip install -r requirements.txt`, `pytest -q`, loop de `jupyter nbconvert --execute` para `*/*.ipynb`, `python3 scripts/validar.py`, `python3 scripts/diff_series.py --json`, upload de artifact de `/tmp/nbexec`, criação do PR.

- [ ] **Step 2: Implementar o workflow**

Regras:

- Se `tem_mudanca` for `false`, encerrar sem commit.
- Configurar `user.name` e `user.email` do bot.
- `git checkout -B dados/atualizacao`.
- Adicionar apenas séries: `git add -- '*/*.json' ':!governos/*'`.
- Commit com `dados: atualizacao` ou `dados: revisao historica` conforme `tem_revisao`.
- `git push --force origin dados/atualizacao`.
- Gerar o corpo com `python3 scripts/diff_series.py --markdown > /tmp/pr.md`.
- Criar labels se não existirem:
  ```bash
  gh label create atualizacao-rotina --color 0E8A16 || true
  gh label create revisao-historica --color B60205 || true
  ```
- Se o PR existir, `gh pr edit`; senão, `gh pr create --base main --head dados/atualizacao`.
- Remover as duas labels antes de aplicar a correta.
- Usar `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}`.
- `actions/upload-artifact@v4` com `if: always()` e `path: /tmp/nbexec`.
- Não usar `pull_request_target`.
- Não fazer merge automático.

- [ ] **Step 3: Verificar o workflow localmente**

Run:
```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-dados.yml'))"
python3 scripts/diff_series.py --json
python3 scripts/validar.py
```
Expected: YAML carrega, diff `tem_mudanca: false` e validador exit `0`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/atualizar-dados.yml requirements.txt
git commit -m "ci(dados): executa notebooks e abre pr de atualizacao"
```

---

### Task 13: Aposentar o conversor e validar o ciclo completo

**Files:**
- Delete: `converter-schema-canonico.py`
- Modify: `AGENTS.md` se as instruções sobre o conversor ficarem obsoletas

**Interfaces:**
- Consumes: todas as tasks anteriores.
- Produces: repositório sem o conversor, com validação e diff como únicas ferramentas de contrato.

- [ ] **Step 1: Confirmar que o conversor não é mais necessário**

Run:
```bash
grep -R "converter-schema-canonico" --exclude-dir=.git . || true
```
Expected: nenhuma referência fora de `docs/` e do histórico.

- [ ] **Step 2: Remover o conversor**

```bash
git rm converter-schema-canonico.py
```

- [ ] **Step 3: Rodar todos os testes e o validador**

Run:
```bash
python3 -m pytest -q
python3 scripts/validar.py
```
Expected: PASS e exit `0`.

- [ ] **Step 4: Executar todos os notebooks**

Run:
```bash
mkdir -p /tmp/nbexec-todos
for nb in */*.ipynb; do
  jupyter nbconvert --to notebook --execute --output-dir /tmp/nbexec-todos "$nb" || exit 1
done
python3 scripts/validar.py
```
Expected: todos executam e o validador passa. Se a fonte estiver fora do ar, registre a falha e não commite dados parciais.

- [ ] **Step 5: Conferir que não há alteração inesperada**

Run: `git status --short && git diff --stat`
Expected: nenhum JSON alterado além de acréscimos legítimos; nenhum `/tmp` versionado.

- [ ] **Step 6: Atualizar `AGENTS.md`**

Remova a menção ao `converter-schema-canonico.py` e documente:

```text
- `python3 scripts/validar.py` valida o contrato de todas as séries.
- `python3 scripts/diff_series.py` classifica o diff em novo, acrescimo, revisao ou sem_mudanca.
- Toda execução recalcula a série inteira; não há modo incremental.
- Notebooks publicam apenas períodos encerrados e escrevem o schema canônico diretamente.
```

- [ ] **Step 7: Commit**

```bash
git add AGENTS.md
git commit -m "chore(dados): aposenta o conversor de schema"
```

---

## Self-Review

- **Cobertura do spec:** validador (Task 1), diff (Task 2), normalização de datas (Task 3), contrato de notebook (Task 4), todas as pastas de série (Tasks 4–11), workflow/PR (Task 12), aposentadoria do conversor e documentação (Task 13).
- **Tipos e nomes:** `validar_serie`, `validar_arquivo`, `validar_todos`, `comparar`, `classificar`, `comparar_raiz` são usados com as mesmas assinaturas nas tasks seguintes.
- **Proporção:** as tasks de migração referenciam o contrato e o padrão da Task 4 em vez de repetir o código.
