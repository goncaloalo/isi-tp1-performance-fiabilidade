# ISI TP1 — Performance e campanhas de segurança da gama BMW M

**Relatório final — 22/10/2026:** [Word](docs/relatorio_final.docx), [PDF](docs/relatorio_final.pdf) e [fonte Markdown](docs/relatorio_final.md). Inclui os oito componentes pedidos no enunciado, T1–T6, J_main, PostgreSQL, JSON/XML, email, dashboard, vídeo e QR. Resultados verificados: 28/15/13/6. As conclusões não identificam os BMW M mais fiáveis e destacam a integração ETL.

**Auditoria final das capturas — 21/10/2026:** [inventário e seleção](docs/diagramas/README.md). Foram inspecionados 63 PNG, com 45 conteúdos distintos; destino final com 43 imagens. As duas capturas de J_main foram substituídas pelas versões com T6/Mail e foram acrescentadas quatro capturas T6. As evidências essenciais estão integradas no relatório final; o estado de 20/10 abaixo é histórico.

[Execução com Mail bem-sucedido](docs/diagramas/J_main_metricas_execucao.png) e [email recebido](docs/diagramas/T6_email_recebido.png) comprovam os resultados apresentados: 28 veículos, 15 respostas válidas, 13 sem dados e 6 séries. O utilizador confirmou sucesso com password manual; ${SMTP_PASSWORD} falhou com 535 e não está validado. Captura SMTP e job guardado com password vazia.

**Configuração local preservada:** T4/T5/T6 usam PostgreSQL local, com as credenciais ofuscadas preexistentes. O caminho absoluto de T6 foi mantido para este computador. No Mail, introduzir a password SMTP manualmente e não guardar o job com essa password. O Mail não tem hop de falha explícito. A configuração externa descrita na revisão anterior é histórica e não corresponde às ligações atuais.

- **Unidade curricular:** Integração de Sistemas de Informação (ISI)
- **Curso:** Licenciatura em Engenharia de Sistemas Informáticos — IPCA / EST
- **Ano letivo:** 2026/2027
- **Autor:** Gonçalo Correia, n.º 22840

## 1. Descrição do projeto

A pipeline Pentaho integra especificações de veículos BMW M em CSV com campanhas de segurança da API REST da NHTSA. Limpa os dados, separa rejeitados, calcula indicadores, carrega PostgreSQL e exporta JSON e XML.

O campo `recalls_por_100hp` é um indicador exploratório do exercício ETL. **Não é uma medida científica de fiabilidade mecânica**, nem permite concluir que a potência causa avarias.

### Estado de execução

Em **20/10/2026**, o autor executou manualmente `J_main` no Pentaho com sucesso. T1, T2, T3, T4 e T5 terminaram com `result=true`. Foram carregados **28 registos no PostgreSQL**, exportados **28 veículos em JSON** e **6 séries em XML**. O autor confirmou também 28 registos na tabela PostgreSQL.

Esta confirmação atualiza o estado anterior de validação. Não foi criada uma nova execução ou captura durante a resolução documental. O vídeo fornecido é https://youtu.be/GiM3ijfJCtM; o QR existente foi confirmado e incluído no relatório final.

## 2. Estrutura do repositório

```text
data/raw/                 especificações e lookup de séries
data/staging/             quarentena de validação e de lookup
data/processed/           CSV limpos, consultas NHTSA e consolidado
data/output/              catálogo JSON e resumo XML
kettle/transformations/   T1 a T6
kettle/jobs/              J_main.kjb
sql/                      esquema PostgreSQL
config/                   exemplo histórico de propriedades Kettle
docs/                     relatório e documentação de entrega
docs/diagramas/           capturas existentes do Spoon
```

## 3. Resumo da pipeline

| Fase | Operações principais | Resultado |
|---|---|---|
| T1 | Normalização, regex, validação de peso/potência/cilindrada/ano, deduplicação e lookup de séries. | 28 registos válidos; M3 E92 GTS com peso omisso em quarentena; segundo caminho para falhas de lookup. |
| T2 | Pedidos GET à NHTSA e validação de HTTP, JSON e `Count`. | CSV com contagem, estado da consulta e estado HTTP; respostas inválidas mantêm contagem nula. |
| T3 | `LEFT OUTER JOIN`, seleção de campos e cálculo de `recalls_por_100hp`. | CSV consolidado com 28 veículos e 18 campos; nulos preservados. |
| T4 | No KTR original atual, Table Output com TRUNCATE e 18 mapeamentos. | Tabela `bmw_m_performance_fiabilidade` em `carros_etl`. |
| T5 | Leitura SQL e cópia do fluxo para JSON e agregação XML. | 28 veículos e 6 séries; médias de potência decimais e `modelos_com_resposta_nhtsa`. |
| T6 | Consulta estatísticas PostgreSQL e publica quatro variáveis no parent job. | 28 veículos, 15 respostas válidas, 13 sem dados, 6 séries. |
| J_main | T1–T6, Mail e Sucesso ETL; falhas T1–T6 para Abortar por Erro. Mail sem hop de falha explícito. | Captura de sucesso com Mail em 21/10/2026. |

