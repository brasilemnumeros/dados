# Atualização Agendada por Família Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Manter os JSON dos indicadores atualizados com um workflow por família, cadência própria da fonte e PR para qualquer mudança, sem executar todos os notebooks diariamente.

**Architecture:** Um workflow reutilizável executa o notebook da família, valida o contrato, detecta diff e publica na branch `dados/atualizacao/<familia>`. Oito callers declaram apenas família e cron. O PR é criado só se não houver um aberto; o PAT `DADOS_BOT_TOKEN` faz o check obrigatório `validar` rodar.

**Tech Stack:** GitHub Actions, Python 3.12, Jupyter/nbconvert, pytest, `gh` CLI, git. Sem script auxiliar.

**Spec:** `docs/superpowers/specs/2026-11-02-atualizacao-agendada-design.md`

## Global Constraints

- Python 3.12; runner `ubuntu-latest`; job com `timeout-minutes: 30`.
- Um caller por família em `.github/workflows/atualizar-<familia>.yml`; lógica em `.github/workflows/atualizar-familia.yml`.
- Cron em UTC; `15:00 UTC` = `12:00` de Brasília.
- Cadência exata:
  - `ipca`: `0 15 12,20 * *`
  - `igp-m`: `0 15 2,8 * *`
  - `selic`: `0 15 2,8 * *`
  - `caged`: `0 15 3,10 * *`
  - `mvgr`: `0 15 5 * *`
  - `pib`: `0 15 10 3,6,9,12 *` e `0 15 20 3 *`
  - `populacao`: `0 15 5 9,10 *`
  - `homicidios`: `0 15 15 7,8,12 *`
- Branch fixa por família: `dados/atualizacao/<familia>`.
- Segredo: `DADOS_BOT_TOKEN` (PAT fine-grained; `Contents: Read and write`, `Pull requests: Read and write`, `Metadata: Read`; validade de um ano).
- Configuração do repositório: `Settings → General → Pull Requests → Automatically delete head branches` deve estar ligada antes do primeiro merge. É o que apaga a branch ao mergear.
- Checkout com `persist-credentials: false`; o PAT entra só no step de publicação.
- `permissions: contents: read` nos callers; escrita via PAT.
- Publicação só quando `steps.diff.outputs.mudou == 'true'`, `inputs.seco != true` e `github.ref == 'refs/heads/main'`.
- Toda execução recalcula a série inteira, publica só períodos fechados e roda `python3 scripts/validar.py` + `python3 -m pytest -q` antes de publicar.
- Qualquer mudança nos JSONs, inclusive acréscimo, gera PR. Não há classificador de diff nem merge automático.
- Sem mudança, nenhum branch, commit ou PR.
- `git add -- "indicadores/$FAMILIA/*.json"` restrito à família. Não há script de escopo; o que o notebook escrever em outra pasta fica fora do commit.
- Execução: `jupyter nbconvert --to notebook --execute --ExecutePreprocessor.kernel_name=python3 --ExecutePreprocessor.timeout=600 --output-dir "$RUNNER_TEMP/nbexec"`.
- Não usar `--inplace`, `--allow-errors`, `pull_request_target` ou `gh pr merge`.
- `DADOS_RAIZ=${{ github.workspace }}`; o notebook escreve em `indicadores/<familia>/`.
- Commit do updater: `chore(dados): atualiza <familia>`; título do PR: `dados: atualiza <familia>`.
- Conventional Commits em português com escopo `dados`.
- Não criar script auxiliar (`github_pr.py`), tabela de resumo, teste de workflow nem alterar `requirements-ci.txt`.
- Não alterar notebooks, `scripts/validar.py`, `.github/workflows/validar.yml`, `indicadores/catalogo.json` nem `tests/contrato/`.
- O watchdog semanal fica fora deste plano.

## Review Focus

