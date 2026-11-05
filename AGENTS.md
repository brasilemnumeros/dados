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

**Fonte de verdade:** `../sitio/docs/contrato-de-indicadores.md` (repo irmão `sitio`; `versao` **1**, regras `C1…C15`).
Este repositório só o **implementa e referencia** — se a prosa e o código divergirem, o
documento vale e a divergência é defeito a corrigir no mesmo commit.

- **Indicador novo:** siga `.agents/skills/adicionando-indicador/SKILL.md` — gates de definição,
  fonte e verificação; série + catálogo no mesmo PR.

- Os arquivos moram em `indicadores/<familia>/<id>.json`; o `id` é igual ao nome do arquivo
  sem `.json` e casa com `[a-z0-9-]+`.
- Nível superior: `versao: 1` (única), `id`, `unidade` (`tipo`, `simbolo`, `casas`, opcional
  `idioma`), `eixo`, `medida`, `granularidade` (`diaria` | `mensal` | `anual` | `bienal`), `fonte`,
  opcional `urlFonte`, `dados`.
- `eixo` é a **comparabilidade declarada** (`percentual`, `reais`, `contagem`, `por-100-mil`,
  `por-mil`); obriga o `unidade.tipo` correspondente (`percentual`, `moeda`, `numero`).
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
`nome`, `grupo`, `escala`, `descricao`, `arquivo` (`<familia>/<id>.json`) e `urlNotebook` (URL do
notebook que gera a série, exibida na ficha do app). É editado à mão: os notebooks escrevem a
série inteira do zero, então curadoria não pode morar neles. O app do `sitio` busca o arquivo em
runtime (`${__BASE_DADOS__}/catalogo.json`, ao lado das séries).

- As regras **`K1…K9`** do `validar.py` conferem o catálogo **contra o disco**: todo `arquivo`
  declarado existe e toda série de `indicadores/*/*.json` tem entrada; `id` casa com o nome do
  arquivo e com o `id` da série; `grupo` existe em `grupos`; `versao` é a esperada; `nome` e
  `descricao` são strings não vazias (K7), nem `id` nem `arquivo` se repetem (K8) e
  `urlNotebook` aponta para um `.ipynb` existente sob `indicadores/` (K9). A URL é completa
  (`https://github.com/brasilemnumeros/dados/blob/main/indicadores/...`); um typo de caminho
  reprova o PR em vez de virar link morto na ficha.
- Todo notebook começa com a célula `id: view-in-github` do selo **Open in Colab**, apontando
  para o próprio arquivo em `main/indicadores/`. `tests/test_notebooks.py` reprova se ela sumir
  ou apontar para o caminho antigo.
- As **saídas commitadas são públicas**: notebook não cita caminho absoluto da máquina. O caminho
  de arquivo aparece sempre relativo à raiz (`indicadores/<familia>/<id>.json`, via helper
  `relativo()` na célula de configuração) — `tests/test_notebooks.py` reprova `/Users/`, `/home/`,
  `/root/`, `C:\` e `file://` em qualquer célula ou saída.
- `escala` é a **classe derivada de `unidade.tipo`** da série. Ela é repetida no catálogo para a
  lista pintar o distintivo antes de o dado chegar — por isso é **conferida** (K4), não digitada
  à toa: se divergir da série, o commit reprova.
- **Indicador novo = arquivo da série + entrada no catálogo, no mesmo pull request.** É o par
  que o CI confere; publicar só um dos dois reprova (K1 ou K2). Renomear (o `nome`), reescrever a
  descrição ou mudar de grupo é uma linha do catálogo, sem tocar no dado — renomear o `id` quebra
  `?series=`, presets e posts.

## Editar ou regenerar dados

