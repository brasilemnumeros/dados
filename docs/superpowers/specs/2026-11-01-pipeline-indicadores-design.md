# Pipeline de indicadores: coleta, cálculo e publicação auditável

**Data:** 2026-11-01
**Status:** proposta para aprovação

## Intenção

Substituir os notebooks como pipeline implícito por um processo em que cada indicador seja, ao mesmo tempo:

- a explicação legível de como o dado é obtido, calculado e conferido;
- o programa que o CI executa para gerar ou atualizar o JSON publicado.

O notebook é o único artefato de lógica. Não existe uma biblioteca paralela que esconda a coleta ou o cálculo.

## Objetivos

- Gerar qualquer série do zero quando o JSON não existir.
- Atualizar uma série existente publicando apenas o delta, sem reescrever o histórico por acidente.
- Revisar a metodologia de cada indicador contra a definição da fonte e corrigir erros ou cálculos desnecessariamente frágeis, com justificativa registrada.
- Expor claramente fonte, código da série, janela, fórmula, transformação e validações dentro do notebook.
- Permitir que qualquer pessoa leia e rode o notebook no Colab.
- Rodar de graça e com poucos recursos no GitHub Actions, com PR como ato de publicação.
- Respeitar exclusivamente o contrato de dados consumido pelo `sitio`.
- Tornar revisões históricas da fonte visíveis no diff do PR, para revisão humana sob demanda.

## Não objetivos

- Aplicar revisões históricas automaticamente.
- Fazer merge automático de PRs.
- Criar API, banco de dados, dashboard ou app web.
- Automatizar a curadoria de `governos/`.
- Mover `governos/` para o `sitio`; isso será feito por outro agente, em trabalho separado.
- Garantir reprodução bit a bit de payloads antigos da fonte.
- Recalcular com frequência menor que diária ou em tempo real.
- Classificar automaticamente o diff em acréscimo vs. revisão.

## Anti-objetivos

- Falhar de forma silenciosa: workflow verde sem publicar, coleta parcial tratada como completa ou revisão histórica escondida no meio de acréscimos.
- Duplicar a lógica entre notebook e script.
- Alterar valores publicados sem um diff visível e revisão humana.
- Transformar o workflow em um programa difícil de rodar localmente.
- Inventar campos ou regras que o consumidor não espera.

## Restrições

- Repositório público; GitHub Actions em runner padrão é gratuito.
- `schedule` roda em UTC, com mínimo de 5 minutos e atrasos possíveis.
- Workflows agendados podem ser desativados após 60 dias sem atividade no repositório.
- Fontes públicas sem autenticação: API SGS do Banco Central, `ipeadatapy` e API do Atlas da Violência (IPEA).
- O contrato publicado é o validado em `sitio/app/src/data/validate.js`; ver “Contrato de dados”.
- O notebook precisa continuar abrindo no Colab sem instalação local.
- A troca de valores causada por correção metodológica é uma revisão histórica e precisa ser justificada.

## Contrato de dados

Fonte de verdade: `sitio/app/src/data/validate.js`, `sitio/docs/plans/01-contrato-de-dados.md` e `sitio/docs/plans/11-migracao-do-repo-dados.md`.

Topo da série:

```json
{
  "schema": 1,
  "id": "ipca-acum-12m",
  "unit": { "type": "percentage", "symbol": "%", "decimals": 2 },
  "granularity": "monthly",
  "source": "IBGE",
  "data": [{ "date": "1995-12-01", "value": 20.41 }]
}
```

Regras exatas:

- `schema === 1`.
- `id` textual e igual ao nome do arquivo sem `.json`.
- `unit.type` em `percentage`, `number` ou `currency`.
- `unit.symbol` textual e não vazio.
- `unit.decimals` inteiro maior ou igual a zero.
- `granularity` em `daily`, `monthly` ou `annual`.
- `source` textual e não vazio.
- `data` é uma lista de objetos `{ "date", "value" }`.
- `date` no formato `YYYY-MM-DD`.
- `value` numérico e finito.
- Nenhum mês repetido na mesma série.
- **`rate` não faz parte do contrato publicado.** A fase de convivência terminou; os notebooks publicam somente `value`. O validador tolera `rate` em arquivo transitório, porque o app o descarta, mas o resultado final não o contém.
- O contrato não exige dia 01, ordem ascendente nem período fechado. Essas são decisões do pipeline, não do formato.
- `indicatorName` não existe.

## Abordagens consideradas

### 1. Recalcular tudo e publicar só o delta (escolhida)

O notebook busca a série completa, calcula e escreve o JSON proposto. O CI compara com o arquivo publicado e propõe apenas o delta; se o arquivo não existe, propõe o arquivo inteiro. Alterações em valores já publicados aparecem como linhas removidas/alteradas no diff e exigem revisão humana.

**Não existem modos `update` e `rebuild`, nem parâmetro de modo.** Toda execução, agendada ou manual, recalcula a série inteira a partir da fonte. “Atualizar” e “revisar” descrevem o diff resultante, não caminhos de código diferentes.

