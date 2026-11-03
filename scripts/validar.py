"""Validador do contrato dos arquivos de indicadores.

Fonte de verdade: ``sitio/docs/contrato-de-indicadores.md`` (regras C1…C15). Cada erro
começa pelo CÓDIGO da regra, porque o corpus de conformidade em ``tests/contrato/`` carrega
o código no nome do arquivo — o validador JS (``sitio/app/src/data/validate.js``) roda os
MESMOS casos. É assim que os dois deixam de divergir.

As regras ``K1…K9`` conferem o outro lado: o catálogo publicado
(``indicadores/catalogo.json``) contra as séries no disco — rótulo e dado têm de descrever o
mesmo conjunto. Aqui a fonte de verdade é o próprio produto: o app lê os dois.
"""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import date as _date
from pathlib import Path
from urllib.parse import unquote

VERSAO = 1
VERSAO_CATALOGO = 1
REGRA_ID = re.compile(r"[a-z0-9-]+")
REGRA_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
REGRA_LOCALE = re.compile(r"[a-z]{2}(-[A-Z]{2})?")
REGRA_URL = re.compile(r"https://\S+")
# MESMA regex do runtime (``app/src/data/catalog.js``): caminho relativo de duas partes, sem
# ``..`` nem barra inicial. ``Path(arquivo).parts`` aceitava ``../x.json`` e o catálogo passava
# no CI do `dados` para depois derrubar a lista no navegador.
REGRA_ARQUIVO_CATALOGO = re.compile(r"[a-z0-9-]+/[a-z0-9-]+\.json")
# K9 — o notebook é o método: a URL tem de apontar para um arquivo que existe no repo. O
# prefixo é o endereço canônico do GitHub (branch ``main``); um typo de caminho passa em
# qualquer validação de forma e só morre quando alguém clica.
PREFIXO_NOTEBOOK = "https://github.com/brasilemnumeros/dados/blob/main/indicadores/"
REGRA_NOTEBOOK = re.compile(r"[a-z0-9-]+/[^/]+\.ipynb")

TIPOS_UNIDADE = ("percentual", "numero", "moeda")
GRANULARIDADES = ("diaria", "mensal", "anual")
EIXOS = ("percentual", "reais", "contagem", "por-100-mil")
TIPO_DO_EIXO = {
    "percentual": "percentual",
    "reais": "moeda",
    "contagem": "numero",
    "por-100-mil": "numero",
}
MEDIDAS = ("nivel", "acumulado-12m", "variacao-anual", "estoque", "participacao")

CHAVES_SERIE = {
    "versao", "id", "unidade", "eixo", "medida", "granularidade", "fonte", "urlFonte", "dados",
}
CHAVES_UNIDADE = {"tipo", "simbolo", "casas", "idioma"}
CHAVES_PONTO = {"data", "valor"}


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
    if granularidade == "anual":
        return data[:4]
    if granularidade == "mensal":
        return data[:7]
    return data


