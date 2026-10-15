# ISI TP1 — Análise de Performance e Fiabilidade Automóvel

- **Unidade Curricular:** Integração de Sistemas de Informação (ISI)
- **Curso:** Licenciatura em Engenharia de Sistemas Informáticos (LESI) — IPCA / EST
- **Ano Letivo:** 2026/27
- **Tema:** Pipeline ETL para Análise Comparativa de Performance Mecânica e Fiabilidade Rodoviária (Gama BMW M)

---

## 1. Enquadramento e Objetivos

Este projeto implementa uma pipeline robusta de **Extract, Transform, Load (ETL)** desenvolvida no **Pentaho Data Integration (PDI / Kettle)**. O sistema recolhe, higieniza, valida e cruza dados heterogéneos de especificações técnicas automóveis com dados oficiais de segurança rodoviária obtidos via API REST externa, preparando os artefactos para persistência relacional em PostgreSQL e exportações analíticas multiformato.

O ciclo de vida dos dados cumpre as três fases obrigatórias do enunciado de ISI:
- **Fase 1 (Recolha e Ingestão — "E"):** Ingestão de datasets locais em formato CSV e consumo dinâmico de Web Services REST com respostas estruturadas em JSON.
- **Fase 2 (Processamento e Limpeza — "T"):** Normalização sintática, validação de regras de integridade, segregação de registos inválidos para quarentena (*Dead-Letter Queue*), aplicação de Expressões Regulares (ER) para extração semântica, imputação controlada de valores nulos, deduplicação determinística, junções (*Stream Lookups*) e computação de rácios mecânicos derivados.
- **Fase 3 (Persistência e Exportação — "L"):** Exportação em múltiplos formatos canónicos (CSV, JSON, SQL/relacional).

---

## 2. Estrutura do Repositório

```text
isi-tp1-performance-fiabilidade/
├── data/
│   ├── raw/                 # Dados originais em bruto (specs.csv, series_lookup.csv)
│   ├── staging/             # Quarentena e dados intermédios (rejeitados_specs.csv)
│   ├── processed/           # Datasets canónicos limpos e validados (specs_limpas.csv, nhtsa_recalls.csv, bmw_m_performance_fiabilidade.csv)
│   └── output/              # Relatórios analíticos finais (bmw_m_catalogo_completo.json, bmw_m_resumo_series.xml)
├── kettle/
│   ├── transformations/     # Ficheiros de transformação Kettle (.ktr)
│   │   ├── T1_extract_specs.ktr
│   │   ├── T2_extract_nhtsa.ktr
│   │   ├── T3_consolidate_metrics.ktr
│   │   ├── T4_load_postgres.ktr
│   │   └── T5_export_reports.ktr
│   └── jobs/                # Jobs de orquestração (.kjb)
│       └── J_main.kjb       # Job master de orquestração global ponta a ponta
├── docs/
│   ├── decisoes_etl.md      # Caderno formal de decisões técnicas e arquitetura
│   └── diagramas/           # Checklist e inventário de capturas para o relatório final
├── prints/                  # Capturas de ecrã consolidadas do Pentaho Spoon
├── sql/                     # Esquemas DDL, tabelas de dimensão/facto e views analíticas
│   └── 01_schema.sql        # DDL da tabela consolidada bmw_m_performance_fiabilidade
└── logs/                    # Ficheiros de registo e auditoria de execução ETL
```

---

## 4. Transformações Desenvolvidas (Secção 4 do Relatório)

### 4.1. Transformação T1: Extração e Limpeza de Especificações (`T1_extract_specs.ktr`)

A Transformação T1 é responsável pela leitura, validação, limpeza e enriquecimento das especificações mecânicas da gama desportiva BMW M.

#### Arquitetura do Fluxo
O pipeline processa 29 registos originais, isola 1 tuplo com dados omissos para quarentena e materializa 28 modelos enriquecidos em `data/processed/specs_limpas.csv`.