Por que foi escolhida: um único caminho de código, sem cache velho, com indicadores derivados sempre corretos e com qualquer revisão da fonte visível no diff. O custo é refazer requisições pequenas, aceitável para 13 séries.

### 2. Notebook com modos `update` e `rebuild` (descartada)

Uma célula de parâmetros escolheria entre buscar uma janela recente e buscar tudo. Menos requisições, mas dois caminhos que podem divergir e um merge incremental capaz de esconder revisões antigas.

### 3. Incremental puro (descartada)

Buscar apenas depois da última data. Quebra indicadores acumulados de 12 meses, que precisam de histórico anterior para calcular o primeiro ponto novo.

## Arquitetura

### Estrutura do repositório

```
indicadores/<indicador>/
  <Indicador>.ipynb      # fonte da verdade: coleta, cálculo, validação e escrita
  <id>.json              # dado publicado; id == nome do arquivo sem .json
scripts/
  validar.py             # valida o contrato do JSON; não calcula indicador
tests/
  test_validar.py
requirements.txt         # dependências fixadas para CI
.github/workflows/
  atualizar-dados.yml
```

A unidade de execução é o **notebook**, não a série. Uma pasta pode ter um notebook que publica vários JSONs, como já ocorre em `indicadores/selic/`, `indicadores/mvgr/`, `indicadores/populacao/` e `indicadores/homicidios/`. O notebook é responsável por todas as séries que publica.

Séries derivadas são calculadas dentro do próprio notebook a partir das fontes brutas. Um notebook não lê o JSON publicado de outra pasta e não depende da ordem de execução dos demais.

`scripts/` contém apenas validação. Nenhum script busca, calcula ou classifica indicador.

### Contrato do notebook

Cada notebook deve:

1. Declarar no topo, em markdown: fonte, URL/endpoint, códigos das séries, unidade, granularidade, período coberto, definição do indicador e fórmula usada.
2. Declarar a data inicial fixa de coleta: `1995-01-01`. A série publicada começa no primeiro ponto calculável a partir desse recorte; séries acumuladas de 12 meses começam após o aquecimento da janela.
3. Buscar a série completa desde essa data, mostrando a URL e a resposta bruta ou um resumo verificável dela.
4. Fazer a transformação e o cálculo em células visíveis, sem funções escondidas.
5. Publicar apenas períodos encerrados: um mês só entra depois de fechado; um ano só entra depois de encerrado. O período em curso fica de fora para não gerar revisão a cada execução.
6. Produzir no máximo um ponto por mês ou ano, sem duplicatas.
7. Preservar a convenção de data já usada na série publicada. O contrato aceita qualquer dia; a convenção existe para evitar diffs desnecessários.
8. Escrever diretamente todos os JSONs canônicos que a pasta publica, com `schema`, `id`, `unit`, `granularity`, `source` e `data`, e pontos `{ "date", "value" }`.
9. Terminar com uma célula de validação inline que falha se o contrato não for atendido e com as conferências de cálculo da revisão metodológica.
10. Ser determinístico: mesma fonte, mesmo resultado; sem upload manual, estado de sessão ou dependência da ordem de execução fora do fluxo top-to-bottom.
11. Poder rodar no Colab e no CI. O caminho de saída é relativo à raiz do repositório, configurável por variável de ambiente, com fallback para o diretório atual.

Toda execução recalcula a série inteira. Não há modo incremental, cache de pontos ou parâmetro `update`/`rebuild`.

O notebook não deve importar uma biblioteca interna de coleta/cálculo. Código repetido entre notebooks é aceitável em nome da transparência e da independência de cada indicador.

### Revisão metodológica

Antes da migração de cada notebook, a lógica atual deve ser conferida contra a definição da fonte e a matemática do indicador. O resultado vai para `docs/metodologia.md` e para o markdown do notebook.

Pontos obrigatórios:

- Definir o indicador em uma frase, com unidade e granularidade.
- Registrar a série/código da fonte e o que a fonte mede exatamente.
- Registrar a fórmula aplicada e por que ela é a correta.
- Verificar se taxas acumuladas usam composição (`(∏(1 + r/100) − 1) × 100`) e não soma simples.
- Verificar séries reais contra o deflator e a data-base.
- Verificar proporções e variações contra identidades aritméticas.
- Adicionar pelo menos uma conferência independente no notebook.
- Se a correção mudar valores publicados, registrar antes/depois, a razão e a fonte; isso é uma revisão histórica, não uma atualização rotineira.
- Se a revisão concluir que a fórmula atual está correta, registrar a evidência e não mudar valores.

Suspeitas conhecidas a investigar, sem presumir o resultado:

