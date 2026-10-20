# ISI TP1 — Performance e campanhas de segurança da gama BMW M

- **Unidade curricular:** Integração de Sistemas de Informação (ISI)
- **Curso:** Licenciatura em Engenharia de Sistemas Informáticos — IPCA / EST
- **Ano letivo:** 2026/2027
- **Autor:** Gonçalo Correia, n.º 22840

## 1. Descrição do projeto

A pipeline Pentaho integra especificações de veículos BMW M em CSV com campanhas de segurança da API REST da NHTSA. Limpa os dados, separa rejeitados, calcula indicadores, carrega PostgreSQL e exporta JSON e XML.

O campo `recalls_por_100hp` é um indicador exploratório do exercício ETL. **Não é uma medida científica de fiabilidade mecânica**, nem permite concluir que a potência causa avarias.

### Estado de execução

Em **20/10/2026**, o autor executou manualmente `J_main` no Pentaho com sucesso. T1, T2, T3, T4 e T5 terminaram com `result=true`. Foram carregados **28 registos no PostgreSQL**, exportados **28 veículos em JSON** e **6 séries em XML**. O autor confirmou também 28 registos na tabela PostgreSQL.

Esta confirmação atualiza o estado anterior de validação. Não foi criada uma nova execução ou captura durante a resolução documental. O vídeo e o QR Code continuam pendentes.

## 2. Estrutura do repositório

```text
data/raw/                 especificações e lookup de séries
data/staging/             quarentena de validação e de lookup
data/processed/           CSV limpos, consultas NHTSA e consolidado
data/output/              catálogo JSON e resumo XML
kettle/transformations/   T1 a T5
kettle/jobs/              J_main.kjb
sql/                      esquema PostgreSQL
tests/                    testes locais e fixtures NHTSA
config/                   exemplo de propriedades Kettle
docs/                     relatório, guião e checklists
docs/diagramas/           capturas existentes do Spoon
```

## 3. Resumo da pipeline

| Fase | Operações principais | Resultado |
|---|---|---|
| T1 | Normalização, regex, validação de peso/potência/cilindrada/ano, deduplicação e lookup de séries. | 28 registos válidos; M3 E92 GTS com peso omisso em quarentena; segundo caminho para falhas de lookup. |
| T2 | Pedidos GET à NHTSA e validação de HTTP, JSON e `Count`. | CSV com contagem, estado da consulta e estado HTTP; respostas inválidas mantêm contagem nula. |
| T3 | `LEFT OUTER JOIN`, seleção de campos e cálculo de `recalls_por_100hp`. | CSV consolidado com 28 veículos e 18 campos; nulos preservados. |
| T4 | No KTR atual, `Insert/Update` pela chave `(make, model, year)`. | Tabela `bmw_m_performance_fiabilidade` em `carros_etl`. |
| T5 | Leitura SQL e cópia do fluxo para JSON e agregação XML. | 28 veículos e 6 séries; médias de potência decimais e `modelos_com_resposta_nhtsa`. |
| J_main | Execução sequencial de T1 a T5 com caminhos de erro para `Abortar por Erro`. | Execução manual confirmada pelo autor em 20/10/2026. |

A fonte tem **29 registos e nenhum duplicado** na chave `(make, model, year)`. Um registo é rejeitado por peso omisso. `Sort Rows` e `Unique Rows` permanecem para demonstrar deduplicação.

T2 envia `make`, `model=model_prefix` e `modelYear=year` a:

```text
https://api.nhtsa.gov/recalls/recallsByVehicle
```

Por exemplo, M3 E46 CSL (2003) é consultado como BMW M3 de 2003. A resposta não comprova que cada campanha se aplica à variante CSL. No KTR atual, os estados distinguem `OK`, `OK_ZERO` e categorias de erro HTTP/JSON/`Count`. Timeout ou falha de transporte fazem T2 falhar.

## 4. Requisitos e configuração

