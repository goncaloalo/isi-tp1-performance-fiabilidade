# Inventário de Diagramas e Capturas do Spoon (Pentaho PDI)

Este diretório armazena todos os diagramas de arquitetura e capturas de ecrã (*prints*) das transformações e jobs desenvolvidos no Pentaho Kettle (Spoon), a incorporar no **Relatório Final** (Secções 4 e 5) e na apresentação da defesa individual.

---

## 1. Convenção de Nomenclatura e Formato

- **Formato:** `.png` (alta fidelidade e nitidez de texto).
- **Resolução recomendada:** Mínimo de 1920x1080 (ou captura em janela maximizada com texto legível).
- **Padrão de nome:** `<etapa>_<descricao_do_print>.png` (ex.: `01_T1_canvas_completo.png`).

---

## 2. Lista de Capturas Consolidadas por Módulo (Secção 4 do Relatório)

### 4.1. Transformação T1: `T1_extract_specs.ktr` (Especificações Automóveis)
Artefactos gráficos consolidados e padronizados para integração na **Secção 4.1 do Relatório**:

| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Integrar no Relatório |
| :--- | :--- | :--- |
| `T1_pipeline_completo.png` | Canvas Global | Visão panorâmica de todo o fluxo sequencial com vistos verdes em todos os steps e desvio de quarentena. |
| `T1_metricas_execucao.png` | Execution Results | Painel *Step Metrics* comprovando 29 registos lidos, 1 rejeitado no filtro de peso e 28 exportados com 0 erros. |
| `T1_preview_dados_finais.png` | Preview Data | Grelha de dados finais com os 28 modelos, colunas calculadas e metadados de séries e carroçarias preenchidos. |
| `T1_config_string_operations.png` | Dialog: *Limpar Strings* | Operações sintáticas (`trim both` e `upper` em `make`; `trim both` em `model`). |
| `T1_config_regex_versao.png` | Dialog: *Extrair versao via Regex* | Expressão regular `.*?\b(Competition\|CSL\|GTS\|CS\|Touring)\b.*` e campo de captura `versao`. |
| `T1_config_tratar_nulos.png` | Dialog: *Tratar nulos* | Imputação semântica de `'Base'` no campo `versao` quando nulo. |
| `T1_config_filter_peso.png` | Dialog: *Validar peso* | Condição `weight_kg IS NOT NULL` com desvio dos registos inválidos para quarentena (`Rejeitados`). |
| `T1_config_regex_prefixo.png` | Dialog: *Extrair prefixo modelo* | Expressão regular `^(M\d)\b.*` para isolar a chave de junção `model_prefix`. |
| `T1_config_calculator_metricas.png` | Dialog: *Calculator* | Cálculos encadeados de `peso_ton`, `litros`, `hp_por_tonelada` e `hp_por_litro` via `const_1000`. |
| `T1_config_stream_lookup.png` | Dialog: *Mapear series e body_type* | Junção por `model_prefix` com `series_lookup.csv` trazendo `series` e `body_type`. |

---

### 4.2. Transformação T2: Ingestão de Dados de Recalls (API NHTSA)

A Transformação T2 é responsável pela extração dinâmica de métricas de segurança rodoviária através do consumo da API pública da NHTSA (*National Highway Traffic Safety Administration*). O objetivo desta etapa consiste em obter o histórico oficial de campanhas de recall por modelo e ano de fabrico, enriquecendo o dataset de especificações mecânicas.

#### 1. Arquitetura do Pipeline ETL
O fluxo é composto por 9 etapas sequenciais:
1. **Leitura e Seleção:** Ingestão de `specs_limpas.csv` e isolamento dos atributos-chave de pesquisa (`make`, `model_prefix` renomeado para `model`, `year`).
2. **Ordenação e Deduplicação:** Ordenação composta (`Sort rows`) seguida de remoção de redundâncias (`Unique rows`), assegurando que apenas combinações únicas de veículo/ano realizam pedidos HTTP, mitigando sobrecarga na rede e latência desnecessária.
3. **Construção Dinâmica do Endpoint:** Script JavaScript encarregue de codificar parâmetros e estruturar o URL REST.
4. **Consumo da API Externa:** Invocação HTTP GET via `REST client`.
5. **Parsing e Extração JSON:** Desserialização do payload JSON através de JSONPath (`$.Count`) no step `JSON input`.
6. **Projeção e Persistência:** Filtragem das variáveis auxiliares (`Select values`) e exportação do artefacto limpo `nhtsa_recalls.csv`.

