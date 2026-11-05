# Quatro indicadores sociais + emenda do contrato — design

- **Data:** 2026-11-04
- **Estado:** aprovado (2026-11-04)
- **Escopo:** quatro séries novas — mortalidade infantil, esgotamento sanitário, Ideb e
  mortes no trânsito — e duas emendas ao contrato (`eixo: por-mil` e `granularidade: bienal`).
- **Fora de escopo:** mudar valor de série existente; publicar projeção populacional como
  observação; emendar PNAD antiga; criar `eixo: indice`; mexer no desenho do painel de
  mandatos além da régua de cobertura; alterar o `versao: 1` dos arquivos.

## Intenção

O lote anterior (dívida, renda domiciliar, desmatamento, câmbio) fechou as perguntas
econômicas e abriu fiscal e meio ambiente. O catálogo continua respondendo "como vai a
economia" e não responde "como vai a vida": não há saúde, educação nem saneamento, e a
violência só aparece como homicídio.

A régua é a mesma do lote anterior: responder pergunta que o site não responde, usar série
oficial, não repetir grupo existente e caber no contrato — **ou emendar o contrato quando a
declaração atual mentir sobre o número**.

## O que entra

| # | Série | Grupo | Família | Fonte | Cobertura | Unidade / eixo / medida | Granularidade |
|---|---|---|---|---|---|---|---|
| 1 | `mortalidade-infantil-anual` | `saude` (novo) | `saude` (nova) | MS/SIM + Sinasc, taxa por mil nascidos vivos | 1996–último ano fechado | `numero` / `por-mil` (**novo**) / `nivel` | anual |
| 2 | `esgoto-rede-coletora-total` | `saneamento` (novo) | `saneamento` (nova) | SNIS/SINISA, população atendida com rede coletora | 1995–2023 | `percentual` / `percentual` / `nivel` | anual |
| 3 | `ideb-anos-iniciais` | `educacao` (novo) | `educacao` (nova) | Inep/Ideb, anos iniciais, rede total | 2005–2025 | `numero` / `contagem` / `nivel` | `bienal` (**novo**) |
| 4 | `mortes-transito-anual` | `mobilidade` (novo) | `mobilidade` (nova) | MS/SIM, CID-10 V01–V99, taxa por 100 mil calculada pelo site | 1996–último ano fechado | `numero` / `por-100-mil` / `nivel` | anual |

Trânsito ganha grupo próprio (`mobilidade`), e não entra em `seguranca-publica`: o grupo é
uma fatia semântica de navegação, não um balde de conveniência. Mortes no trânsito são
mobilidade — no futuro o grupo recebe frota, transporte público e tarifa, que não são
segurança pública. Grupo de uma série só é aceitável quando o nome diz exatamente o que
está lá; o catálogo vai crescer, e juntar por densidade agora obrigaria a desmembrar depois.

## Decisões de produto

### 1. Mortalidade infantil — o indicador que faltava

**Recomendação:** taxa de óbitos de menores de 1 ano por mil nascidos vivos, Brasil, anual,
de 1996 em diante. É o indicador de saúde que qualquer cidadão reconhece e o que melhor
conversa com saneamento e renda no mesmo gráfico.

**O que o número é:** óbitos de crianças com menos de 1 ano divididos pelos nascidos vivos
do mesmo ano, × 1.000. Não é mortalidade na infância (menores de 5 anos), não é esperança
de vida e não é o número absoluto de óbitos.

**Fonte:** a taxa pronta do Datasus (TabNet/SIM-Sinasc) é a primeira opção; se o recorte não
for estável para script, o notebook calcula a taxa a partir das contagens oficiais do SIM e
do Sinasc, com a fórmula declarada — o mesmo caminho já usado em homicídios. O gate de fonte
decide entre as duas e registra o endpoint exato no mapa de fontes.

**Caveat obrigatório na descrição:** a taxa depende da captação de óbitos e nascidos vivos;
nos anos e regiões de pior cobertura, o número é menor que o real. O IBGE publica uma taxa
corrigida por métodos demográficos — esta série não é essa.

### 2. Esgotamento sanitário — rede, não tratamento

