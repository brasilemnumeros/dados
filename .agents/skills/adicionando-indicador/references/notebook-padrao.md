# Notebook padrão

O notebook é o motor: ele busca a fonte, calcula e escreve o JSON inteiro. Não há template para
preencher — use `indicadores/ipca/IPCA.ipynb` como exemplo real e siga as células abaixo.

## Células obrigatórias

1. **Markdown de abertura** — fonte, endpoint/códigos, unidade, eixo, medida, granularidade,
   definição, fórmula, período coberto e arquivo gerado.
2. **Setup e raiz** — imports, `RAIZ`, pasta e destino.
3. **Coleta** — busca a fonte completa, com retentativas; não lê o JSON publicado.
4. **Cálculo/recorte** — células visíveis; fórmula documentada; sem modo incremental.
5. **Filtro de período fechado** — descarta mês/ano corrente ou incompleto.
6. **Escrita** — monta os pontos e grava o JSON inteiro.
7. **Validação inline** — falha em contrato quebrado, C15, duplicata, ordem, valor não finito
   ou divergência com a fonte.

## Raiz e saída

```python
from pathlib import Path
import os
import json

RAIZ = Path(os.environ.get("DADOS_RAIZ", Path.cwd())).resolve()
if os.environ.get("DADOS_RAIZ"):
    PASTA = RAIZ / "indicadores" / "<familia>"
    if not PASTA.is_dir():
        raise SystemExit(f"família não encontrada em {PASTA}")
else:
    PASTA = RAIZ
DESTINO = Path(os.environ.get("<FAMILIA>_SAIDA", PASTA))
```

`DADOS_RAIZ` permite rodar contra uma cópia. `<FAMILIA>_SAIDA` permite ensaio sem tocar no
arquivo publicado; siga o padrão dos notebooks existentes (`IPCA_SAIDA`, `PIB_SAIDA` etc.).
O nome é maiúsculo, sem hífen e sem acento: `igp-m` → `IGPM_SAIDA`, `populacao` →
`POPULACAO_SAIDA`. Sem `DADOS_RAIZ` a pasta é o diretório atual (rodar de dentro da família);
com `DADOS_RAIZ`, a pasta da família tem de existir — não caia para a raiz do repo.

## Coleta

- Busque desde o início da fonte (ou `1995-01-01`, se ela cobrir) até hoje.
- Não leia o JSON publicado para decidir o que buscar.
- Repita em erro HTTP com espera crescente. Para BCB SGS: série diária exige `dataInicial` e
  no máximo 10 anos por requisição; espere 502, timeout e 200 com HTML.
- Se a fonte falhar de forma intermitente, o resultado deve ser determinístico ao rodar de novo.

## Cálculo e recorte

- Deixe a fórmula visível em célula própria.
- Prefira série oficial já calculada; se calcular, documente a fórmula e os insumos.
- Não arredonde o valor publicado; `unidade.casas` é só exibição.
- Filtre períodos abertos antes de montar os pontos.

## Dependências

Se o notebook usar pacote que ainda não está em `[project].dependencies` do `pyproject.toml`
(ex.: `openpyxl`, `beautifulsoup4`, `lxml`), acrescente a versão exata e rode `uv lock` no mesmo PR.
Os workflows instalam a partir do `uv.lock`; sem isso, a primeira execução automática falha no import.

## Escrita

```python
pontos = [
    {"data": data.strftime("%Y-%m-%d"), "valor": float(valor)}
    for data, valor in zip(datas, valores)
]

serie = {
    "versao": 1,
    "id": "<id>",
    "unidade": {"tipo": "percentual", "simbolo": "%", "casas": 2},
    "eixo": "percentual",
    "medida": "nivel",
    "granularidade": "mensal",
    "fonte": "<fonte legível>",
    "urlFonte": "<url https:// do recorte>",
    "dados": pontos,
}

DESTINO.mkdir(parents=True, exist_ok=True)
with (DESTINO / "<id>.json").open("w", encoding="utf-8") as arquivo:
    json.dump(serie, arquivo, ensure_ascii=False, indent=2)
```

- C15: mensal `AAAA-MM-01`; anual `AAAA-01-01`; diária com a data real.
- Normalize antes de formatar: `pd.Timestamp(ano, mes, 1)` no mensal; `pd.Timestamp(ano, 1, 1)`
  no anual. Em trimestre móvel, use o primeiro dia do **mês de encerramento** — não a data de
  publicação.
- Lacuna: omita o ponto; não preencha.
- Ordem ascendente e um ponto por período.

## Caminho do notebook e `urlNotebook`

O caminho do arquivo é contrato de produto: a ficha do app exibe um link “Ver o notebook que
gera estes dados” montado a partir de `urlNotebook` no catálogo, e K9 reprova se a URL não
apontar para um `.ipynb` que existe no disco.

- Um notebook por família, em `indicadores/<familia>/<Notebook>.ipynb`; uma família com várias
  séries pode ter um notebook só (ele grava todas).
- `urlNotebook` é sempre
  `https://github.com/brasilemnumeros/dados/blob/main/indicadores/<familia>/<Notebook>.ipynb` —
  copie o caminho do arquivo, não digite de memória.
- Renomear ou mover o notebook exige atualizar **todas** as entradas de catálogo que apontam
  para ele, no mesmo commit; o teste `tests/test_notebooks.py` também amarra o selo do Colab ao
  caminho.
- O notebook linkado é o que **gera** a série. Não aponte para um notebook de estudo, para a
  pasta da família nem para outro repositório.

## Validação inline

A última célula deve falhar se:

- o conjunto de chaves do topo não for o do contrato;
- `versao`, `id`, `unidade`, `eixo`, `medida`, `granularidade`, `fonte` não baterem;
- houver data fora de C15, período repetido, ordem errada ou valor não finito;
- o primeiro/último ponto ou a contagem divergirem da fonte;
- a conferência independente (quando existir) divergir.

## Rodada de ensaio

```bash
# use o Python do ambiente do repo (.venv/bin/python -m jupyter se necessário)
DADOS_RAIZ="$PWD" <FAMILIA>_SAIDA=/tmp/ensaio jupyter nbconvert \
  --to notebook --execute --ExecutePreprocessor.kernel_name=python3 \
  --ExecutePreprocessor.timeout=600 \
  --output-dir /tmp/nbexec indicadores/<familia>/<Notebook>.ipynb
```

Compare o JSON gerado com o publicado antes de rodar no destino real.
