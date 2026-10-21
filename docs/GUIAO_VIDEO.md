# Guião do vídeo demonstrativo — 3 a 5 minutos

**Atualização das evidências — 21/10/2026:** usar as [capturas finais](diagramas/README.md), incluindo J_main com Mail bem-sucedido e email 28/15/13/6. A auditoria não executou Pentaho. No vídeo, declarar que o envio foi confirmado com password manual; ${SMTP_PASSWORD} falhou com 535. Não mostrar credenciais nem guardar a password introduzida. Rever as pendências de segurança/portabilidade antes de gravar uma nova execução.

**Autor:** Gonçalo Correia, n.º 22840 — ISI, LESI, IPCA / EST, 2026/2027

**Duração prevista:** 4 minutos e 40 segundos

**Formato:** gravação do ecrã com voz, 1080p, texto do Spoon legível

**Estado:** guião preparado; vídeo, publicação e QR Code pendentes.

Em 20/10/2026, o autor confirmou a execução manual de `J_main`: T1 a T5 com `result=true`, 28 registos no PostgreSQL, 28 veículos JSON e 6 séries XML. Esta confirmação não substitui a gravação.

## 1. Preparação

1. Abrir Spoon com T1 a T6 e `J_main.kjb`, pgAdmin/psql e o repositório.
2. Confirmar a ligação `Postgres_Carros`. As ligações atuais têm passwords ofuscadas guardadas, a resolver antes da entrega; não mostrar passwords.
3. Usar uma base nova ou salvaguardada e confirmar o esquema de `sql/01_schema.sql`.
4. Rever [CHECKLIST_CAPTURAS.md](CHECKLIST_CAPTURAS.md) e [CHECKLIST_DEMONSTRACAO.md](CHECKLIST_DEMONSTRACAO.md). Confrontar indicações históricas com os KTR atuais.
5. Preparar os CSV, JSON e XML para apresentação e executar os testes locais.
6. Fechar notificações e janelas com dados pessoais. Testar o microfone.

## 2. Sequência de gravação

### 0:00–0:25 — problema e enquadramento

**Mostrar:** README e estrutura do repositório.

**Dizer:** “Este trabalho integra especificações de veículos BMW M com campanhas de segurança da NHTSA. A pipeline Pentaho limpa, cruza e carrega os dados em PostgreSQL, gerando relatórios JSON e XML.”

### 0:25–0:50 — fontes e limites

**Mostrar:** `data/raw/specs.csv` e `series_lookup.csv`.

**Dizer:** “As especificações são dados locais do projeto, sem fonte externa documentada por valor. A NHTSA fornece campanhas de segurança dos EUA. Consultamos o modelo genérico e o ano, sem confirmar cada variante. O rácio recalls por 100 hp é exploratório e não uma medida científica de fiabilidade mecânica.”

### 0:50–1:25 — T1 e quarentena

**Mostrar:** canvas de T1, `Validar campos obrigatorios`, regex, `Sort Rows` + `Unique Rows`, lookup e `Validar lookup series`.

**Dizer:** “A fonte tem 29 registos, sem duplicados na chave marca, modelo e ano. Validamos peso, potência, cilindrada, ano e correspondência de série. O M3 E92 GTS fica em quarentena por peso omisso. Mantemos 28 veículos válidos e um segundo caminho para rejeitados de lookup.”

Mostrar `rejeitados_specs.csv`, sem inventar o peso em falta. Não afirmar que foi removido um duplicado da fonte atual.

### 1:25–2:05 — T2 e API REST

**Mostrar:** construção do URL, REST Client e `Validar resposta NHTSA`; não procurar o antigo `JSON input`.

**Dizer:** “O pedido GET envia make, model e modelYear. Um M3 E46 CSL de 2003 é consultado como BMW M3 de 2003. Validamos HTTP 2xx, JSON e Count inteiro não negativo. Zero válido fica zero; resposta inválida mantém NULL. O CSV guarda também o estado HTTP e o estado da consulta.”

No KTR original atual, mostrar OK e ERRO: zero válido também recebe OK; erro mantém NULL. Explicar que timeout ou falha de transporte fazem T2 falhar.

### 2:05–2:30 — T3 e consolidação

**Mostrar:** `LEFT OUTER JOIN`, seleção de campos e `Calculator`.

**Dizer:** “Juntamos as fontes pelo modelo genérico e ano, preservando os veículos das especificações. As contagens NHTSA nulas continuam nulas. O rácio é a contagem dividida pela potência, multiplicada por 100. O CSV final tem 28 veículos e 18 campos.”

### 2:30–3:00 — T4 e PostgreSQL

**Mostrar:** Table Output com TRUNCATE, atualmente presente em T4, e pgAdmin/psql.

**Dizer:** “A carga usa Table Output com TRUNCATE e 18 mapeamentos. Substitui o conteúdo da tabela e não garante uma transação atómica global. O preço do M5 E34 permanece NULL.”

Executar as consultas:

```sql
SELECT COUNT(*) FROM bmw_m_performance_fiabilidade;
SELECT model, price_usd
FROM bmw_m_performance_fiabilidade
WHERE model = 'M5 E34';
```

Mostrar o resultado real. O autor já confirmou 28 registos em 20/10/2026.

### 3:00–3:25 — T5 e relatórios

**Mostrar:** query com cast decimal, `GroupBy`, catálogo JSON e resumo XML.

**Dizer:** “O fluxo é copiado para dois ramos. Exportamos 28 veículos em JSON e seis séries em XML. O cast decimal preserva as médias de potência. O campo modelos_com_resposta_nhtsa indica quantas linhas de cada série têm contagem válida.”

Destacar as médias 422.50, 395.00, 487.75, 503.75, 533.50 e 600.00 hp. Não interpretar falta de resposta como zero campanhas.

### 3:25–4:10 — J_main e validação

**Mostrar:** sequência T1–T6, Mail, Sucesso ETL e hops de erro das transformações. Mostrar Set variables e email 28/15/13/6; Mail não tem hop de falha explícito.

**Dizer:** “O job executa as transformações em sequência e desvia falhas para Abortar por Erro. Em 20 de outubro de 2026, confirmei manualmente result=true nas cinco transformações, 28 registos na tabela, 28 veículos em JSON e seis séries em XML.”

Executar o job se o ambiente estiver preparado, ou mostrar uma evidência real guardada dessa execução. Não atribuir a capturas antigas a execução de 20/10/2026 sem confirmação. Não prometer uma duração de execução.

Se houver tempo, mostrar o resultado de:

```powershell
python -m unittest discover -s tests -v
```

### 4:10–4:40 — resultados e conclusão

**Mostrar:** resultados no relatório.

**Dizer:** “A integração foi executada com sucesso. Os resultados demonstram o processo ETL, não uma relação causal entre potência e avarias. As principais limitações são a origem não documentada das especificações, a cobertura dos EUA e a consulta por modelo genérico. Recalls por 100 hp é apenas um indicador exploratório.”

## 3. Publicação e QR Code

1. Rever som, legibilidade e ausência de dados privados.
2. Confirmar duração entre 3 e 5 minutos.
3. Publicar numa plataforma aceite pela unidade curricular.
4. Testar o URL numa janela privada.
5. Só depois gerar e testar o QR Code.
6. Inserir URL e QR Code na secção 5 do relatório e gerar o PDF final.

Não existe ainda URL ou QR Code final confirmado.