def _inicio_do_periodo(data: str, granularidade: str) -> bool:
    """C15 — a data é o primeiro dia do período (mensal: dia 01; anual: 01-01)."""
    if granularidade == "anual":
        return data[5:] == "01-01"
    if granularidade == "mensal":
        return data[8:] == "01"
    return True


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

    if isinstance(serie.get("versao"), bool) or serie.get("versao") != VERSAO:
        erro("C1", f"versao {serie.get('versao')!r} desconhecida (esperado {VERSAO})")

    identificador = serie.get("id")
    if not isinstance(identificador, str) or not REGRA_ID.fullmatch(identificador):
        erro("C2", f"id {identificador!r} ausente ou fora do padrão [a-z0-9-]")
    elif checar_nome and identificador != caminho.stem:
        erro(
            "C2",
            f"id {identificador!r} diverge do nome do arquivo (esperado {caminho.stem!r})",
        )

    unidade = serie.get("unidade")
    if not isinstance(unidade, dict):
        erro("C3", "unidade ausente ou não é um objeto")
        unidade = {}
    else:
        for chave in unidade:
            if chave not in CHAVES_UNIDADE:
                erro("C3", f'unidade: campo desconhecido "{chave}"')
    if unidade.get("tipo") not in TIPOS_UNIDADE:
        erro("C3", f"unidade.tipo {unidade.get('tipo')!r} inválido (percentual|numero|moeda)")
    simbolo = unidade.get("simbolo")
    if not isinstance(simbolo, str) or not simbolo:
        erro("C3", "unidade.simbolo precisa ser string não vazia")
    decimais = unidade.get("casas")
    if not _numero_finito(decimais) or decimais < 0 or decimais != int(decimais):
        erro("C3", f"unidade.casas {decimais!r} inválido (inteiro >= 0)")
    idioma = unidade.get("idioma")
    if idioma is not None and (
        not isinstance(idioma, str) or not REGRA_LOCALE.fullmatch(idioma)
    ):
        erro("C3.1", f"unidade.idioma {idioma!r} fora do formato xx ou xx-XX (ex.: pt-BR)")

    eixo = serie.get("eixo")
    if eixo not in EIXOS:
        erro("C4", f"eixo {eixo!r} desconhecido (percentual|reais|contagem|por-100-mil)")
    elif TIPO_DO_EIXO[eixo] != unidade.get("tipo"):
        erro(
            "C4",
            f"eixo {eixo!r} exige unidade.tipo {TIPO_DO_EIXO[eixo]!r}, "
            f"veio {unidade.get('tipo')!r}",
        )

    medida = serie.get("medida")
    if medida not in MEDIDAS:
        erro(
            "C5",
            f"medida {medida!r} desconhecida "
            "(nivel|acumulado-12m|variacao-anual|estoque|participacao)",
        )

    granularidade = serie.get("granularidade")
    if granularidade not in GRANULARIDADES:
        erro("C6", f"granularidade {granularidade!r} inválida (diaria|mensal|anual)")

    fonte = serie.get("fonte")
    if not isinstance(fonte, str) or not fonte:
        erro("C7", "fonte precisa ser string não vazia")

    url = serie.get("urlFonte")
    if url is not None and (not isinstance(url, str) or not REGRA_URL.fullmatch(url)):
        erro("C7.1", "urlFonte precisa ser URL https://")

    dados = serie.get("dados")
    if not isinstance(dados, list):
        erro("C8", "dados precisa ser uma lista")
        return erros
    if not dados:
        erro("C8", "dados vazia")
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

        data = ponto.get("data")
        if not isinstance(data, str) or not _data_valida(data):
            erro("C9", f"ponto {indice}: data {data!r} fora do formato YYYY-MM-DD")
            data = None

        if "valor" not in ponto:
            erro("C10", f"ponto {indice}: sem campo valor")
        else:
            valor = ponto["valor"]
            if not _numero_finito(valor):
                erro("C10", f"ponto {indice}: valor {valor!r} não é número finito")

        if data is None:
            continue

        if not _inicio_do_periodo(data, granularidade):
            esperado = "YYYY-01-01" if granularidade == "anual" else "YYYY-MM-01"
            erro(
                "C15",
                f"ponto {indice}: data {data!r} não é o início do período "
                f"{granularidade} (esperado {esperado})",
            )

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


