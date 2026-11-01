"""Validador do contrato das séries JSON consumidas pelo sitio.

Contrato (sitio/app/src/data/validate.js): o aplicativo lê apenas ``value``
e tolera campos extras como ``rate``. Não são impostos ordem das datas,
dia 01 nem período fechado. Datas são ``YYYY-MM-DD`` só com dígitos ASCII
(fullmatch, sem quebra de linha). Duplicata por ``YYYY-MM`` em granularidade
mensal/anual e por ``YYYY-MM-DD`` em ``daily``.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

TIPOS_UNIDADE = ("percentage", "number", "currency")
GRANULARIDADES = ("daily", "monthly", "annual")
PASTAS_IGNORADAS = ("governos",)
FORMATO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def validar_serie(serie: dict, caminho: Path) -> list[str]:
    """Valida uma série contra o contrato e devolve erros em português."""
    rotulo = str(caminho)
    if not isinstance(serie, dict):
        return [f"{rotulo}: a raiz do JSON precisa ser um objeto"]

    erros: list[str] = []

    schema = serie.get("schema")
    if isinstance(schema, bool) or schema != 1:
        erros.append(f"{rotulo}: schema {schema!r} não suportado (esperado 1)")

    identificador = serie.get("id")
    if identificador != caminho.stem:
        erros.append(
            f"{rotulo}: id {identificador!r} diverge do nome do arquivo "
            f"(esperado {caminho.stem!r})"
        )

    unidade = serie.get("unit")
    if not isinstance(unidade, dict):
        erros.append(f"{rotulo}: unit ausente ou não é um objeto")
        unidade = {}
    if unidade.get("type") not in TIPOS_UNIDADE:
        erros.append(
            f"{rotulo}: unit.type {unidade.get('type')!r} inválido "
            "(use percentage, number ou currency)"
        )
    simbolo = unidade.get("symbol")
    if not isinstance(simbolo, str) or not simbolo:
        erros.append(f"{rotulo}: unit.symbol precisa ser string não vazia")
    decimais = unidade.get("decimals")
    if isinstance(decimais, bool) or not isinstance(decimais, int) or decimais < 0:
        erros.append(f"{rotulo}: unit.decimals {decimais!r} inválido (inteiro >= 0)")

    granularidade = serie.get("granularity")
    if granularidade not in GRANULARIDADES:
        erros.append(
            f"{rotulo}: granularity {granularidade!r} inválida "
            "(use daily, monthly ou annual)"
        )

    fonte = serie.get("source")
    if not isinstance(fonte, str) or not fonte:
        erros.append(f"{rotulo}: source precisa ser string não vazia")

    dados = serie.get("data")
    if not isinstance(dados, list) or not dados:
        erros.append(f"{rotulo}: data precisa ser lista não vazia")
        return erros

    vistos: dict[str, int] = {}
    for indice, ponto in enumerate(dados):
        if not isinstance(ponto, dict):
            erros.append(f"{rotulo}: ponto {indice}: não é um objeto")
            continue

        data = ponto.get("date")
        if "date" not in ponto:
            erros.append(f"{rotulo}: ponto {indice}: sem campo date")
        elif not isinstance(data, str) or not FORMATO_DATA.fullmatch(data):
            erros.append(
                f"{rotulo}: ponto {indice}: date {data!r} fora do formato YYYY-MM-DD"
            )

        if "value" not in ponto:
            erros.append(f"{rotulo}: ponto {indice}: sem campo value")
        else:
            valor = ponto["value"]
            if isinstance(valor, bool) or not isinstance(valor, (int, float)):
                erros.append(f"{rotulo}: ponto {indice}: value {valor!r} não é numérico")
            elif not math.isfinite(valor):
                erros.append(f"{rotulo}: ponto {indice}: value não é finito")

        if isinstance(data, str) and FORMATO_DATA.fullmatch(data):
            if granularidade == "daily":
                chave, descricao = data, f"data {data} repetida"
            else:
                chave, descricao = data[:7], f"mês {data[:7]} repetido"
            if chave in vistos:
                erros.append(
                    f"{rotulo}: ponto {indice}: {descricao} "
                    f"(também no ponto {vistos[chave]})"
                )
            else:
                vistos[chave] = indice

    return erros


def validar_arquivo(caminho: Path) -> list[str]:
    """Lê o JSON do arquivo e valida a série; erro de leitura/parse vira erro."""
    try:
        texto = caminho.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{caminho}: não foi possível ler o arquivo ({exc})"]
    try:
        serie = json.loads(texto)
    except json.JSONDecodeError as exc:
        return [f"{caminho}: JSON inválido ({exc})"]
    return validar_serie(serie, caminho)


def _series_da_raiz(raiz: Path) -> list[Path]:
    return sorted(
        caminho
        for caminho in raiz.glob("*/*.json")
        if caminho.parent.name not in PASTAS_IGNORADAS
    )


def validar_todos(raiz: Path) -> dict[Path, list[str]]:
    """Valida todas as séries sob ``raiz``; devolve dict só com arquivos com erro."""
    falhas: dict[Path, list[str]] = {}
    for caminho in _series_da_raiz(raiz):
        problemas = validar_arquivo(caminho)
        if problemas:
            falhas[caminho] = problemas
    return falhas


def main(argumentos: list[str] | None = None) -> int:
    """CLI: valida os arquivos indicados (ou todos os da raiz). Exit 0/1."""
    caminhos = [Path(arg) for arg in (sys.argv[1:] if argumentos is None else argumentos)]

    if caminhos:
        alvos = caminhos
    else:
        alvos = _series_da_raiz(Path("."))
        if not alvos:
            print(
                f"nenhuma série encontrada em {Path('.').resolve()}",
                file=sys.stderr,
            )
            return 1

    falhas: dict[Path, list[str]] = {}
    for caminho in alvos:
        problemas = validar_arquivo(caminho)
        if problemas:
            falhas[caminho] = problemas

    for problemas in falhas.values():
        for problema in problemas:
            print(problema)

    if falhas:
        print(f"{len(falhas)} arquivo(s) fora do contrato", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
