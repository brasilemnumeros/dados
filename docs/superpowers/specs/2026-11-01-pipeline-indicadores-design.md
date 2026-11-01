# Pipeline de indicadores: coleta, cálculo e publicação auditável

**Data:** 2026-11-01
**Status:** proposta para aprovação

## Intenção

Substituir os notebooks como pipeline implícito por um processo em que cada indicador seja, ao mesmo tempo:

- a explicação legível de como o dado é obtido e calculado;
- o programa que o CI executa para gerar ou atualizar o JSON publicado.

O notebook é o único artefato de lógica. Não existe uma biblioteca paralela que esconda a coleta ou o cálculo.

## Objetivos

- Gerar qualquer série do zero quando o JSON não existir.
- Atualizar uma série existente publicando apenas o delta, sem reescrever o histórico por acidente.
- Expor claramente fonte, código da série, janela, transformação e validações dentro do notebook.
- Permitir que qualquer pessoa leia e rode o notebook no Colab.
- Rodar de graça e com poucos recursos no GitHub Actions, com PR como ato de publicação.
- Detectar revisões históricas da fonte e tratá-las como caso de revisão, não como atualização rotineira.

## Não objetivos

- Aplicar revisões históricas automaticamente.
- Fazer merge automático de PRs.
- Criar API, banco de dados, dashboard ou app web.
- Automatizar a curadoria de `governos/`.
- Garantir reprodução bit a bit de payloads antigos da fonte.
- Recalcular com frequência menor que diária ou em tempo real.

## Anti-objetivos

- Falhar de forma silenciosa: workflow verde sem publicar, coleta parcial tratada como completa ou revisão histórica escondida no meio de acréscimos.
- Duplicar a lógica entre notebook e script.
- Alterar valores publicados sem um diff visível e revisão humana.
- Transformar o workflow em um programa difícil de rodar localmente.

## Restrições

- Repositório público; GitHub Actions em runner padrão é gratuito.
- `schedule` roda em UTC, com mínimo de 5 minutos e atrasos possíveis.
- Workflows agendados podem ser desativados após 60 dias sem atividade no repositório.
- Fontes públicas sem autenticação: API SGS do Banco Central, `ipeadatapy` e API do Atlas da Violência (IPEA).
- O schema publicado atual não pode mudar de forma incompatível com o app consumidor.
- O notebook precisa continuar abrindo no Colab sem instalação local.

## Abordagens consideradas

### 1. Recalcular tudo e publicar só o delta (escolhida)

O notebook busca a série completa, calcula e escreve o JSON proposto. O CI compara com o arquivo publicado e propõe apenas o delta; se o arquivo não existe, propõe o arquivo inteiro. Alterações em datas já publicadas viram revisão histórica explícita.

**Não existem modos `update` e `rebuild`, nem parâmetro de modo.** Toda execução, agendada ou manual, recalcula a série inteira a partir da fonte. “Atualizar” e “revisar” são apenas classificações do diff resultante, não caminhos de código diferentes.

Por que foi escolhida: um único caminho de código, sem cache velho, com indicadores derivados sempre corretos e com qualquer revisão da fonte visível no diff. O custo é refazer requisições pequenas, aceitável para 13 séries.

### 2. Notebook com modos `update` e `rebuild` (descartada)

Uma célula de parâmetros escolheria entre buscar uma janela recente e buscar tudo. Menos requisições, mas dois caminhos que podem divergir e um merge incremental capaz de esconder revisões antigas. Descartada nesta fase.

### 3. Incremental puro

Buscar apenas depois da última data. Descartada porque quebra indicadores acumulados de 12 meses, que precisam de histórico anterior para calcular o primeiro ponto novo.

## Arquitetura

### Estrutura do repositório

```
<indicador>/
  <Indicador>.ipynb      # fonte da verdade: coleta, cálculo, validação e escrita
  <id>.json              # dado publicado
<indicador>/<id>.json    # id == nome do arquivo sem .json
scripts/
  validar.py             # valida schema e contrato; não calcula indicador
  diff_series.py         # classifica diff em acréscimo vs revisão histórica
requirements.txt         # dependências fixadas para CI
.github/workflows/
  atualizar-dados.yml
```

A unidade de execução é o **notebook**, não a série. Uma pasta pode ter um notebook que publica vários JSONs, como já ocorre em `selic/`, `mvgr/`, `populacao/` e `homicidios/`. O notebook é responsável por todas as séries que publica.