def validar_catalogo(raiz: Path) -> list[str]:
    """K1…K9 — o catálogo e o disco descrevem o MESMO conjunto de séries.

    O catálogo publica o rótulo (nome, grupo, escala, descrição) e a série publica o dado;
    se os dois divergirem, o app desenha um gráfico com o rótulo de outro. Por isso a
    conferência é cruzada e qualquer divergência entra no mesmo relatório das séries.

    A mensagem começa pelo código da regra, sem prefixo de caminho: o alvo é o próprio
    ``indicadores/catalogo.json``. Um catálogo que não dá para ler ou interpretar vira
    ``K1`` — o app ficaria com o rótulo de ninguém —, em vez de estourar a validação.
    """
    pasta = raiz / "indicadores"
    caminho = pasta / "catalogo.json"

    try:
        texto = caminho.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ["K1: catalogo.json ausente"]
    except OSError as exc:
        return [f"K1: catalogo.json ilegível ({exc})"]

    try:
        catalogo = json.loads(texto)
    except json.JSONDecodeError as exc:
        return [f"K1: catalogo.json com JSON inválido ({exc})"]

    if not isinstance(catalogo, dict):
        return ["K1: catalogo.json precisa ter um objeto na raiz"]

    versao = catalogo.get("versao")
    if isinstance(versao, bool) or versao != VERSAO_CATALOGO:
        # Versão desconhecida: o resto do arquivo pode significar outra coisa — não vale
        # interpretar. Quem publica corrige a versão e roda de novo.
        return [
            f"K6: catalogo.json com versao {versao!r} desconhecida (esperado {VERSAO_CATALOGO})"
        ]

    erros: list[str] = []

    grupos = catalogo.get("grupos")
    if not isinstance(grupos, dict):
        erros.append('K5: catalogo.json: "grupos" ausente ou não é um objeto')
        grupos = {}

    entradas = catalogo.get("indicadores")
    if not isinstance(entradas, list):
        erros.append('K1: catalogo.json: "indicadores" ausente ou não é uma lista')
        entradas = []

    # Caminhos declarados (<familia>/<id>.json), para não acusar K2 em série já coberta.
    declaradas: set[str] = set()
    # K8 — o runtime indexa id e arquivo: repetido, o navegador lança `each_key_duplicate` na
    # busca. Guarda o índice da PRIMEIRA ocorrência para a mensagem apontar as duas entradas.
    ids_vistos: dict[str, int] = {}
    arquivos_vistos: dict[str, int] = {}

    for indice, entrada in enumerate(entradas):
        if not isinstance(entrada, dict):
            erros.append(f"K3: catalogo.json: entrada {indice} não é um objeto")
            continue

        identificador = entrada.get("id")
        rotulo = identificador if isinstance(identificador, str) else f"entrada {indice}"

        # K7 — o runtime exige `nome` não vazio e rejeita o catálogo INTEIRO sem ele; `descricao`
        # é o texto da ficha. Sem esta conferência, a entrada sem nome passa no CI do `dados` e
        # tira a lista do ar para todo mundo.
        for chave in ("nome", "descricao"):
            valor = entrada.get(chave)
            if not isinstance(valor, str) or not valor:
                erros.append(
                    f"K7: catalogo.json: entrada {rotulo!r}: {chave} precisa ser string não vazia"
                )

        # K8 — id e arquivo são chave de índice no app (`{#each ... (ind.id)}` e o fetch da
        # série); repetido, o catálogo "válido" derruba a busca no navegador.
        if isinstance(identificador, str) and identificador:
            if identificador in ids_vistos:
                erros.append(
                    f"K8: catalogo.json: id {identificador!r} repetido "
                    f"(também na entrada {ids_vistos[identificador]})"
                )
            else:
                ids_vistos[identificador] = indice

        grupo = entrada.get("grupo")
        # lista/objeto é unhashable: checar o tipo antes do `in` é o que vira K5 em vez de
        # TypeError — o validador existe para reportar, não para derrubar o hook. A mensagem
        # separa "não é texto" de "não existe": dizer que um array "não existe em grupos"
        # manda quem lê procurar no lugar errado.
        if not isinstance(grupo, str):
            erros.append(
                f"K5: catalogo.json: entrada {rotulo!r}: grupo {grupo!r} precisa ser texto"
            )
        elif grupo not in grupos:
            erros.append(
                f"K5: catalogo.json: entrada {rotulo!r}: grupo {grupo!r} não existe em grupos"
            )

        # K9 — `urlNotebook` é o link de auditoria da ficha. A URL completa (em vez de um
        # caminho resolvido no app) mantém o host fora do bundle; em troca, o validador confere
        # o prefixo canônico e o arquivo no disco, para um typo não virar link morto em produção.
        # `unquote` existe por causa de `População.ipynb`: a URL é percent-encoded, o disco não.
        url_notebook = entrada.get("urlNotebook")
        if not isinstance(url_notebook, str) or not url_notebook.startswith(PREFIXO_NOTEBOOK):
            erros.append(
                f"K9: catalogo.json: entrada {rotulo!r}: urlNotebook precisa começar em "
                f"{PREFIXO_NOTEBOOK!r}"
            )
        else:
            bruto = url_notebook[len(PREFIXO_NOTEBOOK) :]
            relativo = unquote(bruto)
            if not REGRA_NOTEBOOK.fullmatch(bruto) or not REGRA_NOTEBOOK.fullmatch(relativo):
                erros.append(
                    f"K9: catalogo.json: entrada {rotulo!r}: urlNotebook {url_notebook!r} "
                    "não termina em <familia>/<arquivo>.ipynb"
                )
            elif not (pasta / relativo).is_file():
                erros.append(
                    f"K9: catalogo.json: entrada {rotulo!r}: notebook {relativo!r} não existe"
                )

        arquivo = entrada.get("arquivo")
        if not isinstance(arquivo, str) or not REGRA_ARQUIVO_CATALOGO.fullmatch(arquivo):
            erros.append(
                f"K1: catalogo.json: entrada {rotulo!r}: arquivo {arquivo!r} "
                "não é <familia>/<id>.json"
            )
            continue

        if arquivo in arquivos_vistos:
            erros.append(
                f"K8: catalogo.json: arquivo {arquivo!r} repetido "
                f"(também na entrada {arquivos_vistos[arquivo]})"
            )
        else:
            arquivos_vistos[arquivo] = indice

        declaradas.add(arquivo)
        serie_caminho = pasta / arquivo
        if not serie_caminho.is_file():
            erros.append(f"K1: catalogo.json: entrada {rotulo!r}: arquivo {arquivo!r} não existe")
            continue

        try:
            serie = json.loads(serie_caminho.read_text(encoding="utf-8"))
        except OSError as exc:
            erros.append(
                f"K1: catalogo.json: entrada {rotulo!r}: não foi possível ler {arquivo!r} ({exc})"
            )
            continue
        except json.JSONDecodeError as exc:
            erros.append(
                f"K1: catalogo.json: entrada {rotulo!r}: {arquivo!r} com JSON inválido ({exc})"
            )
            continue

        if not isinstance(serie, dict):
            erros.append(
                f"K1: catalogo.json: entrada {rotulo!r}: {arquivo!r} precisa ter um objeto na raiz"
            )
            continue

        # O id da entrada tem de coincidir com o nome do arquivo E com o id da série. Um só
        # defeito quebra os dois elos, então reporta-se só o primeiro.
        if not isinstance(identificador, str) or identificador != serie_caminho.stem:
            erros.append(
                f"K3: catalogo.json: entrada {rotulo!r}: id diverge do nome do arquivo "
                f"(esperado {serie_caminho.stem!r})"
            )
        elif serie.get("id") != identificador:
            erros.append(
                f"K3: catalogo.json: entrada {rotulo!r}: id diverge do id da série {arquivo!r} "
                f"({serie.get('id')!r})"
            )

        escala = entrada.get("escala")
        unidade = serie.get("unidade")
        tipo = unidade.get("tipo") if isinstance(unidade, dict) else None
        if escala != tipo:
            erros.append(
                f"K4: catalogo.json: entrada {rotulo!r}: escala {escala!r} diverge de "
                f"unidade.tipo {tipo!r} em {arquivo!r}"
            )

    for serie_caminho in _series_da_raiz(raiz):
        relativo = serie_caminho.relative_to(pasta).as_posix()
        if relativo not in declaradas:
            erros.append(f"K2: catalogo.json: série {relativo!r} não tem entrada no catálogo")

    return erros


