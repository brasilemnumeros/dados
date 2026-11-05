# Saneamento dos indicadores anteriores ao Gate de revisão — plano

> **For agentic workers:** plano de execução inline. Cada tarefa termina com `validar.py` +
> `pytest` verdes e diff revisado. As correções vêm dos relatórios em
> `.superpowers/sdd/2026-11-05-revisao-indicadores-antigos/<id>/review.md`.

**Goal:** corrigir os achados `Critical`/`Important` das 19 séries publicadas antes do Gate de
revisão independente, sem mudar valores além da extensão aprovada do PIB per capita nominal.

**Architecture:** um PR só, em blocos por família. Catálogo e arquivos compartilhados pelo
controlador; cada família mexe apenas no seu notebook, JSON e `metodologia.md`.

**Tech Stack:** Python 3.12, Jupyter/Colab, pandas/requests, uv, pytest.

## Global Constraints

- Contrato `C1…C15` e catálogo `K1…K9`; `validar.py` + `pytest` verdes em cada tarefa.
- C15: mensal `AAAA-MM-01`, anual `AAAA-01-01`, diária com a data real.
- Nenhum valor publicado muda, exceto `pib-per-capita-nominal`/`pib-per-capita-real` para
  2024–2025 (aval do usuário em 05/11/2026).
- Notebook público: selo do Colab, `relativo()` em todo print, nenhum caminho absoluto.
- Metodologia no presente do indicativo; história da fonte fica, história da nossa metodologia sai.
- Commits em português, Conventional Commits, escopo `dados`.

## Review Focus

- **Verificação independente ausente:** toda seção precisa do parágrafo com nome, data, valores e
  URL, ou a busca documentada; release do produtor não conta.
- **Notebook não reprodutível:** saída commitada editada à mão enquanto o código imprime caminho
  absoluto; reexecutar deve regravar a saída.
- **Validação que expira:** asserts com ano/vintage fixos que derrubam o workflow agendado.
- **`urlFonte` morto:** link publicado precisa abrir e permitir auditar o número.
- **Descrição enganosa:** denominador, total × per capita, índice × inflação ao consumidor.

---

### Task 1: Catálogo

**Files:**
- Modify: `indicadores/catalogo.json`

- [ ] `igpm-acum-12m`: descrição com o caveat “índice de atacado/reajuste, não é o IPCA”.
- [ ] `pib-real-anual`: “PIB total (não per capita)”.
- [ ] `pib-per-capita-nominal`: remover “de 1996 a 2023”; dizer que é o número oficial.
- [ ] `pib-per-capita-real`: remover “cobertura para em 2023” se a série for estendida.
- [ ] `pnad-desocupacao`: “pessoas de 14 anos ou mais **na força de trabalho**”.
- [ ] Rodar `python3 scripts/validar.py`.

### Task 2: CAGED

**Files:** `indicadores/caged/metodologia.md`, `indicadores/caged/CAGED.ipynb`

- [ ] Metodologia: trocar o Δ de ago/2026 pela identidade “variação = saldo líquido da mesma
  vintage”; acrescentar `Verificação independente` com CNA Brasil 01/10/2026 e Diário do
  Comércio/Estadão 29/09/2026 (valores e URLs do review).
- [ ] Notebook: `print(... relativo(ARQUIVO))`; trocar o par congelado de estoque/saldo por
  checagem tolerante a revisão; reexecutar em ensaio e conferir JSON byte a byte.

### Task 3: Homicídios

**Files:** `indicadores/homicidios/metodologia.md`, `indicadores/homicidios/Homicidios.ipynb`

- [ ] Metodologia: corrigir a Conferência de `homicidios-anual` (2012 = 28,86; 2020 = 23,84) e a
  prosa da célula 2 do notebook; acrescentar `Verificação independente` nas três seções com o G1
  de 26/05/2026 (42.590; 29.870; 70,1%; 20,1/100 mil).
- [ ] Notebook: `print(... relativo(arquivo))`; reexecutar e conferir os três JSONs.

### Task 4: IGP-M

**Files:** `indicadores/igp-m/metodologia.md`, `indicadores/igp-m/IGP-M.ipynb`

- [ ] `Verificação independente`: Valor 29/10/2026 (5,24%), UOL/Gazeta, janela out/2025 (0,92%) e
  set/2026 (3,34%); declarar que todos citam a FGV.
