---
name: Adicionando indicador
description: Use quando for criar ou publicar um indicador novo no repo dados — nova série, novo JSON, entrada no catálogo, notebook de coleta/cálculo ou workflow de atualização.
---

# Adicionando indicador

## Overview

O repo `dados` publica séries em `indicadores/<familia>/<id>.json`, geradas por um notebook e
descritas em `indicadores/catalogo.json`. O contrato é
`../sitio/docs/contrato-de-indicadores.md` (`C1…C15` + `K1…K9`); o validador é a prova
executável. O notebook é o motor: o JSON não é digitado à mão — e é ele que a ficha do app
abre pelo `urlNotebook` do catálogo.

O notebook é **público**: começa com o selo do Colab (para qualquer pessoa rodar) e não cita
caminho absoluto da máquina. `tests/test_notebooks.py` reprova os dois casos; detalhes em
`references/notebook-padrao.md`.

Esta skill conduz do pedido ao PR com três gates — **definição**, **fonte** e **verificação**.
Não comece pelo notebook: sem o brief de definição e o mapa de fontes, não há código.

## Quando usar

- criar um indicador ou uma série nova;
- acrescentar uma série a uma família existente;
- publicar um JSON novo e a entrada correspondente no catálogo;
- criar ou ajustar o notebook de coleta/cálculo;
- acrescentar o workflow recorrente de uma família.

## Quando não usar

- corrigir valor de série existente sem pedido explícito e aval;
- mudar só `nome`, `descricao` ou `grupo` no catálogo (é uma linha, sem dado) — exceto quando a
  `descricao` ficou para trás de uma mudança de cálculo: aí ela entra no PR da revisão;
- mexer no contrato ou no validador (outra decisão, outro PR).

## Gate de definição

Antes de escrever notebook, JSON ou workflow, responda com o usuário:

- O que o número mede (`medida`), em que unidade e com que período de referência?
- É nominal ou real, total ou per capita, ajustado sazonalmente ou não?
- Qual a geografia e a cobertura (Brasil, região, idade, vínculo)?
- É estoque ou fluxo? Qual a comparação natural (mês anterior, mesmo mês do ano anterior,
  12 meses, % do PIB, por 100 mil)?
- **A frequência pedida existe na fonte?** Exemplo: a PNAD Contínua “mensal” é trimestre móvel
  encerrado no mês, não taxa do mês calendário.
- Quais três perguntas o leitor faria? Elas precisam caber na `descricao` e na metodologia.
- O que tornaria este indicador **enganoso**? O caveat vira texto de produto.
- Qual a granularidade mínima que responde à pergunta? Diária só se necessário.
- Já existe indicador no catálogo que responde a isso? Evite redundância.

Saída: **brief de definição** curto no chat/PR. Sem ele, pare.

## Gate de fonte

Ordem de preferência:

1. **Série oficial já calculada** com a definição exata (ex.: IPCA 12m na SGS 13522).
2. **Componentes oficiais com fórmula publicada** (ex.: IGP-M composto geometricamente da 28655).
3. **Cálculo próprio**, documentado e conferido contra fonte independente.

Registre no mapa de fontes:

- produtor vs agregador: o SGS é canal das séries de terceiros; o BCB é produtor das séries
  próprias (Selic, câmbio, crédito, MVG-R);
- código da série/tabela, endpoint e `urlFonte` exato;
- cobertura de 1995-01-01 até o **último período fechado**, não “hoje”;
- frequência, defasagem de publicação, política de revisão, ajuste sazonal, base/deflator;
- estabilidade da API, termos de uso e licença;
- se a fonte começa depois de 1995, começar depois é melhor que emendar; se emendar, documente
  a sobreposição e a quebra.

Para BCB SGS: série diária exige `dataInicial` e aceita no máximo 10 anos por requisição;
espere 502/ReadTimeout e 200 com HTML; repita.

Saída: **mapa de fontes** com primária, fallback, independente, horizonte, emenda e último
período fechado.

## Gate de verificação

**Regra:** nenhum PR de indicador passa sem uma **publicação externa** conferida — ou sem uma
**busca documentada** que mostre que ela não existe. "Ad hoc" é o método da conferência, não a
dispensa da busca.

Antes do PR:

1. **Procure** uma publicação externa que já publicou o indicador: veículo de imprensa,
   instituto, associação ou relatório de terceiro. Registre na metodologia o que procurou,
   onde, quando e o que encontrou.
2. **Release/nota do próprio produtor não conta**, mesmo que o número bata. SIDRA v1 × API v3
   do IBGE é consistência da mesma fonte; release do IBGE é o produtor. Continue procurando
   uma publicação de terceiro.
3. Compare **níveis e variações** em janelas sobrepostas; quantifique a divergência e explique
   (arredondamento, revisão, metodologia, cobertura).
4. **Só depois da busca**, se realmente não houver publicação externa, declare a limitação na
   metodologia e na descrição, com o que foi procurado e por que não serviu.