Séries derivadas são calculadas dentro do próprio notebook a partir das fontes brutas. Um notebook não lê o JSON publicado de outra pasta e não depende da ordem de execução dos demais.

`scripts/` contém apenas encanamento e verificação. Nenhum script busca ou calcula indicador.

### Contrato do notebook

Cada notebook deve:

1. Declarar no topo, em markdown, fonte, URL/endpoint, código da série, unidade, granularidade e período coberto.
2. Declarar a data inicial fixa de coleta: `1995-01-01` para todas as séries. A série publicada começa no primeiro ponto calculável a partir desse recorte; séries acumuladas de 12 meses começam após o aquecimento da janela.
3. Buscar a série completa desde essa data, mostrando a URL e a resposta bruta ou um resumo verificável dela.
4. Fazer a transformação e o cálculo em células visíveis, sem funções escondidas.
5. Publicar apenas períodos encerrados: um mês só entra depois de fechado; um ano só entra depois de encerrado. O período em curso fica de fora para não gerar revisão a cada execução.
6. Produzir no máximo um ponto por mês ou ano, ordenado e sem duplicatas.
7. Escrever diretamente todos os JSONs canônicos que a pasta publica, com `schema`, `id`, `unit`, `granularity`, `source` e `data`.
8. Terminar com uma célula de validação que falha o notebook se o contrato não for atendido.
9. Ser determinístico: mesma fonte, mesmo resultado; sem upload manual, estado de sessão ou dependência da ordem de execução fora do fluxo top-to-bottom.
10. Poder rodar no Colab e no CI. O caminho de saída é relativo à raiz do repositório, configurável por variável de ambiente, com fallback para o diretório atual.

Toda execução recalcula a série inteira. Não há modo incremental, cache de pontos ou parâmetro `update`/`rebuild`.

O notebook não deve importar uma biblioteca interna de coleta/cálculo. Código repetido entre notebooks é aceitável em nome da transparência e da independência de cada indicador.

### Escrita do JSON

O notebook escreve o schema canônico diretamente:

```json
{
  "schema": 1,
  "id": "ipca-acum-12m",
  "unit": { "type": "percentage", "symbol": "%", "decimals": 2 },
  "granularity": "monthly",
  "source": "IBGE",
  "data": [
    { "date": "1995-12-01", "rate": 20.41, "value": 20.41 }
  ]
}
```

`rate` e `value` continuam espelhados na fase de convivência. Datas usam o dia 01 do mês/ano de referência. A exceção atual de `homicidios-armas-fogo-anual.json` (dia 15) será normalizada para dia 01 na migração, sem alterar valores.

### Validação

`scripts/validar.py` verifica, para todas as séries:

- JSON válido e campos obrigatórios presentes;
- `id` igual ao caminho do arquivo;
- datas em `YYYY-MM-01`, ordenadas e sem repetição no período;
- no máximo um ponto por mês/ano conforme `granularity`;
- nenhum ponto de período ainda em curso;
- `rate === value`;
- valores numéricos finitos.

Falha com mensagem apontando arquivo, data e regra violada. Não corrige nada.

`scripts/diff_series.py` compara `HEAD` com a árvore de trabalho e classifica cada série em:

- `novo`: arquivo não existia;
- `acrescimo`: só datas novas, com metadados inalterados;
- `revisao`: alguma data existente mudou ou desapareceu, ou algum metadado (`unit`, `granularity`, `source`, `schema`) mudou.

A classificação alimenta o corpo e as labels do PR.

### Workflow

`.github/workflows/atualizar-dados.yml`:

- gatilhos: `schedule` diário e `workflow_dispatch`;
- `permissions: contents: write` e `pull-requests: write`;
- `concurrency` para impedir execuções sobrepostas;
- Python fixado, dependências instaladas de `requirements.txt` com cache;
- cada notebook é executado com kernel novo via `jupyter nbconvert --execute`, com saída em diretório temporário para não versionar outputs;
- se qualquer notebook falhar, o workflow falha e nenhum PR é aberto;
- `scripts/validar.py` roda depois da execução;
- sem diff, o workflow termina sem escrever nada;
- com diff, cria ou atualiza um branch fixo de atualização, commita os JSONs e abre/atualiza um PR.

### Política de PR

