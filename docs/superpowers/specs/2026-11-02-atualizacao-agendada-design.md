# Atualização agendada dos indicadores, por família

**Data:** 2026-11-02
**Status:** aprovado em 2026-11-02
**Substitui:** a decisão de frequência diária do spec
`2026-11-01-pipeline-indicadores-design.md` e a Task 11 do plano correspondente.

## Intenção

Manter os JSON publicados em dia sem executar todos os notebooks todos os dias. Cada
família ganha um workflow próprio, com a cadência da sua fonte. Toda mudança produzida —
inclusive acréscimo de ponto — vira um pull request; o merge continua sendo o ato de
publicar.

## Contexto

- O workflow de atualização descrito no spec de 2026-11-01 não existe. Hoje só roda o
  `validar.yml`, em pull request e push para `main`.
- Os dados estão em dia em 2026-11-02: IPCA até 2026-09 (outubro sai por volta de 10/11),
  IGP-M e Selic até 2026-10, CAGED e MVG-R até 2026-08, PIB até 2025, População até 2026,
  Homicídios até 2024 (total) e 2023 (armas e proporção).
- O GitHub só descobre workflows em `.github/workflows/*.yml`; um YAML dentro de
  `indicadores/<familia>/` seria ignorado.
- O `GITHUB_TOKEN` não dispara novos workflows: um PR aberto por ele não roda o
  `pull_request` do `validar.yml`. Como `main` exige o check `validar`, o PR ficaria com o
  check pendente.
- `schedule` roda em UTC, pode atrasar e é desativado após 60 dias sem atividade no
  repositório.
- O repositório é público; minutos de Actions são gratuitos. O custo que importa é chamada
  à fonte, execução de notebook e ruído de PR.

## Objetivos

- Rodar cada família somente na janela em que a fonte pode ter mudado.
- Recalcular a série inteira e publicar só períodos fechados, como já fazem os notebooks.
- Abrir ou atualizar **um PR por família** quando houver qualquer mudança nos JSONs.
- Não abrir PR, branch ou commit quando não houver mudança.
- Isolar falhas: uma família fora do ar não impede as outras.
- Rodar `scripts/validar.py` + `pytest` antes de publicar.
- Permitir execução manual, com modo seco.
- Deixar o notebook executado como artifact do run.

## Não objetivos

- Criar script auxiliar de PR, tabela de resumo ou conferência de escopo. O fluxo é shell
  direto no workflow.
- Classificar diff em acréscimo vs. revisão. Qualquer mudança é PR.
- Fazer merge automático ou commitar direto em `main`.
- Rodar todos os notebooks diariamente.
- Alterar fórmula, valor ou definição de indicador.
- Criar, remover ou renomear indicadores, ou editar `indicadores/catalogo.json`.
- Substituir o `validar.yml` ou afrouxar o gate.
- Guardar payload bruto das fontes no repositório.
- Garantir horário exato de execução.
- Watchdog semanal (fica para depois, se fizer falta).

## Anti-objetivos

- Workflow verde sem atualizar porque uma condição interna pulou a execução.
- PR com JSON inválido, catálogo fora de sincronia ou valor não finito.
- PR de dado que também carrega notebook executado, `__pycache__` ou documentação.
- Duplicar lógica de coleta/cálculo no workflow.
- Commit ou PR vazio.
- Uma família quebrada impedir as demais.
- Revisão histórica publicada sem revisão humana.
- Token com escopo amplo, versionado ou impresso no log.

## Decisões tomadas

1. **Um workflow por família**, em `.github/workflows/atualizar-<familia>.yml`; a lógica
   comum fica no reutilizável `atualizar-familia.yml`.
2. **Qualquer mudança gera PR**, inclusive acréscimo. Sem classificador, sem merge
   automático.
3. **Branch fixa por família** (`dados/atualizacao/<familia>`). O push atualiza o PR aberto
   sozinho; um PR novo só é criado se não houver PR aberto para a branch.
4. **PAT fine-grained** (`DADOS_BOT_TOKEN`) para o PR disparar o `validar.yml`. O
   `GITHUB_TOKEN` não serve para isso.
