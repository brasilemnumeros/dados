"""Validador do contrato dos arquivos de indicadores.

Fonte de verdade: ``sitio/docs/contrato-de-indicadores.md`` (regras C1…C14). Cada erro
começa pelo CÓDIGO da regra, porque o corpus de conformidade em ``tests/contrato/`` carrega
o código no nome do arquivo — o validador JS (``sitio/app/src/data/validate.js``) roda os
MESMOS casos. É assim que os dois deixam de divergir.
"""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date as _date
from pathlib import Path

SCHEMA = 1
REGRA_ID = re.compile(r"[a-z0-9-]+")
REGRA_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
REGRA_LOCALE = re.compile(r"[a-z]{2}(-[A-Z]{2})?")
REGRA_URL = re.compile(r"https://\S+")

TIPOS_UNIDADE = ("percentage", "number", "currency")
GRANULARIDADES = ("daily", "monthly", "annual")
EIXOS = ("percentual", "reais", "contagem", "por-100-mil")
TIPO_DO_EIXO = {
    "percentual": "percentage",
    "reais": "currency",
    "contagem": "number",
    "por-100-mil": "number",
}
MEDIDAS = ("nivel", "acumulado-12m", "variacao-anual", "estoque", "participacao")

CHAVES_SERIE = {
    "schema", "id", "unit", "eixo", "medida", "granularity", "source", "sourceUrl", "data",
}
CHAVES_UNIDADE = {"type", "symbol", "decimals", "locale"}
CHAVES_PONTO = {"date", "value"}


def _numero_finito(valor: object) -> bool:
    """True para int/float não-booleano representável como float finito."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return False
    try:
        return math.isfinite(valor)
    except OverflowError:
        return False


def _data_valida(texto: str) -> bool:
    """C9 — formato e calendário (rejeita 2019-02-31)."""
    if not REGRA_DATA.fullmatch(texto):
        return False
    try:
        _date.fromisoformat(texto)
    except ValueError:
        return False
    return True


def _chave_periodo(data: str, granularidade: str) -> str:
    """C11 — dia, mês ou ano conforme a granularidade."""
    if granularidade == "annual":
        return data[:4]
    if granularidade == "monthly":
        return data[:7]
    return data


def validar_serie(serie: object, caminho: Path, checar_nome: bool = True) -> list[str]:
    """Valida uma série contra o contrato e devolve erros em português (com o código C#).

    ``checar_nome=False`` serve ao corpus de conformidade: o nome do arquivo lá carrega o
    CÓDIGO da regra (ex.: ``C3.1-locale-invalido.json``), não o id da série.
    """
    rotulo = str(caminho)

    if not isinstance(serie, dict):
        return [f"{rotulo}: C1: a raiz do JSON precisa ser um objeto"]

    erros: list[str] = []

    def erro(codigo: str, texto: str) -> None:
        erros.append(f"{rotulo}: {codigo}: {texto}")

    for chave in serie:
        if chave not in CHAVES_SERIE:
            erro("C8.1", f'campo desconhecido na raiz: "{chave}"')

    if isinstance(serie.get("schema"), bool) or serie.get("schema") != SCHEMA:
        erro("C1", f"schema {serie.get('schema')!r} desconhecido (esperado {SCHEMA})")

    identificador = serie.get("id")
    if not isinstance(identificador, str) or not REGRA_ID.fullmatch(identificador):
        erro("C2", f"id {identificador!r} ausente ou fora do padrão [a-z0-9-]")
    elif checar_nome and identificador != caminho.stem:
        erro(
            "C2",
            f"id {identificador!r} diverge do nome do arquivo (esperado {caminho.stem!r})",
        )

    unidade = serie.get("unit")
    if not isinstance(unidade, dict):
        erro("C3", "unit ausente ou não é um objeto")
        unidade = {}
    else:
        for chave in unidade:
            if chave not in CHAVES_UNIDADE:
                erro("C3", f'unit: campo desconhecido "{chave}"')
    if unidade.get("type") not in TIPOS_UNIDADE:
        erro("C3", f"unit.type {unidade.get('type')!r} inválido (percentage|number|currency)")
    simbolo = unidade.get("symbol")
    if not isinstance(simbolo, str) or not simbolo:
        erro("C3", "unit.symbol precisa ser string não vazia")
    decimais = unidade.get("decimals")
    if not _numero_finito(decimais) or decimais < 0 or decimais != int(decimais):
        erro("C3", f"unit.decimals {decimais!r} inválido (inteiro >= 0)")
    locale = unidade.get("locale")
    if locale is not None and (
        not isinstance(locale, str) or not REGRA_LOCALE.fullmatch(locale)
    ):
        erro("C3.1", f"unit.locale {locale!r} fora do padrão BCP 47 (ex.: pt-BR)")

    eixo = serie.get("eixo")
    if eixo not in EIXOS:
        erro("C4", f"eixo {eixo!r} desconhecido (percentual|reais|contagem|por-100-mil)")
    elif TIPO_DO_EIXO[eixo] != unidade.get("type"):
        erro(
            "C4",
            f"eixo {eixo!r} exige unit.type {TIPO_DO_EIXO[eixo]!r}, "
            f"veio {unidade.get('type')!r}",
        )

    medida = serie.get("medida")
    if medida not in MEDIDAS:
        erro(
            "C5",
            f"medida {medida!r} desconhecida "
            "(nivel|acumulado-12m|variacao-anual|estoque|participacao)",
        )

    granularidade = serie.get("granularity")
    if granularidade not in GRANULARIDADES:
        erro("C6", f"granularity {granularidade!r} inválida (daily|monthly|annual)")

    fonte = serie.get("source")
    if not isinstance(fonte, str) or not fonte:
        erro("C7", "source precisa ser string não vazia")

    url = serie.get("sourceUrl")
    if url is not None and (not isinstance(url, str) or not REGRA_URL.fullmatch(url)):
        erro("C7.1", "sourceUrl precisa ser URL https://")

    dados = serie.get("data")
    if not isinstance(dados, list):
        erro("C8", "data precisa ser uma lista")
        return erros
    if not dados:
        erro("C8", "data vazia")
        return erros

    vistos: dict[str, int] = {}
    anterior: str | None = None
    for indice, ponto in enumerate(dados):
        if not isinstance(ponto, dict):
            erro("C8", f"ponto {indice}: não é um objeto")
            continue

        for chave in ponto:
            if chave not in CHAVES_PONTO:
                erro("C8.1", f'ponto {indice}: campo desconhecido "{chave}"')

        data = ponto.get("date")
        if not isinstance(data, str) or not _data_valida(data):
            erro("C9", f"ponto {indice}: date {data!r} fora do formato YYYY-MM-DD")
            data = None

        if "value" not in ponto:
            erro("C10", f"ponto {indice}: sem campo value")
        else:
            valor = ponto["value"]
            if not _numero_finito(valor):
                erro("C10", f"ponto {indice}: value {valor!r} não é número finito")

        if data is None:
            continue

        chave = _chave_periodo(data, granularidade)
        if chave in vistos:
            erro(
                "C11",
                f"ponto {indice}: período {chave!r} repetido "
                f"(também no ponto {vistos[chave]})",
            )
        else:
            vistos[chave] = indice

        if anterior is not None and data <= anterior:
            erro(
                "C12",
                f"ponto {indice}: {data!r} não é posterior a {anterior!r} "
                "(ordem ascendente)",
            )
        anterior = data

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
    return sorted(raiz.glob("indicadores/*/*.json"))


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
