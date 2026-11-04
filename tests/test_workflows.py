"""Guardas do agendamento: toda família precisa de caller, e todo caller precisa de família.

O `atualizar-familia.yml` roda `indicadores/<familia>/*.ipynb` e publica
`indicadores/<familia>/*.json`. Se faltar o caller ou a linha na allowlist, a família
existe no disco mas nunca atualiza — e nada no CI reclamaria. Este teste fecha essa
lacuna sem rede e sem dependência nova (o grupo `ci` instala só pytest).
"""

from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
FAMILIAS = RAIZ / "indicadores"
WORKFLOWS = RAIZ / ".github" / "workflows"


def pastas_de_familia(raiz_indicadores=FAMILIAS):
    """Famílias são as pastas de `indicadores/` que publicam ao menos uma série."""
    return sorted(
        pasta.name
        for pasta in raiz_indicadores.iterdir()
        if pasta.is_dir() and any(pasta.glob("*.json"))
    )


def caminho_do_caller(familia, workflows=WORKFLOWS):
    return workflows / f"atualizar-{familia}.yml"


def familia_do_caller(caminho):
    texto = caminho.read_text(encoding="utf-8")
    achado = re.search(r"^\s*familia:\s*([a-z0-9-]+)\s*$", texto, re.MULTILINE)
    assert achado, f"{caminho.name}: sem `familia:` no bloco `with`"
    return achado.group(1)


def allowlist(workflows=WORKFLOWS):
    texto = (workflows / "atualizar-familia.yml").read_text(encoding="utf-8")
    achado = re.search(
        r'case\s+"\$FAMILIA"\s+in\s*\n\s*([a-z0-9|-]+)\)', texto
    )
    assert achado, 'atualizar-familia.yml: bloco `case "$FAMILIA" in` não encontrado'
    return set(achado.group(1).split("|"))


def problemas_da_familia(
    familia, permitidas, raiz_indicadores=FAMILIAS, workflows=WORKFLOWS
):
    caminho = caminho_do_caller(familia, workflows)
    if not caminho.exists():
        return [f"{familia}: falta {caminho.name}"]

    problemas = []
    try:
        declarada = familia_do_caller(caminho)
    except AssertionError as erro:
        problemas.append(str(erro))
    else:
        if declarada != familia:
            problemas.append(f"{familia}: {caminho.name} aponta para `{declarada}`")
    if familia not in permitidas:
        problemas.append(f"{familia}: fora da allowlist de atualizar-familia.yml")
    if not any((raiz_indicadores / familia).glob("*.ipynb")):
        problemas.append(f"{familia}: pasta sem notebook")

    texto = caminho.read_text(encoding="utf-8")
    if not re.search(r"^\s*-\s*cron:\s*'", texto, re.MULTILINE):
        problemas.append(f"{familia}: caller sem `schedule`/`cron`")
    if "uses: ./.github/workflows/atualizar-familia.yml" not in texto:
        problemas.append(f"{familia}: caller não usa o workflow reutilizável")
    return problemas


def test_toda_familia_tem_caller_na_allowlist_e_notebook():
    familias = pastas_de_familia()
    assert familias, "nenhuma família encontrada em indicadores/"
    permitidas = allowlist()

    problemas = []
    for familia in familias:
        problemas.extend(problemas_da_familia(familia, permitidas))

    assert not problemas, "agendamento incompleto:\n- " + "\n- ".join(problemas)


def test_todo_caller_aponta_para_familia_existente():
    permitidas = allowlist()
    problemas = []

    for caminho in sorted(WORKFLOWS.glob("atualizar-*.yml")):
        if caminho.name == "atualizar-familia.yml":
            continue
        familia = familia_do_caller(caminho)
        if not (FAMILIAS / familia).is_dir():
            problemas.append(f"{caminho.name}: família `{familia}` não existe no disco")
        elif familia not in permitidas:
            problemas.append(f"{caminho.name}: `{familia}` fora da allowlist")

    assert not problemas, "callers órfãos:\n- " + "\n- ".join(problemas)


def test_guarda_reprova_familia_sem_caller(tmp_path):
    indicadores = tmp_path / "indicadores"
    workflows = tmp_path / "workflows"
    (indicadores / "pnad").mkdir(parents=True)
    (indicadores / "pnad" / "pnad-desocupacao.json").write_text("{}", encoding="utf-8")
    (indicadores / "pnad" / "PNAD.ipynb").write_text("{}", encoding="utf-8")
    workflows.mkdir()
    (workflows / "atualizar-familia.yml").write_text(
        'case "$FAMILIA" in\n  ipca|pnad) ;;\nesac\n', encoding="utf-8"
    )

    problemas = problemas_da_familia(
        "pnad", allowlist(workflows), indicadores, workflows
    )

    assert any("falta" in problema for problema in problemas), problemas


def test_guarda_aceita_familia_com_caller_completo(tmp_path):
    indicadores = tmp_path / "indicadores"
    workflows = tmp_path / "workflows"
    (indicadores / "pnad").mkdir(parents=True)
    (indicadores / "pnad" / "pnad-desocupacao.json").write_text("{}", encoding="utf-8")
    (indicadores / "pnad" / "PNAD.ipynb").write_text("{}", encoding="utf-8")
    workflows.mkdir()
    (workflows / "atualizar-familia.yml").write_text(
        'case "$FAMILIA" in\n  ipca|pnad) ;;\nesac\n', encoding="utf-8"
    )
    (workflows / "atualizar-pnad.yml").write_text(
        "on:\n"
        "  schedule:\n"
        "    - cron: '0 15 5,28 * *'\n"
        "jobs:\n"
        "  atualizar:\n"
        "    uses: ./.github/workflows/atualizar-familia.yml\n"
        "    with:\n"
        "      familia: pnad\n",
        encoding="utf-8",
    )

    problemas = problemas_da_familia(
        "pnad", allowlist(workflows), indicadores, workflows
    )

    assert problemas == [], problemas