**Recomendação:** percentual da população total atendida com rede coletora de esgoto, Brasil,
anual, de 1995 a 2023 (SNIS até 2022; Sinisa em 2023). É o indicador de saneamento com a
série mais longa e o que o cidadão entende sem glossário.

**O que o número é:** população atendida por rede coletora dividida pela **população total
residente do Brasil** (IBGE), × 100 — não pela população da amostra de municípios que
reportaram. A escolha é deliberada: a pergunta do cidadão é "quanto do Brasil tem rede", e
um denominador de amostra premiaria o município que não reporta. O custo é que a série vira
um **piso**: quem não reporta entra como não atendido. **Não é** esgoto tratado: uma cidade
pode coletar e lançar in natura. Também não é domicílio com fossa adequada, que é outro
recorte.

**Por que não publicar as duas:** a versão oficial (denominador = população dos municípios
da pesquisa) e a nacional não são dois indicadores; são o mesmo indicador com dois
denominadores, e a diferença entre elas mede **cobertura da pesquisa**, não esgoto. Duas
linhas quase idênticas obrigariam o leitor a aprender amostragem para escolher, e a oficial
sobe quando a amostra cresce — o que a torna pior para ler 30 anos. O número oficial entra
na metodologia como conferência, não no catálogo. Critério: duas séries quando a diferença
entre elas **é o fenômeno** (nominal × real, meta × over); uma quando a diferença é o
instrumento de medida.

**Emenda SNIS → Sinisa:** o SNIS encerrou a coleta em 2023 com dados de **2022**; o Sinisa
assumiu em **2023** com código novo (IES0001). Não há ano de sobreposição — a condição do
critério abaixo não se aplica. A série emenda os dois com a quebra documentada na metodologia
e na descrição; o degrau de 2022→2023 (−0,71 p.p.) é artefato de amostra e de troca de
sistema, não queda real, e o notebook o registra como diagnóstico.

**Critério de aceite da emenda:** quando houver ano de sobreposição, comparar o mesmo ano
calculado pelas duas fontes com o mesmo denominador. Se a diferença absoluta for **≤ 0,1
ponto percentual** — a unidade de arredondamento da série —, a emenda entra e a diferença
medida vai para a metodologia. Acima disso, a série para no último ano da fonte antiga e a
metodologia declara o motivo; não se ajusta o número para colar. Sem sobreposição, a emenda
entra com a quebra declarada e o teste vira diagnóstico.

**Caveat:** a amostra de municípios muda de ano para ano (o SNIS cobre ~5.3 mil dos 5.570
municípios); a série mede o país, não um conjunto fixo de cidades. Crescimento do
atendimento pode refletir entrada de município na amostra, não só obra. A rampa de
1995–1999 é dominada pela entrada de municípios na amostra (1995→1996 sobe 13,85 p.p.);
o começo da série não é uma "explosão" de obras.

**2024 fica fora:** o IBGE muda a base populacional em 2024 (212,58 milhões contra 203,08
milhões), o que criaria um degrau de denominador de ~4,6%. A série entra em 2024 quando
houver população nacional comparável; até lá, o último ponto é 2023.

### 3. Ideb — o índice que exige `bienal`

**Recomendação:** Ideb dos anos iniciais do ensino fundamental, rede total, Brasil,
2005–2025 (11 pontos, de dois em dois anos).

**O que o número é:** índice de 0 a 10 que combina a proficiência média no Saeb com o
indicador de rendimento (aprovação) do Censo Escolar. Não é percentual de aprendizado, não
é nota de escola e não mede o ensino médio (que é outra série, se entrar depois).

**`eixo: contagem` é compromisso consciente, não descuido:** o índice 0–10 não é contagem,
mas um terceiro eixo (`indice`) não mudaria nada visível — o app não agrupa eixo (usa
amplitude) e a ficha lê `unidade.tipo`, não `eixo`. O ganho real vem do rótulo da ficha,
tratado abaixo. A `descricao` diz "índice de 0 a 10".

**Por que `bienal` e não `anual`:** a periodicidade do indicador é de dois anos. Declarar
`anual` faria o painel de mandatos esperar quatro pontos por mandato e encontrar dois —
marcando "parcial" em célula que está completa. O contrato não tem essa palavra hoje; a
emenda abaixo a cria.