def _falhas_dos_caminhos(caminhos: list[Path]) -> dict[Path, list[str]]:
    """Valida cada arquivo avulso e devolve só o que tem erro — o laço dos dois caminhos."""
    falhas: dict[Path, list[str]] = {}
    for caminho in caminhos:
        problemas = validar_arquivo(caminho)
        if problemas:
            falhas[caminho] = problemas
    return falhas


def validar_todos(raiz: Path) -> dict[Path, list[str]]:
    """Valida todas as séries sob ``raiz`` e o catálogo; devolve só o que tem erro."""
    falhas = _falhas_dos_caminhos(_series_da_raiz(raiz))
    problemas_catalogo = validar_catalogo(raiz)
    if problemas_catalogo:
        falhas[raiz / "indicadores" / "catalogo.json"] = problemas_catalogo
    return falhas


def main(argumentos: list[str] | None = None) -> int:
    """CLI: valida os arquivos indicados (ou todos os da raiz, mais o catálogo). Exit 0/1."""
    caminhos = [Path(arg) for arg in (sys.argv[1:] if argumentos is None else argumentos)]

    if caminhos:
        # Arquivos avulsos: o catálogo descreve o conjunto inteiro, então fica de fora —
        # conferir a raiz a partir de um recorte produziria K2 falso.
        falhas = _falhas_dos_caminhos(caminhos)
    else:
        if not _series_da_raiz(Path(".")):
            print(
                f"nenhuma série encontrada em {Path('.').resolve()}",
                file=sys.stderr,
            )
            return 1
        falhas = validar_todos(Path("."))

    for problemas in falhas.values():
        for problema in problemas:
            print(problema)

    if falhas:
        print(f"{len(falhas)} arquivo(s) fora do contrato", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