- [ ] Limitações: jul/ago-1994 na conversão URV da ADPF 77 (4,33%/3,94%) contra a série da FGV
  (40,00%/7,56%); de 1995-08 em diante a diferença máxima é 0,03 p.p.

### Task 5: IPCA

**Files:** `indicadores/ipca/metodologia.md`, `indicadores/ipca/IPCA.ipynb`

- [ ] `Verificação independente`: Agência Brasil 09/10/2026 (4,58% em set/2026; 4,22% em ago/2026)
  e G1; declarar que citam o IBGE.
- [ ] Notebook: `DESTINO = Path(os.environ.get("IPCA_SAIDA", PASTA))`; `ARQUIVO` sob `DESTINO`.

### Task 6: MVG-R

**Files:** `indicadores/mvgr/metodologia.md`

- [ ] `mvgr-nominal`: `Verificação independente` com Poder360 01/06/2017 e UOL/Seconci-Rio
  29/10/2021; defasagem de ~90 dias.
- [ ] `mvgr-real`: `Verificação independente` com ABECIP 28/10/2021; defasagem de ~90 dias.

### Task 7: PIB

**Files:** `indicadores/pib/metodologia.md`, `indicadores/pib/PIB.ipynb`,
`indicadores/pib/*.json`, `pyproject.toml`, `uv.lock`

- [ ] `pib-real-anual`: `Verificação independente` com G1/Agência Brasil 03/03/2026 e Folha
  07/03/2025.
- [ ] Notebook: `BASE_PER_CAPITA = 2023` constante; encadear o real para frente com a variação
  oficial; trocar `assert datas[-1] == "2025-01-01"` por checagem estrutural; sem literais de
  vintage.
- [ ] `pib-per-capita-nominal`/`real`: estender a 2024–2025 com R$ 55.247,45 e R$ 59.687,49
  (Contas Nacionais Trimestrais, 4º tri), lendo o caderno do IBGE; `fonte` declara a emenda.
- [ ] Metodologia: corrigir “para 2024 e 2025 não há nível publicado”; documentar a emenda e a
  política de revisão; ano-base fixo em 2023.
- [ ] Se usar PDF: `pypdf` com versão exata em `pyproject.toml` + `uv lock`; no Colab, `%pip`.

### Task 8: PNAD

**Files:** `indicadores/pnad/metodologia.md`, `indicadores/pnad/PNAD.ipynb`

- [ ] `pnad-desocupacao`: URLs das publicações; defasagem ~1 mês; reponderação de 2025; corrigir
  o denominador.
- [ ] `pnad-nivel-ocupacao`: trocar “out–dez/2025” por “set–out–nov/2025”; acrescentar `Revisão`.
- [ ] `pnad-participacao`: corrigir a janela do Dadobruto (jun–ago/2026 = `2026-08`).
- [ ] `pnad-rendimento-real`: remover os asserts de nível absoluto; manter invariantes;
  documentar base móvel, reexpressão e defasagem.
- [ ] `Revisão` em todas as seções mensais.

### Task 9: População

**Files:** `indicadores/populacao/metodologia.md`, `indicadores/populacao/População.ipynb`

- [ ] `populacao-total-anual` e `populacao-variacao-anual`: `Verificação independente` com
  Agência Brasil 28/08/2026 (214,2 mi; +0,37%; +0,39% em 2024/2025) e InfoMoney.
- [ ] Metodologia: regra de corte (última estimativa do DOU/SIDRA 6579) e defasagem de agosto.
- [ ] Notebook: `print(... relativo(caminho))`; reexecutar e conferir os dois JSONs.

### Task 10: Selic

**Files:** `indicadores/selic/*.json`, `indicadores/selic/metodologia.md`,
`indicadores/selic/Selic.ipynb`

- [ ] `urlFonte` das duas séries para `https://www.bcb.gov.br/estatisticas/txjuros` (ou recorte
  com janela de 10 anos); manter o endpoint na metodologia.
- [ ] Notebook: atualizar `URL_OVER`/`ESPERADO` e o assert.
- [ ] `Verificação independente` nas duas seções: Agência Brasil 18/06/2025 (15,00%), 16/09/2026
  (13,75%), Poder360 18/03/2026 (14,75%); Brasil Indicadores 04/11/2026 para o over.

### Task 11: Gates e PR

- [ ] `python3 scripts/validar.py`
- [ ] `uv run --frozen --group ci pytest -q`
- [ ] Parse de todos os JSON; `git diff --check`.
- [ ] Revisão final independente do diff completo; corrigir Critical/Important.
- [ ] Commit e PR.