5. **Excluir a branch automaticamente ao mergear**: configuração do repositório
   (`Settings → General → Pull Requests → Automatically delete head branches`). Assim o
   próximo ciclo recria a branch e abre um PR novo sem estado extra.
6. **Duas tentativas** nas janelas mensais (uma no MVG-R, pela defasagem de três meses); a
   segunda é rede de segurança para divulgação atrasada.
7. **Sem gate de “período esperado”**: a segunda tentativa é barata.
8. **Validação dentro do updater** antes de publicar, mesmo com o check do PR.
9. **Sem script auxiliar**: decisão de PR é uma condição de shell; o corpo do PR é texto
   fixo; o `git add` é restrito à pasta da família.
10. **Nenhum notebook é alterado** por este trabalho.

## Cadência

A unidade é o notebook da família. O cron é UTC; `15:00 UTC` = `12:00` de Brasília, depois
das divulgações matinais.

| Família / séries | Fonte e comportamento | Janela típica | Cron | Execuções/ano |
|---|---|---|---|---|
| IPCA (`ipca-acum-12m`) | SGS 13522; mensal | ~dia 10 do mês seguinte | `0 15 12,20 * *` | 24 |
| IGP-M (`igpm-acum-12m`) | SGS 28655; mensal | último dia útil do mês | `0 15 2,8 * *` | 24 |
| Selic (`selic-meta`, `selic-over-acum-12m`) | SGS 432 e 11; diária, publica mês fechado | 1º dia útil após o fechamento | `0 15 2,8 * *` | 24 |
| CAGED (`caged-total-mensal`) | SGS 28763; mensal, com atraso do SGS | fim do mês seguinte | `0 15 3,10 * *` | 24 |
| MVG-R (`mvgr-nominal`, `mvgr-real`) | SGS 25419 + IPCA 433; mensal, defasagem ~3 meses | ao longo do mês | `0 15 5 * *` | 12 |
| PIB (`pib-real-anual`) | SGS 7326 + SIDRA; anual (Q4) e revisões trimestrais | início de março | `0 15 10 3,6,9,12 *` e `0 15 20 3 *` | 5 |
| População (`populacao-total-anual`, `populacao-variacao-anual`) | IBGE, projeção 2024 + SIDRA 6579; anual e revisão irregular | fim de agosto | `0 15 5 9,10 *` | 2 |
| Homicídios (`homicidios-anual`, `homicidios-armas-fogo-anual`, `proporcao-homicidios-armas-fogo-anual`) | IPEA/Atlas; anual, defasagem 1–2 anos | jun/jul | `0 15 15 7,8,12 *` | 3 |

Total: ~118 execuções/ano, contra ~2.920 do desenho diário (8 notebooks × 365) — cerca de
96% menos. As mudanças reais são ~70/ano; o resto são tentativas que não alteram o JSON e
não geram PR.

## Onde mora o workflow

```
.github/workflows/
  validar.yml                    # gate existente, não muda
  atualizar-familia.yml          # reutilizável: execução, validação, diff e PR
  atualizar-ipca.yml             # caller: cron + workflow_dispatch
  atualizar-igp-m.yml
  atualizar-selic.yml
  atualizar-caged.yml
  atualizar-mvgr.yml
  atualizar-pib.yml
  atualizar-populacao.yml
  atualizar-homicidios.yml
indicadores/<familia>/
  <Familia>.ipynb                # fonte da verdade, não muda
  <id>.json                      # dado publicado
```

O GitHub não suporta workflow fora de `.github/workflows/`. Cada caller tem um comentário
apontando para `indicadores/<familia>/`.

Não vale um workflow por JSON: `selic`, `mvgr`, `populacao` e `homicidios` têm um notebook
que publica mais de uma série.

## Arquitetura

### Caller (exemplo: IPCA)