A fonte tem **29 registos e nenhum duplicado** na chave `(make, model, year)`. Um registo é rejeitado por peso omisso. `Sort Rows` e `Unique Rows` permanecem para demonstrar deduplicação.

T2 envia `make`, `model=model_prefix` e `modelYear=year` a:

```text
https://api.nhtsa.gov/recalls/recallsByVehicle
```

Por exemplo, M3 E46 CSL (2003) é consultado como BMW M3 de 2003. A resposta não comprova que cada campanha se aplica à variante CSL. No KTR original atual, os estados são OK e ERRO. Zero válido também recebe OK; erro mantém NULL. Timeout ou falha de transporte fazem T2 falhar.

## 4. Requisitos e configuração

Na revisão técnica foram usados **PDI 10.2.0.0-222**, **Java 21.0.12.1** e Git 2.45.0. É necessária uma instância PostgreSQL, o driver JDBC no PDI e acesso HTTPS à NHTSA. Python não é necessário para executar a pipeline.

Numa base nova ou salvaguardada, preparar a tabela:

```powershell
createdb -h localhost -p 5432 -U postgres carros_etl
psql -h localhost -p 5432 -U postgres -d carros_etl -f .\sql\01_schema.sql
```

O DDL não migra automaticamente uma tabela antiga já existente.

T4, T5 e T6 usam a ligação direta `Postgres_Carros`: `localhost:5432`, base `carros_etl`, utilizador `postgres`. As configurações locais funcionais foram preservadas. O exemplo `config/kettle.properties.example` pertence à revisão anterior e não é necessário para estas ligações.

No Spoon, abrir a ligação `Postgres_Carros` e usar **Test**.

## 5. Execução e verificação

No Spoon, abrir `kettle/jobs/J_main.kjb`, introduzir a password SMTP no Mail sem a guardar, executar localmente com log `Basic` e confirmar `result=true` em T1 a T6 e Mail. Rever também os estados NHTSA: sucesso do job não significa que todas as consultas HTTP sejam válidas.

Confirmar os quatro totais preparados por T6: 28 veículos, 15 respostas válidas, 13 sem dados e 6 séries. O envio foi validado pelo utilizador com password manual no Spoon; a execução automática do email sem essa introdução não está validada.

Os testes Python da revisão anterior foram retirados por não serem necessários ao Pentaho. Os resultados históricos permanecem na documentação de decisões.

## 6. Resultados e limitações

As médias de potência por série são 422.50, 395.00, 487.75, 503.75, 533.50 e 600.00 hp. T5 agrega `engine_hp_agregacao`, obtido com `CAST(engine_hp AS NUMERIC(10,2))`, e formata a média como `0.00`.

- As especificações locais não têm fonte externa documentada por valor; não são apresentadas como dados BMW oficialmente verificados.
- A NHTSA cobre campanhas de segurança dos EUA. A consulta por modelo genérico não confirma cobertura por VIN ou variante.
- Zero só é aceite com HTTP 2xx, JSON válido e `Count` inteiro não negativo. Falha de consulta mantém `NULL`.
- T3 preserva contagens/rácios nulos e o preço nulo do M5 E34.
- Table Output executa TRUNCATE; uma falha pode deixar a tabela vazia ou parcialmente carregada. Não existe atomicidade global.
- O job não constitui uma transação distribuída entre API, ficheiros e PostgreSQL.
- O PDI testado devolveu código de processo 0 numa falha de ligação em Pan; rever também o log e o resultado Kettle.
- Capturas antigas podem mostrar configurações anteriores; confrontar com os KTR atuais.
- Vídeo e QR incluídos no relatório final. O acesso público e a reprodução do vídeo devem ser confirmados numa janela privada antes da submissão.

## Dashboard local

Visualização dos resultados ETL, sem dependências nem internet: [instruções de arranque e utilização](dashboard/README.md). Na raiz do repositório, execute `python -m http.server 8000 --bind 127.0.0.1` e abra [a dashboard local](http://localhost:8000/dashboard/).

## 7. Documentação

- [Relatório técnico](docs/relatorio_final.md)
- [Inventário de diagramas](docs/diagramas/README.md)
- [Decisões ETL](docs/decisoes_etl.md)
- [Relatório final editável em Word](docs/relatorio_final.docx)
- [Relatório final em PDF](docs/relatorio_final.pdf)
- [Enunciado do TP1](docs/enunciado_tp1_2026_2027.pdf)
- [Verificação e pendências da entrega](docs/ENTREGA_RELATORIO_FINAL.md)

Os registos históricos e algumas capturas antecedem a execução manual agora confirmada. O estado atualizado encontra-se neste README e no relatório.
