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
PASTA = RAIZ / "indicadores" / "<familia>" if (RAIZ / "indicadores" / "<familia>").is_dir() else RAIZ
DESTINO = Path(os.environ.get("<FAMILIA>_SAIDA", PASTA))
```

`DADOS_RAIZ` permite rodar contra uma cópia. `<FAMILIA>_SAIDA` permite ensaio sem tocar no
arquivo publicado; siga o padrão dos notebooks existentes (`IPCA_SAIDA`, `PIB_SAIDA` etc.).

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
- Lacuna: omita o ponto; não preencha.
- Ordem ascendente e um ponto por período.

## Validação inline

A última célula deve falhar se:

- o conjunto de chaves do topo não for o do contrato;
- `versao`, `id`, `unidade`, `eixo`, `medida`, `granularidade`, `fonte` não baterem;
- houver data fora de C15, período repetido, ordem errada ou valor não finito;
- o primeiro/último ponto ou a contagem divergirem da fonte;
- a conferência independente (quando existir) divergir.

## Rodada de ensaio

```bash
DADOS_RAIZ="$PWD" <FAMILIA>_SAIDA=/tmp/ensaio ./.venv/bin/jupyter nbconvert \
  --to notebook --execute --ExecutePreprocessor.kernel_name=python3 \
  --ExecutePreprocessor.timeout=600 \
  --output-dir /tmp/nbexec indicadores/<familia>/<Notebook>.ipynb
```

Compare o JSON gerado com o publicado antes de rodar no destino real.