```yaml
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

### Reutilizável

Entrada: `familia` (string), `seco` (bool). Segredo: `token` (PAT). Passos:

1. `actions/checkout@v7` com `persist-credentials: false`.
2. `actions/setup-python@v7` com Python 3.12 e cache de pip em `requirements.txt`.
3. `python3 -m pip install -r requirements.txt`.
4. `python3 -m ipykernel install --user --name python3`.
5. Validar a família contra a lista das oito.
6. Executar todos os `indicadores/<familia>/*.ipynb` com `jupyter nbconvert --execute`,
   `DADOS_RAIZ=${{ github.workspace }}`, `--ExecutePreprocessor.timeout=600` e saída em
   `$RUNNER_TEMP/nbexec`. Uma retentativa com espera de 60 s.
7. `python3 scripts/validar.py` e `python3 -m pytest -q`.
8. `git add -- "indicadores/<familia>/*.json"`; se `git diff --cached --quiet`, encerrar
   com uma mensagem de “sem mudanças” e sem PR.
9. Se `seco=false`, houver diff e o ref for `main`, atualizar a `main` (`git fetch origin
   main` + `git reset --mixed origin/main`), reaplicar o `git add`, rechecar o diff e
   publicar.
10. Publicar o artifact com o notebook executado (`if: always()`, `continue-on-error: true`).

O `git add` restrito já é a proteção de escopo: se o notebook escrever em outra pasta, o
arquivo fica fora do commit e a próxima execução daquela família o trata.

### Publicação

```bash
git fetch origin main
git reset --mixed origin/main
git add -- "indicadores/$FAMILIA/*.json"
if git diff --cached --quiet; then
  echo "Sem mudanças depois de atualizar a main; nada a publicar."
  exit 0
fi

git checkout -B "dados/atualizacao/$FAMILIA"
git commit -m "chore(dados): atualiza $FAMILIA"
git push --force origin "dados/atualizacao/$FAMILIA"

if [ -z "$(gh pr list --head "dados/atualizacao/$FAMILIA" --state open --json number -q '.[].number')" ]; then
  gh pr create --base main --head "dados/atualizacao/$FAMILIA" \
    --title "dados: atualiza $FAMILIA" \
    --body "Atualização automática de \`$FAMILIA\`. O diff é a fonte de verdade."
fi
```

- Antes de commitar, a branch é reconstruída sobre a `main` atual. Se a `main` já contém a
  mudança (por exemplo, um PR anterior foi mergeado durante a execução), o run encerra sem
  PR.

- PR aberto: o push atualiza o diff; o `if` não cria outro.
- Sem PR aberto: cria.
- PR mergeado: a branch é apagada pela configuração do repositório; o próximo ciclo cria
  branch e PR novos.
- PR fechado sem merge: a branch continua; o `gh pr create` pode falhar. Nesse caso, apague
  a branch (ou reabra o PR) e rode de novo. Não existe configuração nativa para apagar a
  branch no fechamento sem merge.

### Token

O check obrigatório `validar` só roda em PR se o evento não vier do `GITHUB_TOKEN`. Por
isso o updater usa um **PAT fine-grained**, guardado no segredo `DADOS_BOT_TOKEN`:

- escopo: somente este repositório;
- permissões: `Contents: Read and write`, `Pull requests: Read and write`,
  `Metadata: Read`;
- validade: um ano, com lembrete de renovação.

O token é usado só no step de publicação (`GH_TOKEN` e URL do push); o código do notebook
nunca o vê. O `GITHUB_TOKEN` fica com `contents: read`.

Alternativa: um GitHub App com `actions/create-github-app-token` evita token pessoal e usa
identidade de bot, mas exige criar e instalar o App. Para este repositório, o PAT é o
caminho mais simples.

Fallback, se você não quiser o PAT: usar o `GITHUB_TOKEN` e mergear como admin
(`enforce_admins` está desligado). O PR fica com o check `validar` pendente; o CI não roda.

### Falhas

- Notebook falha → job falha, artifact sobe, nenhum PR é aberto.
- `validar.py` ou `pytest` falha → job falha, nenhum PR.
- Fonte fora do ar → o notebook repete; se ainda falhar, o job falha visivelmente.
- Duas execuções da mesma família → `concurrency` serializa; a segunda pode encontrar diff
  vazio e encerrar sem PR.
- PAT ausente/expirado → job falha no push/PR; a falha é visível.

### Execução manual

`workflow_dispatch` em cada caller:

- `seco=true` (padrão): executa, valida e mostra o diff, mas não publica.
- `seco=false` em `main`: força a publicação fora do calendário.

O passo de publicação só roda quando `github.ref == 'refs/heads/main'`; rodar em branch de
teste nunca abre PR.

## Abordagens consideradas

1. **Um workflow por família + reutilizável (escolhida).** Cadência exata, falha isolada,
   log mostra só o que rodou. Custo: nove arquivos pequenos e um PR por família quando há
   mudança.
2. **Um workflow diário único com matriz dinâmica.** Um arquivo, mas exige lógica de
   “família vencida” testável e roda checkout todo dia. Descartada.
3. **Um workflow por cadência (mensal/trimestral/anual).** Três arquivos, mas roda
   notebooks que não mudaram e mistura falhas. Descartada.
4. **Script auxiliar de PR (`github_pr.py`) com decisão de estado, tabela e escopo.**
   Resolvia casos raros e cosmética, mas era mais código do que o fluxo pedia. Descartada.
5. **Publicação:** PR para qualquer mudança (escolhida); híbrido com classificador
   (descartado pelo autor); commit direto (descartado: revisão histórica sem aval).

## Riscos e mitigações

- **Volume de PRs.** ~5–8 por mês, um por família. Mitigação: branch fixa atualiza o PR
  aberto em vez de criar outro; mergear fecha o ciclo.
- **PR não mergeado.** O dado fica velho e o próximo ciclo atualiza o mesmo PR. Mitigação:
  mergear com frequência; o PR é o aviso.
- **Schedule desativado após 60 dias sem atividade.** Mitigação: mergear pelo menos um PR
  a cada 60 dias; na prática as séries mensais geram PRs todo mês.
- **PR fechado sem merge.** A branch fica e o `gh pr create` pode falhar. Mitigação:
  apagar a branch ou reabrir o PR; o próximo run recria. Não há configuração nativa para
  apagar no close.
- **Divulgação atrasada.** Segunda tentativa na janela; se ainda atrasar, o próximo ciclo
  captura os dois períodos de uma vez.
- **Fonte instável.** Retentativas no notebook + uma retentativa do passo; falha visível,
  sem dado parcial.
- **PAT expira.** Falha visível; renovação anual documentada no AGENTS.
- **PR com valor antigo alterado.** É o caminho normal: o diff mostra a alteração e o
  merge exige revisão. Não há classificação automática.
- **Assertion de notebook presa a uma divulgação.** Uma nova edição pode deixar uma
  conferência desatualizada; o job falha e a correção é um PR separado, sem tocar no dado.

## Rollout

1. Abrir um único PR com `atualizar-familia.yml`, os oito callers e a documentação.
2. Criar o segredo `DADOS_BOT_TOKEN` antes do merge.
3. Ativar `Settings → General → Pull Requests → Automatically delete head branches` antes do
   primeiro merge.
4. Mergear o PR dos workflows. Só a partir daqui os schedules valem; eles rodam a partir da
   `main`.
5. Na `main`, rodar `workflow_dispatch` com `seco=true` para IPCA e População. Isso prova
   kernel, dependências, execução, validação, diff e artifact; não abre PR.
6. Na `main`, rodar `workflow_dispatch` com `seco=false` para IPCA. Hoje o esperado é
   “nenhum PR”; se a fonte já publicou, o resultado correto é um PR.
7. A primeira janela real é o teste ponta a ponta: o PR deve rodar o `validar`, mostrar o
   diff e o artifact. Se a criação do PR falhar, o dado não foi publicado; corrija e rode
   de novo.
8. Atualizar `AGENTS.md` com cadência, fluxo de PR, PAT e a configuração de auto-delete;
   acrescentar no spec de 2026-11-01 a nota de substituição.
9. Watchdog semanal fica fora deste trabalho.

**Aceitação:** não se declara a publicação “verificada” antes da primeira janela real. Até
lá, o que está provado é execução, validação, diff e no-op.

## O que fica para o plano de implementação

- YAML completo do reutilizável e dos oito callers.
- Nomes exatos de steps, mensagens e corpo do PR.
- Instruções de criação/renovação do PAT.
- Configuração de auto-delete das branches.
- Testes locais: execução de IPCA e População em cópia, `validar.py`, `pytest`, no-op.
- Atualização de `AGENTS.md` e da nota no spec de 2026-11-01.