#### 2. Mapeamento de Artefactos de Imagem (`prints/` e `docs/diagramas/`)

| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Integrar no Relatório |
| :--- | :--- | :--- |
| `T2_pipeline_completo.png` | Canvas Global | Visão geral do pipeline com os 9 steps e status de execução com sucesso. |
| `T2_metricas_execucao.png` | Execution Results | Métricas de execução (28 tuplos processados, 0 erros, ~5.3s). |
| `T2_config_javascript_url.png` | Dialog: *Construir URL NHTSA* | Configuração do step de concatenação e encoding do URL via JavaScript. |
| `T2_config_rest_client.png` | Dialog: *Chamar API Recalls* | Configuração da chamada REST (HTTP GET dinâmico). |
| `T2_config_json_input.png` | Dialog: *Extrair recalls JSON* | Configuração do separador Fields com a expressão JSONPath `$.Count`. |
| `T2_preview_dados_finais.png` | Preview Data | Grelha de validação dos dados finais com os recalls extraídos (`nhtsa_recalls.csv`). |

#### 3. Excertos Técnicos de Configuração e Código

- **Script JavaScript de Construção do URL (`Construir URL NHTSA`):**
```javascript
var url_recalls = "https://api.nhtsa.gov/recalls/recallsByVehicle?make=" 
                  + encodeURIComponent(make) 
                  + "&model=" 
                  + encodeURIComponent(model) 
                  + "&modelYear=" 
                  + year;
```

---

### 4.3. Transformação T3: Consolidação e Métricas Finais (`T3_consolidate_metrics.ktr`)

A Transformação T3 consolida os dados de especificações técnicas (`specs_limpas.csv`) com o histórico de fiabilidade e segurança rodoviária da NHTSA (`nhtsa_recalls.csv`). Esta etapa calcula indicadores analíticos combinados e gera o artefacto tabular final do projeto.

#### 1. Arquitetura do Pipeline ETL
O fluxo é composto por 10 steps organizados em 2 ramos concorrentes e um tronco de consolidação:
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

#### 2. Mapeamento de Artefactos de Imagem (`prints/` e `docs/diagramas/`)

| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Integrar no Relatório |
| :--- | :--- | :--- |
| `T3_pipeline_completo.png` | Canvas Global | Canvas global no Spoon com os dois ramos concorrentes, a junção central e visto verde em todos os 10 steps. |
| `T3_metricas_execucao.png` | Execution Results | Painel Step Metrics comprovando a leitura das duas fontes, junção de 28 tuplos e gravação sem erros (~0.5s). |
| `T3_config_merge_join.png` | Dialog: *Juntar specs e recalls* | Configuração do Merge Join exibindo a modalidade LEFT OUTER JOIN e as chaves de correspondência de ambos os passos. |
| `T3_config_select_values.png` | Dialog: *Limpar campos duplicados* | Configuração da remoção das colunas duplicadas da stream da direita (`make_1`, `model_1`, `year_1`). |
| `T3_config_calculator_metricas.png` | Dialog: *Calcular metricas fiabilidade* | Configuração das operações de divisão e multiplicação no Calculator. |
| `T3_preview_dados_finais.png` | Preview Data | Pré-visualização da grelha de dados consolidada com todos os atributos mecânicos, identificadores de série e rácios calculados. |

#### 3. Excertos Técnicos de Configuração e Cálculos

- **Configuração da Junção Ordenada (`Merge join`):**
  - Tipo: `LEFT OUTER`
  - Chaves Stream 1 (`Ordenar specs`): `make`, `model_prefix`, `year`
  - Chaves Stream 2 (`Ordenar recalls`): `make`, `model`, `year`
