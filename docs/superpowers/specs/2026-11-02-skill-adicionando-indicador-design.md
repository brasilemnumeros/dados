# Skill `adicionando-indicador` — desenho

**Data:** 2026-11-02
**Status:** aprovado em 2026-11-03
**Fonte de verdade do dado:** `../sitio/docs/contrato-de-indicadores.md` (`C1…C15` + `K1…K9`)

> **Emenda 2026-11-03:** o catálogo passou a exigir `urlNotebook` (K9) — o link de auditoria
> que a ficha do app abre. A skill foi atualizada no mesmo dia: o campo entrou no passo 6, na
> seção **Catálogo**, no `contrato-resumo.md`, no `notebook-padrao.md` e no checklist. O texto
> abaixo, onde fala em `K1…K8`, é o registro do desenho original.

## Intenção

Dar ao agente um caminho repetível para criar um indicador novo no repo `dados`: decidir a
família e os metadados, escrever o notebook que coleta e calcula, publicar o JSON no contrato,
entrar no catálogo, documentar a metodologia e acrescentar o workflow recorrente da família.
O notebook continua sendo o motor; o validador continua sendo a prova executável.

O problema que a skill resolve é de sequência e de decisão, não de fórmula: são muitos arquivos
com donos diferentes (série, catálogo, notebook, metodologia, workflow) e é fácil publicar um
sem o outro. A skill existe para não deixar nenhum par fora de sincronia.

## Contexto

- O repo `dados` publica séries organizadas em famílias; cada pasta tem o notebook que gera os
  JSONs.
- O contrato é normativo e mora no repo irmão `sitio`; o `validar.py` e o `validate.js` rodam o
  mesmo corpus (`tests/contrato/`).
- O catálogo (`indicadores/catalogo.json`) é editado à mão e conferido contra o disco por
  `K1…K8`.
- O workflow de atualização agendada já está em `origin/main`: o reutilizável
  `atualizar-familia.yml`, os oito callers e a tabela de cadência no `AGENTS.md`. O checkout
  local pode estar atrás; a skill confere o disco e, se faltar, manda sincronizar a branch em
  vez de recriar a infraestrutura.
- OpenCode descobre skills de projeto em `.opencode/skills`, `.claude/skills` e
  `.agents/skills`. O último é o formato Agent Skills portátil e é o escolhido.

## Objetivos

- Conduzir a criação de um indicador do começo ao fim, com checkpoints de decisão e validação.
- Cobrir os dois casos: série nova numa família existente e família nova.
- Encodar a decisão operacional que o contrato não dá de graça: família, `id`, `nome`,
  `descricao`, grupo, `unidade`, `eixo`, `medida`, `granularidade`, fonte, `urlFonte` e cadência.
- Garantir o par série + catálogo no mesmo PR, com `validar.py` verde.
- Garantir a convenção de data de C15: mensal no dia 01, anual em 01/01, diária no dia real.
- Pesquisar e escolher a fonte com critério de confiabilidade e cobertura, preferindo série
  oficial já calculada a cálculo próprio.
- Verificar o resultado contra uma fonte independente que já tenha publicado o indicador.
- Atribuir corretamente todas as fontes no `fonte`, no `urlFonte` e na metodologia.
- Acrescentar o caller de atualização da família quando ela ainda não tem caller, sem
  duplicar o workflow reutilizável.
- Registrar a definição, a fonte e a fórmula em `docs/metodologia.md`.
- Deixar o notebook executável e o JSON reproduzível a partir dele.

## Não objetivos

- Inventar fórmula, valor, fonte ou recorte. A definição vem do usuário e da fonte.
- Rever valores publicados ou alterar série existente sem pedido explícito e aval.
- Copiar o contrato inteiro para dentro da skill. A fonte de verdade continua sendo o `sitio`.
- Criar script que reescreva o catálogo inteiro ou que “corrija” JSON.
- Criar workflow por JSON: o workflow é por família.
- Reescrever o `atualizar-familia.yml`, o `validar.yml` ou o `AGENTS.md`: a skill só acrescenta
  a família à allowlist do reutilizável e a linha da cadência no `AGENTS.md`.
- Usar a mesma fonte (ou um espelho dela) como verificação independente.
- Tratar agregador como produtor: BCB SGS é acesso; IBGE/FGV/Ipea são produtores.
- Publicar sem atribuição completa de todas as fontes e sem dizer o que é cálculo próprio.
- Criar campo novo de lista de fontes no contrato: a atribuição usa `fonte`/`urlFonte` e a
  metodologia; mudar o schema seria outra decisão.
