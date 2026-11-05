# Metodologia — IPCA

## ipca-acum-12m

- **Definição:** variação percentual do IPCA acumulada nos últimos 12 meses — taxa efetiva do
  período. `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: acumulado-12m`,
  granularidade `mensal`.
- **Fonte e código:** IBGE, via API de Dados Abertos do Banco Central (SGS), série **13522**
  (“IPCA — variação acumulada em 12 meses”, %). Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados?formato=json`.
- **Fórmula:** nenhuma. A série é publicada tal como o BCB/IBGE a divulga; o notebook busca,
  mantém apenas os meses fechados e formata. A série 433 (variação mensal) não gera a saída:
  somar as 12 taxas mensais não reproduz o acumulado oficial, porque a soma aritmética ignora
  a capitalização — em jun/2025 a soma dá 5,23% e a 13522 registra 5,35%.
- **Cobertura:** 1995-01 a 2026-09, **381 pontos**, sem lacuna. A 13522 tem valores anteriores
  a 1995; o recorte em 1995-01 alinha a série à janela das demais séries de preços.
- **Conferência:** em inflação alta a diferença entre somar e capitalizar cresce: dez/2002,
  11,90% (soma das mensais) contra 12,53% (13522); fev/2003, 14,84% contra 15,85%.
- **Limitações:** é o acumulado de 12 meses, não a variação do mês nem a inflação do
  ano-calendário; o mês em curso fica de fora.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
