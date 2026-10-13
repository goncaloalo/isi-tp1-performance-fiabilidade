# Inventário de Diagramas e Capturas do Spoon (Pentaho PDI)

Este diretório armazena todos os diagramas de arquitetura e capturas de ecrã (*prints*) das transformações e jobs desenvolvidos no Pentaho Kettle (Spoon), a incorporar no **Relatório Final** (Secções 4 e 5) e na apresentação da defesa individual.

---

## 1. Convenção de Nomenclatura e Formato

- **Formato:** `.png` (alta fidelidade e nitidez de texto).
- **Resolução recomendada:** Mínimo de 1920x1080 (ou captura em janela maximizada com texto legível).
- **Padrão de nome:** `<etapa>_<descricao_do_print>.png` (ex.: `01_T1_canvas_completo.png`).

---

## 2. Lista de Capturas Obrigatórias por Módulo

### 2.1. Transformação T1: `T1_extract_specs.ktr` (Especificações Automóveis)
Estes prints comprovam as decisões técnicas, a validação de dados e as expressões regulares explicadas em [`docs/decisoes_etl.md`](file:///C:/Users/gfcco/OneDrive/Documentos/isi-tp1-performance-fiabilidade/docs/decisoes_etl.md):

| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `01_T1_canvas_completo.png` | Canvas Global | Visão panorâmica de todos os steps e hops da transformação, incluindo o desvio para rejeitados e o step de constantes. |
| `T1_step01_csv_input.png` | Dialog: *Ler specs CSV* | Janela de configuração com o delimitador `,`, encoding `UTF-8` e a grelha de campos e tipos (`Number` em `zero_to_sixty_mph`). |
| `T1_step02_string_operations.png` | Dialog: *Limpar strings* | Janela de operações sobre strings (`trim both` e `upper` em `make`; `trim both` em `model`). |
| `T1_step03_regex_versao.png` | Dialog: *Extrair versao via Regex* | Janela com a expressão regular `.*?\b(Competition\|CSL\|GTS\|CS\|Touring)\b.*` e o campo de captura `versao`. |
| `T1_step04_null_if.png` | Dialog: *Tratar nulos* | Janela do step `If field value is null` configurando a imputação de `'Base'` no campo `versao`. |
| `T1_step05_filter_peso.png` | Dialog: *Validar peso* | Condição `weight_kg IS NOT NULL` e o direcionamento dos registos inválidos para o step de rejeitados. |
| `T1_step06_regex_prefixo.png` | Dialog: *Extrair prefixo modelo* | Expressão regular `^(M\d)\b.*` para isolar o prefixo do modelo para o lookup. |
| `T1_step07_sort_unique.png` | Dialog: *Remover duplicados* | Encadeamento de `Sort rows` com `Unique rows` baseado na chave composta `make, model, year`. |
| `T1_step08_add_constants.png` | Dialog: *Add constants* | Configuração do step `Add constants` com o campo `const_1000` (Type: `Number`, Value: `1000`) para viabilizar a divisão no `Calculator`. |
| `T1_step09_calculator.png` | Dialog: *Calcular métricas* | Grelha de fórmulas do `Calculator` com os cálculos encadeados de `peso_ton`, `litros`, `hp_por_tonelada` e `hp_por_litro` consumindo `const_1000`. |
| `T1_step10_stream_lookup.png` | Dialog: *Mapear séries* | Junção por `model_prefix` com `series_lookup.csv` e campos recuperados (`series`, `body_type`). |
| `T1_step11_text_output.png` | Dialog: *Exportar staging* | Janela de configuração do destino final `data/staging/specs_limpas.csv`. |
| `T1_execucao_metrics.png` | Execution Results | Painel inferior após execução no Spoon: *Step Metrics* (linhas lidas, escritas e rejeitadas) e separador *Preview data*. |

---

### 2.2. Transformação T2: `T2_extract_nhtsa.ktr` (API REST Recalls & Complaints)
| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `10_T2_canvas_completo.png` | Canvas Global | Fluxo completo de consulta à API externa da NHTSA (recalls e queixas). |
| `11_T2_step_rest_client.png` | Dialog: *REST Client* | Configuração do endpoint HTTP/REST, método GET e tratamento de códigos de resposta. |
| `12_T2_step_json_input.png` | Dialog: *JSON input* | Mapeamento dos campos e expressões *JSONPath* para contagem de problemas. |

---

### 2.3. Transformação T3: `T3_transform_merge.ktr` (Fusão e Agregações)
| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `13_T3_canvas_completo.png` | Canvas Global | Cruzamento dos fluxos de performance e fiabilidade com cálculo de rankings. |
| `14_T3_step_merge_join.png` | Dialog: *Merge Join* | Janela do operador de junção (ordenado por marca, modelo e ano). |
| `15_T3_step_group_by.png` | Dialog: *Group by* | Configuração de agregações por série/geração (médias e somatórios). |

---

### 2.4. Transformação T4: `T4_load_postgres.ktr` (Carga Relacional)
| Ficheiro Alvo | Elemento no Spoon | Descrição do Conteúdo a Capturar |
| :--- | :--- | :--- |
| `16_T4_canvas_completo.png` | Canvas Global | Carga nas tabelas `dim_modelo`, `fact_performance` e `fact_fiabilidade`. |
| `17_T4_step_table_output.png` | Dialog: *Insert / Update* | Mapeamento de chaves e campos para a base de dados PostgreSQL. |

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