- Publicar dado sem notebook, sem fonte ou sem validação.

## Anti-objetivos

- Skill verde que produz série válida mas catálogo desatualizado, ou o contrário.
- Notebook que lê o JSON publicado para decidir o que buscar.
- JSON escrito à mão com valores que o notebook não reproduz.
- Workflow apontando para um reutilizável inexistente.
- Caller novo para uma série que já é coberta pelo caller da família.
- PR com arquivo de outra família, `__pycache__`, notebook executado ou mudança de valor
  acidental.
- Contrato resumido que contradiz o documento do `sitio`.

## Restrições

- Python 3.12; comandos do repo (`python3 scripts/validar.py`, `python3 -m pytest -q`).
- Contrato `C1…C15` e catálogo `K1…K8`; a skill não redefine nenhum dos dois.
- A skill mora em `.agents/skills/adicionando-indicador/`, com `SKILL.md` e arquivos de apoio.
- Workflow agendado: um caller por família em `.github/workflows/atualizar-<familia>.yml`;
  lógica comum em `.github/workflows/atualizar-familia.yml`; cron em UTC, 15:00 = 12:00 de
  Brasília. A skill acrescenta a família à allowlist do reutilizável; não reescreve o resto.
- Base de implementação: o estado de `origin/main` (workflows e tabela de cadência já
  existentes) mais o trabalho de C15 deste PR. Se o checkout local estiver atrás, sincronizar
  antes de implementar; a skill não recria o que já está no `origin/main`.
- Publicação sempre por PR; merge é o ato de publicar.
- Commits em Conventional Commits, em português, escopo `dados`.

## Abordagens consideradas

1. **Fina, só referências.** `SKILL.md` aponta para `AGENTS.md`, o contrato no `sitio`, um
   notebook real e o plano do workflow. Zero duplicação, mas o agente precisa abrir quatro
   arquivos, o link do contrato quebra num clone só do `dados` e a sequência fica fácil de
   pular. Descartada.

2. **Autocontida.** Copia o contrato resumido, um template completo de notebook e os YAMLs do
   workflow para dentro da skill. Funciona sozinha, mas duplica o contrato e os YAMLs que o
   plano de atualização agendada já define; envelhece em dois lugares. Descartada.

3. **Híbrida (escolhida).** `SKILL.md` carrega o passo a passo e as decisões; as referências
   guardam só o que é operacional e pesado; os assets guardam só o que precisa ser copiado
   exato. O contrato continua no `sitio` e o validador continua sendo a prova. O notebook real
   é o exemplo, não um template a preencher.

**Por que a híbrida:** o contrato é fonte de verdade e não deve ser copiado inteiro; o que a
skill precisa capturar é a decisão operacional e a ordem dos passos. Um notebook real ensina
melhor que um template; o caller do workflow é pequeno e precisa ser copiado exato.

## Decisões

### Local e formato

```
.agents/skills/adicionando-indicador/
  SKILL.md
  references/
    contrato-resumo.md
    notebook-padrao.md
    qualidade-e-fontes.md
    workflow-recorrente.md
  assets/
    atualizar-familia-caller.yml
```

- ID: `adicionando-indicador` (nome da pasta).
- Frontmatter: `name: Adicionando indicador` e `description` em português, começando por
  “Use quando…”, com os gatilhos (novo indicador, nova série, catálogo, notebook, workflow).
  A descrição não resume o fluxo.
- `SKILL.md` é o checklist; as referências são carregadas sob demanda.

### Fluxo

1. **Gate de definição (entrevista).** Entender o significado antes de escrever código: o que o
   número mede, período de referência, nominal/real, per capita, sazonalidade, geografia,
   estoque vs fluxo, perguntas do leitor, o que tornaria o indicador enganoso, comparação
   natural e granularidade mínima. Saída: brief curto no chat/PR.
2. **Gate de fonte (pesquisa).** Escolher a fonte, medir confiabilidade, cobertura e cadência;
   decidir se emenda séries. Saída: mapa de fontes com primária, fallback, independente,
   horizonte, emenda e último período fechado.