```mermaid
flowchart LR
    A["Ler specs CSV"] --> B["Limpar Strings"]
    B --> C["Extrair versao via Regex"]
    C --> D["Tratar nulos"]
    D --> E{"Validar peso"}
    E -- "Inválidos" --> REJ["Rejeitados (Quarentena)"]
    E -- "Válidos" --> F["Extrair prefixo modelo"]
    F --> G["Ordenar & Deduplicar"]
    G --> H["Add constants (1000)"]
    H --> I["Calculator (Métricas)"]
    LOOKUP["series_lookup.csv"] --> J["Mapear series & body_type"]
    I --> J
    J --> K["Exportar specs_limpas CSV"]
```

#### Fragmentos Técnicos e Regras de Negócio de T1

1. **Normalização de Strings (`Limpar Strings` — `String operations`):**
   - **Campos:** `make`, `model`
   - **Operações:** `Trim type = both`, `Lower/Upper = upper` para o campo `make`; `Trim type = both` para `model`.

2. **Expressões Regulares (`Regex evaluation`):**
   - **Extração de Edições/Versões de Alto Rendimento (`Extrair versao via Regex`):**
     - Campo avaliado: `model` $\rightarrow$ Campo de captura criado: `versao`
     ```regex
     .*?\b(Competition|CSL|GTS|CS|Touring)\b.*
     ```
   - **Normalização da Chave de Série (`Extrair prefixo modelo`):**
     - Campo avaliado: `model` $\rightarrow$ Campo de captura criado: `model_prefix` (ex.: `"M2"`, `"M3"`, `"M4"`, `"M5"`, `"M6"`, `"M8"`)
     ```regex
     ^(M\d)\b.*
     ```

3. **Imputação Semântica de Nulos (`Tratar nulos` — `If field value is null`):**
   - **Campo:** `versao`
   - **Valor de substituição:** `'Base'` (separa a extração léxica da regra de negócio, prevenindo nulos em dimensões relacionais).

4. **Controlo de Qualidade e Isolamento de Rejeitados (`Validar peso` — `Filter rows`):**
   - **Condição booleana:** `weight_kg IS NOT NULL`
   - **Saída TRUE (Válidos):** Segue para `Extrair prefixo modelo` (fluxo analítico principal).
   - **Saída FALSE (Inválidos):** Desvia para `Rejeitados` (`data/staging/rejeitados_specs.csv`) como *Dead-Letter Queue* (isolou o modelo `M3 E92 GTS`).

5. **Fórmulas de Engenharia Automóvel (`Calculator` via constante `const_1000 = 1000`):**
   - `peso_ton = weight_kg / const_1000` (Cálculo `A / B`)
   - `litros = engine_cc / const_1000` (Cálculo `A / B`)
   - `hp_por_tonelada = engine_hp / peso_ton` (Cálculo `A / B`)
   - `hp_por_litro = engine_hp / litros` (Cálculo `A / B`)

6. **Cruzamento em Memória (`Mapear series e body_type` — `Stream lookup`):**
   - **Chave de junção:** `model_prefix` = `model_prefix` (cruzamento com `data/raw/series_lookup.csv`)
   - **Campos recuperados:** `series` (ex.: `"Série 3 M"`), `body_type` (ex.: `"Sedan/Touring"`, `"Coupé"`).

#### Artefactos Visuais de T1 (em `prints/` e `docs/diagramas/`)
- `T1_pipeline_completo.png` — Canvas panorâmico no Spoon com vistos verdes em todos os 12 steps.
- `T1_metricas_execucao.png` — Painel Step Metrics (29 lidos $\rightarrow$ 1 rejeitado $\rightarrow$ 28 exportados).
- `T1_preview_dados_finais.png` — Grelha tabular do resultado limpo (`specs_limpas.csv`).
- `T1_config_string_operations.png` — Diálogo do step *Limpar Strings*.
- `T1_config_regex_versao.png` — Diálogo do step *Extrair versao via Regex*.
- `T1_config_tratar_nulos.png` — Diálogo do step *Tratar nulos*.
- `T1_config_filter_peso.png` — Diálogo do step *Validar peso*.
- `T1_config_regex_prefixo.png` — Diálogo do step *Extrair prefixo modelo*.
- `T1_config_calculator_metricas.png` — Diálogo do step *Calculator*.
- `T1_config_stream_lookup.png` — Diálogo do step *Mapear series e body_type*.

