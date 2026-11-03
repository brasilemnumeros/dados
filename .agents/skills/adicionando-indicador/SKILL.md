---
name: Adicionando indicador
description: Use quando for criar ou publicar um indicador novo no repo dados — nova série, novo JSON, entrada no catálogo, notebook de coleta/cálculo ou workflow de atualização.
---

# Adicionando indicador

## Overview

O repo `dados` publica séries em `indicadores/<familia>/<id>.json`, geradas por um notebook e
descritas em `indicadores/catalogo.json`. O contrato é
`../sitio/docs/contrato-de-indicadores.md` (`C1…C15` + `K1…K8`); o validador é a prova
executável. O notebook é o motor: o JSON não é digitado à mão.

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
- mudar só `nome`, `descricao` ou `grupo` no catálogo (é uma linha, sem dado);
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

- produtor vs agregador (BCB SGS é acesso; IBGE/FGV/Ipea são produtores);
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

Antes do PR:

- compare com pelo menos uma **fonte independente** que já publicou o indicador. Independente é
  **outra instituição ou publicação**, não outro endpoint do mesmo produtor. SIDRA v1 × API v3
  do IBGE é consistência da mesma fonte, não verificação independente;
- compare níveis **e** variações em janelas sobrepostas; quantifique a divergência e explique
  (arredondamento, revisão, metodologia, cobertura);
- se não houver fonte independente, declare a limitação na metodologia e na descrição;
- compare também com um número publicado em release, artigo ou gráfico, para pegar erro de
  unidade, base ou escala;
- rode o notebook duas vezes e confira primeiro/último ponto, lacunas, duplicatas, ordem, C15 e
  uma amostra contra a fonte;
- documente a divergência; não ajuste o número para bater com o publicado.

## Fluxo

1. Gate de definição → brief.
2. Gate de fonte → mapa de fontes.
3. Classifique o caso:
   - **Série em família existente:** confira a cadência contra o cron do caller. Se divergir,
     pare e pergunte. Se compatível, use o notebook que já busca a mesma fonte ou crie um
     notebook novo na pasta. O caller existente roda todos os `.ipynb`; não crie outro nem
     mexa na allowlist.
   - **Família nova:** crie `indicadores/<familia>/`, notebook, JSON, catálogo, caller,
     allowlist e linha no `AGENTS.md`.
   - **Família existente sem caller:** crie o caller, a allowlist e a linha no `AGENTS.md`.
4. Escreva/ajuste o notebook conforme `references/notebook-padrao.md`.
5. Gere o JSON executando o notebook; nunca digite valores.
6. Entre no catálogo com `id`, `nome`, `grupo`, `escala` (= `unidade.tipo`), `descricao` e
   `arquivo`.
7. Acrescente o workflow conforme `references/workflow-recorrente.md`.
8. Documente a metodologia com todas as fontes, URLs, fórmula, evidência, caveats e verificação.
9. Rode o gate de verificação e registre a evidência.
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
- `descricao` é uma frase sobre o dado, com unidade, período e o caveat principal.
- Grupo novo exige decisão do usuário sobre nome e posição.
- Rode `validar.py` na raiz: K1/K2 exigem série + catálogo no mesmo PR.

## Workflow recorrente

- Família com caller: nada a fazer; o caller roda todos os notebooks da pasta.
- Família sem caller: crie `.github/workflows/atualizar-<familia>.yml` a partir de
  `assets/atualizar-familia-caller.yml`, acrescente a família à allowlist do step “Validar
  família” em `atualizar-familia.yml` (só a linha do `case`) e a linha da cadência no `AGENTS.md`.
- Reutilizável ausente no checkout: pare e peça para sincronizar com `origin/main`; não recrie.
- Cadência divergente da família: pare e pergunte; mudar o cron afeta as outras séries.
- Cron em UTC; 15:00 = 12:00 de Brasília.

## Atribuição de fonte(s)

- `fonte` é a linha legível da ficha: nomeie todas as fontes com papel/período e diga o que é
  cálculo próprio. Não trate agregador como produtor.
- `urlFonte` é a URL exata do recorte; todas as URLs/códigos vão para `docs/metodologia.md`.
- A atribuição canônica mora na série e na metodologia; não crie campo paralelo no catálogo.
- **Confira se a ficha exibe a fonte.** Hoje `Ficha.svelte` usa `estado.series.source`, mas a
  série expõe `fonte`; se a linha estiver vazia, abra um PR separado no `sitio` para corrigir.
- Verifique licença/termos e exigência de atribuição.

## Validação

```bash
python3 scripts/validar.py
python3 -m pytest -q
python3 -c "import json,glob; [json.load(open(f)) for f in glob.glob('indicadores/*.json')+glob.glob('indicadores/*/*.json')]"
python3 -c "import yaml; yaml.safe_load(open('.github/workflows/atualizar-<familia>.yml'))"
git diff --check
```

Além disso: rode o notebook em ensaio com `DADOS_RAIZ` e `<FAMILIA>_SAIDA`, compare o JSON
gerado com o publicado, revise o diff numérico e confirme K1/K2.

## Erros comuns / red flags

- Começar o notebook antes do brief de definição.
- Chamar o agregador de produtor ou omitir a segunda fonte de uma emenda.
- Chamar outro endpoint do mesmo produtor de “verificação independente”.
- Criar família nova sem allowlist ou ignorar cadência incompatível.
- Gravar data fora de C15 (mensal no dia 15, anual em fevereiro).
- Escrever JSON à mão ou arredondar o valor publicado.
- Publicar sem `fonte` legível, sem `urlFonte` exata ou sem conferir a ficha.
- Mudar valor existente sem pedido e aval.

## Referências

- `references/contrato-resumo.md` — schema, enums e regras operacionais.
- `references/notebook-padrao.md` — células obrigatórias e exemplo real.
- `references/qualidade-e-fontes.md` — gates, hierarquia de fontes, emenda e verificação.
- `references/workflow-recorrente.md` — caller, allowlist, cadência e família.
- `assets/atualizar-familia-caller.yml` — caller copiável.
