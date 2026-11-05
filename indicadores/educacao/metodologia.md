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