---

### 4.2. Transformação T2: Ingestão de Dados de Recalls via API NHTSA (`T2_extract_nhtsa.ktr`)

A Transformação T2 é responsável pela extração dinâmica de métricas de fiabilidade e segurança rodoviária através do consumo da API pública RESTful da **NHTSA** (*National Highway Traffic Safety Administration*).

#### Arquitetura do Pipeline ETL
O fluxo é composto por 9 etapas sequenciais:

```mermaid
flowchart LR
    A["Ler specs_limpas CSV"] --> B["Selecionar marca modelo ano"]
    B --> C["Ordenar por modelo e ano"]
    C --> D["Deduplicar para API"]
    D --> E["Construir URL NHTSA (JS)"]
    E --> F["Chamar API Recalls (REST GET)"]
    F --> G["Extrair recalls JSON (JSONPath)"]
    G --> H["Selecionar campos recalls"]
    H --> I["Exportar recalls CSV"]
```

1. **Leitura e Seleção:** Ingestão de `specs_limpas.csv` e isolamento dos atributos-chave de pesquisa (`make`, `model_prefix` renomeado para `model`, `year`).
2. **Ordenação e Deduplicação:** Ordenação composta (`Sort rows`) seguida de remoção de redundâncias (`Unique rows`), assegurando que apenas combinações estritamente únicas de gama/ano realizam pedidos HTTP, mitigando latência e respeitando *rate limits*.
3. **Construção Dinâmica do Endpoint:** Script JavaScript encarregue de codificar parâmetros e estruturar o URL REST.
4. **Consumo da API Externa:** Invocação HTTP GET via `REST client`.
5. **Parsing e Extração JSON:** Desserialização do payload JSON através de JSONPath (`$.Count`) no step `JSON input`.
6. **Projeção e Persistência:** Filtragem das variáveis auxiliares (`Select values`) e exportação do artefacto limpo `data/processed/nhtsa_recalls.csv`.

#### Fragmentos Técnicos e Regras de Negócio de T2

1. **Construção Dinâmica de URL (`Construir URL NHTSA` — `Modified Java Script Value`):**
   ```javascript
   var url_recalls = "https://api.nhtsa.gov/recalls/recallsByVehicle?make=" 
                     + encodeURIComponent(make) 
                     + "&model=" 
                     + encodeURIComponent(model) 
                     + "&modelYear=" 
                     + year;
   ```

2. **Invocação de Web Service REST (`Chamar API Recalls` — `REST client`):**
   - **Método HTTP:** `GET`
   - **Campo do URL:** `url_recalls`
   - **Campo de resposta:** `resposta_json`

3. **Parsing e Desserialização JSON (`Extrair recalls JSON` — `JSON input`):**
   - **Fonte:** Campo de stream `resposta_json`
   - **Expressão JSONPath:** `$.Count`
   - **Campo extraído:** `nhtsa_recalls_count` (`Integer`)

#### Artefactos Visuais de T2 (em `prints/` e `docs/diagramas/`)
- `T2_pipeline_completo.png` — Canvas do pipeline com os 9 steps e status de execução com sucesso.
- `T2_metricas_execucao.png` — Métricas de execução (28 tuplos processados, 0 erros, tempo de resposta ~5.3s).
- `T2_config_javascript_url.png` — Configuração do step de concatenação e encoding do URL.
- `T2_config_rest_client.png` — Configuração da chamada REST (HTTP GET dinâmico).
- `T2_config_json_input.png` — Configuração do separador Fields com a expressão JSONPath `$.Count`.
- `T2_preview_dados_finais.png` — Grelha de validação dos dados finais com os recalls extraídos (`nhtsa_recalls.csv`).

