# Inventário de diagramas e capturas

Este diretório contém apenas capturas reais já existentes. O inventário foi confrontado com o sistema de ficheiros em 20/10/2026.

Algumas capturas antecedem as correções finais de T1, T2, T4 e T5. Não devem ser usadas como prova da nova configuração sem serem repetidas. A implementação atual encontra-se nos ficheiros `.ktr` e `.kjb`.

## T1 — especificações

| Ficheiro | Conteúdo |
|---|---|
| `T1_pipeline_completo.png` | Canvas do fluxo T1 anterior à validação final do lookup. |
| `T1_metricas_execucao.png` | Métricas de 29 lidos, 1 rejeitado e 28 válidos. |
| `T1_preview_dados_finais.png` | Pré-visualização de `specs_limpas.csv`. |
| `T1_config_string_operations.png` | Normalização de strings. |
| `T1_config_regex_versao.png` | Extração de versão. |
| `T1_config_tratar_nulos.png` | Preenchimento de `versao = Base`. |
| `T1_config_filter_peso.png` | Filtro original de peso; necessita nova captura com todas as regras. |
| `T1_config_regex_prefixo.png` | Extração de `model_prefix`. |
| `T1_config_calculator_metricas.png` | Cálculos mecânicos. |
| `T1_config_stream_lookup.png` | Lookup de série e carroçaria. |

## T2 — NHTSA

| Ficheiro | Conteúdo |
|---|---|
| `T2_pipeline_completo.png` | Canvas anterior à introdução da validação HTTP/JSON. |
| `T2_metricas_execucao.png` | Métricas de uma execução anterior. |
| `T2_preview_dados_finais.png` | Preview anterior aos campos de rastreabilidade. |
| `T2_config_javascript_url.png` | Construção do URL. |
| `T2_config_rest_client.png` | REST Client e campos de resposta/estado. |
| `T2_config_json_input.png` | Parser anterior; foi substituído pela validação JavaScript explícita. |

## T3 — consolidação

| Ficheiro | Conteúdo |
|---|---|
| `T3_pipeline_completo.png` | Canvas anterior à remoção de `Tratar recalls nulos`. |
| `T3_metricas_execucao.png` | Métricas de execução anterior. |
| `T3_preview_dados_finais.png` | Preview anterior à semântica de nulos revista. |
| `T3_config_merge_join.png` | Configuração do `LEFT OUTER JOIN`, ainda aplicável. |
| `T3_config_select_values.png` | Remoção de campos; deve ser atualizada para os metadados NHTSA. |
| `T3_config_calculator_metricas.png` | Fórmula de `recalls_por_100hp`. |

## T4 — PostgreSQL

| Ficheiro | Conteúdo |
|---|---|
| `T4_pipeline_completo.png` | Canvas anterior à substituição de `Table Output` por `Insert/Update`. |
| `T4_metricas_execucao.png` | Métricas de uma execução anterior. |
| `T4_config_csv_input.png` | Entrada CSV, ainda aplicável. |
| `T4_ddl_create_table.png` | Evidência de DDL anterior; o script atual tem restrições adicionais. |
| `T4_dados_postgres.png` | Consulta a dados carregados numa execução anterior. |

Não existe `T4_config_table_output.png`. O inventário anterior que o mencionava estava incorreto e a própria configuração deixou de usar `Table Output`.

## T5 — exportação

| Ficheiro | Conteúdo |
|---|---|
| `T5_pipeline_completo.png` | Canvas do fluxo; necessita nova captura após os campos auxiliares. |
| `T5_metricas_execucao.png` | Métricas de uma execução anterior. |
| `T5_config_groupby.png` | GroupBy anterior à correção de `media_hp` e cobertura NHTSA. |
| `T5_preview_json.png` | Preview dos artefactos anteriores à revisão. |

## Job

| Ficheiro | Conteúdo |
|---|---|
| `J_main_pipeline_completo.png` | Sequência T1–T5 e hops de erro. |
| `J_main_metricas_execucao.png` | Execução completa anterior à revisão. |
| `J_main_config_trans.png` | Caminho relativo de uma entrada `TRANS`. |

## Ficheiros anteriormente anunciados mas inexistentes

Os seguintes nomes foram removidos do inventário porque não existem:

- `T4_config_table_output.png`;
- `21_arquitetura_global_etl.png`;
- `22_modelo_dados_pgadmin.png`.

Não foram criadas imagens substitutas artificiais.

## Capturas a atualizar antes da entrega

1. T1: filtro com todas as regras e validação do lookup.
2. T2: canvas final, validação HTTP/JSON e preview com estados/nulos.
3. T3: canvas sem imputação de zero.
4. T4: `Insert/Update` e teste da ligação por variáveis.
5. T5: query com cast decimal, GroupBy e XML final.
6. J_main: execução final depois de PostgreSQL estar configurado.

As novas capturas devem mostrar data legível, configuração relevante e ausência de passwords.