- **Sem mudança:** uma execução que não altera JSON deve terminar sem branch, commit ou PR. Verificação: o step de publicação exige `steps.diff.outputs.mudou == 'true'`; a Task 3 confirma o no-op na `main`.
- **Ref que não é `main`:** `seco=false` em branch de teste não pode publicar. Verificação: o step de publicação exige `github.ref == 'refs/heads/main'`.
- **PAT ausente/expirado:** a publicação deve falhar visivelmente. Verificação: o step de publicação tem o guard `DADOS_BOT_TOKEN ausente` + `exit 1`.
- **PR mergeado:** a branch é apagada pela configuração do repositório; o próximo ciclo recria branch e PR. Verificação: checklist de rollout (Task 3).
- **PR fechado sem merge:** a branch continua e o `gh pr create` pode falhar. Verificação: documentado no AGENTS; a saída é apagar a branch ou reabrir o PR. Não há configuração nativa para apagar no close.
- **Arquivo de outra família:** não entra no commit porque o `git add` é restrito à pasta da família. Verificação: o comando do step usa `indicadores/$FAMILIA/*.json`.

## File Structure

- `.github/workflows/atualizar-familia.yml`: execução, validação, diff e publicação.
- `.github/workflows/atualizar-<familia>.yml` (8): cron, `workflow_dispatch` e chamada do reutilizável.
- `AGENTS.md`: cadência, fluxo de PR, PAT, auto-delete e caso de PR fechado sem merge.
- `docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md`: nota de substituição da frequência diária.
- `docs/superpowers/plans/2026-11-01-pipeline-indicadores.md`: nota de substituição da Task 11.
- `docs/superpowers/specs/2026-11-02-atualizacao-agendada-design.md`: design aprovado, entra no PR.
- `docs/superpowers/plans/2026-11-02-atualizacao-agendada.md`: este plano, entra no PR.

---

### Task 1: Workflow reutilizável

**Files:**
- Create: `.github/workflows/atualizar-familia.yml`

**Interfaces:**
- Produces: workflow `atualizar-familia.yml` com `workflow_call` inputs `familia` (string, obrigatório) e `seco` (bool, default `false`), segredo `token` (obrigatório), steps nomeados e publicação em `dados/atualizacao/<familia>`.

- [ ] **Step 1: Criar o workflow reutilizável**

Crie `.github/workflows/atualizar-familia.yml`:

```yaml
name: atualizar-familia

on:
  workflow_call:
    inputs:
      familia:
        required: true
        type: string
      seco:
        required: false
        type: boolean
        default: false
    secrets:
      token:
        required: true

jobs:
  atualizar:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - name: Checkout
        uses: actions/checkout@v7
        with:
          persist-credentials: false

      - name: Configurar Python
        uses: actions/setup-python@v7
        with:
          python-version: "3.12"
          cache: pip
          cache-dependency-path: requirements.txt

      - name: Instalar dependências
        run: python3 -m pip install -r requirements.txt

      - name: Registrar kernel
        run: python3 -m ipykernel install --user --name python3

      - name: Validar família
        env:
          FAMILIA: ${{ inputs.familia }}
        run: |
          set -euo pipefail
          case "$FAMILIA" in
            ipca|igp-m|selic|caged|mvgr|pib|populacao|homicidios) ;;
            *) echo "::error::família inválida: $FAMILIA"; exit 1 ;;
          esac

      - name: Executar notebooks
        env:
          DADOS_RAIZ: ${{ github.workspace }}
          FAMILIA: ${{ inputs.familia }}
        run: |
          set -euo pipefail
          mkdir -p "$RUNNER_TEMP/nbexec"
          compgen -G "indicadores/$FAMILIA/*.ipynb" > /dev/null || {
            echo "::error::nenhum notebook em indicadores/$FAMILIA"
            exit 1
          }
          for nb in indicadores/"$FAMILIA"/*.ipynb; do
            for tentativa in 1 2; do
              if jupyter nbconvert \
                --to notebook \
                --execute \
                --ExecutePreprocessor.kernel_name=python3 \
                --ExecutePreprocessor.timeout=600 \
                --output-dir "$RUNNER_TEMP/nbexec" \
                "$nb"; then
                break
              fi
              if [ "$tentativa" -eq 2 ]; then
                echo "::error::falha ao executar $nb"
                exit 1
              fi
              sleep 60
            done
          done

      - name: Validar contrato
        run: python3 scripts/validar.py

      - name: Rodar testes
        run: python3 -m pytest -q

      - name: Preparar diff
        id: diff
        env:
          FAMILIA: ${{ inputs.familia }}
        run: |
          set -euo pipefail
          git add -- "indicadores/$FAMILIA/*.json"
          if git diff --cached --quiet; then
            echo "mudou=false" >> "$GITHUB_OUTPUT"
            echo "Sem mudanças em indicadores/$FAMILIA; nada a publicar."
          else
            echo "mudou=true" >> "$GITHUB_OUTPUT"
          fi

      - name: Mostrar diff
        if: steps.diff.outputs.mudou == 'true'
        run: git diff --cached --stat -- 'indicadores/*/*.json'

      - name: Publicar
        if: steps.diff.outputs.mudou == 'true' && inputs.seco != true && github.ref == 'refs/heads/main'
        env:
          GH_TOKEN: ${{ secrets.token }}
          FAMILIA: ${{ inputs.familia }}
        run: |
          set -euo pipefail
          if [ -z "${GH_TOKEN:-}" ]; then
            echo "::error::segredo DADOS_BOT_TOKEN ausente"
            exit 1
          fi
          BRANCH="dados/atualizacao/$FAMILIA"
          git config user.name "dados-bot"
          git config user.email "dados-bot@users.noreply.github.com"
          git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
          git fetch origin main
          git reset --mixed origin/main
          git add -- "indicadores/$FAMILIA/*.json"
          if git diff --cached --quiet; then
            echo "Sem mudanças em indicadores/$FAMILIA depois de atualizar a main; nada a publicar."
            exit 0
          fi
          git checkout -B "$BRANCH"
          git commit -m "chore(dados): atualiza $FAMILIA"
          git push --force origin "$BRANCH"
          abertos=$(gh pr list --head "$BRANCH" --state open --json number -q '.[].number')
          if [ -z "$abertos" ]; then
            gh pr create \
              --base main \
              --head "$BRANCH" \
              --title "dados: atualiza $FAMILIA" \
              --body "Atualização automática de \`$FAMILIA\`. O diff é a fonte de verdade."
          fi

      - name: Publicar artifact
        if: always()
        continue-on-error: true
        uses: actions/upload-artifact@v7
        with:
          name: nbexec-${{ inputs.familia }}-${{ github.run_id }}-${{ github.run_attempt }}
          path: ${{ runner.temp }}/nbexec
          if-no-files-found: ignore
          retention-days: 14
```

- [ ] **Step 2: Conferir a sintaxe YAML**

Run:

```bash
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-familia.yml'))"
```

Expected: exit `0`, sem saída. (O `PyYAML` está em `requirements.txt`; use o Python do `.venv` se necessário.)

- [ ] **Step 3: Conferir as condições de segurança**

Run:

```bash
grep -F "github.ref == 'refs/heads/main'" .github/workflows/atualizar-familia.yml
grep -F "DADOS_BOT_TOKEN ausente" .github/workflows/atualizar-familia.yml
grep -F "gh pr merge" .github/workflows/atualizar-familia.yml || true
```

Expected: as duas primeiras linhas aparecem; o terceiro comando não imprime nada (não há merge automático).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/atualizar-familia.yml
git commit -m "ci(dados): adiciona workflow reutilizavel de atualizacao"
```

---

### Task 2: Callers por família

**Files:**
- Create: `.github/workflows/atualizar-ipca.yml`
- Create: `.github/workflows/atualizar-igp-m.yml`
- Create: `.github/workflows/atualizar-selic.yml`
- Create: `.github/workflows/atualizar-caged.yml`
- Create: `.github/workflows/atualizar-mvgr.yml`
- Create: `.github/workflows/atualizar-pib.yml`
- Create: `.github/workflows/atualizar-populacao.yml`
- Create: `.github/workflows/atualizar-homicidios.yml`

**Interfaces:**
- Consumes: `atualizar-familia.yml` da Task 1.
- Produces: oito callers com `workflow_dispatch` (`seco` default `true`), `permissions: contents: read`, `concurrency` por família e o cron da tabela.

- [ ] **Step 1: Criar os oito callers**

Use `atualizar-ipca.yml` como modelo:

```yaml
# Workflow da família IPCA; o notebook e os dados vivem em indicadores/ipca/.
name: atualizar ipca
on:
  schedule:
    - cron: '0 15 12,20 * *'
  workflow_dispatch:
    inputs:
      seco:
        description: Executar sem publicar
        type: boolean
        default: true
