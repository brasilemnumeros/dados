# AGENTS.md

## Visão geral

Arquivos públicos de dados (`*.json`) do **brasilemnumeros**, consumidos pelo app do repo `sitio`. O JSON é o produto. Cada pasta de indicador contém o notebook Colab usado para extrair, calcular e publicar aqueles dados. O validador (`scripts/validar.py`) e os testes (`pytest`) rodam no CI em todo pull request e em push para `main` — ver seção **CI**.

## Ao encontrar um problema

- **Diagnóstico sem solução não vale.** Todo problema apontado vem com **a** solução recomendada
  (uma, com o porquê e o custo), não com um menu de alternativas.
- Questão técnica tem resposta certa: decida e explique o critério, não ofereça caminhos. Só
  pergunte quando a dúvida for sobre **o que o produto deve comunicar** — e então pergunte
  sobre a intenção, nunca sobre a implementação.
- Quando a correção muda valor publicado, a recomendação vem separada em "o que eu faria" e
  "o que depende de aval" — e o aval é pedido antes de aplicar.
- Preferir consertar rótulo a mexer em número: se o dado está certo e a descrição engana, o
  defeito é da descrição.

## Contrato das séries

**Fonte de verdade:** `../sitio/docs/contrato-de-indicadores.md` (repo irmão `sitio`; `versao` **1**, regras `C1…C14`).
Este repositório só o **implementa e referencia** — se a prosa e o código divergirem, o
documento vale e a divergência é defeito a corrigir no mesmo commit.

- Os arquivos moram em `indicadores/<familia>/<id>.json`; o `id` é igual ao nome do arquivo
  sem `.json` e casa com `[a-z0-9-]+`.
- Nível superior: `versao: 1` (única), `id`, `unidade` (`tipo`, `simbolo`, `casas`, opcional
  `idioma`), `eixo`, `medida`, `granularidade` (`diaria` | `mensal` | `anual`), `fonte`,
  opcional `urlFonte`, `dados`.
- `eixo` é a **comparabilidade declarada** (`percentual`, `reais`, `contagem`, `por-100-mil`);
  obriga o `unidade.tipo` correspondente (`percentual`, `moeda`, `numero`).
- `medida` diz **o que o número é** (`nivel`, `acumulado-12m`, `variacao-anual`, `estoque`,
  `participacao`) — não confundir com `granularidade`, que é o espaçamento das datas.
- Cada ponto tem **exatamente** `{ "data": "YYYY-MM-DD", "valor": número finito }`;
  campo desconhecido é erro.
- Datas ascendentes, um ponto por período (dia/mês/ano conforme a granularidade), data de
  calendário válida. Lacuna é **ausência de ponto** — nunca `null`, nunca zero.
- **Corpus de conformidade:** `tests/contrato/` (`validos/` e `invalidos/`, o código da regra
  no nome do arquivo). O validador Python e o `validate.js` do `sitio` rodam os MESMOS casos —
  é assim que os dois concordam.

### Catálogo de apresentação (`indicadores/catalogo.json`)

Irmão das pastas de família, `indicadores/catalogo.json` é a **fonte da apresentação**: `versao`
(1), `grupos` (mapa `id` → `{ nome }`, na ordem de navegação) e `indicadores`, cada um com `id`,
`nome`, `grupo`, `escala`, `descricao` e `arquivo` (`<familia>/<id>.json`). É editado à mão: os
notebooks escrevem a série inteira do zero, então curadoria não pode morar neles. O app do
`sitio` busca o arquivo em runtime (`${__BASE_DADOS__}/catalogo.json`, ao lado das séries).

- As regras **`K1…K6`** do `validar.py` conferem o catálogo **contra o disco**: todo `arquivo`
  declarado existe e toda série de `indicadores/*/*.json` tem entrada; `id` casa com o nome do
  arquivo e com o `id` da série; `grupo` existe em `grupos`; `versao` é a esperada.
- `escala` é a **classe derivada de `unidade.tipo`** da série. Ela é repetida no catálogo para a
  lista pintar o distintivo antes de o dado chegar — por isso é **conferida** (K4), não digitada
  à toa: se divergir da série, o commit reprova.
- **Indicador novo = arquivo da série + entrada no catálogo, no mesmo pull request.** É o par
  que o CI confere; publicar só um dos dois reprova (K1 ou K2). Renomear, reescrever a descrição
  ou mudar de grupo é uma linha do catálogo, sem tocar no dado.

