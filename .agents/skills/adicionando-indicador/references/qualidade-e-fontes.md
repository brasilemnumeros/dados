# Qualidade, fontes e atribuição

Este é o detalhamento dos três gates da skill. Eles vêm antes do notebook e antes do PR.

## Gate de definição

Pergunte o que **muda o número**, não só o rótulo:

| Pergunta | Por que muda |
|---|---|
| O que o número mede (`medida`)? | nível, acumulado, variação, estoque ou participação exigem séries diferentes |
| Período de referência? | mês calendário, trimestre móvel, ano civil ou data de corte |
| Nominal ou real? | deflator, base e poder de compra mudam o valor |
| Total ou per capita? | denominador e comparabilidade |
| Sazonalmente ajustado? | a série bruta e a ajustada não são intercambiáveis |
| Geografia e cobertura? | Brasil, região, idade, vínculo, informalidade |
| Estoque ou fluxo? | nível num instante vs soma no período |
| Frequência pedida existe? | PNAD Contínua “mensal” é trimestre móvel, não mês calendário |
| Qual a comparação natural? | mês anterior, mesmo mês do ano anterior, 12 meses, % do PIB, por 100 mil |
| Qual a granularidade mínima? | diária só se a pergunta exigir; mensal/anual reduz ruído e tamanho |

Pergunte também:

- **Quais três perguntas o leitor faria?** Elas precisam caber na `descricao` e na metodologia.
- **O que tornaria este indicador enganoso?** Exemplos: taxa de desocupação de trimestre móvel
  lida como mês; valor nominal comparado como real; estoque lido como fluxo; homicídio
  subnotificado; amostra que muda de composição.
- **Já existe indicador no catálogo que responde a isso?** Se sim, prefira série derivada ou
  visualização a um indicador redundante.

Saída: brief curto no chat/PR. Sem brief, não escreva notebook.

## Gate de fonte

### Hierarquia

1. **Série oficial já calculada** com a definição exata. Ex.: IPCA 12m na SGS 13522.
2. **Componentes oficiais com fórmula publicada.** Ex.: IGP-M composto geometricamente da 28655.
3. **Cálculo próprio**, documentado e conferido contra fonte independente.

Se você calcular, diga por que a série pronta não serve (definição diferente, recorte diferente,
cobertura menor) e mostre a fórmula.

### O que registrar

- **Produtor vs agregador.** O SGS é canal das séries de terceiros; o BCB é produtor das séries
  próprias (Selic, câmbio, crédito, MVG-R). IBGE, FGV, Ipea e MTE são produtores das suas. A
  metodologia cita a produtora; a `fonte` pode dizer “IBGE, via SGS 13522”.
- **Código/tabela e endpoint.** Série SGS, tabela SIDRA + variável + localidade, arquivo XLSX,
  PDF e página.
- **Cobertura.** De `1995-01-01` (ou o início real) até o **último período fechado**, não “hoje”.
- **Frequência e defasagem.** Quando a fonte publica e quanto atrasa.
- **Revisão.** A série é final ou provisória? A fonte revisa? O workflow vai capturar a revisão.
- **Ajuste sazonal, base de índice, deflator.**
- **Estabilidade e licença.** API, termos de uso, exigência de atribuição.

### Horizonte e emenda

- Se a fonte começa depois de 1995, **começar depois é preferível a emendar**.
- Se emendar, documente: quais fontes, qual período cada uma cobre, qual a sobreposição, por que
  são compatíveis e onde está a quebra.
- Não emende níveis sem ajuste; não esconda a quebra na descrição.
- Lacuna é ausência de ponto; não interpole nem preencha zero.

### Armadilhas de API

- **BCB SGS:** série diária exige `dataInicial` e no máximo 10 anos por requisição; sem isso,
  406. Série mensal/anual pode pedir tudo.
- **BCB SGS:** 502, `ReadTimeout` e **200 com HTML** acontecem; repita com espera crescente.
  Um 200 com HTML ainda estoura o parser — rodar de novo é o caminho.
- **IBGE/SIDRA:** metadados podem não responder de dentro do GitHub Actions; o notebook da
  População cai para conferência do último ano, com aviso.
- **PDF/tabela:** cite página/tabela e a data de acesso quando o link não for estável.

Saída: mapa de fontes com primária, fallback, independente, horizonte, emenda e último período
fechado.

## Gate de verificação

**Independente** significa outra instituição ou publicação, não outro endpoint do mesmo
produtor. Exemplo: SIDRA v1 × API v3 do IBGE é consistência da mesma fonte; não é verificação
independente. Para a PNAD, uma verificação independente seria um número publicado por outra
instituição ou um artigo/release que cite a mesma taxa.

- Compare **níveis e variações** em janelas sobrepostas.
- Quantifique a divergência e explique: arredondamento, revisão, metodologia, cobertura.
- Compare também com um número publicado em release, artigo ou gráfico, para pegar erro de
  unidade, base ou escala.
- Se não houver fonte independente, declare a limitação na metodologia e na descrição.
- Rode o notebook duas vezes e compare os JSONs.
- Confira primeiro/último ponto, lacunas, duplicatas, ordem, C15 e uma amostra contra a fonte.
- Documente a divergência; não ajuste o número para bater com o publicado.

## Atribuição de fonte(s)

O contrato tem **um** `fonte` (texto) e **um** `urlFonte` (URL). Para múltiplas fontes:

- `fonte` é a linha legível da ficha. Nomeie todas as fontes com papel/período e diga o que é
  cálculo próprio. Ex.:
  `IPEA/Atlas da Violência (SIM/DATASUS); 2014–2024: Atlas da Violência 2026 (FBSP/Ipea), Tabela 11.1`.
- `urlFonte` é a URL principal/mais completa do recorte. Nunca invente URL: sem recorte
  estável, omita e registre o motivo na metodologia. Todas as URLs, códigos e tabelas vão para
  `docs/metodologia.md`.
- Não trate agregador como produtor.
- Se o indicador é calculado pelo site (por 100 mil, deflacionado, proporção), diga isso e
  mostre a fórmula/insumos na metodologia.
- Não crie campo paralelo de fonte no catálogo; a atribuição canônica mora na série e na
  metodologia. A `descricao` pode citar a fonte em prosa.
- **Confira se a ficha exibe a fonte.** Se a linha “Fonte” estiver vazia, o app pode estar
  usando `estado.series.source` em vez de `fonte`; abra um PR separado no `sitio` para trocar
  para `estado.series.fonte` e cobrir com teste.
- Verifique licença/termos e exigência de atribuição; registre na metodologia.

## Checklist antes do PR

- [ ] Brief de definição existe.
- [ ] Mapa de fontes existe, com produtor, cobertura, emenda e independente.
- [ ] O JSON tem `fonte` e, quando houver recorte, `urlFonte`.
- [ ] A fonte escolhida é a mais próxima possível de “oficial já calculada”.
- [ ] A verificação independente foi feita ou a limitação foi declarada.
- [ ] `fonte`/`urlFonte` contam a mesma história que a metodologia.
- [ ] A ficha do app exibe a fonte (ou o bug foi registrado para PR no `sitio`).
- [ ] Datas em C15, sem lacuna preenchida, sem valor arredondado.
