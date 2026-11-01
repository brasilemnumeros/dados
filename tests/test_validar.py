from pathlib import Path

from scripts.validar import validar_serie

CAMINHO = Path("indicadores/ipca/ipca-acum-12m.json")


def serie(**over):
    base = {
        "schema": 1,
        "id": "ipca-acum-12m",
        "unit": {"type": "percentage", "symbol": "%", "decimals": 2},
        "granularity": "monthly",
        "source": "IBGE",
        "data": [{"date": "2026-09-30", "value": 5.0}],
    }
    base.update(over)
    return base


def test_serie_valida():
    assert validar_serie(serie(), CAMINHO) == []


def test_aceita_rate_extra():
    s = serie(data=[{"date": "2026-09-30", "rate": 5.0, "value": 5.0}])
    assert validar_serie(s, CAMINHO) == []


def test_recusa_ponto_sem_value():
    s = serie(data=[{"date": "2026-09-30", "rate": 5.0}])
    assert any("value" in e for e in validar_serie(s, CAMINHO))


def test_recusa_schema_desconhecido():
    assert any("schema" in e for e in validar_serie(serie(schema=2), CAMINHO))


def test_recusa_id_divergente():
    assert any("id" in e for e in validar_serie(serie(id="outro"), CAMINHO))


def test_recusa_tipo_de_unidade():
    s = serie(unit={"type": "peso", "symbol": "kg", "decimals": 1})
    assert any("unit.type" in e for e in validar_serie(s, CAMINHO))


def test_recusa_simbolo_vazio():
    s = serie(unit={"type": "number", "symbol": "", "decimals": 0})
    assert any("symbol" in e for e in validar_serie(s, CAMINHO))


def test_recusa_decimals_invalido():
    s = serie(unit={"type": "number", "symbol": "x", "decimals": -1})
    assert any("decimals" in e for e in validar_serie(s, CAMINHO))


def test_recusa_granularidade():
    assert any("granularity" in e for e in validar_serie(serie(granularity="semanal"), CAMINHO))


def test_recusa_source_vazio():
    assert any("source" in e for e in validar_serie(serie(source=""), CAMINHO))


def test_recusa_data_fora_do_formato():
    s = serie(data=[{"date": "31/03/1999", "value": 1.0}])
    assert any("YYYY-MM-DD" in e for e in validar_serie(s, CAMINHO))


def test_recusa_valor_nao_finito():
    s = serie(data=[{"date": "2026-09-30", "value": float("nan")}])
    assert any("finito" in e for e in validar_serie(s, CAMINHO))


def test_recusa_mes_repetido():
    s = serie(data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-31", "value": 6.0},
    ])
    assert any("repetido" in e for e in validar_serie(s, CAMINHO))


def test_aceita_data_fora_do_dia_01():
    s = serie(data=[{"date": "1999-03-31", "value": 44.22}])
    assert validar_serie(s, CAMINHO) == []


def test_aceita_fora_de_ordem():
    s = serie(data=[
        {"date": "2026-09-01", "value": 5.0},
        {"date": "2026-08-01", "value": 4.0},
    ])
    assert validar_serie(s, CAMINHO) == []


def test_aceita_periodo_aberto():
    s = serie(data=[{"date": "2026-11-01", "value": 5.0}])
    assert validar_serie(s, CAMINHO) == []


def test_recusa_data_com_quebra_de_linha():
    s = serie(data=[{"date": "2026-09-30\n", "value": 5.0}])
    assert any("YYYY-MM-DD" in e for e in validar_serie(s, CAMINHO))


def test_recusa_dias_diferentes_no_mesmo_mes_daily():
    s = serie(granularity="daily", data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-31", "value": 6.0},
    ])
    assert any("repetido" in e for e in validar_serie(s, CAMINHO))


def test_recusa_data_repetida_daily():
    s = serie(granularity="daily", data=[
        {"date": "2026-08-01", "value": 5.0},
        {"date": "2026-08-01", "value": 6.0},
    ])
    assert any("repetido" in e for e in validar_serie(s, CAMINHO))


def test_aceita_decimals_float_integral():
    s = serie(unit={"type": "percentage", "symbol": "%", "decimals": 2.0})
    assert validar_serie(s, CAMINHO) == []


def test_recusa_decimals_fracionario():
    s = serie(unit={"type": "percentage", "symbol": "%", "decimals": 2.5})
    assert any("decimals" in e for e in validar_serie(s, CAMINHO))


def test_recusa_valor_inteiro_gigante():
    s = serie(data=[{"date": "2026-09-30", "value": 10**400}])
    assert any("finito" in e for e in validar_serie(s, CAMINHO))
