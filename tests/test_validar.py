import json
from pathlib import Path

from scripts.validar import validar_catalogo, validar_serie

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


# Catálogo (K1…K8): o catálogo publicado e o disco descrevem o MESMO conjunto de séries.
# Uma raiz mínima tem uma série em disco e o catálogo que deveria descrevê-la; cada teste
# estraga uma peça e cobra o código da regra correspondente.


def montar_raiz(
    raiz: Path,
    *,
    catalogo_arquivo: str = "ipca/ipca-acum-12m.json",
    omitir_entrada: bool = False,
    catalogo_id: str = "ipca-acum-12m",
    catalogo_escala: str = "percentual",
    catalogo_grupo: object = "inflacao",
    catalogo_versao: int = 1,
    catalogo_nome: object = "IPCA (%)",
    catalogo_descricao: object = "Variação acumulada do IPCA em 12 meses",
    entradas_extras: list[dict] | None = None,
) -> None:
    pasta = raiz / "indicadores" / "ipca"
    pasta.mkdir(parents=True)
    (pasta / "ipca-acum-12m.json").write_text(json.dumps(serie()), encoding="utf-8")

    entrada = {
        "id": catalogo_id,
        "nome": catalogo_nome,
        "grupo": catalogo_grupo,
        "arquivo": catalogo_arquivo,
        "escala": catalogo_escala,
        "descricao": catalogo_descricao,
    }
    entradas = [] if omitir_entrada else [entrada]
    entradas.extend(entradas_extras or [])
    catalogo = {
        "versao": catalogo_versao,
        "indicadores": entradas,
        "grupos": {"inflacao": {"nome": "📈 Inflação"}},
    }
    (raiz / "indicadores" / "catalogo.json").write_text(
        json.dumps(catalogo, ensure_ascii=False), encoding="utf-8"
    )


def test_catalogo_ok(tmp_path):
    montar_raiz(tmp_path)
    assert validar_catalogo(tmp_path) == []


def test_catalogo_arquivo_inexistente(tmp_path):
    montar_raiz(tmp_path, catalogo_arquivo="selic/nao-existe.json")
    assert any(e.startswith("K1") for e in validar_catalogo(tmp_path))


def test_catalogo_serie_sem_entrada(tmp_path):
    montar_raiz(tmp_path, omitir_entrada=True)
    assert any(e.startswith("K2") for e in validar_catalogo(tmp_path))


def test_catalogo_id_divergente(tmp_path):
    montar_raiz(tmp_path, catalogo_id="outro-id")
    assert any(e.startswith("K3") for e in validar_catalogo(tmp_path))


def test_catalogo_escala_divergente(tmp_path):
    montar_raiz(tmp_path, catalogo_escala="moeda")
    assert any(e.startswith("K4") for e in validar_catalogo(tmp_path))


def test_catalogo_grupo_inexistente(tmp_path):
    montar_raiz(tmp_path, catalogo_grupo="nao-existe")
    assert any(e.startswith("K5") for e in validar_catalogo(tmp_path))


def test_catalogo_grupo_que_nao_e_string(tmp_path):
    # lista é unhashable: `grupo not in grupos` estoura TypeError se não houver checagem de tipo
    montar_raiz(tmp_path, catalogo_grupo=["inflacao"])
    assert any(e.startswith("K5") for e in validar_catalogo(tmp_path))


def test_catalogo_versao_desconhecida(tmp_path):
    montar_raiz(tmp_path, catalogo_versao=2)
    assert any(e.startswith("K6") for e in validar_catalogo(tmp_path))


def test_catalogo_arquivo_fora_do_formato(tmp_path):
    # `../ipca-acum-12m.json` tem duas partes para `Path(...).parts` e passava no validador —
    # passava no CI do `dados` e reprovava no `validateCatalog` do app. K1 cobre o formato.
    montar_raiz(tmp_path, catalogo_arquivo="../ipca-acum-12m.json")
    assert any(
        e.startswith("K1") and "não é <familia>/<id>.json" in e
        for e in validar_catalogo(tmp_path)
    )


def test_catalogo_nome_vazio(tmp_path):
    montar_raiz(tmp_path, catalogo_nome="")
    assert any(
        e.startswith("K7") and "nome" in e for e in validar_catalogo(tmp_path)
    )


def test_catalogo_descricao_ausente(tmp_path):
    montar_raiz(tmp_path, catalogo_descricao=None)
    assert any(
        e.startswith("K7") and "descricao" in e for e in validar_catalogo(tmp_path)
    )


def test_catalogo_id_repetido(tmp_path):
    montar_raiz(
        tmp_path,
        entradas_extras=[
            {
                "id": "ipca-acum-12m",
                "nome": "IPCA (duplicado)",
                "grupo": "inflacao",
                "arquivo": "ipca/outro.json",
                "escala": "percentual",
                "descricao": "duplicata",
            }
        ],
    )
    assert any(
        e.startswith("K8") and "'ipca-acum-12m' repetido" in e
        for e in validar_catalogo(tmp_path)
    )


def test_catalogo_arquivo_repetido(tmp_path):
    montar_raiz(
        tmp_path,
        entradas_extras=[
            {
                "id": "ipca-outro",
                "nome": "Outro",
                "grupo": "inflacao",
                "arquivo": "ipca/ipca-acum-12m.json",
                "escala": "percentual",
                "descricao": "duplicata",
            }
        ],
    )
    assert any(
        e.startswith("K8") and "'ipca/ipca-acum-12m.json' repetido" in e
        for e in validar_catalogo(tmp_path)
    )


def test_catalogo_ausente(tmp_path):
    pasta = tmp_path / "indicadores" / "ipca"
    pasta.mkdir(parents=True)
    (pasta / "ipca-acum-12m.json").write_text(json.dumps(serie()), encoding="utf-8")
    assert validar_catalogo(tmp_path) == ["K1: catalogo.json ausente"]


def test_catalogo_grupos_que_nao_e_objeto(tmp_path):
    montar_raiz(tmp_path)
    caminho = tmp_path / "indicadores" / "catalogo.json"
    catalogo = json.loads(caminho.read_text(encoding="utf-8"))
    catalogo["grupos"] = []
    caminho.write_text(json.dumps(catalogo), encoding="utf-8")
    erros = validar_catalogo(tmp_path)
    assert any(e.startswith("K5") and "grupos" in e for e in erros)


def test_catalogo_entrada_que_nao_e_objeto(tmp_path):
    montar_raiz(tmp_path)
    caminho = tmp_path / "indicadores" / "catalogo.json"
    catalogo = json.loads(caminho.read_text(encoding="utf-8"))
    catalogo["indicadores"].append("nao-e-objeto")
    caminho.write_text(json.dumps(catalogo), encoding="utf-8")
    assert any(e.startswith("K3") and "não é um objeto" in e for e in validar_catalogo(tmp_path))


def test_catalogo_um_defeito_uma_mensagem(tmp_path):
    """Id divergente quebra dois elos (nome do arquivo e id da série) e reporta UM só."""
    montar_raiz(tmp_path, catalogo_id="outro-id")
    erros = validar_catalogo(tmp_path)
    assert len(erros) == 1, erros
    assert erros[0].startswith("K3")