- **Nunca altere valores ao mudar a forma.** Correção de fórmula é revisão histórica: registre definição, fonte e impacto em `docs/metodologia.md` e peça aval antes.
- Os notebooks escrevem o **formato inteiro** (`versao`, `id`, `unidade`, `eixo`, `medida`, `granularidade`, `fonte`, `urlFonte`, `dados`) direto em `indicadores/<familia>/` — campos de apresentação não entram. Cada um aceita uma variável de ambiente (`IPCA_SAIDA`, `IGPM_SAIDA`, `SELIC_SAIDA`, `PIB_SAIDA`, `MVGR_SAIDA`, `CAGED_SAIDA`, `POPULACAO_SAIDA`, `HOMICIDIOS_SAIDA`, `PNAD_SAIDA`, `FISCAL_SAIDA`, `MEIO_AMBIENTE_SAIDA`, `CAMBIO_SAIDA`, `SAUDE_SAIDA`, `SANEAMENTO_SAIDA`, `EDUCACAO_SAIDA`, `MOBILIDADE_SAIDA`) para gravar num diretório de ensaio em vez do arquivo publicado.
- Toda execução deve recalcular a série inteira; não há modo incremental.
- O endpoint de metadados do SIDRA (`servicodados.ibge.gov.br/api/v3/agregados/6579/periodos`)
  pode não responder de dentro do GitHub Actions. O notebook da População cai para a conferência
  apenas do último ano, com aviso; os valores continuam vindo do XLSX da projeção.
- `python3 scripts/validar.py` valida o contrato de todas as séries. Não corrige nem calcula nada.
- **Ambiente e dependências:** uv + `pyproject.toml`, resolução congelada em `uv.lock`. `uv sync`
  instala a stack dos notebooks; `uv sync --only-group ci` instala só o gate (`pytest`).
  `.python-version` fixa **3.12**, a mesma do CI — não dependa do `python3` do PATH, que pode ser
  outra versão. Dependência nova entra em `[project].dependencies` (notebook) ou no grupo `dev`
  (ferramenta local), com versão exata e `uv.lock` no mesmo commit.

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
com `actions/checkout` → `astral-sh/setup-uv` (Python **3.12** vindo do `.python-version`) →
`uv sync --frozen --only-group ci` → `uv run --no-sync python scripts/validar.py` → `uv run --no-sync pytest -q`.

- **O grupo `ci` é só o gate** (`pytest`): o validador e os testes são biblioteca padrão, e
  instalar a stack dos notebooks para conferir JSON faria uma quebra de wheel alheia reprovar um PR
  de dado. Por isso o job usa `--only-group ci`, que não instala `[project].dependencies` nem o
  grupo `dev`. A stack dos notebooks e a versão do pytest vêm do mesmo `uv.lock`, então não há pin
  duplicado para divergir.
- **Indicador novo entra por pull request**, não por commit direto em `main`. O gate é esse par de
  comandos: `validar.py` reprova contrato quebrado (`C1…C15`) e catálogo fora de sincronia com as
  séries (`K1…K9`); o `pytest` reprova regressão do próprio validador.
- O job se chama `validar` e está configurado como **check obrigatório** em `main` (branch protection,
  fora do repositório). `enforce_admins` fica desligado de propósito: o dono consegue passar numa
  emergência, mas o caminho normal — PR — exige o check verde.
- O hook em `.githooks/pre-commit` continua valendo para quem commita localmente, mas não roda no PR de
  quem nunca o instalou — quem garante o gate é o CI.

## Atualização agendada

Cada família tem um workflow em `.github/workflows/atualizar-<familia>.yml`, que chama o
reutilizável `atualizar-familia.yml`. A cadência segue a fonte (UTC):

