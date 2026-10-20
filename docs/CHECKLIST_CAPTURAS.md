# Inventário e Checklist de Atualização das Capturas de Ecrã

Este documento analisa as **34 capturas de ecrã** presentes em `docs/diagramas/`, documenta a sua correspondência com o relatório técnico e identifica as capturas que necessitam de atualização ou atenção antes da entrega final.

---

## 1. Estado Global das Capturas

| Módulo | Ficheiro do Pipeline | Capturas Existentes | Estado Atual na Master | Necessidade de Atualização Imediata |
| :--- | :--- | :---: | :---: | :---: |
| **T1** | `T1_extract_specs.ktr` | 10 | Válido e Completo | Nenhuma (perfeitamente alinhado) |
| **T2** | `T2_extract_nhtsa.ktr` | 6 | Válido e Completo | Condicional (ver secção 2) |
| **T3** | `T3_consolidate_metrics.ktr` | 6 | Válido e Completo | Nenhuma (perfeitamente alinhado) |
| **T4** | `T4_load_postgres.ktr` | 5 | Válido e Completo | Condicional (ver secção 2) |
| **T5** | `T5_export_reports.ktr` | 4 | Válido e Completo | Condicional (ver secção 2) |
| **J_main** | `J_main.kjb` | 3 | Válido e Completo | Condicional (ver secção 2) |
| **Total** | — | **34** | **100% Cobertura** | — |

---

## 2. Identificação das Capturas a Atualizar

As capturas em `docs/diagramas/` refletem fielmente a versão estável e validada da `master`. Contudo, foram identificadas situações específicas que exigem atualização ou atenção futura:

### Cenário A: Se as simplificações de código do Codex forem integradas
Caso as alterações experimentais em curso noutra branch venham a ser adotadas no futuro, as seguintes capturas terão de ser renovadas no Pentaho Spoon:

1. **`T2_pipeline_completo.png` e `T2_config_javascript_url.png`:**
   - *Motivo:* Se a lógica de construção de URLs ou de validação de códigos HTTP for alterada/simplificada, os diálogos e o fluxo do canvas devem refletir a nova estrutura de steps.
2. **`T4_pipeline_completo.png` e `T4_metricas_execucao.png`:**
   - *Motivo:* Se o step de carregamento passar de `Table output` (com *Truncate*) para outro operador (como `Insert / Update`), é necessário capturar a nova janela de configuração e a respetiva grelha de execução.
3. **`T5_config_groupby.png` e `T5_preview_json.png`:**
   - *Motivo:* Se os nomes dos campos calculados ou as precisões decimais forem reajustados, o diálogo do `GroupBy` e o preview dos ficheiros de saída devem ser atualizados para total correspondência com os dados em disco.
4. **`J_main_pipeline_completo.png` e `J_main_metricas_execucao.png`:**
   - *Motivo:* Qualquer alteração nos nomes das transformações ou reexecução do job exige um novo print do canvas e do histórico de execução com visto verde.

### Cenário B: Elementos em Falta para a Entrega e Defesa
Para enriquecer a entrega académica e o relatório, devem ser preparadas as seguintes imagens complementares:

1. **QR Code do Vídeo Demonstrativo:**
   - *Ficheiro sugerido:* `docs/diagramas/qrcode_video_demonstracao.png`.
   - *Ação:* Após gravar o vídeo de 3 a 5 minutos e publicá-lo (no e-learning ou YouTube não listado), gerar o QR Code correspondente e inseri-lo na Secção 5 do `docs/relatorio_final.md`.
2. **Configuração Explícita do Table Output em T4 (`T4_config_table_output.png`):**
   - *Situação:* Existe em `prints/T4_config_table_output.png`, mas a pasta `docs/diagramas/` utiliza atualmente 5 capturas para a T4 (que cobrem o DDL, o CSV de entrada, o pipeline, as métricas e os dados na base de dados). Caso se pretenda ilustrar a opção *Truncate table*, pode ser copiada diretamente de `prints/`.

---

## 3. Lista Detalhada das 34 Capturas Atuais

