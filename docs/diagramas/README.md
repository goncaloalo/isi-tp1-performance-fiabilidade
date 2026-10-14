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