| família | cron | quando |
|---|---|---|
| ipca | `0 15 12,20 * *` | mensal, após a divulgação |
| igp-m | `0 15 2,8 * *` | mensal, após o último dia útil |
| selic | `0 15 2,8 * *` | mensal, após o fechamento |
| cambio | `0 15 3 * *` | mensal, após o fechamento |
| caged | `0 15 3,10 * *` | mensal, com atraso do SGS |
| mvgr | `0 15 5 * *` | mensal, defasagem de ~3 meses |
| pib | `0 15 10 3,6,9,12 *` + `0 15 20 3 *` | trimestral, com Q4 em março |
| fiscal | `0 15 4,20 * *` | mensal, após a divulgação das estatísticas fiscais |
| saude | `0 15 10 6 *` | anual, após o fechamento do SIM e do SINASC |
| saneamento | `0 15 10 4 *` | anual, após a publicação do Sinisa |
| educacao | `0 15 10 9 *` | anual, após a divulgação do Ideb (agosto) |
| mobilidade | `0 15 10 1,9 *` | anual, após o fechamento do SIM (janeiro e setembro) |
| populacao | `0 15 5 9,10 *` | anual, após a estimativa de agosto |
| homicidios | `0 15 15 7,8,12 *` | anual, com o Atlas |
| meio-ambiente | `0 15 15 10 *` | anual, após a consolidação do PRODES |
| pnad | `0 15 5,28 * *` | mensal, após a divulgação |

- As famílias `saude`, `saneamento`, `educacao` e `mobilidade` entraram em 2026-11-05 com uma
  série anual cada — mortalidade infantil, esgoto com rede coletora, Ideb dos anos iniciais
  e mortes no trânsito. Cada uma tem o seu caller e a sua linha na tabela acima.
- Toda execução recalcula a série inteira e roda `scripts/validar.py` + `pytest` antes de
  publicar.
- Qualquer mudança nos JSONs — inclusive acréscimo — abre ou atualiza um PR na branch
  `dados/atualizacao/<familia>`. Não há classificação de diff nem merge automático; o merge
  é o ato de publicar.
- Sem mudança, nenhum PR, branch ou commit é criado.
- O PR é aberto com o PAT `DADOS_BOT_TOKEN` (fine-grained, um ano) para que o check
  `validar` rode; renove antes do vencimento.
- O repositório precisa ter `Settings → General → Pull Requests → Automatically delete head
  branches` ligado antes do primeiro merge: a branch é apagada ao mergear, e o próximo ciclo
  cria outra.
- Se um PR for fechado sem merge, a branch continua; apague a branch ou reabra o PR antes
  do próximo ciclo. Não há configuração nativa para apagar no close.
- `workflow_dispatch` com `seco=true` executa e valida sem publicar; `seco=false` em `main`
  força a publicação.
- O `schedule` roda a partir de `main` e é desativado após 60 dias sem atividade; mergeie
  os PRs com regularidade.
- O notebook executado fica no artifact do run, não no repositório.
- O cron da família é a **união das janelas de divulgação** das séries dela; a série mais
  lenta é reexecutada nas outras datas e não gera PR quando o diff fica vazio. Exemplo: o PIB
  roda trimestralmente para pegar a primeira taxa do ano (março) e a revisão das Contas
  Nacionais Anuais (novembro), mas as três séries são anuais.
- `tests/test_workflows.py` fecha o buraco do agendamento: reprova família em `indicadores/`
  sem `atualizar-<familia>.yml`, caller fora da allowlist, caller apontando para pasta
  inexistente, caller sem `cron` ou sem o workflow reutilizável. Família nova sem caller
  passaria no contrato e nunca atualizaria; agora reprova no CI.

## Antes de commitar

- Instale o hook uma vez por clone: `git config core.hooksPath .githooks`. Ele roda `scripts/validar.py` e `pytest` quando o commit toca `indicadores/`, `scripts/`, `tests/`, `pyproject.toml` ou `uv.lock`. Foi assim que o IPCA voltou a escrever o formato antigo sem ninguém notar: o validador existia, mas não era executado.
- Rode `uv run --frozen --group ci pytest -q` (é o mesmo comando do hook e o mesmo Python 3.12 do CI).
- Valide o parse de todos os arquivos — as séries em `indicadores/<familia>/` **e** o catálogo editado à mão em `indicadores/`: `python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"`.
- Revise o `git diff` em busca de mudanças numéricas acidentais; alterações de data e ordenação se escondem facilmente em diffs grandes de JSON.
- As mensagens de commit seguem Conventional Commits em português com escopo `dados` (ex.: `fix(dados): ...`), e o corpo explica o impacto nos dados.