5. Rode o notebook duas vezes e confira primeiro/último ponto, lacunas, duplicatas, ordem, C15
   e uma amostra contra a fonte.
6. Documente a divergência; não ajuste o número para bater com o publicado.

**Critério de aceite:** a metodologia tem um parágrafo "Verificação independente" com a
publicação externa (nome, data, valores e URL) **ou** com a busca feita e o motivo de não
haver. Sem esse parágrafo, o gate não passou.

**Publicação externa ≠ segunda medição.** A publicação externa (mesmo citando o produtor) pega
erro de unidade, base e escala; a segunda medição é outra instituição que calculou o indicador.
O gate exige a publicação externa; se só houver citação, diga na metodologia que não há segunda
medição.

## Fluxo

1. Gate de definição → brief.
2. Gate de fonte → mapa de fontes.
3. Classifique o caso:
   - **Série em família existente:** confira a cadência contra o cron do caller. Se divergir,
     pare e pergunte. Se compatível, use o notebook que já busca a mesma fonte ou crie um
     notebook novo na pasta. O caller existente roda todos os `.ipynb`; não crie outro nem
     mexa na allowlist.
   - **Família nova:** crie `indicadores/<familia>/`, notebook, JSON, catálogo, caller,
     allowlist, linha no `AGENTS.md` e a variável `<FAMILIA>_SAIDA`.
   - **Família existente sem caller:** crie o caller, a allowlist e a linha no `AGENTS.md`.
4. Escreva/ajuste o notebook conforme `references/notebook-padrao.md`: a **primeira célula** é
   o selo do Colab, e nenhum caminho absoluto da máquina entra no código nem nas saídas. Se
   precisar de dependência nova, acrescente a versão exata em `[project].dependencies` do
   `pyproject.toml` e rode `uv lock` no mesmo PR.
5. Gere o JSON executando o notebook; nunca digite valores. O JSON inclui `fonte` e, quando
   houver recorte estável, `urlFonte`; a atribuição não é opcional. Nunca invente URL: sem
   recorte, omita e registre o motivo na metodologia.
6. Entre no catálogo com `id`, `nome`, `grupo`, `escala` (= `unidade.tipo`), `descricao`,
   `arquivo` e `urlNotebook` (o link de auditoria da ficha; K9 confere que o `.ipynb` existe).
7. Acrescente o workflow conforme `references/workflow-recorrente.md`.
8. Documente a metodologia com todas as fontes, URLs, fórmula, evidência, caveats e verificação,
   e confira que a `descricao` do catálogo conta a mesma história que a metodologia.
9. Rode o gate de verificação (busca por publicação externa incluída) e registre a evidência.
10. Valide, revise o diff e abra o PR.

## Tabela de decisão

| `eixo` | `unidade.tipo` |
|---|---|
| `percentual` | `percentual` |
| `reais` | `moeda` |
| `contagem` | `numero` |
| `por-100-mil` | `numero` |

- `medida`: `nivel`, `acumulado-12m`, `variacao-anual`, `estoque`, `participacao`.
- `granularidade`: `diaria`, `mensal`, `anual`.
- C15: mensal `AAAA-MM-01`; anual `AAAA-01-01`; diária com a data real.

## Catálogo

- Entrada em `indicadores/catalogo.json`, sem reordenar as existentes.
- `escala` é `unidade.tipo`; divergência reprova K4.
- `descricao` é uma frase sobre o **dado**: o que o número é, em que unidade, em que período e
  qual o caveat principal. Ela aparece na ficha antes de a série carregar, então não pode
  depender de o leitor abrir o notebook. Se a fórmula, a fonte ou a cobertura mudarem, a
  `descricao` muda **no mesmo PR** — descrição que sobrevive a uma revisão de cálculo vira
  afirmação falsa sobre o número.
- `urlNotebook` é a URL completa do notebook que **gera aquela série**, no formato
  `https://github.com/brasilemnumeros/dados/blob/main/indicadores/<familia>/<Notebook>.ipynb`.
  Não é link para tutorial, artigo ou repositório: é o caminho que a ficha exibe como “Ver o
  notebook que gera estes dados”. K9 reprova URL fora do prefixo `.../blob/main/indicadores/`
  ou apontando para um `.ipynb` que não existe no disco — mover ou renomear o notebook exige
  atualizar a entrada no mesmo commit.
- Grupo novo exige decisão do usuário sobre nome e posição.
- Rode `validar.py` na raiz: K1/K2 exigem série + catálogo no mesmo PR; K9 exige o notebook no
  disco.

## Notebook público

- **Primeira célula: o selo Open in Colab** (`metadata.id = "view-in-github"`), apontando para o
  próprio notebook em
  `https://colab.research.google.com/github/brasilemnumeros/dados/blob/main/indicadores/<familia>/<Notebook>.ipynb`.
  O GitHub mostra o código; o selo leva ao Colab para rodar. O modelo exato da célula está em
  `references/notebook-padrao.md`.
