# Inventário e Checklist de Atualização das Capturas de Ecrã

## Checklist final — 21/10/2026

O [inventário revisto](diagramas/README.md) classifica as imagens após inspeção visual de todos os 45 conteúdos distintos nas duas pastas. Total inicial: 63 PNG, dos quais 18 duplicados exatos. Total final em diagramas: 43 PNG. Screenshots tem prioridade; originais preservados.

- [x] T1: [canvas final](diagramas/T1_pipeline_completo.png) e [métricas](diagramas/T1_metricas_execucao.png): 29 dados de entrada, 1 rejeitado, 28 válidos, dois caminhos de rejeitados.
- [x] T2: [validação atual](diagramas/T2_config_validar_resposta.png) e [preview](diagramas/T2_preview_dados_finais.png): 15 OK, 13 ERRO e NULL.
- [x] T3: [canvas sem imputação de zero](diagramas/T3_pipeline_completo.png), [28 linhas](diagramas/T3_metricas_execucao.png) e [nulos](diagramas/T3_preview_dados_finais.png).
- [x] T4: [Table Output/TRUNCATE](diagramas/T4_config_table_output.png), [18 mapeamentos](diagramas/T4_config_database_fields.png), [28 resultados](diagramas/T4_dados_postgres.png) e [13 contagens/rácios NULL](diagramas/T4_validacao_nulls.png).
- [x] T5: [GroupBy atual](diagramas/T5_config_groupby.png), [JSON 28/XML 6](diagramas/T5_metricas_execucao.png), [JSON](diagramas/T5_preview_json.png) e [XML](diagramas/T5_preview_xml.png).
- [x] T6: [canvas](diagramas/T6_pipeline_completo.png), [quatro variáveis no parent job](diagramas/T6_config_set_variables.png) e [email 28/15/13/6](diagramas/T6_email_recebido.png).
- [x] [Job T1–T6 e Mail](diagramas/J_main_pipeline_completo.png) e [execução com Mail bem-sucedido](diagramas/J_main_metricas_execucao.png), ambos substituídos pelas capturas finais.
- [x] Opcional disponível: [SMTP Outlook 587/TLS sem password](diagramas/T6_config_mail.png). Não é necessário repetir.
- [x] Nenhuma imagem antiga mantida em preferência a uma equivalente recente e tecnicamente correta.

JSON input T2 e DDL T4 são obsoletos; Select Values T3 é parcial. Filtro T1 com scroll e recortes T3/XML têm limites documentados no inventário, complementados por KTR, canvas e métricas. Não faltam novas capturas opcionais para iniciar a revisão final.

Pendências: passwords PostgreSQL ofuscadas guardadas em T4/T5/T6; caminho absoluto preexistente para T6; ausência de hop de falha de Mail; revisão final do relatório/vídeo e posterior URL, QR Code e PDF. Não foram alterados ficheiros técnicos ou credenciais. Mail com password manual validado pelo utilizador; ${SMTP_PASSWORD} falhou com 535 e não está validado.

Esta auditoria não executou Pentaho nem enviou email. A lista seguinte fica preservada como histórico, sem exigir capturas opcionais já suficientes.

Esta checklist histórica analisava 34 capturas de ecrã. A organização de 20/10/2026 substituiu o preview T2 e acrescentou quatro capturas. Para a lista atual, consultar o [inventário de diagramas](diagramas/README.md). As contagens e os estados nas tabelas seguintes pertencem à revisão original.

---

## 1. Estado histórico das capturas — não usar como checklist final

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

A análise histórica seguinte antecede a auditoria de 21/10/2026. As afirmações de cobertura integral e os pedidos condicionais não constituem o estado atual; consultar a checklist final acima.

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
   - *Atualização de 20/10/2026:* [Table Output com Truncate table](diagramas/T4_config_table_output.png) e [18 mapeamentos Database fields](diagramas/T4_config_database_fields.png) copiados de Screenshots. As imagens documentam a configuração capturada no Spoon.

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

## Capturas organizadas em 20/10/2026

- [Validar resposta NHTSA](diagramas/T2_config_validar_resposta.png): janela JavaScript.
- [Preview T2 substituído](diagramas/T2_preview_dados_finais.png): 28 linhas, estados OK/ERRO e códigos HTTP; não mostra ERRO_HTTP_400 como estado.
- [Preview XML T5](diagramas/T5_preview_xml.png): inclui séries M2/M3/M4, médias decimais e cobertura NHTSA.

Os originais em Screenshots foram preservados. Estas capturas não validam automaticamente todas as afirmações históricas desta checklist.
