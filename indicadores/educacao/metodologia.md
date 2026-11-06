# Metodologia — Educação

## ideb-anos-iniciais

- **Definição:** Índice de Desenvolvimento da Educação Básica (Ideb) do Brasil para os anos
  iniciais (1º ao 5º ano) do ensino fundamental regular, rede total (pública + privada). Escala
  de 0 a 10. `numero` (`índice`, 1 casa), `eixo: contagem`, `medida: nivel`, granularidade
  `bienal` (C15: `AAAA-01-01`).
- **Fórmula:** `Ideb = N × P`, em que `N` é a nota média padronizada do Saeb (Língua Portuguesa e
  Matemática) e `P` é o indicador de rendimento (taxa de aprovação do Censo Escolar). O índice é
  calculado pelo Inep; a série lê a coluna `VL_OBSERVADO_AAAA` da planilha oficial e **não
  recalcula** o valor.
- **Fonte e código:** Inep — planilha Brasil da edição vigente do Ideb
  (`https://download.inep.gov.br/ideb/resultados/divulgacao_brasil_ideb_AAAA.zip`, aba
  “Brasil (Anos Iniciais)”, linha `Brasil`/`Total`). O notebook descobre a edição vigente na
  página de resultados
  (`https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados`),
  confere o md5 do XLSX e falha se o link não estiver lá. `urlFonte` é essa página estável de
  resultados — nem a aba da edição nem o zip, cujos nomes mudam a cada ciclo.
- **Periodicidade e paridade.** O Saeb é bienal e o Ideb só existe nas edições ímpares; a série
  declara `bienal` e **todos os 11 pontos caem em anos ímpares** (2005, 2007, …, 2025). Não há
  ponto em ano par nem interpolação: se o Inep publicar um ano par, o notebook falha em vez de
  descartar o ano, porque mudar a periodicidade é decisão de contrato.
- **Cobertura:** 2005–2025, **11 pontos**. Primeiro 3,8 (2005); 2021 5,8 (queda sobre 5,9 em
  2019, efeito da pandemia); 2023 6,0; último 6,3 (2025, máximo da série). O Inep publicou nota
  informativa sobre o impacto da pandemia no Ideb de 2021 — a leitura 2019→2021 não é a de um
  biênio normal.
- **O que o número é — e o que não é.** É o Ideb observado da rede total do país nos anos
  iniciais. Não é percentual de aprendizado (é índice composto de proficiência e fluxo), não é
  nota de escola/município/estado (é o agregado nacional), não é anos finais nem ensino médio e
  não é a meta (`VL_PROJECAO_AAAA`), que é projeção pactuada, não valor observado.
- **TLS do Inep.** O servidor de downloads entrega só o certificado do site, sem o intermediário
  da cadeia (RNP ICPEdu), e o bundle de raízes do `requests` não o tem. O notebook tenta a
  conexão normal e, se ela falhar, baixa o intermediário público no endereço AIA do próprio
  certificado e refaz a sessão com raízes + intermediário. A verificação TLS continua ligada de
  ponta a ponta — o intermediário é validado contra a raiz GlobalSign na mesma conexão; o TLS
  nunca é desligado.
- **Verificação independente:** o Inep divulgou **6,3** em 05/08/2026
  (`https://www.gov.br/inep/pt-br/centrais-de-conteudo/noticias/ideb/ideb-avanca-em-todas-as-etapas-da-educacao-basica`);
  a CNN Brasil, o Valor Econômico, o Exame e O Globo (05–06/08/2026) publicaram o mesmo 6,3 para
  os anos iniciais, e a Agência Secom registra a rede pública em 6,1. A planilha é a fonte; as
  publicações são a conferência de que o número é o que o país leu. Não há segunda medição: todas
  citam o Inep.
- **Revisão:** os valores são os publicados pelo Inep; reexecutar o notebook só muda número se o
  Inep republicar a planilha. Nesse caso a revisão é registrada neste arquivo antes de publicar,
  e as âncoras de valor da validação são o alarme.

## ideb-anos-finais

- **Definição:** Índice de Desenvolvimento da Educação Básica (Ideb) do Brasil para os anos
  finais (6º ao 9º ano) do ensino fundamental regular, rede total (pública + privada). Escala de
  0 a 10. `numero` (`índice`, 1 casa), `eixo: contagem`, `medida: nivel`, granularidade `bienal`
  (C15: `AAAA-01-01`).
- **Fórmula:** `Ideb = N × P`, em que `N` é a nota média padronizada do Saeb (Língua Portuguesa e
  Matemática) e `P` é o indicador de rendimento (taxa de aprovação do Censo Escolar). O índice é
  calculado pelo Inep; a série lê a coluna `VL_OBSERVADO_AAAA` da planilha oficial e **não
  recalcula** o valor.
- **Fonte e código:** Inep — planilha Brasil da edição vigente do Ideb, aba “Brasil (Anos
  Finais)”, linha `Brasil`/`Total`. A página de resultados
  (`https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados`)
  é o `urlFonte`: o notebook descobre nela a edição vigente, baixa o zip em
  `https://download.inep.gov.br/ideb/resultados/divulgacao_brasil_ideb_AAAA.zip`, confere o md5
  do XLSX e falha se o link não estiver lá. Na edição de 2025, a linha de códigos
  `VL_OBSERVADO_AAAA` da aba **não traz o código de 2023**, embora a coluna “IDEB 2023 (N x P)”
  exista e tenha 5,0; por isso o notebook mapeia o ano pelo cabeçalho visível e usa o código,
  quando presente, só como conferência — ler pelos códigos perderia 2023 em silêncio.