**Caveat:** é um índice composto, com escala arbitrária (0–10) e metas políticas; comparar
"pontos de Ideb" entre etapas não significa a mesma coisa que comparar percentuais.

### 4. Mortes no trânsito — o complemento barato da violência

**Recomendação:** óbitos por acidentes de transporte (CID-10 V01–V99), taxa por 100 mil
habitantes, Brasil, anual, de 1996 em diante.

**O que o número é:** mortes cuja causa básica é acidente de transporte, divididas pela
população residente, × 100.000. Inclui pedestre, motociclista, ocupante e ciclista; inclui
vias urbanas e rodovias. **Não é** número de sinistros, de feridos, de multas nem de mortes
em rodovias federais (essa é a série da PRF, outra).

**Fonte e denominador:** SIM/Datasus para o numerador; a mesma população residente usada em
homicídios para o denominador, para que as duas taxas sejam comparáveis. O notebook calcula
a taxa (numerador ÷ população) em vez de republicar taxa pronta de terceiro, pelo mesmo
motivo de homicídios: o denominador muda de safra ao longo do tempo.

**Caveat:** subregistro e mudança de codificação de causa entre 1996 e hoje; a série usa
CID-10 desde 1996, sem emendar a CID-9.

## Emenda do contrato

Duas mudanças, uma edição, nos dois repositórios. Nenhuma altera `versao: 1` (a forma do
arquivo não muda) nem valor publicado.

### `C4` — novo eixo `por-mil`

| `eixo` | `unidade.tipo` | exemplo |
|---|---|---|
| `por-mil` | `numero` | mortalidade infantil |

- `EIXOS` e `TIPO_DO_EIXO` em `validar.py` e `validate.js`.
- Tabela do `C4` no contrato.
- Corpus: um caso válido (`por-mil` + `numero`) e um inválido (`por-mil` + `percentual`).
- O eixo só participa da validação; o rótulo visível da ficha é tratado na seção do app.

**Por que melhora o produto:** hoje a mortalidade infantil só caberia em `contagem`, o
mesmo furo semântico que o desmatamento usa para km². O eixo passa a dizer o que o número
é, e o símbolo `"por mil"` espelha o `"por 100 mil"` dos homicídios.

### `C6` — nova granularidade `bienal`

- `GRANULARIDADES` em `validar.py` e `validate.js`.
- `chaveDoPeriodo` e `inicioDoPeriodo` tratam `bienal` no ramo do ano (a chave é `AAAA`;
  a data é `AAAA-01-01`), como `anual`.
- **Paridade obrigatória:** todos os pontos da série têm o mesmo ano par/ímpar do primeiro
  ponto. `bienal` não é só etiqueta — ponto fora da paridade reprova, senão a série passa
  e o painel calcula a expectativa errada. Lacuna de um ponto (4 anos entre medições)
  continua permitida; o que não pode é 2005, 2006 e 2007 na mesma série.
- `C6`, `C11` e `C15` do contrato ganham a menção a `bienal`.
- Corpus: um caso válido bienal, um inválido de paridade (2005 + 2006) e um inválido de
  data fora de `AAAA-01-01`.

**Impacto no painel de mandatos (o ponto que a emenda resolve):**

1. `pontosEsperados` passa a receber a série, não só `(granularidade, mandato)`. A **fase**
   é o ano do primeiro ponto; a expectativa é quantos anos da janela caem nessa paridade.
   Para o Ideb (fase 2005): 2019–2022 espera 2; 2016–2018 espera 1; 2015–2016 espera 1.
   A fase vem de `series.dados[0].data` — não precisa de campo novo no contrato.
2. `deltaNoMandato` passa a série para `pontosEsperados`; o Δ continua sendo
   último − primeiro ponto dentro do mandato, e `ponto-unico` continua sem Δ.
3. `motivoDaAusencia` ganha um terceiro caso: janela **entre** duas medições (ex.: um
   mandato de um ano num ano par). Hoje ele diria "série termina em …", o que é falso —
   a série continua, só não mede aquele ano. O texto passa a "sem medição no período".

