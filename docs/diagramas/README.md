# Inventário de diagramas e capturas

## Atualização do relatório final em 22/10/2026

O relatório final reutiliza as capturas essenciais verificadas, inclui o [QR existente](QR_Video_Projeto_ISI_BMW_M_CORRIGIDO.png) e acrescenta [dashboard_relatorio_final.png](dashboard_relatorio_final.png). Esta última é uma captura real da dashboard executada numa cópia dos ficheiros atuais; não representa uma nova execução ETL.

O QR foi descodificado e aponta para https://youtu.be/GiM3ijfJCtM. Word e PDF final foram gerados e revistos visualmente. As referências a vídeo/QR/PDF pendentes no registo de 21/10 abaixo são históricas e ficam ultrapassadas por esta atualização. As restantes capturas foram preservadas. O QR anterior foi substituído pelo QR corrigido fornecido pelo autor, com atualização do link no relatório e na documentação.

## Resultado da auditoria de 21/10/2026

Screenshots é a fonte prioritária das novas evidências. Inventário inicial: 24 PNG na origem e 39 no destino; 63 ficheiros, 45 conteúdos distintos e 18 duplicados exatos por SHA-256. Todos os conteúdos distintos foram inspecionados visualmente e comparados com os seis KTR e o job reais. Seleção final: 43 PNG.

Substituídos: J_main_pipeline_completo.png e J_main_metricas_execucao.png. Acrescentados: [T6_pipeline_completo.png](T6_pipeline_completo.png), [T6_config_set_variables.png](T6_config_set_variables.png), [T6_email_recebido.png](T6_email_recebido.png) e [T6_config_mail.png](T6_config_mail.png).

T6 mostra consulta de estatísticas e Set variables, com quatro variáveis no parent job. O email recebido em 21/10/2026, 01:52, mostra 28 veículos, 15 respostas válidas, 13 sem dados e 6 séries, com NULL explícito. A captura opcional Mail mostra smtp.office365.com, porta 587, autenticação e TLS, com password vazia.

As outras 18 imagens da origem já eram idênticas ao destino. T5_preview_json_xml.png é igual a T5_preview_json.png e mostra apenas JSON; não foi criada outra cópia com nome enganador. Nenhuma captura antiga foi mantida em preferência a uma equivalente recente e correta. Originais de Screenshots preservados; nenhuma imagem histórica referenciada eliminada.

[T4_validacao_nulls.png](T4_validacao_nulls.png) confirma total=28, recalls_null=13 e ratio_null=13; a consulta SQL está fora do recorte. T5_metricas_execucao.png mostra JSON 28/XML 6; as 56 emissões são cópias para dois ramos. O XML mostra seis séries, médias decimais e cobertura NHTSA, com extremo direito parcialmente cortado.

**Ressalvas:** JSON input T2 e DDL T4 são históricos; Select Values T3 é parcial. O job tem caminho absoluto local preexistente para T6 e não tem hop Mail → Abortar por Erro. Não foram alterados. Mail guardado com password vazia; o utilizador confirmou sucesso com introdução manual e falha 535 com ${SMTP_PASSWORD}. Não se apresenta essa variável como funcional.

T4/T5/T6 contêm campos de password PostgreSQL ofuscados e não vazios. Não foram reproduzidos, decifrados ou alterados. Não é possível declarar os ficheiros livres de credenciais; resolver antes de entregar ou versionar. Capturas sem passwords visíveis, mas com identificação pessoal/conta institucional.

As evidências essenciais estão disponíveis para revisão final do relatório e vídeo. Não são necessárias novas capturas opcionais. Esta auditoria não executou Pentaho nem enviou email. Vídeo, URL, QR Code e PDF final continuam pendentes. Sem alterações a KTR/KJB, SQL, dados, testes ou credenciais; sem commit, push ou merge.

Este diretório contém apenas capturas reais já existentes. O inventário foi novamente confrontado com as imagens e os KTR/KJB originais em 21/10/2026.

As imagens foram inspecionadas visualmente. As limitações e os elementos históricos estão identificados abaixo; a implementação atual encontra-se nos KTR/KJB originais.

## T1 — especificações

| Ficheiro | Conteúdo |
|---|---|
| `T1_pipeline_completo.png` | Canvas atual: 16 steps, validação de campos e de lookup, dois caminhos de rejeitados. |
| `T1_metricas_execucao.png` | Métricas de 29 lidos, 1 rejeitado e 28 válidos. |
| `T1_preview_dados_finais.png` | Pré-visualização de `specs_limpas.csv`. |
| `T1_config_string_operations.png` | Normalização de strings. |
| `T1_config_regex_versao.png` | Extração de versão. |
| `T1_config_tratar_nulos.png` | Preenchimento de `versao = Base`. |
| `T1_config_filter_peso.png` | Recorte parcial do filtro atual: peso não nulo e positivo; restantes condições abaixo do scroll, confirmadas no KTR. Não exige nova captura opcional. |
| `T1_config_regex_prefixo.png` | Extração de `model_prefix`. |
| `T1_config_calculator_metricas.png` | Cálculos mecânicos. |
| `T1_config_stream_lookup.png` | Lookup de série e carroçaria. |

