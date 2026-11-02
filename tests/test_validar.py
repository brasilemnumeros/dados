import json
from pathlib import Path

from scripts.validar import validar_serie

CAMINHO = Path("indicadores/ipca/ipca-acum-12m.json")
CONTRATO = Path(__file__).parent / "contrato"


def serie(**over):
    base = {
        "versao": 1,
        "id": "ipca-acum-12m",
        "unidade": {"tipo": "percentual", "simbolo": "%", "casas": 2},
        "eixo": "percentual",
        "medida": "acumulado-12m",
        "granularidade": "mensal",
        "fonte": "IBGE",
        "dados": [{"data": "2026-09-01", "valor": 5.0}],
    }
    base.update(over)
    return base


def erros(s):
    return validar_serie(s, CAMINHO)


def test_serie_valida():
    assert erros(serie()) == []


def test_recusa_campo_extra_no_ponto():
    s = serie(dados=[{"data": "2026-09-01", "valor": 5.0, "unidade": "x"}])
    assert any(e.split(": ")[1] == "C8.1" for e in erros(s))


def test_recusa_ponto_sem_valor():
    s = serie(dados=[{"data": "2026-09-01"}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_versao_desconhecida():
    assert any(e.split(": ")[1] == "C1" for e in erros(serie(versao=2)))


def test_recusa_id_divergente():
    assert any(e.split(": ")[1] == "C2" for e in erros(serie(id="outro")))


def test_recusa_tipo_de_unidade():
    s = serie(unidade={"tipo": "peso", "simbolo": "kg", "casas": 1})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_recusa_simbolo_vazio():
    s = serie(unidade={"tipo": "numero", "simbolo": "", "casas": 0})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_recusa_casas_fracionarias():
    s = serie(unidade={"tipo": "percentual", "simbolo": "%", "casas": 2.5})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_aceita_casas_float_integral():
    s = serie(unidade={"tipo": "percentual", "simbolo": "%", "casas": 2.0})
    assert erros(s) == []


def test_recusa_idioma_fora_do_padrao():
    s = serie(
        unidade={"tipo": "moeda", "simbolo": "R$", "casas": 0, "idioma": "portugues"},
        eixo="reais",
        medida="nivel",
    )
    assert any(e.split(": ")[1] == "C3.1" for e in erros(s))


def test_recusa_eixo_incompativel_com_unidade():
    assert any(e.split(": ")[1] == "C4" for e in erros(serie(eixo="reais")))


def test_recusa_medida_desconhecida():
    assert any(e.split(": ")[1] == "C5" for e in erros(serie(medida="media-movel")))


def test_recusa_granularidade():
    assert any(e.split(": ")[1] == "C6" for e in erros(serie(granularidade="semanal")))


def test_recusa_fonte_vazia():
    assert any(e.split(": ")[1] == "C7" for e in erros(serie(fonte="")))


def test_recusa_url_da_fonte_invalida():
    assert any(e.split(": ")[1] == "C7.1" for e in erros(serie(urlFonte="ftp://x")))


def test_recusa_dados_vazios():
    assert any(e.split(": ")[1] == "C8" for e in erros(serie(dados=[])))


def test_recusa_data_fora_do_calendario():
    s = serie(dados=[{"data": "2026-02-31", "valor": 1.0}])
    assert any(e.split(": ")[1] == "C9" for e in erros(s))


def test_recusa_valor_nao_finito():
    s = serie(dados=[{"data": "2026-09-01", "valor": float("nan")}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_valor_inteiro_gigante():
    s = serie(dados=[{"data": "2026-09-01", "valor": 10**400}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_mes_repetido():
    s = serie(dados=[
        {"data": "2026-08-01", "valor": 5.0},
        {"data": "2026-08-31", "valor": 6.0},
    ])
    assert any(e.split(": ")[1] == "C11" for e in erros(s))


def test_recusa_fora_de_ordem():
    s = serie(dados=[
        {"data": "2026-09-01", "valor": 5.0},
        {"data": "2026-08-01", "valor": 4.0},
    ])
    assert any(e.split(": ")[1] == "C12" for e in erros(s))


def test_aceita_periodo_aberto_e_dia_15():
    s = serie(granularidade="anual", dados=[{"data": "2026-12-15", "valor": 5.0}])
    assert erros(s) == []


def test_recusa_data_com_quebra_de_linha():
    s = serie(dados=[{"data": "2026-09-01\n", "valor": 5.0}])
    assert any(e.split(": ")[1] == "C9" for e in erros(s))


def test_recusa_dois_pontos_no_mesmo_dia_diaria():
    s = serie(granularidade="diaria", dados=[
        {"data": "2026-08-01", "valor": 5.0},
        {"data": "2026-08-01", "valor": 6.0},
    ])
    assert any(e.split(": ")[1] == "C11" for e in erros(s))


def test_casos_validos_do_corpus_passam():
    arquivos = sorted((CONTRATO / "validos").glob("*.json"))
    assert arquivos, "corpus vazio"
    for caminho in arquivos:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
        assert validar_serie(bruto, caminho) == [], caminho.name


def test_casos_invalidos_do_corpus_falham_com_o_codigo_do_nome():
    arquivos = sorted((CONTRATO / "invalidos").glob("*.json"))
    assert arquivos, "corpus vazio"
    for caminho in arquivos:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
        codigo = caminho.stem.split("-")[0]
        encontrados = [e.split(": ")[1] for e in validar_serie(bruto, caminho, checar_nome=False)]
        assert codigo in encontrados, f"{caminho.name}: esperava {codigo}, veio {encontrados}"