> [!NOTE] **Nota Metodológica sobre a Cobertura da NHTSA**
> A base da NHTSA reflete exclusivamente o mercado rodoviário dos EUA. Modelos ou variantes exclusivos do mercado europeu (como o **M3 E46 CSL** e a carrinha **M3 G81 Touring**) não foram comercializados nos EUA, justificando a inexistência de registos locais e a consequente imputação semântica de `0` recalls em T3.

---

### 4.3. Transformação T3: Consolidação e Métricas Finais (`T3_consolidate_metrics.ktr`)

A Transformação T3 consolida os dados de especificações técnicas (`specs_limpas.csv`) com o histórico de fiabilidade e segurança rodoviária da NHTSA (`nhtsa_recalls.csv`). Esta etapa calcula indicadores analíticos combinados e gera o artefacto tabular final do projeto.

#### Arquitetura do Pipeline ETL
O fluxo é composto por 10 steps organizados em 2 ramos concorrentes e um tronco de consolidação:

```mermaid
flowchart TD
    subgraph RAMO_SPECS["Ramo Superior: Especificações"]
        A1["Ler specs_limpas CSV\n(Lazy conversion = N)"] --> A2["Ordenar specs\n(make, model_prefix, year)"]
    end

    subgraph RAMO_RECALLS["Ramo Inferior: Recalls NHTSA"]
        B1["Ler nhtsa_recalls CSV"] --> B2["Ordenar recalls\n(make, model, year)"]
    end

    A2 --> M["Juntar specs e recalls\n(Merge join: LEFT OUTER)"]
    B2 --> M

    M --> C["Limpar campos duplicados\n(Remover make_1, model_1, year_1)"]
    C --> D["Tratar recalls nulos\n(null -> 0)"]
    D --> E["Add const 100\n(const_100 = 100)"]
    E --> F["Calcular metricas fiabilidade\n(Calculator)"]
    F --> G["Exportar dataset consolidado CSV\n(bmw_m_performance_fiabilidade.csv)"]
```

1. **Ramo Superior (Especificações):** Ingestão de `specs_limpas.csv` (`CSV file input` com *Lazy Conversion* desativada) seguido de ordenação multi-chave (`Sort rows` por `make ASC`, `model_prefix ASC`, `year ASC`).
2. **Ramo Inferior (Recalls NHTSA):** Ingestão de `nhtsa_recalls.csv` seguido de ordenação multi-chave (`Sort rows` por `make ASC`, `model ASC`, `year ASC`).
3. **Junção Ordenada (`Merge join`):** Realização de um `LEFT OUTER JOIN` garantindo a preservação integral dos registos mecânicos, utilizando a chave composta `(make, model_prefix, year) = (make, model, year)`.
4. **Limpeza de Metadados (`Select values`):** Remoção das colunas redundantes geradas na junção (`make_1`, `model_1`, `year_1`).
5. **Imputação de Valores Ausentes (`If field value is null`):** Substituição de valores nulos em `nhtsa_recalls_count` por `0`, refletindo ausência de registo de campanhas de recall.
6. **Cálculo de Indicadores de Fiabilidade:**
   - Injeção de constante (`Add constants`): `const_100 = 100` (Number).
   - Cálculos analíticos (`Calculator`):
     - Rácio base de recalls por unidade de potência: `recalls_por_hp = nhtsa_recalls_count / engine_hp`
     - Métrica normalizada de fiabilidade: `recalls_por_100hp = recalls_por_hp * const_100`
7. **Persistência Final (`Text file output`):** Exportação do dataset analítico consolidado para `data/processed/bmw_m_performance_fiabilidade.csv` (28 registos, formato delimitado por vírgula com cabeçalho UTF-8).

#### Fragmentos Técnicos e Regras de Negócio de T3

