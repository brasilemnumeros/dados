# Workflow recorrente

O GitHub só descobre YAML **diretamente** em `.github/workflows/` na raiz. Um workflow dentro de
`indicadores/<familia>/` não roda. O que mora na pasta é o notebook; o caller fica em
`.github/workflows/`.

## Anatomia do caller

Cada família tem um caller pequeno; a lógica comum está em `atualizar-familia.yml`.

```yaml
# Workflow da família <familia>; o notebook e os dados vivem em indicadores/<familia>/.
name: atualizar <familia>
on:
  schedule:
    - cron: '<cron>'
  workflow_dispatch:
    inputs:
      seco:
        description: Executar sem publicar
        type: boolean
        default: true
permissions:
  contents: read
concurrency:
  group: atualizar-<familia>
  cancel-in-progress: false
jobs:
  atualizar:
    uses: ./.github/workflows/atualizar-familia.yml
    with:
      familia: <familia>
      seco: ${{ inputs.seco == true }}
    secrets:
      token: ${{ secrets.DADOS_BOT_TOKEN }}
```

- `schedule` em UTC; `0 15 ...` = 12:00 de Brasília.
- `workflow_dispatch` com `seco=true` por padrão: executa e valida sem publicar.
- `permissions: contents: read`; a escrita usa o PAT `DADOS_BOT_TOKEN`.
- `concurrency` por família, sem cancelar a execução em andamento.
- O caller não tem lógica de coleta/cálculo.

## Regras por caso

| Caso | O que fazer |
|---|---|
| Família com caller | Nada no workflow. Confira a cadência; o caller roda todos os `.ipynb` da pasta. |
| Família sem caller | Criar `atualizar-<familia>.yml`, acrescentar a família à allowlist e a linha no `AGENTS.md`. |
| Família nova | O mesmo do caso anterior, mais a pasta, o notebook e o JSON. |
| Cadência divergente da família | **Parar e perguntar.** Mudar o cron afeta as outras séries. |
| Reutilizável ausente no checkout | **Parar** e pedir para sincronizar com `origin/main`; não recriar. |

## Allowlist do reutilizável

O step “Validar família” em `atualizar-familia.yml` tem a lista:

```bash
case "$FAMILIA" in
  ipca|igp-m|selic|caged|mvgr|pib|populacao|homicidios) ;;
  *) echo "::error::família inválida: $FAMILIA"; exit 1 ;;
esac
```

Acrescente a família nova nessa linha. Não altere o resto do reutilizável.

## Tabela de cadência do `AGENTS.md`

A seção **Atualização agendada** repete a cadência. Acrescente a linha da família nova:

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

## Escolha do cron

1. Descubra quando a fonte publica o período fechado (calendário de divulgação).
2. Use 15:00 UTC (12:00 de Brasília), depois das divulgações matinais.
3. Para fonte mensal, duas tentativas (ex.: dia 2 e dia 8, ou 12 e 20) para cobrir atraso.
4. Para fonte anual, duas ou três tentativas na janela de divulgação.
5. Evite cron diário: a execução é por família e o notebook busca a fonte inteira.

## O que não fazer

- Um workflow por JSON: o workflow é por família; um notebook pode publicar várias séries.
- `pull_request_target` ou `gh pr merge`: o merge é ato humano.
- Recriar `atualizar-familia.yml` ou mexer no `validar.yml`.
- Criar caller que aponta para um reutilizável que não existe no checkout.
- Mudar o cron de uma família para encaixar uma série nova sem aval.
