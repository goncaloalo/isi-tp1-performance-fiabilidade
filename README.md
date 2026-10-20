# ISI TP1 — Pipeline ETL: Performance vs. Fiabilidade da Gama BMW M

- **Unidade Curricular:** Integração de Sistemas de Informação (ISI)
- **Curso:** Licenciatura em Engenharia de Sistemas Informáticos (LESI) — IPCA / EST
- **Ano Letivo:** 2026/27
- **Autor:** Gonçalo Correia (n.º 22840)

---

## 1. Descrição do Projeto

Este projeto consiste na implementação de um pipeline de **Extract, Transform, Load (ETL)** desenvolvido no **Pentaho Data Integration (PDI / Kettle)**. O objetivo é cruzar especificações mecânicas de automóveis da gama BMW M (1985–2024) com dados de segurança rodoviária obtidos em tempo real via **API REST da NHTSA (*National Highway Traffic Safety Administration*)**.

O fluxo recolhe e limpa os dados brutos, separa registos incompletos para quarentena, calcula rácios de potência e o indicador compósito `recalls_por_100hp`, carrega os dados validados numa base de dados **PostgreSQL 18** e gera exportações analíticas em **JSON** e **XML**. O pipeline é orquestrado de forma sequencial e com mecanismo de paragem por erro (*fail-fast*) através do Job `J_main.kjb`.

---

## 2. Estrutura do Repositório

```text
isi-tp1-performance-fiabilidade/
├── data/
│   ├── raw/                 # Ficheiros originais em bruto (specs.csv, series_lookup.csv)
│   ├── staging/             # Ficheiro de quarentena (rejeitados_specs.csv)
│   ├── processed/           # Datasets canónicos limpos (specs_limpas.csv, nhtsa_recalls.csv, bmw_m_performance_fiabilidade.csv)
│   └── output/              # Relatórios analíticos finais (bmw_m_catalogo_completo.json, bmw_m_resumo_series.xml)
├── kettle/
│   ├── transformations/     # Ficheiros de transformação (.ktr)
│   │   ├── T1_extract_specs.ktr
│   │   ├── T2_extract_nhtsa.ktr
│   │   ├── T3_consolidate_metrics.ktr
│   │   ├── T4_load_postgres.ktr
│   │   └── T5_export_reports.ktr
│   └── jobs/                # Job mestre de orquestração (.kjb)
│       └── J_main.kjb
├── docs/
│   ├── relatorio_final.md   # Relatório técnico completo com todas as evidências visuais
│   ├── decisoes_etl.md      # Caderno formal de decisões técnicas detalhadas
│   ├── GUIAO_VIDEO.md       # Guião estruturado para gravação do vídeo de demonstração (3-5 min)
│   ├── CHECKLIST_CAPTURAS.md# Inventário e estado das 34 capturas de ecrã do projeto
│   └── diagramas/           # Capturas de ecrã do Spoon e esquemas (.png)
├── prints/                  # Cópia das capturas de ecrã do Spoon
└── sql/
    └── 01_schema.sql        # Script DDL da tabela bmw_m_performance_fiabilidade
```

---

## 3. Resumo do Pipeline ETL

| Fase | Ficheiro | Descrição Resumida | Entradas | Saídas |
| :--- | :--- | :--- | :--- | :--- |
| **T1** | `T1_extract_specs.ktr` | Limpeza de texto, quarentena de peso nulo (M3 E92 GTS), regex para versões, deduplicação, cálculo de rácios de potência e lookup da série. | `data/raw/specs.csv`<br>`data/raw/series_lookup.csv` | `data/processed/specs_limpas.csv` (28 válidos)<br>`data/staging/rejeitados_specs.csv` (1 rejeitado) |
| **T2** | `T2_extract_nhtsa.ktr` | Construção de URLs, chamada HTTP GET à API REST da NHTSA e extração da contagem de recalls via JSONPath (`$.Count`). | `data/processed/specs_limpas.csv` | `data/processed/nhtsa_recalls.csv` (28 registos) |
| **T3** | `T3_consolidate_metrics.ktr` | Junção (*LEFT OUTER JOIN*), limpeza de campos duplicados, tratamento de nulos e cálculo de `recalls_por_100hp`. | `data/processed/specs_limpas.csv`<br>`data/processed/nhtsa_recalls.csv` | `data/processed/bmw_m_performance_fiabilidade.csv` |
| **T4** | `T4_load_postgres.ktr` | Carga relacional no PostgreSQL com *Truncate table* para idempotência. Preço do M5 E34 mantido como `NULL`. | `data/processed/bmw_m_performance_fiabilidade.csv` | Tabela `bmw_m_performance_fiabilidade` |
| **T5** | `T5_export_reports.ktr` | Leitura SQL ordenada e bifurcação de fluxo: catálogo JSON (28 modelos) e resumo agregado por série em XML (6 séries). | Tabela no PostgreSQL | `data/output/bmw_m_catalogo_completo.json`<br>`data/output/bmw_m_resumo_series.xml` |
| **J_main** | `J_main.kjb` | Orquestração sequencial `T1 -> T2 -> T3 -> T4 -> T5` com caminhos relativos e desvio para `Abortar por Erro` em caso de falha. | Disparo manual / Kitchen CLI | Execução ponta a ponta (~10s, 0 erros) |