## T2 — NHTSA

| Ficheiro | Conteúdo |
|---|---|
| `T2_pipeline_completo.png` | Canvas atual: 9 steps, com validação HTTP/JSON e sem JSON input. |
| `T2_metricas_execucao.png` | 28 linhas processadas, sem erros de execução; não significa 28 respostas válidas. |
| `T2_preview_dados_finais.png` | Preview de 28 linhas com estados `OK`/`ERRO`, estado HTTP e contagens nulas nas respostas inválidas. |
| `T2_config_validar_resposta.png` | JavaScript do step Validar resposta NHTSA, com validação HTTP/JSON. |
| `T2_config_javascript_url.png` | Construção do URL. |
| `T2_config_rest_client.png` | REST Client e campos de resposta/estado. |
| `T2_config_json_input.png` | Parser anterior; foi substituído pela validação JavaScript explícita. |

## T3 — consolidação

| Ficheiro | Conteúdo |
|---|---|
| `T3_pipeline_completo.png` | Canvas atual: 9 steps, sem imputação de zero. |
| `T3_metricas_execucao.png` | 28 linhas consolidadas, sem erros. |
| `T3_preview_dados_finais.png` | 28 linhas e 13 contagens NHTSA NULL; coluna do rácio fora do recorte. |
| `T3_config_merge_join.png` | Configuração do `LEFT OUTER JOIN`, ainda aplicável. |
| `T3_config_select_values.png` | Histórica/parcial: só mostra três remoções; o KTR remove também os dois metadados NHTSA. |
| `T3_config_calculator_metricas.png` | Fórmula de `recalls_por_100hp`. |

## T4 — PostgreSQL

| Ficheiro | Conteúdo |
|---|---|
| `T4_pipeline_completo.png` | Canvas atual: CSV e Table Output. |
| `T4_metricas_execucao.png` | Métricas de uma execução anterior. |
| `T4_config_csv_input.png` | Entrada CSV, ainda aplicável. |
| `T4_ddl_create_table.png` | Evidência de DDL anterior; o script atual tem restrições adicionais. |
| `T4_dados_postgres.png` | Cabeçalho indica 28 resultados; preço do M5 E34 NULL. |
| `T4_config_table_output.png` | Configuração capturada de Table Output, com Truncate table ativo. |
| `T4_config_database_fields.png` | Separador Database fields com 18 mapeamentos. |

Estas duas capturas correspondem ao KTR real: Table Output, Truncate ativo e 18 mapeamentos. O DDL capturado acima é histórico: mostra defaults zero e chave model/year, distintos do SQL atual.

## T5 — exportação

| Ficheiro | Conteúdo |
|---|---|
| `T5_pipeline_completo.png` | Canvas atual com cópia do fluxo para JSON e GroupBy/XML. |
| `T5_metricas_execucao.png` | Métricas de uma execução anterior. |
| `T5_config_groupby.png` | GroupBy atual: 7 agregações, engine_hp_agregacao e modelos_com_resposta_nhtsa. |
| `T5_preview_json.png` | Excerto apenas JSON, legível; não prova sozinho a contagem total. |
| `T5_preview_xml.png` | XML com um elemento por série; inclui M2, M3 e M4, médias decimais e cobertura NHTSA. |

## Job

| Ficheiro | Conteúdo |
|---|---|
| `J_main_pipeline_completo.png` | Versão final substituída: T1–T6, Mail, Sucesso ETL e seis hops de falha T1–T6; sem hop de falha de Mail. |
| `J_main_metricas_execucao.png` | Versão final substituída: sucesso de T1–T6, Mail, Sucesso ETL e J_main em 21/10/2026. Hora truncada; não associar à execução do email apenas pela data. |
| `J_main_config_trans.png` | Caminho relativo de uma entrada `TRANS`. |

## Ficheiros anteriormente anunciados mas inexistentes

Os seguintes nomes foram removidos do inventário porque não existem:

- `21_arquitetura_global_etl.png`;
- `22_modelo_dados_pgadmin.png`.

Não foram criadas imagens substitutas artificiais.

## Pedidos históricos de atualização — substituídos pela auditoria de 21/10/2026

1. T1: filtro com todas as regras e validação do lookup.
2. T2: canvas final; validação HTTP/JSON e preview com estados/nulos já adicionados. O preview mostra `OK`/`ERRO`, sem os estados detalhados descritos no relatório.
3. T3: canvas sem imputação de zero.
4. T4: `Insert/Update` e teste da ligação por variáveis.
5. T5: query com cast decimal e GroupBy; preview XML já adicionado.
6. J_main: execução final depois de PostgreSQL estar configurado.

Os pedidos históricos acima não exigem novas capturas opcionais. Consultar o resultado da auditoria e as ressalvas no início deste inventário.
