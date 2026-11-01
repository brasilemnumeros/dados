# AGENTS.md

## Visão geral

Arquivos públicos de dados (`*.json`) do **brasilemnumeros**, consumidos pelo app do repo `sitio`. O JSON é o produto. Cada pasta de indicador contém o notebook Colab usado para extrair, calcular e publicar aqueles dados. Há validador e testes em Python; ainda não há CI nem build.

## Contrato das séries

Fonte de verdade: `sitio/app/src/data/validate.js` e `sitio/docs/plans/01-contrato-de-dados.md`.

- São 13 séries em `indicadores/<indicador>/<id>.json`; o `id` deve ser igual ao nome do arquivo sem `.json`.
- Nível superior: `schema: 1`, `id`, `unit` (`type`, `symbol`, `decimals`), `granularity` (`daily` | `monthly` | `annual`), `source`, `data`.
- `unit.type` em `percentage` | `number` | `currency`; `unit.symbol` não vazio; `unit.decimals` inteiro ≥ 0.
- Cada ponto deve ter `{ "date": "YYYY-MM-DD", "value": número finito }`.
- `rate` **não faz parte do contrato**. O IPCA já publica somente `value`; as outras 12 séries ainda carregam `rate` durante a transição. O validador tolera `rate` extra, mas não o exige.
- `date` não precisa ser dia 01, mas cada série preserva sua convenção para evitar diffs desnecessários. `indicadores/homicidios/homicidios-armas-fogo-anual.json` usa dia 15.
- No máximo um ponto por mês/ano; meses repetidos são um defeito.
- O contrato não exige ordem ascendente nem período fechado; o pipeline publica apenas períodos encerrados por decisão própria.

## Editar ou regenerar dados

- **Nunca altere valores ao mudar a forma.** Correção de fórmula é revisão histórica: registre definição, fonte e impacto em `docs/metodologia.md` e peça aval antes.
- O IPCA é o piloto já migrado: `indicadores/ipca/IPCA.ipynb` busca a SGS 13522 e escreve `{date, value}` diretamente.
- Os demais notebooks ainda estão no formato antigo e escrevem em `/content`; ao rodá-los fora do Colab, copie o resultado de volta.
- Toda execução deve recalcular a série inteira; não há modo incremental.
- `python3 scripts/validar.py` valida o contrato de todas as séries. Não corrige nem calcula nada.
- Dependências fixadas em `requirements.txt`.
- O conversor antigo (`converter-schema-canonico.py`) foi removido: ele reintroduziria `rate` no IPCA.

## `governos/` saiu daqui (2026-11-01)

O registro de mandatos (índice + `federal.json`) mora agora no repo `sitio`, em
`app/src/data/governos/`, e é embutido no bundle do app. Este repositório guarda só as
séries. O schema de lá é o mesmo que estava aqui (exercício efetivo, sem sobreposição,
`mandatoDe`, `emCurso`).

## Antes de commitar

- Rode `python3 scripts/validar.py`.
- Rode `python3 -m pytest -q`.
- Valide o parse de todos os arquivos: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*/*.json')]"`.
- Revise o `git diff` em busca de mudanças numéricas acidentais; alterações de data e ordenação se escondem facilmente em diffs grandes de JSON.
- As mensagens de commit seguem Conventional Commits em português com escopo `dados` (ex.: `fix(dados): ...`), e o corpo explica o impacto nos dados.
