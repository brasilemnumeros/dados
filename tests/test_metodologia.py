"""Guarda da metodologia: uma por família, uma seção por série, sem histórico.

A metodologia mora em `indicadores/<familia>/metodologia.md`, ao lado do notebook e das
séries, e acompanha o PR da família. Este teste garante que ela existe, cobre exatamente as
séries publicadas na pasta e continua descrevendo a regra em vigor — não a linha do tempo
de versões anteriores.
"""

from pathlib import Path
import re

RAIZ = Path(__file__).resolve().parents[1]
FAMILIAS = RAIZ / "indicadores"

ROTULOS = ("**Definição:**", "**Fonte e código:**", "**Fórmula:**", "**Cobertura:**")

# Rótulos e frases que só fazem sentido num relatório de revisão, não na metodologia vigente.
HISTORICOS = (
    "Fórmula atual",
    "Fórmula proposta",
    "Veredito",
    "Impacto esperado",
    "Decisão pendente",
    "versão anterior",
    "antes era",
)


def familias_com_series(raiz_indicadores=FAMILIAS):
    """Famílias são as pastas de `indicadores/` que publicam ao menos uma série."""
    return sorted(
        pasta
        for pasta in raiz_indicadores.iterdir()
        if pasta.is_dir() and any(pasta.glob("*.json"))
    )


def secoes(texto):
    """Mapa `id` → corpo da seção `## <id>` (o cabeçalho de nível 1 fica de fora)."""
    partes = re.split(r"^## ", texto, flags=re.MULTILINE)[1:]
    achadas = {}
    for parte in partes:
        linhas = parte.splitlines()
        if not linhas:
            continue
        achadas[linhas[0].strip()] = "\n".join(linhas[1:])
    return achadas


def problemas_da_familia(pasta):
    problemas = []
    arquivo = pasta / "metodologia.md"
    if not arquivo.exists():
        return [f"{pasta.name}: falta metodologia.md"]

    ids = sorted(caminho.stem for caminho in pasta.glob("*.json"))
    texto = arquivo.read_text(encoding="utf-8")
    achadas = secoes(texto)

    for serie in ids:
        if serie not in achadas:
            problemas.append(f"{pasta.name}: série `{serie}` sem seção `## {serie}`")
            continue
        for rotulo in ROTULOS:
            if rotulo not in achadas[serie]:
                problemas.append(
                    f"{pasta.name}: seção `{serie}` sem o rótulo {rotulo}"
                )

    for secao in sorted(set(achadas) - set(ids)):
        problemas.append(f"{pasta.name}: seção `{secao}` não corresponde a uma série da pasta")

    for marcador in HISTORICOS:
        if marcador in texto:
            problemas.append(
                f"{pasta.name}: texto histórico ({marcador!r}); descreva só a regra em vigor"
            )

    return problemas


def test_toda_familia_tem_metodologia_completa_e_atual():
    familias = familias_com_series()
    assert familias, "nenhuma família encontrada em indicadores/"

    problemas = []
    for pasta in familias:
        problemas.extend(problemas_da_familia(pasta))

    assert not problemas, "metodologia incompleta:\n- " + "\n- ".join(problemas)


def test_guarda_reprova_serie_sem_secao(tmp_path):
    familia = tmp_path / "ipca"
    familia.mkdir()
    (familia / "ipca-acum-12m.json").write_text("{}", encoding="utf-8")
    (familia / "metodologia.md").write_text(
        "# Metodologia — IPCA\n\n"
        "## outro-id\n\n"
        "- **Definição:** x\n"
        "- **Fonte e código:** x\n"
        "- **Fórmula:** x\n"
        "- **Cobertura:** x\n",
        encoding="utf-8",
    )

    problemas = problemas_da_familia(familia)

    assert any("sem seção `## ipca-acum-12m`" in problema for problema in problemas), problemas
    assert any("não corresponde" in problema for problema in problemas), problemas


def test_guarda_reprova_rotulo_historico(tmp_path):
    familia = tmp_path / "ipca"
    familia.mkdir()
    (familia / "ipca-acum-12m.json").write_text("{}", encoding="utf-8")
    (familia / "metodologia.md").write_text(
        "# Metodologia — IPCA\n\n"
        "## ipca-acum-12m\n\n"
        "- **Definição:** x\n"
        "- **Fonte e código:** x\n"
        "- **Fórmula:** x\n"
        "- **Cobertura:** x\n"
        "- **Fórmula atual:** soma das taxas\n",
        encoding="utf-8",
    )

    problemas = problemas_da_familia(familia)

    assert any("texto histórico" in problema for problema in problemas), problemas