permissions:
  contents: read
concurrency:
  group: atualizar-ipca
  cancel-in-progress: false
jobs:
  atualizar:
    uses: ./.github/workflows/atualizar-familia.yml
    with:
      familia: ipca
      seco: ${{ inputs.seco == true }}
    secrets:
      token: ${{ secrets.DADOS_BOT_TOKEN }}
```

Repita para as outras sete famílias, trocando `name`, `familia`, `group` e o(s) `cron`:

| arquivo | família | cron(s) |
|---|---|---|
| `atualizar-igp-m.yml` | `igp-m` | `0 15 2,8 * *` |
| `atualizar-selic.yml` | `selic` | `0 15 2,8 * *` |
| `atualizar-caged.yml` | `caged` | `0 15 3,10 * *` |
| `atualizar-mvgr.yml` | `mvgr` | `0 15 5 * *` |
| `atualizar-pib.yml` | `pib` | `0 15 10 3,6,9,12 *` e `0 15 20 3 *` |
| `atualizar-populacao.yml` | `populacao` | `0 15 5 9,10 *` |
| `atualizar-homicidios.yml` | `homicidios` | `0 15 15 7,8,12 *` |

Cada arquivo começa com um comentário apontando para `indicadores/<familia>/`.

- [ ] **Step 2: Conferir a matriz de famílias e crons**

Run:

```bash
python3 - <<'PY'
import yaml
from pathlib import Path

esperado = {
    "ipca": ["0 15 12,20 * *"],
    "igp-m": ["0 15 2,8 * *"],
    "selic": ["0 15 2,8 * *"],
    "caged": ["0 15 3,10 * *"],
    "mvgr": ["0 15 5 * *"],
    "pib": ["0 15 10 3,6,9,12 *", "0 15 20 3 *"],
    "populacao": ["0 15 5 9,10 *"],
    "homicidios": ["0 15 15 7,8,12 *"],
}
for familia, crons in esperado.items():
    caminho = Path(f".github/workflows/atualizar-{familia}.yml")
    doc = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    gatilhos = doc.get("on") or doc.get(True)
    assert [s["cron"] for s in gatilhos["schedule"]] == crons, familia
    assert gatilhos["workflow_dispatch"]["inputs"]["seco"]["default"] is True, familia
    job = doc["jobs"]["atualizar"]
    assert job["with"]["familia"] == familia, familia
    assert job["secrets"]["token"] == "${{ secrets.DADOS_BOT_TOKEN }}", familia
print("ok: 8 callers com cron e família corretos")
PY
```

Expected: `ok: 8 callers com cron e família corretos`.

- [ ] **Step 3: Conferir a sintaxe de todos os workflows**

Run:

```bash
python3 - <<'PY'
import glob
import yaml

for caminho in sorted(glob.glob(".github/workflows/*.yml")):
    yaml.safe_load(open(caminho, encoding="utf-8"))
    print("ok", caminho)
PY
```

Expected: `ok` para cada um dos 10 workflows (os 9 novos e o `validar.yml`).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/atualizar-*.yml
git commit -m "ci(dados): agenda atualizacao por familia"
```

---

### Task 3: Documentação, verificação local e rollout

**Files:**
- Modify: `AGENTS.md`
- Modify: `docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md`
- Modify: `docs/superpowers/plans/2026-11-01-pipeline-indicadores.md`
- Add: `docs/superpowers/specs/2026-11-02-atualizacao-agendada-design.md`
- Add: `docs/superpowers/plans/2026-11-02-atualizacao-agendada.md`

- [ ] **Step 1: Documentar a atualização agendada no `AGENTS.md`**

Acrescente uma seção `## Atualização agendada` (antes de `## Antes de commitar`) com:

```markdown
## Atualização agendada

Cada família tem um workflow em `.github/workflows/atualizar-<familia>.yml`, que chama o
reutilizável `atualizar-familia.yml`. A cadência segue a fonte (UTC):

| família | cron | quando |
|---|---|---|
| ipca | `0 15 12,20 * *` | mensal, após a divulgação |
| igp-m | `0 15 2,8 * *` | mensal, após o último dia útil |
| selic | `0 15 2,8 * *` | mensal, após o fechamento |
| caged | `0 15 3,10 * *` | mensal, com atraso do SGS |
| mvgr | `0 15 5 * *` | mensal, defasagem de ~3 meses |
| pib | `0 15 10 3,6,9,12 *` + `0 15 20 3 *` | trimestral, com Q4 em março |
| populacao | `0 15 5 9,10 *` | anual, após a estimativa de agosto |
| homicidios | `0 15 15 7,8,12 *` | anual, com o Atlas |

- Toda execução recalcula a série inteira e roda `scripts/validar.py` + `pytest` antes de
  publicar.
- Qualquer mudança nos JSONs — inclusive acréscimo — abre ou atualiza um PR na branch
  `dados/atualizacao/<familia>`. Não há classificação de diff nem merge automático; o merge
  é o ato de publicar.
- Sem mudança, nenhum PR, branch ou commit é criado.
- O PR é aberto com o PAT `DADOS_BOT_TOKEN` (fine-grained, um ano) para que o check
  `validar` rode; renove antes do vencimento.
- O repositório precisa ter `Settings → General → Pull Requests → Automatically delete head
  branches` ligado antes do primeiro merge: a branch é apagada ao mergear, e o próximo ciclo
  cria outra.
- Se um PR for fechado sem merge, a branch continua; apague a branch ou reabra o PR antes
  do próximo ciclo. Não há configuração nativa para apagar no close.
- `workflow_dispatch` com `seco=true` executa e valida sem publicar; `seco=false` em `main`
  força a publicação.
- O `schedule` roda a partir de `main` e é desativado após 60 dias sem atividade; mergeie
  os PRs com regularidade.
- O notebook executado fica no artifact do run, não no repositório.
```

- [ ] **Step 2: Marcar a substituição no spec de 2026-11-01**

No topo de `docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md`, acrescente:

```markdown
> **Nota (2026-11-02):** a decisão de frequência diária foi substituída pelo spec
> `2026-11-02-atualizacao-agendada-design.md`. As demais decisões continuam valendo.
```

- [ ] **Step 3: Marcar a substituição no plano de 2026-11-01**

No topo de `docs/superpowers/plans/2026-11-01-pipeline-indicadores.md`, e junto do título da
Task 11, acrescente:

```markdown
> **Nota (2026-11-02):** a Task 11 foi substituída pelo plano
> `2026-11-02-atualizacao-agendada.md`. As demais tasks continuam valendo.
```

- [ ] **Step 4: Rodar o validador e os testes existentes**

Run:

```bash
python3 scripts/validar.py
python3 -m pytest -q
```

Expected: exit `0` e todos os testes passando. Nenhum teste novo foi criado; a suíte é a
que já existia.

- [ ] **Step 5: Executar IPCA e População contra uma cópia**

Run:

```bash
tmp=$(mktemp -d)
mkdir -p "$tmp/indicadores" "$tmp/out"
cp -R indicadores/ipca "$tmp/indicadores/ipca"
cp -R indicadores/populacao "$tmp/indicadores/populacao"
DADOS_RAIZ="$tmp" ./.venv/bin/jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.kernel_name=python3 \
  --ExecutePreprocessor.timeout=600 \
  --output-dir "$tmp/out" \
  "$tmp/indicadores/ipca/IPCA.ipynb"
DADOS_RAIZ="$tmp" ./.venv/bin/jupyter nbconvert --to notebook --execute \
  --ExecutePreprocessor.kernel_name=python3 \
  --ExecutePreprocessor.timeout=600 \
  --output-dir "$tmp/out" \
  "$tmp/indicadores/populacao/População.ipynb"
TMP="$tmp" ./.venv/bin/python - <<'PY'
import json
import os
from pathlib import Path

tmp = Path(os.environ["TMP"])
pares = [
    "indicadores/ipca/ipca-acum-12m.json",
    "indicadores/populacao/populacao-total-anual.json",
    "indicadores/populacao/populacao-variacao-anual.json",
]
for caminho in pares:
    publicado = json.loads(Path(caminho).read_text(encoding="utf-8"))
    gerado = json.loads((tmp / caminho).read_text(encoding="utf-8"))
    assert publicado == gerado, caminho
print("ok: séries geradas idênticas às publicadas")
PY
```

