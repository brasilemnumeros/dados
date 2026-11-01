# AGENTS.md

## Visão geral

Arquivos públicos de dados (`*.json`) do **brasilemnumeros**, consumidos por outro app. Não há build, testes, lint nem CI aqui — o JSON é o produto. Cada pasta de indicador também contém o notebook Colab usado para extrair/atualizar aqueles dados.

## Contrato das séries

- São 13 séries em `<indicador>/<id>.json`; o `id` deve ser igual ao nome do arquivo sem `.json`.
- Nível superior: `schema: 1`, `id`, `unit` (`type`, `symbol`, `decimals`), `granularity` (`monthly` | `annual`), `source`, `data`.
- Cada ponto: `{ "date": "YYYY-MM-DD", "rate": ..., "value": ... }`. Na fase de convivência atual, `rate === value`; mantenha os dois em sincronia.
- As datas são ordenadas de forma ascendente e, por convenção, carimbadas no dia 01 do mês/ano de referência (`YYYY-MM-01`). Exceção conhecida: `homicidios/homicidios-armas-fogo-anual.json` ainda usa o dia 15.
- Um ponto por mês/ano; meses repetidos são um defeito.

## Editar ou regenerar dados

- **Nunca altere valores ao mudar a forma.** O invariante do conversor é só de forma: ele normaliza metadados, espelha `rate` em `value`, ordena e deduplica meses repetidos (mantendo a última leitura).
- `python3 converter-schema-canonico.py` reescreve as 13 séries (UTF-8, `ensure_ascii=False`, indentação de 2 espaços). Rode após adicionar uma série ou corrigir metadados.
- `python3 converter-schema-canonico.py --check` **não** compara a saída, apesar do que diz a docstring; ele apenas evita a escrita. Verifique as mudanças com `git diff`.
- Adicionar uma série exige uma entrada na tabela `META` do script (`unit`, `granularity`, `source`); caso contrário, o conversor imprime `PULADO (sem metadados)` e não a altera.
- Os notebooks salvam em `/content` (`output_dir = "/content"`), então rodá-los fora do Colab não atualiza este repositório; copie os resultados de volta. As dependências (`python-bcb`, `ipeadatapy`, pandas, matplotlib/seaborn/plotly) são instaladas nas células; não há lockfile nem ambiente local.

## `governos/` saiu daqui (2026-11-01)

O registro de mandatos (índice + `federal.json`) mora agora no repo `sitio`, em
`app/src/data/governos/`, e é embutido no bundle do app. Este repositório guarda só as
séries. O schema de lá é o mesmo que estava aqui (exercício efetivo, sem sobreposição,
`mandatoDe`, `emCurso`).

## Antes de commitar

- Valide o parse de todos os arquivos: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('*/*.json')]"`.
- Revise o `git diff` em busca de mudanças numéricas acidentais; alterações de data e ordenação se escondem facilmente em diffs grandes de JSON.
- As mensagens de commit seguem Conventional Commits em português com escopo `dados` (ex.: `fix(dados): ...`), e o corpo explica o impacto nos dados.
