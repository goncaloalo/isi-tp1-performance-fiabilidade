# Decisões técnicas da pipeline ETL

Este documento regista as decisões que correspondem à implementação versionada após a revisão final. As capturas existentes podem anteceder algumas correções; em caso de divergência, os ficheiros `.ktr`, `.kjb`, o DDL e os testes são a referência técnica.

## 1. Princípios

- Preservar a arquitetura T1 → T2 → T3 → T4 → T5.
- Não imputar especificações ausentes sem fonte.
- Não interpretar uma falha externa como zero.
- Manter o dataset consolidado com 18 campos.
- Usar caminhos relativos e configuração local sem segredos.
- Preferir validações reproduzíveis a conclusões não demonstradas.

## 2. T1 — especificações

### 2.1. Entrada e normalização

`specs.csv` é lido em UTF-8. `make` recebe `trim` e conversão para maiúsculas; `model` recebe `trim`. A expressão `.*?\b(Competition|CSL|GTS|CS|Touring)\b.*` extrai a versão e `Base` é usado apenas quando a designação não contém uma das versões conhecidas.

### 2.2. Regras de rejeição

O step `Validar campos obrigatorios` aceita uma linha apenas quando:

- `weight_kg` não é nulo e é superior a zero;
- `engine_hp` é superior a zero;
- `engine_cc` é superior a zero;
- `year` está entre 1886 e 2100.

As linhas inválidas seguem para `data/staging/rejeitados_specs.csv`. A fonte atual produz um rejeitado: M3 E92 GTS (2010), por peso omisso.

Depois do `Stream Lookup`, `Validar lookup series` exige `series` e `body_type` não nulos. Uma futura falha de mapeamento segue para `data/staging/rejeitados_lookup_series.csv`. Na execução revista não houve falhas de lookup.

### 2.3. Deduplicação

`Sort Rows` ordena por `make`, `model` e `year`; `Unique Rows` usa os mesmos campos. A fonte atual não contém duplicados. O operador foi mantido como controlo preventivo e é coberto por um teste com duplicado artificial, sem alterar o CSV original.

### 2.4. Métricas

Uma constante numérica `1000` suporta os cálculos:

```text
peso_ton = weight_kg / 1000
litros = engine_cc / 1000
hp_por_tonelada = engine_hp / peso_ton
hp_por_litro = engine_hp / litros
```

## 3. T2 — NHTSA

### 3.1. Granularidade da consulta

T2 seleciona `make`, renomeia `model_prefix` para `model` e mantém `year`. O URL é construído como:

```text
https://api.nhtsa.gov/recalls/recallsByVehicle?make=<make>&model=<model>&modelYear=<year>
```

Logo, a pesquisa de `M3 E46 CSL` usa `model=M3`. A contagem pertence à combinação genérica reconhecida pela API e não é evidência de aplicabilidade a uma variante concreta.

### 3.2. Validação da resposta

O REST Client devolve `resposta_json` e `http_status`. O JavaScript de `Validar resposta NHTSA` classifica:

| Estado | Condição | Contagem |
|---|---|---:|
| `OK` | HTTP 2xx, JSON válido, `Count` inteiro > 0 | valor de `Count` |
| `OK_ZERO` | HTTP 2xx, JSON válido, `Count = 0` | 0 |
| `ERRO_HTTP_n` | HTTP fora de 2xx | NULL |
| `JSON_INVALIDO` | erro de parsing | NULL |
| `COUNT_AUSENTE` | propriedade inexistente | NULL |
| `COUNT_INVALIDO` | valor negativo, fracionário ou não numérico | NULL |

Respostas inválidas são registadas no log com os parâmetros de consulta, estado HTTP e categoria. O corpo completo não é escrito no CSV e não existem credenciais NHTSA. Erros de transporte e timeout lançados pelo REST Client fazem T2 falhar e são propagados pelos hops de erro de `J_main`.

O ficheiro `nhtsa_recalls.csv` contém seis campos para rastreabilidade. T3 remove os dois campos técnicos antes do artefacto final.

### 3.3. Resultado observado

Na execução de 20/10/2026, 15 pedidos devolveram HTTP 200 e 13 devolveram HTTP 400, embora os corpos dos 400 apresentassem `Count = 0`. A revisão não aceita esse zero porque o estado HTTP não é de sucesso. As 13 contagens foram preservadas como nulas.

## 4. T3 — consolidação

Os dois fluxos são ordenados e unidos por `Merge Join LEFT OUTER`:

```text
(make, model_prefix, year) = (make, model, year)
```

O step anterior `Tratar recalls nulos` foi removido. A ausência de uma resposta válida fica nula e o `Calculator` propaga o nulo para `recalls_por_100hp`.

```text
recalls_por_100hp = nhtsa_recalls_count / engine_hp × 100
```

O indicador é exploratório. Não mede diretamente fiabilidade mecânica e não deve ser usado para afirmações causais.

## 5. T4 — PostgreSQL

### 5.1. Configuração

As duas ligações `Postgres_Carros`, em T4 e T5, usam:

```text
${PGHOST}
${PGPORT}
${PGDATABASE}
${PGUSER}
${PGPASSWORD}
```

O exemplo `config/kettle.properties.example` não contém uma password. O ficheiro local real está excluído pelo `.gitignore`.

### 5.2. Modelo físico

O DDL mantém 18 atributos de negócio, `id` e `loaded_at`. As decisões principais são:

- chave única `(make, model, year)` alinhada com T1 e T4;
- `price_usd` nulo para preservar o M5 E34;
- `nhtsa_recalls_count` e `recalls_por_100hp` nulos quando a consulta não é válida;
- `CHECK` para ano, potência, peso, cilindrada e valores NHTSA não negativos;
- `NUMERIC` para métricas decimais.

### 5.3. Estratégia de carga

O antigo `Table Output` com `TRUNCATE` foi substituído por `Insert/Update`. A procura usa `(make, model, year)` e os restantes campos são atualizados.

Vantagens:

- não apaga previamente a tabela;
- uma reexecução não cria duplicados;
- reduz o risco de deixar a tabela vazia após uma falha inicial.

Limitações:

- a transformação completa não é uma única transação atómica;
- uma falha pode deixar parte das linhas atualizada;
- registos removidos da fonte não são apagados automaticamente.

Uma futura versão pode carregar para uma tabela temporária, validar contagens e efetuar a substituição dentro de uma transação explícita.

## 6. T5 — exportação

### 6.1. Correção da potência média

`engine_hp` é inteiro na tabela. Para não depender da propagação de metadados inteiros no `GroupBy`, a query cria:

```sql
CAST(engine_hp AS NUMERIC(10,2)) AS engine_hp_agregacao
```

`media_hp` usa esse campo e o XML aplica o formato `0.00`. O catálogo JSON continua a usar `engine_hp` inteiro.

Resultados esperados e validados contra o CSV:

| Série | `media_hp` |
|---|---:|
| Série 2 M | 422.50 |
| Série 3 M | 395.00 |
| Série 4 M | 487.75 |
| Série 5 M | 503.75 |
| Série 6 M | 533.50 |
| Série 8 M | 600.00 |

### 6.2. Cobertura NHTSA no XML

A query cria `nhtsa_consulta_valida` com base em `nhtsa_recalls_count IS NOT NULL`. O `GroupBy` soma este campo para produzir `modelos_com_resposta_nhtsa`. Desta forma, um total de campanhas não é apresentado sem contexto de cobertura.

Quando uma série não tem respostas válidas, o total e a média de recalls ficam vazios no XML, em vez de serem apresentados como zero confirmado.

### 6.3. Proteção dos ficheiros publicados

`JsonOutput` e `XMLOutput` usam a opção **Do not open new file at init**. A configuração foi introduzida depois de uma execução controlada sem PostgreSQL ter demonstrado que a inicialização dos steps podia substituir os artefactos existentes por ficheiros vazios antes de a leitura da base falhar. Com a opção ativa, o ficheiro só é aberto quando chega a primeira linha. Esta proteção não torna a publicação transacional; uma falha durante a escrita continua a exigir validação dos ficheiros gerados.

## 7. Job

`J_main.kjb` mantém a sequência T1–T5. Os hops verdes dependem do sucesso da transformação anterior e cada transformação tem um hop vermelho para `Abortar por Erro`.

Este desenho é *fail-fast*, mas não constitui uma transação distribuída entre ficheiros, HTTP e PostgreSQL. A descrição documental foi corrigida para evitar o termo “atómico” aplicado ao job completo.

## 8. Testes

A suite em `tests/test_pipeline.py` separa:

- validação dos artefactos existentes;
- inspeção estrutural dos KTR/KJB;
- testes unitários de regras com fixtures locais.

Os testes de fixtures cobrem resposta positiva, zero válido, erro HTTP, timeout, JSON inválido, `Count` ausente e `Count` inválido. Não fazem pedidos à API pública.

## 9. Validações executadas nesta revisão

| Validação | Resultado |
|---|---|
| XML de 5 KTR e 1 KJB | válido |
| T1 com PDI 10.2 | 29 lidos, 1 rejeitado, 28 válidos, código 0 |
| T2 com PDI 10.2 | 28 pedidos, 28 linhas, 15 válidas, 13 HTTP 400, código 0 |
| T3 com PDI 10.2 | 28 linhas, 13 contagens nulas, código 0 |
| Testes Python | 23/23 com sucesso |
| T4/T5/J_main | pendente por ausência de PostgreSQL configurado |

## 10. Pendências

- Testar DDL, T4, T5 e duas execuções consecutivas de `J_main` numa base salvaguardada.
- Confirmar o comportamento real do `SUM` de um grupo totalmente nulo em T5; o artefacto esperado usa elementos vazios.
- Atualizar capturas do Spoon que mostram configurações anteriores.
- Gravar vídeo, publicar URL real, criar QR Code e inseri-lo no relatório.
- Inserir o QR Code real no PDF técnico já gerado e repetir a revisão visual da versão definitiva.
