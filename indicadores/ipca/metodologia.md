# Metodologia — IPCA

A série grava 2 casas, a mesma precisão da SGS 13522; `unidade.casas` é só exibição.

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
- **Verificação independente:** a Agência Brasil de 09/10/2026
  (`https://agenciabrasil.ebc.com.br/economia/noticia/2026-10/inflacao-oficial-de-setembro-fica-em-082-mostra-ibge`)
  registra 4,58% em 12 meses em setembro/2026 e 4,22% em agosto/2026, exatamente os dois
  últimos pontos; o G1 de 09/10/2026 repete 4,58%
  (`https://g1.globo.com/economia/noticia/2026/10/09/ipca-setembro.ghtml`). As duas citam o
  IBGE; **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** é o acumulado de 12 meses, não a variação do mês nem a inflação do
  ano-calendário; o mês em curso fica de fora.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** Dados abertos do IBGE, lidos na SGS/BCB; atribuição ao IBGE e ao Banco Central do Brasil. Uso sujeito aos termos de uso do IBGE.
