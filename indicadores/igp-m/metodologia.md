# Metodologia — IGP-M

## igpm-acum-12m

- **Definição:** variação percentual do IGP-M acumulada nos últimos 12 meses — taxa efetiva do
  período. `percentual` (`%`, 2 casas), `eixo: percentual`, `medida: acumulado-12m`,
  granularidade `mensal`.
- **Fonte e código:** FGV, via SGS **28655** — variação mensal do IGP-M calculada sobre os
  números-índices da FGV, a mesma série que o BCB usa na Calculadora do Cidadão para correção
  pelo IGP-M. Endpoint:
  `https://api.bcb.gov.br/dados/serie/bcdata.sgs.28655/dados?formato=json`. A 0189 (variação
  mensal publicada, 2 casas) é buscada apenas para conferência.
- **Fórmula:** composição geométrica das 12 variações mensais da 28655,
  `(∏(1 + i/100) − 1) × 100`. O IGP-M não tem série pronta de acumulado em 12 meses no SGS —
  o catálogo de séries da FGV/BCB lista apenas a variação mensal, os decêndios e os
  componentes —, por isso o acumulado é calculado. A soma aritmética das taxas subestima o
  resultado porque não capitaliza.
- **Cobertura:** 1995-01 a 2026-10, **382 pontos**, sem lacuna. A fonte fecha janelas de 12
  meses desde 1990-05 (o IGP-M começa em jun/1989); o recorte em 1995-01 alinha a série ao
  IPCA e deixa fora a cauda de hiperinflação.
- **Conferência:** a 28655 coincide com a 0189 até a 2ª casa nos 449 meses da história (única
  diferença: jul/1989, 35,9051% contra 35,90%). A composição da 28655 reproduz os 14 valores
  da tabela de 12 meses publicada pela FGV de nov/2024 a dez/2025; a da 0189 reproduz 8. Em
  out/2026, a composição dá 5,2369% (arredonda para 5,24%), igual ao publicado pela FGV.
- **Verificação independente:** o Valor de 29/10/2026 publica 5,24% em 12 meses para out/2026
  (`https://valor.globo.com/brasil/noticia/2026/10/29/igp-m.ghtml`); a Gazeta Mercantil e o UOL
  repetem o valor, e a tabela mensal de 12 meses de 2026 do ToemCasa reproduz a série. A janela
  sobreposta também confere: out/2025 = 0,92% e set/2026 = 3,34%. Todas as publicações citam a
  FGV, portanto **não há segunda medição**. Busca feita em 05/11/2026.
- **Limitações:** o IGP-M é índice de atacado e de reajuste contratual, não custo de vida; o
  acumulado de 12 meses não é a inflação do ano-calendário. De 1995-01 a 1995-07 o acumulado
  embute jul/ago-1994 na conversão URV da ADPF 77, com 4,33% e 3,94% na 28655, e não a variação
  histórica da FGV (40,00% e 7,56%); por isso 1995-01 dá 603,74% aqui e 877,21% na série da
  FGV. De 1995-08 em diante a diferença máxima é 0,03 p.p. A tabela da FGV é do próprio
  produtor, não uma segunda medição.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