1. **Configuração da Junção Ordenada (`Merge join`):**
   - **Tipo de Junção:** `LEFT OUTER`
   - **Stream 1 (`Ordenar specs`):** `make`, `model_prefix`, `year`
   - **Stream 2 (`Ordenar recalls`):** `make`, `model`, `year`

2. **Limpeza de Metadados e Sufixos (`Select values`):**
   - **Campos removidos:** `make_1`, `model_1`, `year_1` (redundâncias geradas pelo step de merge).

3. **Imputação Semântica de Nulos (`If field value is null`):**
   - **Campo:** `nhtsa_recalls_count`
   - **Valor de substituição:** `0` (interpretação de inexistência de campanhas de recall).

4. **Fórmulas de Engenharia e Fiabilidade (`Calculator` com `const_100 = 100`):**
   - `recalls_por_hp = nhtsa_recalls_count / engine_hp` (Cálculo `A / B`)
   - `recalls_por_100hp = recalls_por_hp * const_100` (Cálculo `A * B`)

#### Artefactos Visuais de T3 (em `prints/` e `docs/diagramas/`)
- `T3_pipeline_completo.png` — Canvas global no Spoon com os dois ramos concorrentes, a junção central e visto verde em todos os 10 steps.
- `T3_metricas_execucao.png` — Painel Step Metrics comprovando a leitura das duas fontes, junção de 28 tuplos e gravação sem erros (~0.5s).
- `T3_config_merge_join.png` — Configuração do Merge Join exibindo a modalidade LEFT OUTER JOIN e as chaves de correspondência de ambos os passos.
- `T3_config_select_values.png` — Configuração da remoção das colunas duplicadas da stream da direita (`make_1`, `model_1`, `year_1`).
- `T3_config_calculator_metricas.png` — Configuração das operações de divisão e multiplicação no Calculator.
- `T3_preview_dados_finais.png` — Pré-visualização da grelha de dados consolidada com todos os atributos mecânicos, identificadores de série e rácios calculados.

---

### 4.4. Transformação T4: Carga Relacional em PostgreSQL (`T4_load_postgres.ktr`)

A Transformação T4 concretiza a **Fase 3 (Carregamento e Persistência)**, carregando os dados limpos e consolidados de performance mecânica e fiabilidade rodoviária na base de dados relacional **PostgreSQL 18** (`carros_etl`, tabela `bmw_m_performance_fiabilidade`).

#### Arquitetura do Fluxo
O pipeline ingere o ficheiro consolidado `bmw_m_performance_fiabilidade.csv` de forma portável e persiste 28 tuplos na tabela `bmw_m_performance_fiabilidade` com taxa de erro nula (**`E=0`**):

```mermaid
flowchart LR
    A["Ler dataset consolidado CSV\n(CsvInput:\nbmw_m_performance_fiabilidade.csv)"] --> B["Carregar PostgreSQL\n(TableOutput:\nTruncate = Y, Batch = 1000)"]
    
    subgraph SGBD["PostgreSQL 18 (carros_etl)"]
        B -.-> TAB[("Tabela:\nbmw_m_performance_fiabilidade\n(28 registos, E=0)")]
    end

    classDef step fill:#eef6ff,stroke:#3366cc,stroke-width:1px;
    classDef db fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px;
    class A,B step;
    class TAB db;
```

#### Fragmentos Técnicos e Decisões de T4

1. **Portabilidade e Higienização de Strings (`CsvInput`):**
   - **Caminho Relativo:** `${Internal.Entry.Current.Directory}/../../data/processed/bmw_m_performance_fiabilidade.csv`.
   - **Formatação de Atributos:** `<length>-1</length>`, `<trim_type>both</trim_type>` e `<currency/>` para todos os atributos, prevenindo padding e símbolos residuais.
   - **Tipificação Numérica:** Campos inteiros lidos como `Integer` e rácios decimais com precisão estrita e ponto decimal `.`.