- `ipca-acum-12m` e `igpm-acum-12m`: soma rolante de 12 meses vs. composição.
- `selic-meta-acum-12m`: o nome sugere acumulado, mas o notebook publica média mensal da meta.
- `selic-over-acum-12m`: anualização da taxa diária e janela de 12 meses.
- `mvgr-real`: deflator, data-base e fonte da série nominal.
- `homicidios` e `proporcao-homicidios-armas-fogo-anual`: anos cobertos diferentes e uso de taxas vs. contagens.
- `populacao-variacao-anual`: base populacional e anos de estimativa vs. censo.

### Política de períodos

O contrato não exige período fechado, mas o pipeline publica apenas períodos encerrados para evitar que o último ponto mude a cada execução. Um mês entra depois de fechado; um ano entra depois de encerrado.

### Validação

`scripts/validar.py` verifica, para todas as séries:

- JSON válido e campos obrigatórios presentes;
- `schema === 1`;
- `id` igual ao nome do arquivo;
- `unit` com tipo permitido, símbolo não vazio e `decimals` inteiro ≥ 0;
- `granularity` em `daily`/`monthly`/`annual`;
- `source` não vazio;
- cada ponto com `date` ISO e `value` numérico finito;
- nenhum mês repetido.

Não verifica dia 01, ordem, período fechado, `rate` nem `rate == value`: isso não faz parte do contrato.

Falha com mensagem apontando arquivo e regra violada. Não corrige nada.

Não há classificação automática de diff. O workflow usa `git diff --quiet` para decidir se há qualquer mudança, e o PR mostra o diff completo para revisão humana.

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
- Título fixo: `dados: atualização`.
- Corpo gerado com `git diff --stat` e uma checklist que pergunta explicitamente se algum valor de data já publicada foi alterado.
- O merge é o ato de publicar; não há merge automático.
- Commits usam Conventional Commits em português com escopo `dados`, explicando o impacto.

### Auditoria

- Permanente: histórico do Git, diff do PR, mensagens de commit, `docs/metodologia.md` e o próprio notebook.
- Por execução: o notebook executado é publicado como artifact do workflow, com retenção padrão, mostrando URL, contagens e validações.
- Não se versionam payloads brutos nem outputs de notebook. Se a fonte revisar o passado, o PR mostra exatamente o valor antigo e o novo.
- Revisões históricas e correções metodológicas são aplicadas sob demanda: a rotina detecta, mas quem decide mergear é uma pessoa.

### `governos/`

Permanece manual e intocado neste trabalho. O `sitio` é seu consumidor; a mudança para lá será feita por outro agente, em trabalho separado. A remoção daqui só pode acontecer depois que o `sitio` deixar de buscar `dados/governos/federal.json`.

## Migração

1. Adicionar `requirements.txt`, `scripts/validar.py`, `tests/test_validar.py` e o workflow.
2. Escrever `docs/metodologia.md` com a revisão de cada indicador e as decisões de fórmula.
3. Migrar um notebook piloto sem cálculo (PIB) para validar o pipeline sem alterar valores.
4. Migrar os demais notebooks um a um, aplicando as correções aprovadas na revisão metodológica e comparando o resultado com o arquivo atual.
5. Remover `rate` de todos os JSONs publicados; a fase de convivência terminou.
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
- A lógica dos indicadores será revisada e corrigida quando houver evidência; não é uma preservação cega das fórmulas atuais.
- O contrato publicado terá apenas `value`; `rate` sai.
- Não há classificação automática de diff; revisões históricas aparecem no diff do PR e exigem revisão humana.
- `converter-schema-canonico.py` sai de cena após a migração.
- `scripts/` pode conter validação, mas não lógica de indicador.
- `governos/` não é movido neste trabalho.

## Riscos e mitigações

- **Desativação do `schedule` após 60 dias sem atividade:** as séries combinadas devem gerar commits com frequência; monitorar e usar `workflow_dispatch` se necessário.
- **Atraso do cron:** não prometer horário exato; o PR é a evidência, não o relógio.
- **Fonte fora do ar:** o workflow falha visivelmente e não publica nada parcial.
- **Mudança silenciosa de metodologia da fonte:** aparece como valor alterado no diff e exige revisão.
- **Correção metodológica mal fundamentada:** só entra com definição da fonte, fórmula documentada e conferência independente.
- **Notebook pesado ou instável no CI:** dependências fixadas, kernel novo, timeout e execução top-to-bottom.
- **Rate limit por recalcular tudo:** volume atual é pequeno; se necessário, adicionar cache bruto depois sem mudar o contrato do notebook.
- **Mover `governos/` cedo demais:** quebra o `sitio`, que ainda busca `dados/governos/federal.json`. A ordem é: adaptar o `sitio`, publicar, depois remover daqui.

## O que fica para o plano de implementação

- Nomes exatos dos arquivos, funções e mensagens.
- Estrutura das células dos notebooks e ordem da migração.
- Conteúdo inicial de `docs/metodologia.md`.
- Formato exato do corpo do PR.
- Estratégia de pinagem das dependências.
- Detalhes de `nbconvert`, cache do pip e timeout.