Na revisão técnica foram usados **PDI 10.2.0.0-222**, **Java 21.0.12.1**, Python 3.14.5 e Git 2.45.0. É necessária uma instância PostgreSQL, o driver JDBC no PDI e acesso HTTPS à NHTSA. Não se assume compatibilidade com outras versões sem teste.

Numa base nova ou salvaguardada, preparar a tabela:

```powershell
createdb -h localhost -p 5432 -U postgres carros_etl
psql -h localhost -p 5432 -U postgres -d carros_etl -f .\sql\01_schema.sql
```

O DDL não migra automaticamente uma tabela antiga já existente.

Nos KTR atuais, T4 e T5 usam `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD`. Configurar estas propriedades em `%USERPROFILE%\.kettle\kettle.properties`, usando `config/kettle.properties.example` como referência. Preservar propriedades locais existentes e reiniciar o Spoon após alterações. Não guardar passwords no Git. Definir apenas variáveis PowerShell não as tornou automaticamente disponíveis no PDI testado.

No Spoon, abrir a ligação `Postgres_Carros` e usar **Test**.

## 5. Execução e testes

No Spoon, abrir `kettle/jobs/J_main.kjb`, executar localmente com log `Basic` e confirmar `result=true` em T1 a T5. Rever também as mensagens NHTSA: sucesso do job não significa que todas as consultas HTTP sejam válidas.

No Windows, a partir da raiz do repositório:

```powershell
& "C:\caminho\para\data-integration\Kitchen.bat" /file:"$PWD\kettle\jobs\J_main.kjb" /level:Basic
python -m unittest discover -s tests -v
```

A revisão técnica registou 23 testes aprovados, sobre CSV, fórmulas, nulos, JSON/XML, estrutura Kettle e fixtures HTTP. Estes testes são distintos da execução manual confirmada pelo autor. Não foi confirmado um tempo de execução para essa execução.

## 6. Resultados e limitações

As médias de potência por série são 422.50, 395.00, 487.75, 503.75, 533.50 e 600.00 hp. T5 agrega `engine_hp_agregacao`, obtido com `CAST(engine_hp AS NUMERIC(10,2))`, e formata a média como `0.00`.

- As especificações locais não têm fonte externa documentada por valor; não são apresentadas como dados BMW oficialmente verificados.
- A NHTSA cobre campanhas de segurança dos EUA. A consulta por modelo genérico não confirma cobertura por VIN ou variante.
- Zero só é aceite com HTTP 2xx, JSON válido e `Count` inteiro não negativo. Falha de consulta mantém `NULL`.
- T3 preserva contagens/rácios nulos e o preço nulo do M5 E34.
- `Insert/Update` não garante atomicidade global nem elimina linhas removidas da fonte.
- O job não constitui uma transação distribuída entre API, ficheiros e PostgreSQL.
- O PDI testado devolveu código de processo 0 numa falha de ligação em Pan; rever também o log e o resultado Kettle.
- Capturas antigas podem mostrar configurações anteriores. A checklist deve ser confrontada com os KTR atuais.
- Vídeo, URL publicado e QR Code continuam por produzir. O PDF existente não foi atualizado nesta resolução.

## 7. Documentação

- [Relatório técnico](docs/relatorio_final.md)
- [Guião do vídeo de 3 a 5 minutos](docs/GUIAO_VIDEO.md)
- [Checklist das capturas](docs/CHECKLIST_CAPTURAS.md)
- [Checklist da demonstração](docs/CHECKLIST_DEMONSTRACAO.md)
- [Inventário de diagramas](docs/diagramas/README.md)
- [Decisões ETL](docs/decisoes_etl.md)
- [Registo histórico da revisão](docs/REVISAO_FINAL.md)
- [PDF técnico existente](output/pdf/relatorio_final_revisao.pdf)

Os registos históricos e algumas capturas antecedem a execução manual agora confirmada. O estado atualizado encontra-se neste README e no relatório.