2. **Esquema Relacional DDL (`sql/01_schema.sql`):**
   - Estrutura física composta por 20 colunas (chave primária `id SERIAL`, 18 atributos analíticos mapeados e carimbo de auditoria `loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`).
   - Restrição de integridade `CONSTRAINT uq_model_year UNIQUE (model, year)` impedindo duplicações semânticas.
   - **Preservação de Valores Ausentes:** O preço de comercialização do BMW M5 E34 é mantido estritamente como `price_usd = NULL` (coluna sem restrição `NOT NULL`), respeitando a fidelidade de dados e evitando imputações espúrias.

3. **Idempotência Determinística via TRUNCATE (`TableOutput`):**
   - Ativação do parâmetro `<truncate>Y</truncate>` (Truncate table), que esvazia atomicamente a tabela de destino antes da inserção em lote (`commit = 1000`).
   - Articulação direta com a constraint `uq_model_year (model, year)`, garantindo que reexecuções parciais ou repetidas da pipeline ETL decorrem sem falhas por colisão de chaves únicas ou inconsistências de dados residuais.

4. **Mapeamento Explícito de 18 Atributos:**
   - Inserção estrita dos 18 atributos analíticos, delegando no PostgreSQL a atribuição do `id` sequencial e do timestamp `loaded_at`.

#### Artefactos Visuais de T4 (em `prints/` e `docs/diagramas/`)
- `T4_pipeline_completo.png` — Canvas panorâmico no Spoon com os passos *Ler dataset consolidado CSV* e *Carregar PostgreSQL* com visto verde.
- `T4_config_csv_input.png` — Diálogo do step `CsvInput` evidenciando o caminho relativo, tipagem dos 18 campos e ausência de padding.
- `T4_config_table_output.png` — Diálogo do step `TableOutput` com a opção *Truncate table* ativada, batch commit de 1000 e mapeamento explícito dos 18 campos.
- `T4_ddl_create_table.png` — Execução do script DDL de criação da tabela no pgAdmin / editor SQL.
- `T4_metricas_execucao.png` — Painel Step Metrics comprovando 28 linhas lidas e 28 linhas inseridas com 0 erros (`E=0`).
- `T4_dados_postgres.png` — Visualização dos 28 registos carregados na tabela PostgreSQL via pgAdmin (incluindo `price_usd = NULL` no M5 E34).

---

### 4.5. Transformação T5: Exportações Analíticas Heterogéneas (`T5_export_reports.ktr`)

A Transformação T5 concretiza a **Fase 4 (Exportação e Disseminação)**, extraindo os dados relacionais do PostgreSQL e materializando relatórios analíticos em dois formatos heterogéneos: um catálogo integral em formato JSON e um resumo executivo com agregações por série em formato XML.

#### Arquitetura do Fluxo
O pipeline consome a tabela `bmw_m_performance_fiabilidade` e duplica o stream em memória (**Copy data to next steps**) para dois ramos concorrentes sem leituras redundantes à base de dados:

```mermaid
flowchart TD
    DB[("PostgreSQL 18\n(carros_etl.\nbmw_m_performance_fiabilidade)")] --> A["Ler PostgreSQL\n(TableInput: ORDER BY series, year\nDistribute = N / Copy Stream)"]
    
    %% Ramo A - JSON
    A -->|"Cópia 1 (28 tuplos)"| B["Exportar Catalogo JSON\n(JsonOutput: catalogo_bmw_m\nwrite to file, 1 bloco)"]
    B --> OUT_JSON[("data/output/\nbmw_m_catalogo_completo.json\n(28 modelos, 18 atributos)")]
    
    %% Ramo B - XML
    A -->|"Cópia 2 (28 tuplos)"| C["Agregar por Serie\n(GroupBy: group by series\n6 métricas agregadas)"]
    C -->|"6 séries agregadas"| D["Exportar Resumo XML\n(XMLOutput: relatorio_series_bmw_m\nrepeat: serie_analise)"]
    D --> OUT_XML[("data/output/\nbmw_m_resumo_series.xml\n(6 séries analisadas)")]

    classDef step fill:#eef6ff,stroke:#3366cc,stroke-width:1px;
    classDef db fill:#e8f5e9,stroke:#2e7d32,stroke-width:1px;
    classDef file fill:#fff3e0,stroke:#e65100,stroke-width:1px;
    class A,B,C,D step;
    class DB db;
    class OUT_JSON,OUT_XML file;
```

