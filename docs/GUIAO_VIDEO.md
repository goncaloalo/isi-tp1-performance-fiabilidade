# Guião do vídeo demonstrativo

**Duração alvo:** 3 a 5 minutos

**Formato sugerido:** gravação do ecrã com voz, 1080p, texto do Spoon legível
**Estado:** ação manual necessária

## Preparação

- Abrir o repositório, Spoon, PostgreSQL/pgAdmin e um terminal.
- Configurar localmente as variáveis Kettle `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD` através de `%USERPROFILE%\.kettle\kettle.properties`; reiniciar o Spoon depois da alteração.
- Executar `sql/01_schema.sql` numa base nova ou salvaguardada.
- Executar os testes Python e guardar o resultado visível.
- Fechar janelas com dados pessoais, passwords ou tokens.
- Confirmar que T1–T5 e `J_main` abrem sem avisos inesperados.

## Sequência de gravação

### 0:00–0:25 — apresentação

“Este é o Trabalho Prático 1 de Integração de Sistemas de Informação. O objetivo é integrar especificações da gama BMW M com contagens de campanhas de segurança da NHTSA através de uma pipeline Pentaho T1 a T5.”

Mostrar brevemente o README e a árvore `data/`, `kettle/`, `sql/`, `tests/` e `docs/`.

### 0:25–0:50 — fontes e limitações

Mostrar `data/raw/specs.csv` e `series_lookup.csv`.

Explicar:

- as especificações são dados de entrada do projeto sem fonte externa documentada;
- a NHTSA é uma fonte oficial de campanhas de segurança dos EUA;
- a consulta usa o prefixo genérico, por exemplo M3, e não comprova aplicabilidade a uma variante específica;
- `recalls_por_100hp` é exploratório, não uma medida científica de fiabilidade.

### 0:50–1:25 — T1 e quarentena

Abrir `T1_extract_specs.ktr` e mostrar:

- normalização e regex;
- `Validar campos obrigatorios`;
- `Sort Rows` + `Unique Rows`;
- `Stream Lookup` e `Validar lookup series`;
- saídas válidas e de quarentena.

Executar T1. Confirmar 29 registos lidos, 1 rejeitado e 28 válidos. Mostrar o M3 E92 GTS com peso vazio em `rejeitados_specs.csv`.

### 1:25–2:05 — T2 e chamada REST

Abrir T2. Mostrar a construção do URL e o REST Client. Usar um exemplo como `BMW M3 2003`.

Mostrar `Validar resposta NHTSA` e explicar as categorias `OK`, `OK_ZERO`, erro HTTP, JSON inválido e `Count` ausente/inválido. Executar T2 apenas com acesso à Internet.

Mostrar `nhtsa_recalls.csv`: respostas 2xx têm contagem; respostas inválidas têm contagem vazia e estado explícito. Não apresentar HTTP 400 como zero recalls.

### 2:05–2:30 — T3 e métricas

Abrir T3 e mostrar o `LEFT OUTER JOIN` e o `Calculator`. Explicar que nulos NHTSA permanecem nulos. Executar T3 e mostrar os 28 registos finais e o preço nulo do M5 E34.

### 2:30–3:00 — T4 e PostgreSQL

Mostrar `sql/01_schema.sql`, a ligação por variáveis e o step `Insert/Update`. Explicar que não existe `TRUNCATE` e que a carga é idempotente por chave, mas não é uma transação atómica global.

Executar T4 numa base salvaguardada. Consultar:

```sql
SELECT COUNT(*) FROM bmw_m_performance_fiabilidade;
SELECT model, price_usd FROM bmw_m_performance_fiabilidade WHERE model = 'M5 E34';
```

### 3:00–3:25 — T5 e relatórios

Mostrar a query de T5, destacando o cast decimal de `engine_hp_agregacao`. Executar T5 e abrir:

- `data/output/bmw_m_catalogo_completo.json`;
- `data/output/bmw_m_resumo_series.xml`.

Confirmar seis séries e as médias 422.50, 395.00, 487.75, 503.75, 533.50 e 600.00 hp. Mostrar `modelos_com_resposta_nhtsa`.

### 3:25–4:10 — J_main e testes

Abrir `J_main.kjb`, mostrar a sequência e os hops de erro. Executar o job completo apenas depois de T4/T5 terem sido validados separadamente.

No terminal, executar:

```powershell
python -m unittest discover -s tests -v
```

Mostrar o total de testes com sucesso.

### 4:10–4:40 — conclusão

Resumir os 28 veículos válidos, a quarentena, a integração REST, PostgreSQL e os dois formatos finais. Repetir as limitações de cobertura, granularidade NHTSA e proveniência das especificações.

## Publicação

1. Ver o vídeo integralmente.
2. Publicar num serviço aceite pela unidade curricular.
3. Abrir o URL numa janela privada e confirmar áudio, imagem e permissões.
4. Só depois criar o QR Code.
5. Inserir URL e QR Code em `docs/relatorio_final.md` e no PDF final.

Não usar um URL provisório ou um QR Code não testado.