---

## 4. Tecnologias Utilizadas

- **Pentaho Data Integration (PDI / Kettle) 10.2:** Ferramenta central de ETL (Spoon para desenho, Kitchen para execução em linha de comandos).
- **PostgreSQL 18:** Base de dados relacional (`carros_etl`) com driver JDBC nativo.
- **API REST da NHTSA:** Web Service público para obtenção de recalls de veículos nos EUA (`https://api.nhtsa.gov/recalls/recallsByVehicle`).
- **Formatos de Dados:** CSV, JSON, XML e SQL DDL.

---

## 5. Como Executar o Pipeline

### Pré-requisitos
1. **Java Runtime Environment (JRE):** Java 8, 11 ou 17 instalado e configurado na variável de ambiente `JAVA_HOME`.
2. **Pentaho Data Integration:** PDI 9.x ou 10.x extraído localmente.
3. **PostgreSQL:** Instância em execução no porto `5432` com a base de dados `carros_etl` criada.

### Passo 1: Preparação da Base de Dados
Executar o script DDL para criar a tabela relacional:
```bash
psql -U postgres -d carros_etl -f sql/01_schema.sql
```

### Passo 2: Execução via Pentaho Spoon (Interface Gráfica)
1. Abrir o Pentaho Spoon (`spoon.bat` em Windows ou `spoon.sh` em Linux).
2. Abrir o Job principal em `kettle/jobs/J_main.kjb`.
3. Clicar no botão **Run** (ícone de reprodução) e confirmar o arranque local.
4. Verificar que todas as 5 transformações concluem com visto verde.

### Passo 3: Execução via Linha de Comandos (Kitchen CLI)
Para executar o pipeline de forma automatizada sem interface gráfica:
```powershell
& "<caminho_pdi>\Kitchen.bat" /file:"kettle/jobs/J_main.kjb" /level:Basic
```
A execução completa demora cerca de **10 a 11 segundos**, consumindo as chamadas de rede à API da NHTSA cerca de 8 segundos do tempo total.

---

## 6. Resultados e Ficheiros Gerados

Após a execução, os dados ficam materializados em:
- **`data/staging/rejeitados_specs.csv`:** Registo do BMW M3 E92 GTS (2010), rejeitado na validação de peso não nulo.
- **`data/processed/bmw_m_performance_fiabilidade.csv`:** Dataset canónico consolidado com 28 modelos e 18 atributos.
- **Tabela `bmw_m_performance_fiabilidade`:** 28 registos populados na base de dados PostgreSQL `carros_etl`.
- **`data/output/bmw_m_catalogo_completo.json`:** Catálogo detalhado com os 28 veículos num único array JSON.
- **`data/output/bmw_m_resumo_series.xml`:** Relatório com as 6 séries agregadas (Série 2 M a Série 8 M) com contagens, médias de potência e rácios de recalls.

---

## 7. Documentação do Projeto

Para consulta aprofundada, consultar os seguintes documentos:
- [Relatório Técnico Final (`docs/relatorio_final.md`)](file:///C:/Users/gfcco/OneDrive/Documentos/isi-tp1-performance-fiabilidade/docs/relatorio_final.md) — Documento completo com toda a fundamentação, análise de dados e as 34 capturas de ecrã do Spoon.
- [Caderno de Decisões Técnicas (`docs/decisoes_etl.md`)](file:///C:/Users/gfcco/OneDrive/Documentos/isi-tp1-performance-fiabilidade/docs/decisoes_etl.md) — Registo formal e exaustivo das decisões de modelação, operadores e configurações.
- [Guião para Vídeo de Demonstração (`docs/GUIAO_VIDEO.md`)](file:///C:/Users/gfcco/OneDrive/Documentos/isi-tp1-performance-fiabilidade/docs/GUIAO_VIDEO.md) — Sequência detalhada de 3 a 5 minutos para apresentação e gravação da defesa.
- [Inventário de Capturas (`docs/CHECKLIST_CAPTURAS.md`)](file:///C:/Users/gfcco/OneDrive/Documentos/isi-tp1-performance-fiabilidade/docs/CHECKLIST_CAPTURAS.md) — Lista das 34 capturas e notas sobre validação em Spoon.