3. **Classificar o caso:**
   - **Série nova em família existente:** conferir a cadência da fonte contra o cron do caller
     da família. Se divergir, parar e perguntar — mudar o cron afeta as outras séries da
     família. Se for compatível, preferir o notebook que já busca a mesma fonte; se a fonte
     for outra, criar um notebook novo na pasta. O caller existente já roda todos os `.ipynb`
     da pasta: não criar caller novo nem mexer na allowlist.
   - **Família nova:** criar `indicadores/<familia>/`, o notebook, o JSON, a entrada no
     catálogo, o caller `atualizar-<familia>.yml`, acrescentar a família à allowlist do
     reutilizável e a linha da cadência no `AGENTS.md`.
   - **Família existente sem caller:** criar o caller, acrescentar a família à allowlist e a
     linha da cadência no `AGENTS.md`; o notebook entra na pasta existente.
4. **Escrever/ajustar o notebook** conforme `references/notebook-padrao.md`.
5. **Gerar o JSON** executando o notebook, nunca digitando valores.
6. **Entrar no catálogo** com `id`, `nome`, `grupo`, `escala` (= `unidade.tipo`), `descricao` e
   `arquivo`; criar grupo novo só com decisão do usuário.
7. **Acrescentar o workflow** quando a família é nova ou ainda não tem caller, conforme
   `references/workflow-recorrente.md`.
8. **Documentar a metodologia** em `docs/metodologia.md`, com todas as fontes e o plano de
   verificação.
9. **Gate de verificação.** Comparar com fonte independente, quantificar divergência e
   registrar a evidência ou a limitação.
10. **Validar e revisar o diff**; abrir PR.

### Entradas obrigatórias

A skill não começa a escrever sem:

- `id` em `[a-z0-9-]+`, igual ao nome do arquivo, distinto dos existentes.
- família existente ou nova, com o grupo do catálogo definido.
- `unidade.tipo` e `eixo` compatíveis (`percentual`↔`percentual`, `reais`↔`moeda`,
  `contagem`/`por-100-mil`↔`numero`).
- `medida` entre `nivel`, `acumulado-12m`, `variacao-anual`, `estoque`, `participacao`.
- `granularidade` entre `diaria`, `mensal`, `anual`.
- brief de definição: perguntas do leitor, caveat, comparação natural e granularidade mínima.
- mapa de fontes: primária, fallback, independente, horizonte, emenda e último período fechado.
- fonte e, quando houver, `urlFonte` `https://` do recorte exato.
- definição e fórmula (ou “sem fórmula, leitura direta da fonte”).
- cadência da fonte e compatibilidade com a cadência do caller da família; se a família é
  existente e a cadência diverge, a skill para e pergunta antes de acrescentar a série.

### Qualidade, fontes e atribuição

**Gate de definição.** Antes de código, a skill precisa saber:

- o que o número mede (`medida`), em que unidade, com que período de referência;
- nominal ou real, total ou per capita, ajustado sazonalmente ou não, geografia e cobertura;
- estoque vs fluxo, e qual a comparação natural (mês anterior, mesmo mês do ano anterior,
  12 meses, % do PIB, por 100 mil etc.);
- as três perguntas que o leitor faria — elas precisam caber na `descricao` e na metodologia;
- o que tornaria o indicador enganoso — o caveat vira texto de produto;
- a granularidade mínima que responde à pergunta (diária só se necessário);
- se já existe indicador no catálogo que responde a isso (evitar redundância).

**Gate de fonte.** A ordem de preferência é:

1. série oficial já calculada com a definição exata (ex.: IPCA 12m na SGS 13522);
2. componentes oficiais com fórmula publicada (ex.: IGP-M composto geometricamente da 28655);
3. cálculo próprio, documentado e conferido contra fonte independente.

Ao pesquisar, registrar: produtor vs agregador; código da série/tabela; endpoint; cobertura
(1995-01-01 até o último período fechado); frequência; defasagem de publicação; política de
revisão; ajuste sazonal; base de índice/deflator; estabilidade da API; termos de uso/licença.
Se a fonte começa depois de 1995, começar depois é preferível a emendar; se emendar, documentar
a sobreposição e a quebra. Para BCB SGS, lembrar do limite de 10 anos na série diária e das
falhas intermitentes (502, timeout, 200 com HTML).

**Gate de verificação.** Antes do PR:

- comparar com pelo menos uma fonte **independente** que já publicou o indicador — não a mesma
  série nem um espelho dela;
- comparar níveis e variações em janelas sobrepostas; quantificar a divergência e explicar
  (arredondamento, revisão, metodologia, cobertura);
