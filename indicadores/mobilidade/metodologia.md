# Metodologia — Mobilidade

## mortes-transito-anual

- **Definição:** óbitos por acidentes de transporte (CID-10 V01–V99) por 100 mil habitantes, por
  local de residência, no ano-calendário. Inclui todos os modos — pedestre, ciclista,
  motocicleta, automóvel, caminhão, ônibus, aquaviário e aéreo — em vias urbanas e rodovias.
  `numero` (`por 100 mil`, 2 casas), `eixo: por-100-mil`, `medida: nivel`, granularidade `anual`
  (C15: `AAAA-01-01`).
- **Fonte e código:** MS/SIM/Datasus, microdados de causas externas `DOEXT{AA}.dbc` em
  `dissemin/publicos/SIM/CID10/DOFET/` (dados finais, um por ano). O notebook baixa o `.dbc`
  inteiro, descomprime com `pyreaddbc` (PKWare DCL) e conta os registros com `CAUSABAS` em
  V01–V99; códigos de três caracteres entram. Y10–Y34 (intenção indeterminada) e Y85+ (sequelas)
  ficam de fora. Os registros marcados como apagados não são contados.
- **Denominador:** população residente, série IPEADATA `AVIOL12_VIOLPOP` — a mesma de
  `homicidios`, para que as taxas sejam comparáveis. 2022 e 2023 são interpolação exponencial
  entre 2021 e 2024, conforme a metadata da série; é a limitação conhecida do denominador.
- **Fórmula:** `taxa = 100.000 × óbitos V01–V99 ÷ população`, por ano. Sem média móvel e sem
  taxa herdada.
- **Cobertura:** 1996–2025, **30 pontos**. O notebook exclui o ano corrente e exige os 12 meses
  do último ano antes de publicar. Primeiro ponto 22,63 (1996: 35.545 ÷ 157.070.163); último
  17,78 (2025: 37.954 ÷ 213.415.160).
- **`urlFonte` ausente:** o recorte é um caminho `ftp://`, que C7.1 não aceita; o portal de
  transferência do Datasus não é o recorte. O caminho exato está acima e no markdown do
  notebook.
- **O que não é:** número de sinistros (um sinistro pode ter várias vítimas), de feridos, de
  multas ou de veículos; não é o recorte de rodovias federais da PRF.
- **V01–V99 não é V01–V89.** A série publicada inclui aquaviário (V90–V94), aéreo (V95–V97) e os
  residuais V98–V99 — 1.103 óbitos a mais que o V01–V89 em 2024 (2,9%). Por isso a taxa de 2024 é
  17,99, e não 17,48 (o V01–V89 com a mesma população). As publicações de terceiro usam V01–V89;
  a comparação de nível só é justa no mesmo recorte, e o notebook imprime a conferência nos dois.
- **Limitações:** a série usa CID-10 desde 1996, sem emenda com a CID-9; 1996–1997 têm contagem
  mais alta (35,5 mil) e ela cai para ~30 mil em 1998–2000, e 2010 tem salto de +14% sobre 2009 —
  mudanças de cobertura/codificação do SIM que não são corrigidas aqui.
- **Verificação independente:** as contagens de transporte terrestre (V01–V89) reproduzem as do
  ONSV — *Dados Consolidados de Óbitos no Trânsito Brasileiro – 2024*, divulgado em 14/01/2026 e
  analisado em 31/07/2026 (`https://onsv.github.io/analise-datasus-2024/datasus2024.html`) — em
  2019–2024: 31.945, 32.716, 33.813, 33.894, 34.881 e 37.150, **exatas**. A taxa de 2023 do Atlas
  da Violência (G1, 12/05/2025) é 16,2; o mesmo recorte aqui dá 16,41, porque o denominador do
  Atlas é outro (215,3 milhões implícitos contra 212,57 milhões da VIOLPOP). A OMS estima 16 por
  100 mil em 2021 (aqui: 16,42 em V01–V99; 15,85 em V01–V89). Nenhuma é segunda medição: todas
  usam o SIM/Datasus.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