- **Nenhum caminho absoluto da máquina** (`/Users/`, `/home/`, `/root/`, `C:\`, `file://`) no
  código nem nas saídas commitadas. Use `relativo()` na célula de configuração em todo print de
  caminho; a saída deve ler `indicadores/<familia>/<id>.json`, igual ao markdown.
- `tests/test_notebooks.py` reprova selo ausente/errado e caminho local em qualquer célula ou
  saída. `pytest` roda os dois; não os silencie.

## C15 — datas

- `mensal`: normalize para o primeiro dia do **mês de referência** (`AAAA-MM-01`); não use a
  data de publicação.
- `anual`: `AAAA-01-01`.
- `diaria`: a data real do dia.
- Em pandas, `Timestamp(ano, mes, 1)` ou `Period(...).start_time`; para trimestre móvel, o
  primeiro dia do mês de encerramento.

## Workflow recorrente

- Família com caller: nada a fazer; o caller roda todos os notebooks da pasta.
- Família sem caller: crie `.github/workflows/atualizar-<familia>.yml` a partir de
  `assets/atualizar-familia-caller.yml`, acrescente a família à allowlist do step “Validar
  família” em `atualizar-familia.yml` (só a linha do `case`), a linha da cadência no `AGENTS.md`
  e a variável `<FAMILIA>_SAIDA` na lista de variáveis.
- Reutilizável ausente no checkout: pare e peça para sincronizar com `origin/main`; não recrie.
- Cadência divergente da família: pare e pergunte; mudar o cron afeta as outras séries.
- Cron em UTC; 15:00 = 12:00 de Brasília.

## Atribuição de fonte(s)

Toda série precisa de `fonte`; `urlFonte` entra quando houver recorte estável. A metodologia
complementa, não substitui.

- `fonte` é a linha legível da ficha: nomeie todas as fontes com papel/período e diga o que é
  cálculo próprio. Não trate agregador como produtor.
- `urlFonte` é a URL exata do recorte; nunca invente URL. Sem recorte estável, omita e registre
  o motivo na metodologia. Todas as URLs/códigos vão para `docs/metodologia.md`.
- A atribuição canônica mora na série e na metodologia; não crie campo paralelo no catálogo.
- **Confira se a ficha exibe a fonte.** Se a linha estiver vazia, o app pode estar usando
  `estado.series.source` em vez de `fonte`; abra um PR separado no `sitio`.
- Verifique licença/termos e exigência de atribuição.

## Validação

```bash
# use o Python do ambiente do repo (.venv/bin/python se existir)
python3 scripts/validar.py
python3 -m pytest -q   # inclui tests/test_notebooks.py: selo do Colab e caminho local
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"
# só no caso de família nova/caller novo:
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-<familia>.yml'))"
git diff --check
```

Além disso: rode o notebook em ensaio com `DADOS_RAIZ` e `<FAMILIA>_SAIDA`, compare o JSON
gerado com o publicado, revise o diff numérico e confirme K1/K2.

## Erros comuns / red flags

- Começar o notebook antes do brief de definição.
- Chamar o agregador de produtor ou omitir a segunda fonte de uma emenda.
- Chamar outro endpoint do mesmo produtor de “verificação independente”.
- Usar release/nota do próprio produtor como verificação independente.
- Declarar “sem fonte independente” sem ter procurado e registrado uma publicação externa.
- Tratar “ad hoc” como dispensa da busca: ad hoc é o método, a busca é obrigatória.
- Criar família nova sem allowlist ou ignorar cadência incompatível.
- Gravar data fora de C15 (mensal no dia 15, anual em fevereiro).
- Escrever JSON à mão ou arredondar o valor publicado.
- Publicar sem `fonte` legível, sem `urlFonte` quando há recorte estável, ou sem conferir a
  ficha. Achar que a entrada do catálogo substitui a atribuição dentro do JSON.
- Entrar no catálogo sem `urlNotebook`, ou apontar para notebook que não gera a série (K9).
- Publicar notebook sem o selo do Colab, ou com a URL apontando para o caminho antigo.
- Deixar print de caminho resolvido (`/Users/...`, `/home/...`) no notebook: as saídas são
  commitadas e o `tests/test_notebooks.py` reprova.
- Deixar a `descricao` falando do cálculo antigo depois de revisar a fórmula.
- Mudar valor existente sem pedido e aval.

| Racionalização | Realidade |
|---|---|
| “O release do produtor já confere.” | É o mesmo produtor; não é publicação externa. |
| “Não achei fonte independente.” | Só vale com a busca registrada (o que, onde, quando). |
| “A verificação é ad hoc.” | Ad hoc é o método; a busca continua obrigatória. |

## Referências

- `references/contrato-resumo.md` — schema, enums e regras operacionais.
- `references/notebook-padrao.md` — células obrigatórias e exemplo real.
- `references/qualidade-e-fontes.md` — gates, hierarquia de fontes, emenda e verificação.
- `references/workflow-recorrente.md` — caller, allowlist, cadência e família.
- `assets/atualizar-familia-caller.yml` — caller copiável.