- **Fórmulas Aritméticas de Fiabilidade (`Calculator` com `const_100 = 100`):**
  - `recalls_por_hp = nhtsa_recalls_count / engine_hp` (Divisão `A / B`)
  - `recalls_por_100hp = recalls_por_hp * const_100` (Multiplicação `A * B`)


---

### 4.4. Transformação T4: Carga Relacional em PostgreSQL (`T4_load_postgres.ktr`)

A Transformação T4 concretiza o carregamento da base de dados relacional em PostgreSQL (`carros_etl`), garantindo a integridade dos dados e a persistência do modelo físico final.

#### Mapeamento de Artefactos de Imagem (`prints/` e `docs/diagramas/`)

| Ficheiro Alvo | Elemento no Spoon / pgAdmin | Descrição do Conteúdo a Integrar no Relatório |
| :--- | :--- | :--- |
| `T4_pipeline_completo.png` | Canvas Global | Visão global do fluxo de carga com os passos *Ler dataset consolidado CSV* e *Carregar PostgreSQL* com visto verde de sucesso. |
| `T4_config_csv_input.png` | Dialog: *Ler dataset consolidado CSV* | Configuração do step `CsvInput` com caminho relativo `${Internal.Entry.Current.Directory}/../../data/processed/bmw_m_performance_fiabilidade.csv` e tipagem explícita. |
| `T4_config_table_output.png` | Dialog: *Carregar PostgreSQL* | Configuração do step `TableOutput` com opção *Truncate table* ativada, batch commit de 1000 e mapeamento explícito dos 18 campos. |
| `T4_ddl_create_table.png` | Editor SQL / pgAdmin | Execução do DDL (`sql/01_schema.sql`) no PostgreSQL com criação de chave primária, chave candidata única e tipos adequados. |
| `T4_metricas_execucao.png` | Execution Results | Painel *Step Metrics* comprovando a leitura de 28 registos no CSV e inserção de 28 linhas na tabela PostgreSQL com 0 erros (`E=0`). |
| `T4_dados_postgres.png` | Data Output / pgAdmin | Consulta SQL de validação (`SELECT * FROM bmw_m_performance_fiabilidade`) evidenciando os 28 registos persistidos com timestamp `loaded_at`. |

---

### 2.5. Transformação T5: `T5_exports.ktr` (Exportações Heterogéneas)
| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `18_T5_canvas_completo.png` | Canvas Global | Geração simultânea dos ficheiros finais nos formatos CSV e JSON (e XML/SQL). |

---

### 2.6. Job de Orquestração: `J_main.kjb`
| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `19_J_main_canvas_completo.png` | Canvas Global | Orquestração sequencial completa, caminhos de sucesso (verde) e de erro (vermelho). |
| `20_J_main_email_config.png` | Dialog: *Mail* | Definições de envio de notificação por email (SMTP, anexos e resumo de execução). |

---

### 2.7. Arquitetura e Base de Dados
| Ficheiro Alvo | Ferramenta | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `21_arquitetura_global_etl.png` | Diagrama (Mermaid/Draw.io) | Diagrama conceitual da arquitetura de 3 fases (Raw $\rightarrow$ Staging $\rightarrow$ PostgreSQL $\rightarrow$ Exports). |
| `22_modelo_dados_pgadmin.png` | pgAdmin / DBeaver | Diagrama ER do esquema relacional e consulta à vista `v_ranking`. |

---

## 3. Boas Práticas para a Captura no Spoon

1. **Limpeza Visual:** Fechar janelas ou painéis laterais redundantes antes de tirar o print.
2. **Destaque:** Assegurar que os nomes dos steps no canvas são perfeitamente legíveis (usar o zoom do Spoon a 100%).
3. **Execução Prévia:** Tirar prints dos canvas preferencialmente após uma execução bem-sucedida, exibindo os ícones de visto verde nos steps e as métricas na barra inferior.
