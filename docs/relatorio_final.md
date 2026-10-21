# Trabalho Prático 1 — Pipeline ETL da gama BMW M

**Auditoria das capturas — 21/10/2026:** o [inventário atualizado](diagramas/README.md) confronta todas as imagens com os KTR/KJB originais. As evidências essenciais estão disponíveis. Não foi executado Pentaho nesta auditoria.

O envio foi confirmado pelo utilizador com password manual; ${SMTP_PASSWORD} falhou com erro 535. O job guardado tem password Mail vazia. T4/T5/T6 têm campos PostgreSQL ofuscados e não vazios, a resolver antes da entrega; nenhum valor foi reproduzido ou alterado. O job mantém um caminho absoluto local preexistente para T6. As descrições históricas de configuração externa e execuções anteriores abaixo não comprovam o estado atual dessas opções.

Evidências adicionais: [T6 — pipeline](diagramas/T6_pipeline_completo.png), [variáveis no parent job](diagramas/T6_config_set_variables.png), [email recebido 28/15/13/6](diagramas/T6_email_recebido.png), [SMTP Outlook 587/TLS sem password visível](diagramas/T6_config_mail.png) e [PostgreSQL: 28 linhas, 13 contagens e rácios NULL](diagramas/T4_validacao_nulls.png).

**Autor:** Gonçalo Correia, n.º 22840

**Unidade curricular:** Integração de Sistemas de Informação (ISI)

**Curso e instituição:** Licenciatura em Engenharia de Sistemas Informáticos, IPCA / Escola Superior de Tecnologia

**Ano letivo:** 2026/2027

**Data:** outubro de 2026