Expected: `ok: séries geradas idênticas às publicadas`. Se a fonte tiver publicado um ponto
novo entre a cópia e a execução, o teste falha por diferença legítima; confira o diff antes
de tratar como regressão.

- [ ] **Step 6: Conferir que o repositório não mudou**

Run: `git status --short`
Expected: nenhum arquivo modificado; nenhum JSON de indicador alterado pela execução local.
Arquivos não rastreados que você criou para o ensaio não contam.

- [ ] **Step 7: Commitar a documentação**

Run: `git diff --check`

Then:

```bash
git add AGENTS.md \
  docs/superpowers/specs/2026-11-01-pipeline-indicadores-design.md \
  docs/superpowers/plans/2026-11-01-pipeline-indicadores.md \
  docs/superpowers/specs/2026-11-02-atualizacao-agendada-design.md \
  docs/superpowers/plans/2026-11-02-atualizacao-agendada.md
git commit -m "docs(dados): documenta atualizacao agendada por familia"
```

- [ ] **Step 8: Abrir o PR dos workflows**

Abra o PR com as mudanças das Tasks 1–3. O `validar` deve ficar verde. O merge é manual.

- [ ] **Step 9: Criar o segredo do PAT e ligar o auto-delete**

Crie um PAT fine-grained com escopo neste repositório e permissões `Contents: Read and
write`, `Pull requests: Read and write`, `Metadata: Read`, validade de um ano. Depois:

```bash
gh secret set DADOS_BOT_TOKEN
gh secret list
```

Expected: `DADOS_BOT_TOKEN` aparece na lista.

No GitHub, ligue `Settings → General → Pull Requests → Automatically delete head branches`.

- [ ] **Step 10: Mergear o PR dos workflows**

Com o PAT e o auto-delete configurados, mergeie o PR. Só a partir daqui os schedules valem;
eles rodam a partir da `main`.

- [ ] **Step 11: Rodar o modo seco e o no-op na `main`**

```bash
gh workflow run atualizar-ipca.yml -f seco=true
gh workflow run atualizar-populacao.yml -f seco=true
gh run watch
gh workflow run atualizar-ipca.yml -f seco=false
gh run watch
gh pr list --head dados/atualizacao/ipca
```

Expected: os dry-runs terminam verdes, executam os notebooks, validam e **não** abrem PR. O
run com `seco=false` termina verde: se não houve divulgação desde a última atualização, a
lista de PRs fica vazia; se a fonte já publicou, o resultado correto é um PR — revise-o.

- [ ] **Step 12: Acompanhar a primeira janela real**

```bash
gh run list --workflow=atualizar-caged.yml --limit 5
gh pr list --head dados/atualizacao/caged
```

Expected: quando a fonte publicar, o workflow abre um PR com o diff, o artifact e o check
`validar` verde. **Não marque esta task como concluída antes de ver esse PR real.** Se a
criação do PR falhar, o dado não foi publicado; corrija e rode de novo.

---

## Self-Review

- **Cobertura do spec:** workflow reutilizável (Task 1), oito callers (Task 2),
  documentação, verificação local e rollout (Task 3). O watchdog ficou explicitamente fora.
- **Sem código novo de produto:** não há script auxiliar, tabela de resumo, teste de
  workflow nem mudança em `requirements-ci.txt`; a verificação é YAML + execução real dos
  notebooks.
- **Consistência:** os nomes dos steps do YAML coincidem com os usados nas verificações; a
  matriz de famílias/crons é a mesma do spec.
- **Review Focus:** no-op, ref não-`main`, PAT, PR mergeado e PR fechado sem merge estão
  cobertos por condição, guard ou checklist de rollout.
- **Proporção:** o plano é curto porque o fluxo é curto; os blocos longos são o YAML e o
  checklist de rollout.
