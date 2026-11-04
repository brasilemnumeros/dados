# Revisor independente

Prompt e checklist para a etapa **Gate de revisão** da skill `adicionando-indicador`. O revisor
não é o implementador e não corrige: ele lê o pacote, verifica contra a fonte e o contrato, e
devolve dois veredictos com achados por severidade.

## Papéis

- **Implementador:** escreve notebook, JSON, catálogo e metodologia; roda o ensaio; corrige os
  achados. Nunca revisa o próprio trabalho.
- **Revisor:** contexto novo, sem o histórico da implementação; recebe o pacote abaixo; não edita
  arquivos; devolve veredicto e achados.
- **Controlador:** monta o pacote, dispatcha o revisor, adjudica divergências, garante a
  re-revisão focada e a revisão final do PR inteiro.

## Pacote de revisão

Entregue ao revisor, como caminhos de arquivo (não como resumo no prompt):

1. **Brief de definição** — o que o número mede, unidade, período, geografia, estoque/fluxo,
   frequência, perguntas do leitor, caveats e redundância.
2. **Mapa de fontes** — produtor vs agregador, código/tabela, endpoint, `urlFonte`, cobertura,
   defasagem, revisão, deflator, licença.
3. **Verificação externa** — publicação de terceiro com nome, data, valores e URL, ou a busca
   documentada e o motivo de não haver.
4. **Diff completo** — `git diff` do commit/working tree, com os arquivos novos e alterados.
5. **JSON publicado e notebook** — os arquivos reais, não só o diff.
6. **Propostas de catálogo e metodologia** — a entrada e a seção que o controlador vai integrar.
7. **Contrato e testes** — `../sitio/docs/contrato-de-indicadores.md`, `scripts/validar.py`,
   `tests/test_notebooks.py` e `tests/test_workflows.py`.

## Regras do revisor

- **Contexto novo.** Não receba o histórico da sessão do implementador nem o raciocínio dele.
- **Não edite.** O revisor reporta; o implementador corrige.
- **Não confie no relatório.** Use o relatório como pista; confira a fonte, o JSON e o notebook.
- **Dois veredictos independentes:** **Spec compliance** (fez o que o brief pede?) e
  **Qualidade** (o dado, a fonte e o notebook são confiáveis?).
- **Severidade:** `Critical` (dado errado, contrato quebrado, fonte errada, PR não pode
  mergear), `Important` (corrige antes do merge; risco real de erro silencioso ou de manutenção)
  e `Minor` (texto, robustez, consistência; pode ir para o próximo PR).
- **Sem prejulgamento.** Não instrua o revisor a ignorar um ponto; se discordar de um achado,
  o controlador adjudica com evidência.
- **Re-revisão focada.** Depois da correção, o revisor verifica só o diff da correção e os
  gates; não reabre o restante.

## Checklist

### Contrato e catálogo

- [ ] `validar.py` passa no arquivo e na raiz (C1…C15, K1…K9).
- [ ] `pytest -q` passa.
- [ ] `id` = nome do arquivo = `id` da série; `arquivo` existe.
- [ ] `escala` = `unidade.tipo`; `grupo` existe em `grupos`; `urlNotebook` gera a série.
- [ ] Nenhuma série existente mudou de valor nem de forma.
- [ ] Nenhum `id`/`arquivo` duplicado; a ordem do catálogo não foi reordenada sem motivo.

### Fonte e cobertura

- [ ] O produtor é o produtor, não um agregador; o `fonte` nomeia o papel de cada fonte.
- [ ] O `urlFonte` é o recorte exato (ou a página estável do recorte, quando o arquivo gira).
- [ ] A cobertura vai do início ao **último período fechado**, sem “hoje”.
- [ ] Período aberto foi descartado; lacuna é ausência de ponto, nunca zero/interpolação.
- [ ] A política de revisão e a defasagem estão na metodologia.
- [ ] A “Verificação independente” tem nome, data, valores e URL, ou a busca documentada;
      release do produtor não conta; “não há segunda medição” está explícito quando for o caso.

### Datas e valores

- [ ] C15: mensal `AAAA-MM-01`, anual `AAAA-01-01`, diária com a data real.
- [ ] Datas ascendentes, um ponto por período, sem duplicata, valores finitos e não booleanos.
- [ ] O valor publicado não foi arredondado; `casas` é só exibição.
- [ ] Uma amostra (primeiro, meio, último) confere com a fonte, não só com o relatório.

### Notebook

- [ ] Primeira célula é o selo Open in Colab, com `metadata.id = "view-in-github"` e a URL do
      próprio arquivo.
- [ ] Nenhum caminho absoluto (`/Users/`, `/home/`, `/root/`, `C:\`, `file://`) em célula ou
      saída; prints de caminho usam `relativo()`.
- [ ] Coleta integral com retry; não lê o JSON publicado para decidir o período.
- [ ] Corte de período fechado; validação inline não é tautológica e não expira na virada de ano.
- [ ] O notebook roda duas vezes e produz o mesmo JSON.

### Catálogo e metodologia

- [ ] A `descricao` conta a mesma história que a metodologia e o `fonte` do JSON.
- [ ] A `descricao` não fixa ano-base, fim de série ou valor que envelhece.
- [ ] A `descricao` nega a confusão com o indicador vizinho (ex.: renda individual × renda
      domiciliar; DLSP × DBGG; PRODES × DETER).
- [ ] A metodologia tem definição, fonte/código, fórmula, cobertura, evidência, caveats e
      verificação independente.
- [ ] A `urlNotebook` é a do notebook que **gera** a série (K9).

### Integração

- [ ] Família nova tem caller, allowlist, linha no `AGENTS.md` e variável `<FAMILIA>_SAIDA`.
- [ ] O cron tem 5 campos e cai depois da divulgação da fonte.
- [ ] A família existente usa o caller que já roda todos os `.ipynb`; não criou caller paralelo.
- [ ] O diff não inclui arquivo alheio ao escopo (série existente, notebook de outra família,
      `.playwright-mcp/`, lixo de ensaio).

## Formato da resposta

```markdown
## Veredictos
- Spec compliance: ✅/❌
- Qualidade: ✅/❌

## Achados
### Critical
- <arquivo:linha> — problema — correção esperada.
### Important
- ...
### Minor
- ...

## Evidências executadas
- <comando> → <resultado>
- <fonte> → <amostra conferida>
```

Na resposta final ao controlador, retorne só: veredictos, achados `Critical`/`Important` e uma
linha de avaliação. O relatório completo fica no arquivo do workspace.