- se não houver fonte independente, declarar a limitação na metodologia e na descrição;
- comparar também com um número publicado em release, artigo ou gráfico, para pegar erro de
  unidade, base ou escala;
- rodar o notebook duas vezes e conferir primeiro/último ponto, lacunas, duplicatas, ordem,
  C15 e uma amostra contra a fonte;
- documentar a divergência, não ajustar o número para bater com o publicado.

**Atribuição de fonte(s).** O contrato tem `fonte` (texto exibido na ficha) e `urlFonte` (uma
URL `https://` do recorte exato). Para múltiplas fontes:

- `fonte` nomeia todas as fontes com papel/período, sem tratar agregador como produtor. Ex.:
  `IBGE, via SGS 13522`; `IPEA/Atlas da Violência (SIM/DATASUS); 2014–2024: Atlas da Violência
  2026 (FBSP/Ipea), Tabela 11.1`.
- `urlFonte` é a URL principal/mais completa; todas as URLs, códigos de série e páginas/tabelas
  vão para `docs/metodologia.md`.
- Se o indicador é calculado pelo site (por 100 mil, deflacionado, proporção), a atribuição diz
  o que é cálculo próprio e a metodologia mostra a fórmula e os insumos.
- A ficha do app deve mostrar `fonte`, não `urlFonte`: a linha precisa ser legível para o
  leitor. Se a ficha estiver vazia, o app pode estar usando `source` em vez de `fonte`; a
  correção é um PR separado no `sitio` e a skill deve conferir isso.
- Não criar campo paralelo de fonte no catálogo; a atribuição canônica mora na série e na
  metodologia. A `descricao` pode citar a fonte em prosa, como já faz hoje.
- Verificar licença/termos e exigência de atribuição; se houver, registrar na metodologia.

### Notebook

O notebook é o motor e deve:

- abrir com markdown declarando fonte, endpoint/códigos, unidade, eixo, medida,
  granularidade, definição, fórmula, período coberto e arquivo gerado;
- resolver a raiz com `DADOS_RAIZ` e aceitar a variável `<FAMILIA>_SAIDA` para ensaio;
- buscar a fonte completa (sem leitura do JSON publicado, sem modo incremental);
- calcular em células visíveis, com a fórmula documentada;
- filtrar períodos abertos antes de montar os pontos;
- escrever o JSON inteiro com `versao`, `id`, `unidade`, `eixo`, `medida`, `granularidade`,
  `fonte`, `urlFonte` e `dados`;
- terminar com uma célula de validação inline que falha em contrato quebrado, data fora de
  C15, período repetido, ordem errada, valor não finito ou divergência com a fonte.

`references/notebook-padrao.md` lista as células obrigatórias e aponta um notebook real como
exemplo. Não há template de notebook para preencher.

### JSON e data

- Caminho: `indicadores/<familia>/<id>.json`.
- C15: mensal `AAAA-MM-01`, anual `AAAA-01-01`, diária com a data real.
- Lacuna é ausência de ponto; não usar `null` nem zero de preenchimento.
- Ordem estritamente ascendente e um ponto por período.
- `unidade.casas` é o que a tela exibe; o valor publicado não é arredondado por causa disso.

### Catálogo

- Entrada nova em `indicadores/catalogo.json`, sem reordenar as existentes.
- `escala` é derivada de `unidade.tipo`; se divergir, K4 reprova.
- `descricao` é uma frase sobre o dado, não sobre a fórmula interna.
- Grupo novo exige `nome` com o mesmo estilo dos existentes e decisão sobre a posição na
  navegação.
- A skill confere `K1…K8` rodando `validar.py` na raiz.

### Workflow recorrente

- Família existente com caller: nada a fazer no workflow; o caller roda todos os notebooks da
  pasta. Conferir a cadência: se a série nova tem cadência diferente da do caller, parar e
  perguntar; mudar o cron da família afeta as outras séries.
- Família sem caller: criar `.github/workflows/atualizar-<familia>.yml` a partir de
  `assets/atualizar-familia-caller.yml`, com `schedule`, `workflow_dispatch` (`seco` padrão
  `true`), `permissions: contents: read`, `concurrency` e `uses: ./.github/workflows/atualizar-familia.yml`.
  Acrescentar a família à allowlist do step “Validar família” em `atualizar-familia.yml` — só
  a linha do `case` — e a linha da cadência na tabela do `AGENTS.md`.