**Repositório:** [isi-tp1-performance-fiabilidade](https://github.com/goncaloalo/isi-tp1-performance-fiabilidade)

## 1. Introdução e problema

O trabalho integra especificações de veículos BMW M, fornecidas em CSV, com campanhas de segurança consultadas na API REST da NHTSA. O objetivo técnico é construir uma pipeline ETL completa: limpar, validar, cruzar e carregar os dados em PostgreSQL, exportando um catálogo JSON e um resumo XML.

Os dados permitem calcular indicadores de potência e o rácio `recalls_por_100hp`. Este rácio é **exploratório e não constitui uma medida científica de fiabilidade mecânica**. A contagem de campanhas de segurança não mede a probabilidade de avaria nem permite concluir que maior potência causa mais falhas.

### 1.1. Metodologia e proveniência

- `data/raw/specs.csv` contém 29 registos de veículos entre 1985 e 2024. Não existe documentação que associe cada especificação a uma fonte BMW ou publicação independente. São dados de entrada do exercício, não especificações oficialmente verificadas.
- `data/raw/series_lookup.csv` é uma tabela local que associa os prefixos M2, M3, M4, M5, M6 e M8 a séries e tipos agregados de carroçaria.
- A NHTSA é a fonte oficial das campanhas de segurança consultadas para o mercado dos EUA. T2 envia `make`, `model=model_prefix` e `modelYear=year`, com codificação dos valores por `encodeURIComponent`.

O endpoint utilizado é:

```text
GET https://api.nhtsa.gov/recalls/recallsByVehicle?make=<make>&model=<model_prefix>&modelYear=<year>
```

Por exemplo, BMW M3 E46 CSL (2003) é consultado como BMW M3 (2003). As campanhas devolvidas para essa combinação genérica não comprovam aplicabilidade à variante CSL ou a um VIN concreto.

A validação técnica combina inspeção dos KTR/KJB, testes locais e execução manual no Pentaho. A execução de 20/10/2026 foi confirmada pelo autor; as capturas existentes são tratadas separadamente para não lhes atribuir uma data ou configuração não verificada.

## 2. Arquitetura da pipeline

A arquitetura mantém seis transformações e um job de orquestração. O diagrama seguinte representa o núcleo de dados T1–T5; T6 e Mail estão documentados nas capturas finais:

```mermaid
flowchart LR
    RAW["specs.csv e series_lookup.csv"] --> T1["T1: limpar e validar"]
    T1 --> LIMPOS["specs_limpas.csv"]
    T1 --> REJ["Quarentena: especificações e lookup"]
    LIMPOS --> T2["T2: consultar NHTSA"]
    API["API REST NHTSA"] --> T2
    T2 --> RECALLS["nhtsa_recalls.csv"]
    LIMPOS --> T3["T3: consolidar"]
    RECALLS --> T3
    T3 --> FINAL["CSV: 28 veículos, 18 campos"]
    FINAL --> T4["T4: carregar PostgreSQL"]
    T4 --> PG[("carros_etl")]
    PG --> T5["T5: exportar"]
    T5 --> JSON["28 veículos JSON"]
    T5 --> XML["6 séries XML"]
```

| Componente | Entrada | Saída |
|---|---|---|
| T1 | Especificações e lookup CSV | CSV limpo e dois caminhos de rejeitados |
| T2 | Modelos genéricos e anos de T1 | Contagens NHTSA e metadados HTTP |
| T3 | Especificações limpas e consultas NHTSA | CSV consolidado com 18 campos |
| T4 | CSV consolidado | Tabela PostgreSQL |
| T5 | Tabela PostgreSQL | Catálogo JSON e resumo XML |
| J_main | Execução manual ou Kitchen | Sequência T1 a T5 e encaminhamento de falhas |

Os caminhos Kettle usam `${Internal.Entry.Current.Directory}`. Esta opção reduz dependências da pasta do repositório, mas continua a exigir configuração local do PDI, JDBC e PostgreSQL.

## 3. Desenvolvimento e decisões técnicas

A inspeção de 21/10/2026 dos KTR originais confirma T4 com Table Output/TRUNCATE e T2 com estados OK/ERRO.

**Capturas:** a auditoria de 21/10/2026 substituiu o canvas e as métricas de J_main pelas versões com T6/Mail e acrescentou quatro capturas T6. As restantes imagens recentes já eram idênticas ao destino, incluindo o excerto JSON com nome normalizado. A [checklist final](CHECKLIST_CAPTURAS.md) e o [inventário revisto](diagramas/README.md) identificam as evidências atuais, as históricas e os limites dos recortes.

### 3.1. T1 — extração, limpeza e enriquecimento

T1 normaliza marca e modelo, extrai versão e prefixo por regex e atribui `Base` quando não encontra uma versão especial. Valida peso preenchido e positivo, potência e cilindrada positivas e ano entre 1886 e 2100.

O BMW M3 E92 GTS (2010) mantém o peso omisso e segue para `data/staging/rejeitados_specs.csv`. Não foi inventado um peso. Depois do lookup, um segundo filtro valida `series` e `body_type`, encaminhando falhas para `rejeitados_lookup_series.csv`.

A fonte atual não tem duplicados na chave `(make, model, year)`. Os operadores `Sort Rows` e `Unique Rows` permanecem para demonstrar a regra, sem alegar que foi removido um duplicado BMW M3.

Os cálculos são:

```text
peso_ton = weight_kg / 1000
litros = engine_cc / 1000
hp_por_tonelada = engine_hp / peso_ton
hp_por_litro = engine_hp / litros
```

A saída contém 28 veículos válidos.

#### Capturas de T1

![Pipeline Completo T1](./diagramas/T1_pipeline_completo.png)

*Figura 1 — Canvas atual de T1: validação de campos e lookup, com dois caminhos de rejeitados.*

![Configuração String Operations T1](./diagramas/T1_config_string_operations.png)

*Figura 2 — Normalização de texto com trim e conversão da marca para maiúsculas.*

![Configuração Validação de Peso T1](./diagramas/T1_config_filter_peso.png)

*Figura 3 — Recorte parcial do filtro atual: peso não nulo e positivo; potência, cilindrada e ano ficam abaixo do scroll e estão confirmados no KTR.*

![Configuração Tratar Nulos T1](./diagramas/T1_config_tratar_nulos.png)

*Figura 4 — Preenchimento da versão Base quando não foi identificada uma edição especial.*

![Configuração Regex Versão T1](./diagramas/T1_config_regex_versao.png)

*Figura 5 — Expressão regular para identificar a versão no nome do modelo.*

![Configuração Regex Prefixo T1](./diagramas/T1_config_regex_prefixo.png)

*Figura 6 — Expressão regular para obter o prefixo genérico do modelo.*

![Configuração Calculator T1](./diagramas/T1_config_calculator_metricas.png)

*Figura 7 — Cálculos mecânicos com a constante 1000.*

![Configuração Stream Lookup T1](./diagramas/T1_config_stream_lookup.png)

*Figura 8 — Lookup de série e carroçaria; a validação posterior é visível no canvas atual.*

![Métricas de Execução T1](./diagramas/T1_metricas_execucao.png)

*Figura 9 — Métricas: 29 dados de entrada, 1 rejeitado, 28 válidos, 0 rejeitados de lookup e 0 erros; sem data de execução visível.*

![Preview dos Dados Finais T1](./diagramas/T1_preview_dados_finais.png)

*Figura 10 — Pré-visualização existente de specs_limpas.csv.*

### 3.2. T2 — API NHTSA e validação de respostas

T2 seleciona combinações únicas de marca, prefixo de modelo e ano, constrói os URLs e executa pedidos GET no REST Client. O step `Validar resposta NHTSA` analisa `http_status` e o JSON.

Uma contagem só é aceite com HTTP 2xx, JSON válido e `Count` inteiro não negativo. O KTR original atual distingue OK e ERRO. Zero válido também recebe OK; respostas inválidas mantêm contagem nula. Não existe classificação detalhada nem logging específico de categorias nesse JavaScript. Timeout e falha de transporte no REST Client fazem a transformação falhar e seguem pelo caminho de erro do job.

O CSV intermédio mantém seis campos:

```text
make, model, year, nhtsa_recalls_count, nhtsa_query_status, nhtsa_http_status
```

Zero válido e ausência de informação válida têm significados diferentes. Uma resposta HTTP 400 com corpo `Count=0` não é aceite como zero campanhas.

#### Capturas de T2

![Pipeline Completo T2](./diagramas/T2_pipeline_completo.png)

*Figura 11 — Canvas atual de T2, com validação HTTP/JSON em JavaScript e sem JSON input.*

![Configuração JavaScript URL T2](./diagramas/T2_config_javascript_url.png)

*Figura 12 — Construção do URL com parâmetros de marca, modelo genérico e ano.*

![Configuração REST Client T2](./diagramas/T2_config_rest_client.png)

*Figura 13 — REST Client configurado para pedidos GET dinâmicos.*

![Configuração JSON Input T2](./diagramas/T2_config_json_input.png)

*Figura 14 — Parser JSON input histórico, substituído no KTR atual por Validar resposta NHTSA.*

![Métricas de Execução T2](./diagramas/T2_metricas_execucao.png)

*Figura 15 — Métricas de uma execução anterior de T2; não confirmam a validade de todas as respostas HTTP.*

![Preview dos Dados Finais T2](./diagramas/T2_preview_dados_finais.png)

*Figura 16 — Preview de nhtsa_recalls.csv com 28 linhas, estados OK/ERRO, códigos HTTP 200/400 e contagens nulas nas respostas inválidas. Os estados OK/ERRO correspondem ao KTR original atual: 15 respostas válidas e 13 inválidas.*

![Validação JavaScript da resposta NHTSA T2](./diagramas/T2_config_validar_resposta.png)

*Figura 16a — Janela Validar resposta NHTSA, com validação HTTP/JSON e saídas api_error_type e nhtsa_recalls_count.*

### 3.3. T3 — consolidação e indicador exploratório

T3 ordena os fluxos e faz `LEFT OUTER JOIN` pela correspondência `(make, model_prefix, year) = (make, model, year)`. Preserva os veículos de T1, remove campos duplicados e os metadados técnicos HTTP da saída final.

As contagens ausentes continuam nulas. O `Calculator` aplica:

```text
recalls_por_100hp = nhtsa_recalls_count / engine_hp * 100
```

O rácio também fica nulo quando não existe contagem válida. O consolidado mantém 28 veículos e 18 campos. O preço do M5 E34 continua nulo.

#### Capturas de T3

![Pipeline Completo T3](./diagramas/T3_pipeline_completo.png)

*Figura 17 — Canvas atual de T3, com preservação de contagens nulas e sem imputação de zero.*

![Configuração Merge Join T3](./diagramas/T3_config_merge_join.png)

*Figura 18 — Merge Join com LEFT OUTER JOIN e chaves compostas.*

![Configuração Select Values T3](./diagramas/T3_config_select_values.png)

*Figura 19 — Seleção de campos anterior; a configuração atual remove também os metadados técnicos NHTSA.*

![Configuração Calculator T3](./diagramas/T3_config_calculator_metricas.png)

*Figura 20 — Cálculo de recalls_por_100hp, indicador exploratório.*

![Métricas de Execução T3](./diagramas/T3_metricas_execucao.png)

*Figura 21 — 28 linhas consolidadas e 0 erros; as 56 entradas no join correspondem aos dois fluxos.*

![Preview dos Dados Finais T3](./diagramas/T3_preview_dados_finais.png)

*Figura 22 — 28 linhas e 13 contagens NHTSA NULL; coluna do rácio fora do recorte.*

### 3.4. T4 — carga PostgreSQL

O esquema de referência é `sql/01_schema.sql`. Mantém os 18 campos de negócio, `id` e `loaded_at`, com chave única `(make, model, year)`. Impõe limites ao ano, valores mecânicos positivos e valores NHTSA não negativos quando presentes. Preço e campos NHTSA admitem `NULL`; as métricas usam tipos `NUMERIC`.

O KTR original atual usa Table Output com TRUNCATE ativo, commit 1000, batch e 18 mapeamentos. Substitui o conteúdo da tabela; uma falha pode deixar a tabela vazia ou parcialmente carregada. Não existe garantia de atomicidade para todo o dataset.

T4 e T5 resolvem a ligação `Postgres_Carros` através das propriedades Kettle `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD`. O exemplo sem segredos está em `config/kettle.properties.example`. A configuração local é descrita no README.

#### Capturas de T4

![DDL Create Table T4](./diagramas/T4_ddl_create_table.png)

*Figura 23 — Preparação anterior do esquema; o DDL atual acrescenta restrições e a chave make, model, year.*

![Pipeline Completo T4](./diagramas/T4_pipeline_completo.png)

*Figura 24 — Canvas atual de T4: leitura CSV e Table Output.*

![Configuração CSV Input T4](./diagramas/T4_config_csv_input.png)

*Figura 25 — Leitura do CSV consolidado com caminho relativo e tipos numéricos.*

![Métricas de Execução T4](./diagramas/T4_metricas_execucao.png)

*Figura 26 — Carga de 28 linhas, sem erros de execução.*

![Dados Persistidos no PostgreSQL T4](./diagramas/T4_dados_postgres.png)

*Figura 27 — Cabeçalho PostgreSQL com 28 resultados e preço do M5 E34 NULL.*

![Configuração Table Output T4](./diagramas/T4_config_table_output.png)

*Figura 27a — Table Output com Truncate table ativo, correspondente ao KTR original atual.*

![Mapeamentos Database fields T4](./diagramas/T4_config_database_fields.png)

*Figura 27b — Separador Database fields do Table Output com 18 mapeamentos.*

### 3.5. T5 — catálogo JSON e resumo XML

T5 lê a tabela ordenada por série e ano. A opção `distribute=N` copia cada linha para dois ramos: catálogo JSON com 18 atributos por veículo e resumo XML agrupado por `series`.

A média de potência usa um campo auxiliar decimal:

```sql
CAST(engine_hp AS NUMERIC(10,2)) AS engine_hp_agregacao
```

O `GroupBy` aplica `AVERAGE(engine_hp_agregacao)`; o XML usa o formato `0.00`. O resumo contém contagem de modelos, médias de potência e rácios mecânicos, soma de campanhas, média do indicador exploratório e `modelos_com_resposta_nhtsa`.

Este último campo conta linhas com contagem NHTSA válida, sem provar cobertura da variante. As agregações NHTSA usam apenas valores não nulos; não se deve interpretar uma série sem respostas válidas como zero campanhas.

Os outputs atuais adiam a abertura dos ficheiros até receberem a primeira linha. Isso protege relatórios existentes se a leitura PostgreSQL falhar antes de produzir dados, mas não torna a escrita transacional.

#### Capturas de T5

![Pipeline Completo T5](./diagramas/T5_pipeline_completo.png)

*Figura 28 — Topologia de T5 com cópia do fluxo para os ramos JSON e XML.*

![Configuração GroupBy T5](./diagramas/T5_config_groupby.png)

*Figura 29 — GroupBy atual: sete agregações, engine_hp_agregacao e modelos_com_resposta_nhtsa.*

![Métricas de Execução T5](./diagramas/T5_metricas_execucao.png)

*Figura 30 — JSON com 28 linhas e XML com 6; 56 emissões PostgreSQL representam cópia para dois ramos.*

![Preview dos Ficheiros JSON e XML T5](./diagramas/T5_preview_json.png)

*Figura 31 — Excerto apenas JSON; contagens totais comprovadas nas métricas.*

![Preview XML por série T5](./diagramas/T5_preview_xml.png)

*Figura 31a — XML com seis séries, médias decimais e cobertura NHTSA; extremo direito parcialmente cortado.*

### 3.6. J_main — orquestração

O job executa T1–T6 por ordem, seguido de Mail e Sucesso ETL. Cada transformação tem um hop de falha para Abortar por Erro; Mail não tem esse hop no job atual. O mecanismo controla a sequência e interrompe o caminho normal perante falha; não cria uma transação distribuída entre API, ficheiros e PostgreSQL.

O autor confirmou uma execução manual completa no Pentaho em 20/10/2026, com `result=true` nas cinco transformações. Não foi fornecida uma duração confirmada para essa execução.

#### Capturas de J_main

![Pipeline Completo J_main](./diagramas/J_main_pipeline_completo.png)

*Figura 32 — Job final T1–T6, Mail, Sucesso ETL e seis hops de erro das transformações.*

![Configuração de Entrada de Transformação J_main](./diagramas/J_main_config_trans.png)

*Figura 33 — Entrada TRANS com caminho relativo.*

![Métricas de Execução J_main](./diagramas/J_main_metricas_execucao.png)

*Figura 34 — Execução em 21/10/2026: sucesso de T1–T6, Mail, Sucesso ETL e J_main. Hora completa truncada.*

## 4. Resultados, validação e limitações

### 4.1. Execução manual confirmada

Em **20/10/2026**, o autor executou manualmente `J_main` no Pentaho e confirmou:

| Verificação | Resultado |
|---|---|
| T1, T2, T3, T4 e T5 | Todas terminaram com `result=true` |
| Registos carregados no PostgreSQL | 28 |
| Contagem confirmada na tabela PostgreSQL | 28 |
| Veículos exportados em JSON | 28 |
| Séries exportadas em XML | 6 |

Esta confirmação substitui a pendência anterior de execução de T4, T5 e do job completo. Não implica que todas as consultas NHTSA tenham uma resposta válida nem comprova testes de falha, rollback ou reexecução da carga.

A fonte mantém 29 registos únicos, dos quais um é rejeitado por peso omisso. Os 28 veículos válidos distribuem-se por seis séries.

### 4.2. Valores por série e interpretação

A revisão anterior registou os seguintes valores nos artefactos consolidados. As médias mecânicas preservam a precisão decimal corrigida:

| Série | Modelos | Potência média (hp) | Respostas NHTSA válidas na revisão anterior | Campanhas nessas respostas | Média exploratória de recalls/100 hp |
|---|---:|---:|---:|---:|---:|
| Série 2 M | 4 | 422.50 | 4 | 5 | 0.2925 |
| Série 3 M | 9 | 395.00 | 6 | 22 | 0.9700 |
| Série 4 M | 4 | 487.75 | 3 | 7 | 0.5000 |
| Série 5 M | 8 | 503.75 | 1 | 1 | 0.1600 |
| Série 6 M | 2 | 533.50 | 0 | n/d | n/d |
| Série 8 M | 1 | 600.00 | 1 | 1 | 0.1700 |

A revisão técnica anterior obteve 15 respostas HTTP 200 válidas e 13 HTTP 400. A distribuição HTTP da execução manual agora confirmada não foi fornecida; não se assume que repetiu esses valores. Estados e contagens da API podem mudar.

As médias NHTSA usam apenas respostas válidas, com cobertura desigual. Um total por série pode contar a mesma campanha em consultas de anos distintos; não representa necessariamente campanhas únicas. A Série 6 sem respostas válidas na revisão anterior não demonstra ausência de campanhas.

Os resultados não sustentam conclusões causais sobre motores turbo, qualidade de construção ou fiabilidade geral. Não foi verificado quais os componentes envolvidos em cada campanha; não se atribuem campanhas a airbags, cablagens ou motores sem análise específica.

### 4.3. Testes locais

A infraestrutura de testes Python foi retirada na simplificação de 21/10/2026, por não ser necessária à execução do Pentaho. Os resultados abaixo ficam preservados como registo histórico.

A suite `unittest`, sem dependências externas, registou 23 testes aprovados na revisão técnica. Verifica CSV, 28 modelos válidos, quarentena, duplicados, campos obrigatórios, fórmulas, preço nulo do M5 E34, coerência CSV/JSON, agregações XML, médias decimais e estrutura Kettle.

As fixtures locais cobrem zero válido, erro HTTP, timeout, JSON inválido e `Count` ausente/inválido. São testes de regras e artefactos, distintos da execução manual agora confirmada.

Na revisão, Pan devolveu código de processo 0 mesmo com erro de ligação no log. Por isso, o código do processo isolado não basta como prova de sucesso: é necessário rever o log e o resultado Kettle.

### 4.4. Limitações

- Falta de fonte externa documentada por especificação do CSV.
- Cobertura NHTSA centrada nos EUA e consulta por modelo genérico, sem confirmação por VIN ou variante.
- Variação temporal da API e distinção obrigatória entre zero válido e falta de informação.
- Ausência de controlo por parque circulante, produção, quilometragem, gravidade ou tempo de exposição.
- `recalls_por_100hp` exploratório, sem validação como medida científica de fiabilidade mecânica.
- Carga e exportações sem garantia transacional global.
- Algumas capturas históricas/parciais foram preservadas e identificadas; as evidências essenciais atuais estão disponíveis segundo o inventário.
- Vídeo, publicação e QR Code ainda pendentes.

## 5. Demonstração em vídeo e QR Code

O [guião](GUIAO_VIDEO.md) organiza uma demonstração de 3 a 5 minutos: problema, fontes, T1 e quarentena, T2 e REST, T3 e junção, T4 e PostgreSQL, T5 e relatórios, job e limitações.

**Estado:** o vídeo ainda não foi produzido nem publicado. Não existe URL final ou QR Code confirmado.

Após a gravação, publicar o vídeo, testar o acesso numa janela privada e só depois gerar o QR Code. Inserir o URL e a imagem nesta secção e atualizar o PDF. Preservam-se a [checklist das capturas](CHECKLIST_CAPTURAS.md) e a [checklist da demonstração](CHECKLIST_DEMONSTRACAO.md).

## 6. Conclusão e trabalhos futuros

A execução manual confirmada demonstra o funcionamento integrado de T1 a T5: limpeza, quarentena, integração REST, consolidação, carga de 28 registos e exportações de 28 veículos JSON e seis séries XML. Os nulos e as médias decimais fazem parte das regras de qualidade descritas.

A análise é técnica e exploratória. Não prova uma relação entre potência e avarias nem uma classificação de fiabilidade das séries. As capturas essenciais já foram auditadas e sincronizadas. Para concluir a entrega académica, falta resolver as ressalvas de segurança/portabilidade, rever o relatório, gravar e publicar o vídeo, criar o QR Code real e atualizar o PDF.

Como trabalhos futuros propõem-se documentar fontes primárias por especificação, registar data e URL de cada consulta, estudar campanhas individualmente e testar uma carga transacional numa base descartável. Comparações entre marcas ou preços de outros mercados só deverão avançar com fontes documentadas.

## 7. Referências bibliográficas

1. National Highway Traffic Safety Administration. “NHTSA Datasets and APIs — Recalls”. <https://www.nhtsa.gov/nhtsa-datasets-and-apis>. Consultado na revisão de 20/10/2026.
2. National Highway Traffic Safety Administration. “Resources Related to Investigations and Recalls”. <https://www.nhtsa.gov/resources-investigations-recalls>. Consultado na revisão de 20/10/2026.
3. Hitachi Vantara. “Pentaho Data Integration 10.2”. <https://docs.pentaho.com/pdia-data-integration/10.2-data-integration>. Consultado na revisão de 20/10/2026.
4. Hitachi Vantara. “REST Client — General tab”. <https://docs.pentaho.com/pdia-data-integration/10.2-data-integration/pdi-transformation-steps-reference-overview/rest-client-step/options-rest-client/general-tab>. Consultado na revisão de 20/10/2026.
5. Hitachi Vantara. “Group By”. <https://docs.pentaho.com/pdia-data-integration/10.2-data-integration/pdi-transformation-steps-reference-overview/group-by-landing-page-article>. Consultado na revisão de 20/10/2026.
6. Hitachi Vantara. “Use Command Line Tools to Run Transformations and Jobs”. <https://docs.pentaho.com/pdia-data-integration/10.2-data-integration/advanced-topics-pentaho-data-integration-overview/use-command-line-tools-to-run-transformations-and-jobs>. Consultado na revisão de 20/10/2026.
7. PostgreSQL Global Development Group. “PostgreSQL 18 — CREATE TABLE”. <https://www.postgresql.org/docs/18/sql-createtable.html>.