Sem isso, o Ideb declarado `anual` produz "parcial" em toda célula e "ponto único" onde há
dois pontos; com a emenda, o painel mostra o estado real.

### App e ficha (`sitio`)

A emenda **não** é invisível para o app. `Ficha.svelte` hoje mostra
`numero → "contagem"` e seu mapa de granularidade só tem `diaria`, `mensal` e `anual`:
o Ideb apareceria com granularidade em branco e a mortalidade infantil com
"por mil (contagem)". O PR do `sitio` inclui:

- `GRANULARIDADE` ganha `bienal: "bienal"`.
- O rótulo entre parênteses da unidade passa a sair do **eixo** (ou do símbolo), não só do
  `unidade.tipo`: `por-100-mil` → "taxa por 100 mil", `por-mil` → "taxa por mil",
  `contagem` → "contagem". Isso corrige de passagem o homicídio, que hoje aparece como
  "por 100 mil (contagem)".
- O distintivo da busca (`SearchModal`) continua lendo `escala` do catálogo (`numero`) e
  mostrando "nº / contagem"; mudá-lo exigiria campo novo no catálogo e fica fora deste
  lote. A ficha é a fonte precisa.

### Ordem de entrega

O app valida a série ao carregar. Se o `dados` publicar `por-mil` ou `bienal` antes de o
`sitio` conhecer os valores, a home abre em `SchemaError`. A ordem é:

1. contrato + corpus + os dois validadores + `mandates.js` + `Ficha.svelte` + `AGENTS.md`
   e a skill `adicionando-indicador` (tabela de decisão e enums) — PRs coordenados nos dois
   repos;
2. séries e catálogo;
3. `urlNotebook` e metodologia no mesmo PR de cada série.

## Grupos e navegação

| Grupo | Nome proposto | Posição | Séries |
|---|---|---|---|
| `saude` | **🩺 Saúde** | depois de `trabalho` | mortalidade infantil |
| `saneamento` | **🚰 Saneamento** | depois de `saude` | esgoto |
| `educacao` | **🎓 Educação** | depois de `saneamento` | Ideb |
| `mobilidade` | **🚗 Mobilidade** | depois de `educacao` | mortes no trânsito |

Ordem final proposta: monetário, inflação, crescimento, fiscal, imobiliário, trabalho,
saúde, saneamento, educação, mobilidade, demografia, segurança pública, meio ambiente.

**Decisão registrada:** grupo novo pode ter uma série só quando o nome é semanticamente
exato; a densidade não decide o agrupamento. Os nomes e a posição acima seguem a ordem
natural de leitura (economia → condições de vida → população → segurança → ambiente).

## Riscos e mitigação

- **Datasus (mortalidade e trânsito):** TabNet não é API estável; o plano prevê o caminho
  de microdados (SIM/Sinasc) com fórmula declarada e conferência contra a taxa publicada.
  Se o download oficial mudar, o notebook falha alto — não cai para número de terceiro.
- **SNIS → Sinisa:** quebra de sistema em 2024. A emenda é documentada e conferida; se a
  sobreposição divergir, a série para em 2023 e a metodologia declara o motivo.
- **Ideb:** XLSX do Inep muda de nome a cada edição; o notebook resolve o arquivo do ano e
  falha se não achar, em vez de reaproveitar safra velha.
- **Contrato em dois repos:** o `sitio` precisa da emenda antes da publicação das séries
  (validadores, `mandates.js` e ficha); o CI de cada repo roda o corpus compartilhado.
- **Verificação externa:** cada série precisa de uma publicação de terceiro conferida
  (imprensa, instituto, relatório) ou da busca registrada. O plano inclui essa etapa por
  série, como no lote anterior.

## O que fica para o plano

- Endpoint exato e fallback de cada fonte (gate de fonte da skill).
- Estrutura dos notebooks e das famílias novas, callers e allowlist.
- Casos concretos do corpus e os testes de `pontosEsperados`/`motivoDaAusencia`.
- Ordem dos commits e dos PRs entre `dados` e `sitio`.
- Textos de `descricao` e de `docs/metodologia.md` série a série.