### Transformação T1 (10 imagens)
- `T1_pipeline_completo.png` — Canvas panorâmico no Spoon (12 steps com visto verde).
- `T1_config_string_operations.png` — Diálogo do step *Limpar Strings* (`trim` e `upper`).
- `T1_config_filter_peso.png` — Diálogo do step *Validar peso* (`weight_kg IS NOT NULL`).
- `T1_config_tratar_nulos.png` — Diálogo do step *Tratar nulos* (imputação de `'Base'`).
- `T1_config_regex_versao.png` — Diálogo do step *Extrair versao via Regex*.
- `T1_config_regex_prefixo.png` — Diálogo do step *Extrair prefixo modelo*.
- `T1_config_calculator_metricas.png` — Diálogo do step *Calculator* (rácios com `const_1000`).
- `T1_config_stream_lookup.png` — Diálogo do step *Mapear series e body_type*.
- `T1_metricas_execucao.png` — Painel Step Metrics (29 lidos, 1 rejeitado, 28 válidos).
- `T1_preview_dados_finais.png` — Grelha tabular de pré-visualização de `specs_limpas.csv`.

### Transformação T2 (6 imagens)
- `T2_pipeline_completo.png` — Canvas panorâmico de T2 com vistos verdes.
- `T2_config_javascript_url.png` — Script JavaScript de montagem de URL com `encodeURIComponent`.
- `T2_config_rest_client.png` — Diálogo de configuração do step *REST client*.
- `T2_config_json_input.png` — Diálogo do step *JSON input* com o seletor `$.Count`.
- `T2_metricas_execucao.png` — Painel Step Metrics com 28 pedidos HTTP executados sem erros.
- `T2_preview_dados_finais.png` — Grelha tabular de pré-visualização de `nhtsa_recalls.csv`.

### Transformação T3 (6 imagens)
- `T3_pipeline_completo.png` — Canvas de T3 com os dois ramos concorrentes e junção central.
- `T3_config_merge_join.png` — Diálogo do step *Merge join* (*LEFT OUTER JOIN*).
- `T3_config_select_values.png` — Diálogo do step *Select values* (remoção de colunas duplicadas).
- `T3_config_calculator_metricas.png` — Diálogo do step *Calculator* (`recalls_por_100hp`).
- `T3_metricas_execucao.png` — Painel Step Metrics comprovando 28 tuplos consolidados com 0 erros.
- `T3_preview_dados_finais.png` — Grelha tabular de pré-visualização de `bmw_m_performance_fiabilidade.csv`.

### Transformação T4 (5 imagens)
- `T4_ddl_create_table.png` — Execução do script DDL `sql/01_schema.sql` no PostgreSQL.
- `T4_pipeline_completo.png` — Canvas de T4 com os steps de leitura do CSV e carga relacional.
- `T4_config_csv_input.png` — Diálogo do step *CsvInput* com caminho relativo portátil.
- `T4_metricas_execucao.png` — Painel Step Metrics comprovando a inserção dos 28 registos com 0 erros.
- `T4_dados_postgres.png` — Consulta SQL evidenciando os 28 registos na tabela e o `price_usd` como `NULL` no M5 E34.

### Transformação T5 (4 imagens)
- `T5_pipeline_completo.png` — Canvas de T5 exibindo a bifurcação de stream para JSON e XML.
- `T5_config_groupby.png` — Diálogo do step *GroupBy* com as 6 fórmulas de agregação por série.
- `T5_metricas_execucao.png` — Painel Step Metrics comprovando 28 lidos, 56 emitidos e 0 erros.
- `T5_preview_json.png` — Visualização comparativa do catálogo JSON e do resumo XML gerados em `data/output/`.

### Job J_main (3 imagens)
- `J_main_pipeline_completo.png` — Canvas de orquestração sequencial com os hops verdes e os 5 hops vermelhos de falha.
- `J_main_config_trans.png` — Diálogo de configuração de um step *TRANS* com `${Internal.Entry.Current.Directory}/...`.
- `J_main_metricas_execucao.png` — Histórico de execução no Spoon/Kitchen comprovando sucesso e 0 erros em ~10s.

---

## 4. Recomendações para a Defesa Individual

1. Abrir o Pentaho Spoon e ter o Job `J_main.kjb` aberto com zoom a 100%.
2. Caso o docente peça para demonstrar a execução ao vivo, assegurar que a base de dados PostgreSQL está ativa no porto 5432 e que a máquina tem ligação à Internet (para a chamada da NHTSA em T2).
3. Ter o terminal aberto para demonstrar a execução alternativa sem interface gráfica via `Kitchen.bat`.