- Família nova: o mesmo do item anterior, mais a pasta, o notebook e o JSON.
- O cadence é decisão do usuário/fonte; a skill usa 15:00 UTC (12:00 de Brasília) e a janela
  típica da publicação. Para fonte mensal, duas tentativas; para anual, a janela de divulgação.
- Se `.github/workflows/atualizar-familia.yml` não existir no checkout, a skill **para** e pede
  para sincronizar a branch com `origin/main`; não recria a infraestrutura nem cria um caller
  que aponta para o vazio. O plano antigo de atualização agendada já foi implementado.
- A skill não altera o resto de `atualizar-familia.yml` nem o `validar.yml`.

### Metodologia

Acrescentar uma seção em `docs/metodologia.md` com definição, todas as fontes e códigos,
URLs/endpoints, fórmula, evidência, perguntas do leitor, limitações, emenda (se houver),
conferência independente e veredito. Se a fonte não tiver fórmula (leitura direta), dizer isso
explicitamente. Não inventar evidência; se não houver conferência numérica, registrar como
pendência. A linha de atribuição da série (`fonte`/`urlFonte`) e a metodologia precisam contar
a mesma história.

### Validação

Antes de abrir PR:

```bash
python3 scripts/validar.py
python3 -m pytest -q
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-<familia>.yml'))"
git diff --check
```

Além disso:

- executar o notebook num diretório de ensaio com `DADOS_RAIZ` e `<FAMILIA>_SAIDA` e comparar o
  JSON gerado com o publicado;
- revisar o `git diff` procurando mudança numérica acidental;
- confirmar que o catálogo e o disco têm exatamente o mesmo conjunto (`K1`/`K2`);
- confirmar que a verificação independente está registrada na metodologia, ou que a limitação
  foi declarada.

### Commit e PR

- Commits em Conventional Commits, português, escopo `dados`:
  `feat(dados): adiciona <id>`.
- Um PR com notebook, JSON, catálogo, metodologia e caller da família (quando houver).
- O corpo do PR registra definição, fonte, fórmula, cadência e o resultado dos gates.
- Não commitar direto em `main`.

## Falhas e paradas

- **Fonte sem cadência definida:** não criar caller; perguntar a janela de publicação.
- **Cadência incompatível com o caller da família:** parar e perguntar; não mudar o cron da
  família sem aval, porque isso afeta as outras séries.
- **Reutilizável de workflow ausente:** parar e pedir para sincronizar a branch com
  `origin/main`; não recriar a infraestrutura.
- **Grupo novo sem decisão:** não inventar grupo; perguntar.
- **Fórmula ou valor sem fonte:** não publicar; registrar a pendência.
- **`validar.py`/`pytest` vermelho:** corrigir antes de abrir PR; não “ajustar” o validador.
- **Divergência entre notebook e JSON publicado:** investigar a fonte; se for revisão
  histórica, pedir aval antes de publicar.

## Critérios de aceitação

- Um agente novo, recebendo um pedido realista de indicador novo, produz série, catálogo,
  notebook, metodologia e caller sem precisar redescobrir o contrato.
- O brief de definição e o mapa de fontes existem antes do notebook; a atribuição de todas as
  fontes está correta e coerente entre série e metodologia.
- O resultado passa em `validar.py` e `pytest`; o catálogo bate o disco; o workflow é YAML
  válido e a família nova está na allowlist do reutilizável.
- Série nova em família existente com cadência incompatível não é publicada silenciosamente:
  a skill para e pergunta.
- A verificação independente foi feita, ou a limitação foi declarada.
- Nenhum valor existente muda sem pedido explícito.
- A skill é descoberta pelo OpenCode a partir de `.agents/skills/adicionando-indicador/SKILL.md`.
- O contrato não é duplicado; o resumo aponta para a fonte de verdade.

## O que fica para o plano de implementação

- Texto exato do `SKILL.md` (checklist, gates, tabela de decisão, erros comuns).
- Conteúdo de `references/contrato-resumo.md`, `references/notebook-padrao.md`,
  `references/qualidade-e-fontes.md` e `references/workflow-recorrente.md`.
- Formato do brief de definição e do mapa de fontes.
- Conteúdo de `assets/atualizar-familia-caller.yml`.
- Cenário de teste da skill (baseline sem skill, aplicação com skill) e critérios de aprovação.
- Ordem de implementação e commits.