- **Periodicidade e paridade.** O Saeb é bienal e o Ideb só existe nas edições ímpares; a série
  declara `bienal` e **todos os 11 pontos caem em anos ímpares** (2005, 2007, …, 2025). Não há
  ponto em ano par nem interpolação: se o Inep publicar um ano par, o notebook falha em vez de
  descartar o ano, porque mudar a periodicidade é decisão de contrato.
- **Cobertura:** 2005–2025, **11 pontos**. Primeiro 3,5 (2005); 2019 4,9; 2021 5,1; 2023 5,0;
  último 5,3 (2025, máximo da série). A diretriz de cobrir desde 1995 foi verificada: o Ideb foi
  criado em 2007 com a primeira edição em 2005 e não tem série comparável antes disso. Busca
  feita em 06/11/2026.
- **Conferência:** mínimo 3,5 (2005); máximo 5,3 (2025); 2025 é o maior valor da série. Em 2021 o
  Ideb subiu em relação a 2019 (4,9 → 5,1) porque a taxa de aprovação aumentou no período da
  pandemia, não porque a aprendizagem tenha melhorado — a leitura 2019→2021 não é a de um biênio
  normal.
- **Verificação independente:** a CNN Brasil de 05/08/2026
  (`https://www.cnnbrasil.com.br/educacao/ideb-ensino-basico-tem-recorde-fundamental-2-e-medio-nao-alcancam-meta/`)
  publica a passagem de **5,0 em 2023 para 5,3 em 2025** nos anos finais da rede total. O Inep
  divulgou os mesmos valores em 05/08/2026, mas é o produtor e não conta como publicação
  externa. Não há segunda medição: a publicação cita o Inep.
- **Limitações:** é um índice composto — a taxa de aprovação pode subir sem ganho de
  aprendizagem, e o contrário também; é a rede total, não a pública isolada; é o agregado
  nacional, não a escola ou o município; não é a meta (`VL_PROJECAO_AAAA`), que é projeção
  pactuada; a pandemia quebra a leitura de 2021; as três etapas não formam uma escala única
  comparável.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** dados abertos do Inep; atribuição ao Inep. Uso sujeito aos termos de
  uso do Inep.

## ideb-ensino-medio

- **Definição:** Índice de Desenvolvimento da Educação Básica (Ideb) do Brasil para o ensino médio
  regular, rede total (pública + privada). Escala de 0 a 10. `numero` (`índice`, 1 casa), `eixo:
  contagem`, `medida: nivel`, granularidade `bienal` (C15: `AAAA-01-01`).
- **Fórmula:** `Ideb = N × P`, em que `N` é a nota média padronizada do Saeb (Língua Portuguesa e
  Matemática) e `P` é o indicador de rendimento (taxa de aprovação do Censo Escolar). O índice é
  calculado pelo Inep; a série lê a coluna `VL_OBSERVADO_AAAA` da planilha oficial e **não
  recalcula** o valor.
- **Fonte e código:** Inep — planilha Brasil da edição vigente do Ideb, aba “Brasil (EM)”, linha
  `Brasil`/`Total`. A página de resultados
  (`https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb/resultados`)
  é o `urlFonte`; o notebook descobre nela a edição vigente, baixa o zip em
  `https://download.inep.gov.br/ideb/resultados/divulgacao_brasil_ideb_AAAA.zip`, confere o md5
  do XLSX e falha se o link não estiver lá. A aba do ensino médio traz a linha de códigos
  `VL_OBSERVADO_AAAA` completa; o notebook mapeia o ano pelo cabeçalho visível e confere o código
  contra ele.
- **Periodicidade e paridade.** O Saeb é bienal e o Ideb só existe nas edições ímpares; a série
  declara `bienal` e **todos os 11 pontos caem em anos ímpares** (2005, 2007, …, 2025). Não há
  ponto em ano par nem interpolação: se o Inep publicar um ano par, o notebook falha em vez de
  descartar o ano, porque mudar a periodicidade é decisão de contrato.
- **Cobertura:** 2005–2025, **11 pontos**. Primeiro 3,4 (2005); 2019 4,2; 2021 4,2; 2023 4,3;
  último 4,5 (2025, máximo da série). A diretriz de cobrir desde 1995 foi verificada: o Ideb foi
  criado em 2007 com a primeira edição em 2005 e não tem série comparável antes disso. Busca
  feita em 06/11/2026.
- **Conferência:** mínimo 3,4 (2005); máximo 4,5 (2025); 2025 é o maior valor da série. O ensino
  médio é a etapa com o menor Ideb das três em todos os anos, e a que menos avançou desde 2005
  (+1,1 ponto, contra +2,5 nos anos iniciais e +1,8 nos anos finais).
- **Verificação independente:** a CNN Brasil de 05/08/2026
  (`https://www.cnnbrasil.com.br/educacao/ideb-ensino-basico-tem-recorde-fundamental-2-e-medio-nao-alcancam-meta/`)
  publica a passagem de **4,3 em 2023 para 4,5 em 2025** no ensino médio da rede total. O Inep
  divulgou os mesmos valores em 05/08/2026, mas é o produtor e não conta como publicação
  externa. Não há segunda medição: a publicação cita o Inep.
- **Limitações:** é um índice composto — a taxa de aprovação pode subir sem ganho de
  aprendizagem, e o contrário também; é a rede total, não a pública isolada; é o agregado
  nacional, não a escola ou o município; não é a meta (`VL_PROJECAO_AAAA`), que é projeção
  pactuada; a pandemia quebra a leitura de 2021; as três etapas não formam uma escala única
  comparável.
- **Revisão:** reexecutar o notebook não muda valor além de revisão da fonte. Mudança de valor é
  revisão da fonte, e a revisão é registrada neste arquivo antes de publicar.
- **Licença e atribuição:** dados abertos do Inep; atribuição ao Inep. Uso sujeito aos termos de
  uso do Inep.
