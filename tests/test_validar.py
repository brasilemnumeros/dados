import json
from pathlib import Path

from scripts.validar import validar_serie

CAMINHO = Path("indicadores/ipca/ipca-acum-12m.json")
CONTRATO = Path(__file__).parent / "contrato"


def serie(**over):
    base = {
        "schema": 1,
        "id": "ipca-acum-12m",
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "eixo": "percentual",
        "medida": "acumulado-12m",
        "granularity": "monthly",
        "source": "IBGE",
        "data": [{"date": "2026-09-01", "value": 5.0}],
    }
    base.update(over)
    return base


def erros(s):
    return validar_serie(s, CAMINHO)


def test_serie_valida():
    assert erros(serie()) == []


def test_recusa_rate_no_ponto():
    s = serie(data=[{"date": "2026-09-01", "rate": 5.0, "value": 5.0}])
    assert any(e.split(": ")[1] == "C8.1" for e in erros(s))


def test_recusa_ponto_sem_value():
    s = serie(data=[{"date": "2026-09-01"}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_schema_desconhecido():
    assert any(e.split(": ")[1] == "C1" for e in erros(serie(schema=2)))


def test_recusa_id_divergente():
    assert any(e.split(": ")[1] == "C2" for e in erros(serie(id="outro")))


def test_recusa_tipo_de_unidade():
    s = serie(unit={"type": "peso", "symbol": "kg", "decimals": 1})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_recusa_simbolo_vazio():
    s = serie(unit={"type": "number", "symbol": "", "decimals": 0})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_recusa_decimals_fracionario():
    s = serie(unit={"type": "percentage", "symbol": "%", "decimals": 2.5})
    assert any(e.split(": ")[1] == "C3" for e in erros(s))


def test_aceita_decimals_float_integral():
    s = serie(unit={"type": "percentage", "symbol": "%", "decimals": 2.0})
    assert erros(s) == []


def test_recusa_locale_fora_do_padrao():
    s = serie(unit={"type": "currency", "symbol": "R$", "decimals": 0, "locale": "portugues"},
              eixo="reais", medida="nivel")
    assert any(e.split(": ")[1] == "C3.1" for e in erros(s))


def test_recusa_eixo_incompativel_com_unidade():
    assert any(e.split(": ")[1] == "C4" for e in erros(serie(eixo="reais")))


def test_recusa_medida_desconhecida():
    assert any(e.split(": ")[1] == "C5" for e in erros(serie(medida="media-movel")))


def test_recusa_granularidade():
    assert any(e.split(": ")[1] == "C6" for e in erros(serie(granularity="semanal")))


def test_recusa_source_vazio():
    assert any(e.split(": ")[1] == "C7" for e in erros(serie(source="")))


def test_recusa_source_url_invalida():
    assert any(e.split(": ")[1] == "C7.1" for e in erros(serie(sourceUrl="ftp://x")))


def test_recusa_data_vazia():
    assert any(e.split(": ")[1] == "C8" for e in erros(serie(data=[])))


def test_recusa_data_fora_do_calendario():
    s = serie(data=[{"date": "2026-02-31", "value": 1.0}])
    assert any(e.split(": ")[1] == "C9" for e in erros(s))


def test_recusa_valor_nao_finito():
    s = serie(data=[{"date": "2026-09-01", "value": float("nan")}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_valor_inteiro_gigante():
    s = serie(data=[{"date": "2026-09-01", "value": 10**400}])
    assert any(e.split(": ")[1] == "C10" for e in erros(s))


def test_recusa_mes_repetido():
    s = serie(data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-31", "value": 6.0},
    ])
    assert any(e.split(": ")[1] == "C11" for e in erros(s))


def test_recusa_fora_de_ordem():
    s = serie(data=[
        {"date": "2026-09-01", "value": 5.0},
        {"date": "2026-08-01", "value": 4.0},
    ])
    assert any(e.split(": ")[1] == "C12" for e in erros(s))


def test_aceita_periodo_aberto_e_dia_15():
    s = serie(granularity="annual", data=[{"date": "2026-12-15", "value": 5.0}])
    assert erros(s) == []


def test_recusa_data_com_quebra_de_linha():
    s = serie(data=[{"date": "2026-09-01\n", "value": 5.0}])
    assert any(e.split(": ")[1] == "C9" for e in erros(s))


def test_recusa_dois_pontos_no_mesmo_dia_daily():
    s = serie(granularity="daily", data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-01", "value": 6.0},
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
