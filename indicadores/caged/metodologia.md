# Metodologia — Caged

## caged-total-mensal

- **Definição:** número de vínculos formais ativos no último dia do mês de competência
  (celetistas; inclui aprendizes, intermitentes e temporários; exclui estatutários). É
  **estoque**, não fluxo. `numero` (`vínculos`, 0 casas), `eixo: contagem`, `medida: estoque`,
  `mensal`.
- **Fonte e código:** MTE (Caged / Novo Caged), via SGS **28763** (“Estoque de empregos formais —
  Total”, unidade “Unidades”), com `urlFonte` no endpoint do SGS. Descartadas: microdados FTP do
  MTE (indisponível/403), página mensal do MTE (só o mês corrente), SGS 28526 (índice, inativa
  desde 2019-12), IBGE (não produz Caged) e IPEA (espelho).
- **Fórmula:** nenhuma. A série oficial de estoque é buscada, recortada nos meses fechados e
  formatada. O saldo mensal não é calculado nem publicado: o número é o nível de vínculos.
- **Cobertura:** 1995-01 a 2026-08, **380 pontos**, sem lacuna. A fonte começa em 1992; o recorte
  em 1995-01 é mantido porque o gráfico só exibe a partir de 1995.
- **Conferência:** o nível anda entre 19,6 e 48,2 milhões; o maior movimento mensal da série é
  −981.331 (2020-04, 2,6% do nível). Δestoque de ago/2026 = 165.827, exatamente o saldo oficial
  do mês (2.294.563 admissões − 2.128.736 desligamentos). Choques: 2008-12 −695.361; 2015-12
  −614.393; 2020-04 −981.331; 2020-02→06 −1,79 milhão. 2025-12 = 47.110.663 é o “estoque RAIS
  2025” usado como base pelo MTE.
- **Limitações:** é estoque de vínculos formais, não taxa de emprego; não cobre informalidade nem
  estatutários. A emenda Caged → Novo Caged (jan/2020) é invisível no nível (2019-12 =
  38.152.770 → 2020-01 = 38.267.044), mas o BCB registra “diferenças metodológicas relevantes”
  entre os trechos.
- **Revisão:** reexecutar o notebook não muda valor. Mudança de valor é revisão da fonte, e a
  revisão é registrada neste arquivo antes de publicar.
