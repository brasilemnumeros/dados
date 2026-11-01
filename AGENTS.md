# AGENTS.md

## Visão geral

Arquivos públicos de dados (`*.json`) do **brasilemnumeros**, consumidos pelo app do repo `sitio`. O JSON é o produto. Cada pasta de indicador contém o notebook Colab usado para extrair, calcular e publicar aqueles dados. Há validador e testes em Python; ainda não há CI nem build.

## Contrato das séries

**Fonte de verdade:** `sitio/docs/contrato-de-indicadores.md` (schema **2**, regras `C1…C14`).
Este repositório só o **implementa e referencia** — se a prosa e o código divergirem, o
documento vale e a divergência é defeito a corrigir no mesmo commit.

- Os arquivos moram em `indicadores/<familia>/<id>.json`; o `id` é igual ao nome do arquivo
  sem `.json` e casa com `[a-z0-9-]+`.
- Nível superior: `schema: 1` (versão única do formato), `id`, `unit` (`type`, `symbol`, `decimals`, opcional `locale`),
  `eixo`, `medida`, `granularity` (`daily` | `monthly` | `annual`), `source`, opcional
  `sourceUrl`, `data`.
- `eixo` é a **comparabilidade declarada** (`percentual`, `reais`, `contagem`, `por-100-mil`);
  obriga o `unit.type` correspondente.
- `medida` diz **o que o número é** (`nivel`, `acumulado-12m`, `variacao-anual`, `estoque`,
  `participacao`) — não confundir com `granularity`, que é o espaçamento das datas.
- Cada ponto tem **exatamente** `{ "date": "YYYY-MM-DD", "value": número finito }`.
  **`rate` não faz parte do contrato**; campo desconhecido é erro.
- Datas ascendentes, um ponto por período (dia/mês/ano conforme a granularidade), data de
  calendário válida. Lacuna é **ausência de ponto** — nunca `null`, nunca zero.
- **Corpus de conformidade:** `tests/contrato/` (`validos/` e `invalidos/`, o código da regra
  no nome do arquivo). O validador Python e o `validate.js` do `sitio` rodam os MESMOS casos —
  é assim que os dois concordam.

## Editar ou regenerar dados

- **Nunca altere valores ao mudar a forma.** Correção de fórmula é revisão histórica: registre definição, fonte e impacto em `docs/metodologia.md` e peça aval antes.
- O IPCA é o piloto já migrado: `indicadores/ipca/IPCA.ipynb` busca a SGS 13522 e escreve `{date, value}` diretamente. Ao migrar os demais, o notebook tem de escrever o **schema 1** inteiro (`schema`, `id`, `unit`, `eixo`, `medida`, `granularity`, `source`, `data`) — `rate` e campos de apresentação não entram.
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
