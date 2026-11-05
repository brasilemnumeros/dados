# Metodologia — Saúde

## mortalidade-infantil-anual

- **Definição:** óbitos de menores de 1 ano por mil nascidos vivos no ano-calendário, por local
  de residência, no Brasil. `numero` (`por mil`, 1 casa), `eixo: por-mil`, `medida: nivel`,
  granularidade `anual` (C15: `AAAA-01-01`). É a taxa **direta** —
  `1000 × óbitos ÷ nascidos vivos` —, **sem correção de sub-registro**.
- **Fonte e código:** MS/SVSA — microdados do SIM (`DOINF{AA}.dbc`, óbitos de menores de 1 ano)
  em `dissemin/publicos/SIM/CID10/DOFET/` e do SINASC (`DNBR{AAAA}.dbc`, nascidos vivos) em
  `dissemin/publicos/SINASC/1996_/Dados/DNRES/`, ambos no FTP do DATASUS
  (`ftp.datasus.gov.br`). O notebook baixa apenas o cabeçalho de cada `.dbc` (que não é
  comprimido) e lê o total de registros; a equivalência com a varredura do arquivo inteiro foi
  conferida nos 29 anos, com zero divergência. A taxa pronta do TabNet (`sim/cnv/inf10uf.def`)
  não está scriptável hoje — o servidor devolve “Tabela de conversao nao encontrada” —, por isso
  o cálculo é próprio.
- **Fórmula:** `taxa = 1000 × óbitos_de_menores_de_1_ano ÷ nascidos_vivos`, por ano.
- **Cobertura:** 1996–2024, **29 pontos**. Um ano só entra quando SIM e SINASC o publicam no
  diretório de dados **finais**; 2025 fica fora porque o SIM 2025 já é final mas o SINASC 2025
  ainda está em `SINASC/PRELIM`. Primeiro ponto 25,47 (1996: 75.024 ÷ 2.945.425); último 12,56
  (2024: 30.020 ÷ 2.389.325).
- **Conferência:** 2000 = 21,27; 2016 = 12,72; 2020 = 11,52; 2023 = 12,62.
- **`urlFonte` ausente:** o recorte é um caminho `ftp://`, que C7.1 não aceita; o portal de
  transferência (`https://datasus.saude.gov.br/transferencia-de-arquivos/`) não é o recorte. Os
  caminhos exatos estão acima e no markdown do notebook.
- **Limitações:** a taxa direta fica **abaixo** da estimativa indireta do IBGE (série CD100,
  2000–2016), que corrige o sub-registro a partir do Censo: a diferença é de ~7,7 por mil em 2000
  (21,27 contra 29,0) e ~0,6 em 2016 (12,72 contra 13,3). Não é a taxa corrigida, a neonatal nem
  a de menores de 5 anos. A cobertura depende da captação de óbitos e nascidos vivos: onde ela é
  pior, o número é menor que o real. O valor de 2024 (12,56) é o cálculo deste notebook; 12,6 é a
  estimativa da Fundação Abrinq e 12,62 (2023) é o boletim da SES/RS, os dois na mesma construção
  direta.
- **Verificação independente:** Fundação Abrinq, *Cenário da Infância e Adolescência no Brasil
  2026* (30/03/2026, `https://fadc.org.br/noticias/mortalidade-infantil-brasil`), publica **12,6
  por mil em 2024** — o cálculo daqui dá 12,56; SES/RS, *Boletim Epidemiológico MMIF 2025*
  (Tabela 22, Brasil,
  `https://saude.rs.gov.br/upload/arquivos/202507/04110055-boletim-mmif-2025-10.pdf`), publica
  **12,62 em 2023** — o cálculo daqui dá 12,62 (32.017 ÷ 2.537.576). O IBGE (CD100, 2000–2016)
  diverge **de propósito**: é a taxa indireta, não a direta. As publicações citam o MS/SIM; não
  há segunda medição.
- **Revisão:** o SIM e o SINASC consolidam declarações com atraso e revisam o histórico. O
  `DNBR2024` foi gravado no FTP em 23/12/2025, e a RIPSA anota dados finais até 2024 atualizados
  em 02/12/2025. Reexecutar só muda valor em revisão da fonte; as âncoras da validação inline
  falham nesse caso, e a revisão tem de ser registrada neste arquivo antes de publicar.
