#!/usr/bin/env python3
"""Converte os JSONs publicados de `dados/` para o schema canônico de série (§6, emenda D7).

Fase da convivência: cada ponto publica `rate` E `value` com o mesmo número.

Uso:
    python3 converter-schema-canonico.py            # converte todos os 13 arquivos
    python3 converter-schema-canonico.py --check     # só compara, não escreve

Regra inviolável: NENHUM valor muda. A conversão é de forma, não de conteúdo.
A única remoção de dado é a deduplicação de meses repetidos (mantém a última
leitura do mês, com aviso), corrigindo o defeito medido em 2026-10-14.
"""

import argparse
import glob
import json
import os
import sys

# --- Metadados por arquivo (tabela do plano 11 / anexo da spec §6) -----------
# id -> unit / granularity / source
META = {
    "selic-meta-acum-12m": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "Banco Central do Brasil",
    },
    "selic-over-acum-12m": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "Banco Central do Brasil",
    },
    "ipca-acum-12m": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "IBGE",
    },
    "igpm-acum-12m": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "FGV",
    },
    "pib-real-anual": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "annual",
        "source": "IBGE",
    },
    "mvgr-nominal": {
        "unit": {"type": "currency", "symbol": "R$", "decimals": 2},
        "granularity": "monthly",
        "source": "Banco Central do Brasil",
    },
    "mvgr-real": {
        "unit": {"type": "currency", "symbol": "R$", "decimals": 2},
        "granularity": "monthly",
        "source": "Banco Central do Brasil",
    },
    "caged-total-mensal": {
        "unit": {"type": "number", "symbol": "vínculos", "decimals": 0},
        "granularity": "monthly",
        "source": "Ministério do Trabalho",
    },
    "populacao-total-anual": {
        "unit": {"type": "number", "symbol": "hab.", "decimals": 0},
        "granularity": "annual",
        "source": "IBGE",
    },
    "populacao-variacao-anual": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "annual",
        "source": "IBGE",
    },
    "homicidios-anual": {
        "unit": {"type": "number", "symbol": "por 100 mil", "decimals": 2},
        "granularity": "annual",
        "source": "IPEA/Atlas da Violência",
    },
    "homicidios-armas-fogo-anual": {
        "unit": {"type": "number", "symbol": "por 100 mil", "decimals": 2},
        "granularity": "annual",
        "source": "IPEA/Atlas da Violência",
    },
    "proporcao-homicidios-armas-fogo-anual": {
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "annual",
        "source": "IPEA/Atlas da Violência",
    },
}

RAIZ = os.path.dirname(os.path.abspath(__file__))


def _valor(ponto):
    """Lê o valor do ponto, aceitando `value` (famílias novas) ou `rate` (antigas)."""
    return ponto["value"] if "value" in ponto else ponto["rate"]


def _dedupe(dados, caminho):
    """Colapsa meses repetidos mantendo a ÚLTIMA leitura do mês (avisa)."""
    meses = {}
    for ponto in dados:
        d = ponto["date"]
        v = _valor(ponto)
        if d[:7] in meses:
            print(f"AVISO: mês repetido {d[:7]} em {caminho} — mantendo o último valor")
        meses[d[:7]] = (d, v)
    return sorted(
        ({"date": d, "rate": v, "value": v} for d, v in meses.values()),
        key=lambda p: p["date"],
    )


def converter(caminho, escrever=True):
    id_ = os.path.basename(caminho)[:-5]
    if id_ not in META:
        print(f"PULADO (sem metadados): {caminho}", file=sys.stderr)
        return None
    with open(caminho, encoding="utf-8") as f:
        bruto = json.load(f)
    pontos = _dedupe(bruto["data"], caminho)
    saida = {"schema": 1, "id": id_, **META[id_], "data": pontos}
    if escrever:
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(saida, f, ensure_ascii=False, indent=2)
        print(f"{caminho}: {len(pontos)} pontos")
    return pontos


def arquivos():
    return sorted(
        f
        for f in glob.glob(os.path.join(RAIZ, "*", "*.json"))
        if os.path.basename(f)[:-5] in META
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="só compara, não escreve")
    args = ap.parse_args()
    for caminho in arquivos():
        converter(caminho, escrever=not args.check)


if __name__ == "__main__":
    main()