#### Fragmentos Técnicos e Decisões de T5

1. **Duplicação Eficiente de Stream (`TableInput`):**
   - Configuração de `<distribute>N</distribute>` (**Copy data to next steps**), duplicando deterministicamente os 28 tuplos para alimentar ambos os ramos em paralelo (56 linhas emitidas), eliminando o overhead de queries concorrentes.
   - Ordenação nativa `ORDER BY series ASC, year ASC` que alimenta diretamente o step `GroupBy` sem necessitar de ordenação intermédia em memória.

2. **Ramo A — Catálogo Integral JSON (`JsonOutput`):**
   - Operação `writetofile` com bloco `catalogo_bmw_m` e `nrRowsInBloc = 0` (todos os 28 modelos num único array JSON).
   - Ficheiro gerado: `data/output/bmw_m_catalogo_completo.json` (codificação UTF-8, 18 atributos mapeados e preservação fiel de `price_usd: null` no M5 E34).

3. **Ramo B — Agregação Dimensional no GroupBy (`GroupBy`):**
   - Agrupamento pela chave dimensional `series` (reduzindo os 28 modelos a 6 famílias M: Séries 2, 3, 4, 5, 6 e 8).
   - Computação de 6 métricas analíticas:
     - `total_modelos` (`COUNT_ALL`)
     - `media_hp` (`AVERAGE`)
     - `media_hp_ton` (`AVERAGE`)
     - `media_hp_litro` (`AVERAGE`)
     - `total_recalls_serie` (`SUM`)
     - `media_recalls_100hp` (`AVERAGE`)

4. **Resumo Executivo em XML (`XMLOutput`):**
   - Ficheiro gerado: `data/output/bmw_m_resumo_series.xml` (codificação UTF-8).
   - Estrutura hierárquica com elemento raiz `<relatorio_series_bmw_m>` e elementos repetidores `<serie_analise>`.
   - Formatação estrita com separador decimal `.` e precisão explícita de duas casas (`#.##`) e quatro casas (`#.####` em `media_recalls_100hp`).

#### Artefactos Visuais de T5 (em `prints/` e `docs/diagramas/`)
- `T5_pipeline_completo.png` — Canvas panorâmico no Spoon evidenciando a duplicação em dois ramos paralelos e visto verde em todos os steps.
- `T5_config_groupby.png` — Diálogo do step `GroupBy` comprovando o agrupamento por `series` e as 6 fórmulas de agregação.
- `T5_metricas_execucao.png` — Painel Step Metrics comprovando 28 linhas lidas do PostgreSQL, 56 linhas emitidas, 28 registos no JSON e 6 séries no XML com taxa de erro nula (`E=0`).
- `T5_preview_json_xml.png` — Pré-visualização dos artefactos gerados em `data/output/`: catálogo JSON formatado e resumo executivo em XML.

---

### 4.6. Job de Orquestração Global (`J_main.kjb`)

O Job global **`J_main.kjb`** orquestra e automatiza a execução de ponta a ponta de todo o pipeline de ETL desenvolvido no Pentaho Kettle, assegurando a integridade do encadeamento de dados, controlo centralizado de falhas (*fail-fast*) e validação de sucesso.

#### Arquitetura do Fluxo
O pipeline coordena sequencialmente as 5 transformações, com transições condicionais de sucesso (linhas verdes) e desvio de falha para um nó comum de abortamento (linhas vermelhas):

