"""O selo "Open in Colab" é parte do contrato público do notebook.

Ele sumiu de 7 dos 8 notebooks quando as células de abertura foram reescritas na migração —
passou despercebido porque nenhum teste olhava para o markdown do notebook. Este teste fecha
essa porta: o primeiro cell é o selo, e ele aponta para o PRÓPRIO arquivo no caminho publicado.
"""

import json
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parents[1] / "indicadores"
PREFIXO = "https://colab.research.google.com/github/brasilemnumeros/dados/blob/main/indicadores/"

# Saídas commitadas vêm de execução local: um print de caminho resolvido vira o diretório
# da máquina de quem rodou (e já apareceu um `dados-skill` que nem existe mais).
CAMINHOS_LOCAIS = ("/Users/", "/home/", "/root/", "C:\\", "file://")


def test_todo_notebook_tem_selo_do_colab():
    notebooks = sorted(RAIZ.glob("*/*.ipynb"))
    assert notebooks, f"nenhum notebook encontrado em {RAIZ}"
    for caminho in notebooks:
        nb = json.loads(caminho.read_text(encoding="utf-8"))
        primeira = nb["cells"][0]
        fonte = "".join(primeira.get("source", []))
        relativo = caminho.relative_to(RAIZ).as_posix()
        esperado = PREFIXO + quote(relativo)
        assert primeira["cell_type"] == "markdown", caminho
        assert primeira.get("metadata", {}).get("id") == "view-in-github", caminho
        assert esperado in fonte, f"{caminho}: selo aponta para {fonte!r}"
        assert "colab-badge.svg" in fonte, caminho


def test_notebook_nao_expoe_caminho_da_maquina():
    """O notebook é publicado com as saídas: nenhuma célula pode citar caminho absoluto.

    O caminho exibido é o relativo à raiz (`indicadores/<familia>/<id>.json`), que é estável
    entre máquinas e igual ao citado no markdown. Vale para o código e para as saídas.
    """
    notebooks = sorted(RAIZ.glob("*/*.ipynb"))
    assert notebooks, f"nenhum notebook encontrado em {RAIZ}"
    for caminho in notebooks:
        texto = caminho.read_text(encoding="utf-8")
        for marca in CAMINHOS_LOCAIS:
            assert marca not in texto, f"{caminho}: caminho local {marca!r} no notebook publicado"
