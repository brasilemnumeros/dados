# Metodologia — Meio Ambiente

## desmatamento-amazonia-legal-anual

- **Definição:** área de vegetação nativa suprimida por corte raso na Amazônia Legal, no ano
  Prodes (1º de agosto a 31 de julho), em km². `numero` (`km²`, 0 casas), `eixo: contagem`,
  `medida: nivel`, granularidade `anual` (C15: `AAAA-01-01`). É fluxo anual, não estoque
  acumulado.
- **Fonte e código:** INPE — PRODES/BiomasBR, via TerraBrasilis:
  `https://terrabrasilis.dpi.inpe.br/app/dashboard/deforestation/biomes/legal_amazon/rates`.
  O notebook baixa o arquivo `rates<ano>.json` vigente (nome resolvido no bundle `app.*.js`;
  fallback para `rates<ano civil>.json` e `rates<ano civil − 1>.json`), soma
  `features[].areas[].area` dos 9 estados de cada período e rotula o ponto pelo `endDate.year`
  do ano Prodes, com data C15 `AAAA-01-01`. O valor é a soma dos 9 estados calculada pelo site;
  não há recálculo de área.
- **Fórmula:** soma das áreas de todos os `features` do período; o ponto é o `endDate.year`.
  Nenhum ajuste, interpolação ou preenchimento.
- **Cobertura:** 1988–2025, **38 pontos**, sem lacuna. O ano do arquivo é descartado porque o
  mesmo arquivo mistura a estimativa do ano do arquivo com as taxas consolidadas, sem marcador;
  por isso o período 2025-08-01–2026-07-31 (3.335 km², estimativa) fica fora. A taxa consolidada
  substitui a estimativa no primeiro semestre seguinte; o workflow roda em **outubro**, depois da
  consolidação, e o notebook corta em ano do arquivo − 1.
- **Conferência:** 1988 = 21.050 km²; 1995 = 29.059 km² (máximo); 2004 = 27.772 km² (pico da
  década de 2000, não da série); 2012 = 4.571 km² (mínimo); 2024 = 6.518 km²; 2025 = 5.731 km²,
  queda de 12,07% sobre 2024. 1993 e 1994 são ambos 14.896 km² na fonte; não é duplicata.
- **Verificação independente:** a Agência Brasil (16/10/2026,
  `https://agenciabrasil.ebc.com.br/meio-ambiente/noticia/2026-10/desmatamento-caiu-418-na-amazonia-e-238-no-cerrado-em-um-ano`)
  noticia 5.731 km² em 2025 e 3.335 km² em 2026 (queda de 41,8%); a Geocracia (25/08/2026) e o
  PNB Online (18/08/2026) noticiam 5.731 km² em 2025 e −12,07% sobre 6.518 km². Os níveis e a
  variação de 2025 batem com a série. Não há segunda medição: o MapBiomas Alerta usa outro
  método e o próprio relatório declara incomparabilidade.
- **Limitações:** a série nacional de desmatamento não existe: os biomas têm inícios e métodos
  diferentes (Amazônia em 1988, Cerrado em 2001, três biomas só em 2024). Por isso o recorte é a
  Amazônia Legal, não “Brasil”. O número não é ano-calendário, não é o DETER (alertas mensais) e
  não é queimada. A partir de 2024 o PRODES usa radar e observa 100% dos tiles; a comparação com
  os anos anteriores a 2024 não isolam política de mudança de método. A imprensa às vezes troca a
  estimativa (5.796 km² em 2025) pela consolidada (5.731 km²); são produtos diferentes.
- **Licença e atribuição:** dados do TerraBrasilis/INPE sob **CC BY-SA 4.0**; atribuição ao
  INPE/TerraBrasilis na `fonte` da série e nesta metodologia.
- **Revisão:** a fonte reescreve a série inteira, sem changelog; reexecutar o notebook segue a
  revisão. Mudança de valor é revisão da fonte, e a revisão é registrada neste arquivo antes de
  publicar.
