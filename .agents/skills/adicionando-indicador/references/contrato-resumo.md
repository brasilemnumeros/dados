# Contrato — resumo operacional

**Fonte de verdade:** `../sitio/docs/contrato-de-indicadores.md` (`C1…C15` + `K1…K9`).
Este arquivo é atalho de consulta; se divergir do documento, o documento vale.

## Arquivo

```
indicadores/<familia>/<id>.json
```

- `id` = nome do arquivo sem `.json`, em `[a-z0-9-]+`.
- `versao: 1` (única). Versão desconhecida reprova.

## Topo

| chave | obrigatória | valor |
|---|---|---|
| `versao` | sim | inteiro `1` |
| `id` | sim | texto, `[a-z0-9-]+`, igual ao arquivo |
| `unidade` | sim | objeto (abaixo) |
| `eixo` | sim | `percentual` \| `reais` \| `contagem` \| `por-100-mil` \| `por-mil` |
| `medida` | sim | `nivel` \| `acumulado-12m` \| `variacao-anual` \| `estoque` \| `participacao` |
| `granularidade` | sim | `diaria` \| `mensal` \| `anual` \| `bienal` |
| `fonte` | sim | texto não vazio; instituição/fonte |
| `urlFonte` | não | URL `https://` do recorte exato |
| `dados` | sim | lista não vazia de `{data, valor}` |

Campo desconhecido no topo, no ponto ou na unidade é erro (C8.1).

## Unidade

```json
{ "tipo": "percentual", "simbolo": "%", "casas": 2 }
```

- `tipo`: `percentual` | `numero` | `moeda`.
- `simbolo`: texto não vazio.
- `casas`: inteiro ≥ 0; é exibição, não arredonda o valor publicado.
- `idioma`: opcional, formato `xx` ou `xx-XX` (ex.: `pt-BR`).

## Eixo ↔ unidade

| `eixo` | `unidade.tipo` |
|---|---|
| `percentual` | `percentual` |
| `reais` | `moeda` |
| `contagem` | `numero` |
| `por-100-mil` | `numero` |
| `por-mil` | `numero` |

`eixo` é comparabilidade **declarada**: duas séries só dividem o mesmo eixo y se o `eixo` for
igual. Não inferir por magnitude.

## Medida

| `medida` | o número é |
|---|---|
| `nivel` | valor no período (taxa, preço, razão por 100 mil) |
| `acumulado-12m` | variação acumulada nos 12 meses até a data |
| `variacao-anual` | variação contra o ano/período anterior |
| `estoque` | total num instante (empregos, habitantes) |
| `participacao` | parte de um todo, em % |

## Granularidade

`diaria` | `mensal` | `anual` | `bienal` — é o espaçamento das datas, não a frequência de
publicação. `bienal` exige paridade de ano: todos os pontos em anos pares ou todos em anos
ímpares (lacuna de 4 anos é permitida).

## Pontos

```json
{ "data": "2026-09-01", "valor": 5.2 }
```

- Exatamente `data` e `valor`.
- `data`: `YYYY-MM-DD`, calendário válido.
- `valor`: número finito; nunca booleano, `null` ou texto.
- Um ponto por período: dia (diária), `AAAA-MM` (mensal), `AAAA` (anual).
- Datas estritamente ascendentes.
- Lacuna = ausência de ponto; não usar `null` nem zero de preenchimento.
- A última data pode ser período aberto; nenhum consumidor extrapola.

## C15 — início do período

- `mensal`: dia `01`, qualquer mês (`AAAA-MM-01`).
- `anual` e `bienal`: `01-01` (`AAAA-01-01`).
- `diaria`: a data real do dia.

## Catálogo

Arquivo `indicadores/catalogo.json`, irmão das famílias:

```json
{
  "id": "ipca-acum-12m",
  "nome": "IPCA (%)",
  "grupo": "inflacao",
  "escala": "percentual",
  "descricao": "Variação acumulada do IPCA em 12 meses",
  "arquivo": "ipca/ipca-acum-12m.json",
  "urlNotebook": "https://github.com/brasilemnumeros/dados/blob/main/indicadores/ipca/IPCA.ipynb"
}
```

- `escala` = `unidade.tipo` da série (K4).
- `grupo` existe em `grupos` (K5).
- `id` = nome do arquivo = `id` da série (K3).
- `nome` e `descricao` não vazios (K7); `id`/`arquivo` únicos (K8).
- `urlNotebook` é URL `https://` completa, sob
  `https://github.com/brasilemnumeros/dados/blob/main/indicadores/`, apontando para um `.ipynb`
  que existe no disco (K9) — é o link de auditoria da ficha.
- Toda série do disco tem entrada (K2); todo `arquivo` existe (K1).
- Indicador novo = série + catálogo no mesmo PR.