- Branch fixa `dados/atualizacao`, atualizada por force-push a cada execução; não se acumulam PRs duplicados.
- Título indica o tipo: `dados: atualização` ou `dados: revisão histórica`.
- Corpo lista, por série, a classificação e os pontos adicionados/alterados.
- `acrescimo` recebe label `atualizacao-rotina`.
- `revisao` recebe label `revisao-historica` e exige revisão humana explícita; nunca é mergeada automaticamente.
- Se qualquer série for `revisao`, o PR inteiro vira “revisão histórica”, mesmo que outras séries tenham apenas acréscimos. Não se separam os dois casos nesta fase.
- O merge é o ato de publicar.
- Commits usam Conventional Commits em português com escopo `dados`, explicando o impacto.

### Auditoria

- Permanente: histórico do Git, diff do PR, mensagens de commit e o próprio notebook.
- Por execução: o notebook executado é publicado como artifact do workflow, com retenção padrão, mostrando URL, contagens e validações.
- Não se versionam payloads brutos nem outputs de notebook. Se a fonte revisar o passado, o PR de revisão mostra exatamente o valor antigo e o novo.
- Revisões históricas são aplicadas sob demanda: a rotina detecta, mas quem decide mergear é uma pessoa.

### `governos/`

Permanece manual. Não é coletado por notebook nem validado como série. Suas regras atuais de mandato efetivo, `mandatoDe` e `emCurso` continuam valendo.

## Migração

1. Adicionar `requirements.txt`, `scripts/validar.py`, `scripts/diff_series.py` e o workflow.
2. Migrar um notebook piloto (IPCA 12M) para o contrato completo e confirmar que o JSON gerado é idêntico ao publicado.
3. Migrar os demais notebooks um a um, comparando o resultado com o arquivo atual. Qualquer diferença de valor deve ser investigada antes de seguir.
4. Substituir a janela móvel de 30 anos do IGP-M por uma data inicial fixa em `1995-01-01` e confirmar que o histórico publicado é preservado.
5. Normalizar as datas de `homicidios-armas-fogo-anual.json` para o dia 01.
6. Aposentar `converter-schema-canonico.py`: os notebooks passam a escrever o schema canônico e `scripts/validar.py` passa a ser a verificação. O histórico do Git preserva o conversor.
7. Ativar o workflow agendado e validar um ciclo completo com PR de acréscimo e um PR simulado de revisão histórica.

## Decisões tomadas pelo autor

- Frequência diária, em horário UTC fixo, com `workflow_dispatch` como escape.
- PR único de atualização, em branch fixa, atualizado por force-push.
- Falha de qualquer notebook bloqueia o PR inteiro.
- Nenhum payload bruto versionado; evidência por execução fica em artifact.
- Todas as séries coletam desde `1995-01-01`; a publicação começa no primeiro ponto calculável.
- Apenas períodos encerrados são publicados; o período em curso fica de fora.
- A unidade de execução é o notebook, que pode publicar vários JSONs.
- Séries derivadas são calculadas dentro do próprio notebook, a partir das fontes brutas.
- Mudança de metadado conta como `revisao`.
- Um PR com qualquer `revisao` é tratado inteiro como revisão histórica.
- Datas de todas as séries normalizadas para o dia 01.
- `converter-schema-canonico.py` sai de cena após a migração.
- `scripts/` pode conter validação e diff, mas não lógica de indicador.

## Riscos e mitigações

- **Desativação do `schedule` após 60 dias sem atividade:** as séries combinadas devem gerar commits com frequência; monitorar e usar `workflow_dispatch` se necessário.
- **Atraso do cron:** não prometer horário exato; o PR é a evidência, não o relógio.
- **Fonte fora do ar:** o workflow falha visivelmente e não publica nada parcial.
- **Mudança silenciosa de metodologia da fonte:** aparece como `revisao` no diff e exige revisão.
- **Notebook pesado ou instável no CI:** dependências fixadas, kernel novo, timeout e execução top-to-bottom.
- **Rate limit por recalcular tudo:** volume atual é pequeno; se necessário, adicionar cache bruto depois sem mudar o contrato do notebook.

## O que fica para o plano de implementação

- Nomes exatos dos arquivos, funções e mensagens.
- Estrutura das células dos notebooks e ordem da migração.
- Formato exato do corpo do PR e das labels.
- Estratégia de pinagem das dependências.
- Detalhes de `nbconvert`, cache do pip e timeout.