```mermaid
flowchart TD
    START([START\nInício do Pipeline]) -->|Sucesso| T1["T1 - Especificações\n(T1_extract_specs.ktr)"]
    T1 -->|Sucesso| T2["T2 - Recalls NHTSA\n(T2_extract_nhtsa.ktr)"]
    T2 -->|Sucesso| T3["T3 - Consolidação Analítica\n(T3_consolidate_metrics.ktr)"]
    T3 -->|Sucesso| T4["T4 - Carga PostgreSQL\n(T4_load_postgres.ktr)"]
    T4 -->|Sucesso| T5["T5 - Exportação JSON e XML\n(T5_export_reports.ktr)"]
    T5 -->|Sucesso| SUC([Sucesso ETL\nConclusão com Sucesso])

    %% Hops de Falha
    T1 -.->|Falha| ABORT(["Abortar por Erro\n(Job Entry: ABORT\nInterrupção Imediata)"])
    T2 -.->|Falha| ABORT
    T3 -.->|Falha| ABORT
    T4 -.->|Falha| ABORT
    T5 -.->|Falha| ABORT

    classDef start fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef trans fill:#eef6ff,stroke:#007bff,stroke-width:1.5px;
    classDef success fill:#c3e6cb,stroke:#155724,stroke-width:2px;
    classDef abort fill:#f8d7da,stroke:#721c24,stroke-width:2px;
    class START start;
    class T1,T2,T3,T4,T5 trans;
    class SUC success;
    class ABORT abort;
```

#### Destaques Arquiteturais de J_main

1. **Pipeline Sequencial e Encadeamento de Dependências:**
   - Respeita o ciclo de vida rigoroso dos dados: Limpeza $\rightarrow$ Extração de Recalls $\rightarrow$ Fusão e Métricas $\rightarrow$ Carga Relacional $\rightarrow$ Exportação Analítica.
2. **Mecanismo Fail-Fast com Tratamento Centralizado de Exceções:**
   - Em caso de falha em qualquer uma das transformações (ex.: erro de rede no step REST de T2, erro de conectividade em T4), o fluxo não prossegue para os passos seguintes e converge imediatamente para o step `Abortar por Erro` (`ABORT`).
3. **Portabilidade Universal:**
   - Todos os steps `TRANS` referenciam as transformações através do caminho relativo portável `${Internal.Entry.Current.Directory}/../transformations/<ficheiro>.ktr`, garantindo funcionamento transparente em qualquer máquina ou ambiente.
4. **Métricas de Execução em Kitchen / Spoon:**
   - Execução integral do pipeline testada em ~10 segundos (sendo ~8.8s dedicados aos 28 pedidos REST HTTP à API da NHTSA).
   - Zero erros em todos os passos (`Errors=0`, `result=[true]`).

#### Artefactos Visuais de J_main (em `prints/` e `docs/diagramas/`)
- `J_main_pipeline_completo.png` — Canvas panorâmico no Spoon com o fluxo global do job (START $\rightarrow$ T1 a T5 $\rightarrow$ Sucesso ETL e ligações de erro para Abortar por Erro) e visto verde de execução.
- `J_main_metricas_execucao.png` — Painel Job Execution Results / Logging comprovando a execução sequencial sem erros e duração global de ~10s.
- `J_main_config_trans.png` — Diálogo de configuração de um step de transformação ilustrando o caminho relativo dinâmico `${Internal.Entry.Current.Directory}/...`.

---

## 5. Estado do Projeto

- [x] **T1 (`T1_extract_specs.ktr`):** Extração, limpeza e métricas mecânicas (Concluída).
- [x] **T2 (`T2_extract_nhtsa.ktr`):** Ingestão de recalls via API NHTSA (Concluída).
- [x] **T3 (`T3_consolidate_metrics.ktr`):** Junção analítica e cálculo de fiabilidade (Concluída).
- [x] **T4 (`T4_load_postgres.ktr`):** Carga relacional idempotente em PostgreSQL (Concluída).
- [x] **T5 (`T5_export_reports.ktr`):** Exportação analítica multiformato em JSON e XML (Concluída).
- [x] **J_main (`J_main.kjb`):** Orquestração sequencial completa do pipeline com controlo fail-fast de erros e caminhos relativos portáteis (Concluída).



