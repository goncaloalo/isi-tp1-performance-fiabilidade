# ISI TP1 - Análise de Performance e Fiabilidade Automóvel

Repositório do Trabalho Prático 1 da unidade curricular de Integração de Sistemas de Informação (ISI).

## Estrutura do Projeto

- **`data/`**
  - `raw/`: Dados em bruto (fontes originais).
  - `staging/`: Dados temporários e intermédios do processo de ETL.
  - `export/`: Dados finais processados e exportados.
- **`kettle/`**
  - `jobs/`: Jobs do Pentaho Data Integration (Kettle) (`.kjb`).
  - `transformations/`: Transformações do Pentaho Data Integration (`.ktr`).
- **`sql/`**
  - Scripts de criação de esquemas, tabelas e consultas SQL.
- **`docs/`**
  - `diagramas/`: Diagramas de arquitetura, fluxos e esquemas de dados.
- **`logs/`**
  - Registos de execução de processos de ETL.