## Editar ou regenerar dados

- **Nunca altere valores ao mudar a forma.** Correção de fórmula é revisão histórica: registre definição, fonte e impacto em `docs/metodologia.md` e peça aval antes.
- Os notebooks escrevem o **formato inteiro** (`versao`, `id`, `unidade`, `eixo`, `medida`, `granularidade`, `fonte`, `urlFonte`, `dados`) direto em `indicadores/<familia>/` — campos de apresentação não entram. Cada um aceita uma variável de ambiente (`IPCA_SAIDA`, `IGPM_SAIDA`, `SELIC_SAIDA`, `PIB_SAIDA`, `MVGR_SAIDA`, `CAGED_SAIDA`, `POPULACAO_SAIDA`, `HOMICIDIOS_SAIDA`) para gravar num diretório de ensaio em vez do arquivo publicado.
- Toda execução deve recalcular a série inteira; não há modo incremental.
- `python3 scripts/validar.py` valida o contrato de todas as séries. Não corrige nem calcula nada.
- Dependências fixadas em `requirements.txt`.

## API do BCB (SGS): o que já mordeu

Quase toda série é lida da API de Dados Abertos do BCB. Ela tem três comportamentos que
custaram execução perdida e não aparecem na documentação:

- **Série diária exige `dataInicial` e aceita no máximo 10 anos por requisição.** Sem isso
  devolve **406** com um JSON de erro explicando a sintaxe. Só a Selic (SGS 11 e 432) é
  diária; o notebook fatia a consulta em décadas e remonta por data. Série mensal/anual não
  tem esse limite — pode pedir tudo de uma vez.
- **Falha intermitente, sem relação com o tamanho da janela.** Já vimos `502`, `ReadTimeout`
  em 60 s e, pior, **200 com HTML** (`Requisição inválida!`) no lugar do JSON — inclusive em
  janelas que funcionaram minutos antes. Os notebooks repetem com espera crescente, mas só em
  erro HTTP: um 200-com-HTML ainda estoura `JSONDecodeError` e derruba a célula. Se acontecer,
  é só rodar de novo — o resultado é determinístico.
- **Consequência:** os notebooks que buscam na fonte precisam de rede para rodar, e reexecutar
  não deve mudar valor nenhum. Se mudar, é revisão da fonte: registre em `docs/metodologia.md`
  antes de publicar.

## `governos/` saiu daqui (2026-11-01)

O registro de mandatos (índice + `federal.json`) mora agora no repo `sitio`, em
`app/src/data/governos/`, e é embutido no bundle do app. Este repositório guarda só as
séries. O schema de lá é o mesmo que estava aqui (exercício efetivo, sem sobreposição,
`mandatoDe`, `emCurso`).

## CI (GitHub Actions)

`.github/workflows/validar.yml`, job `validar`: roda em **todo pull request** e em **push para `main`**,
com `actions/checkout` → `actions/setup-python` em **Python 3.12** (a mesma versão do ambiente local) →
`pip install -r requirements.txt` → `python3 scripts/validar.py` → `python3 -m pytest -q`.

- **Indicador novo entra por pull request**, não por commit direto em `main`. O gate é esse par de
  comandos: `validar.py` reprova contrato quebrado (`C1…C14`) e catálogo fora de sincronia com as
  séries (`K1…K6`); o `pytest` reprova regressão do próprio validador.
- O job se chama `validar`. Torná-lo **check obrigatório** é configuração de *branch protection* no
  GitHub, fora do repositório: sem isso o CI verde informa, não bloqueia.
- O hook em `.githooks/pre-commit` continua valendo para quem commita localmente, mas não roda no PR de
  quem nunca o instalou — quem garante o gate é o CI.

## Antes de commitar

- Instale o hook uma vez por clone: `git config core.hooksPath .githooks`. Ele roda `scripts/validar.py` e `pytest` quando o commit toca `indicadores/`, `scripts/`, `tests/` ou `requirements.txt`. Foi assim que o IPCA voltou a escrever o formato antigo sem ninguém notar: o validador existia, mas não era executado.
- Rode `python3 -m pytest -q`.
- Valide o parse de todos os arquivos: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*/*.json')]"`.
- Revise o `git diff` em busca de mudanças numéricas acidentais; alterações de data e ordenação se escondem facilmente em diffs grandes de JSON.
- As mensagens de commit seguem Conventional Commits em português com escopo `dados` (ex.: `fix(dados): ...`), e o corpo explica o impacto nos dados.
