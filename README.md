# ISI TP1 — Performance e campanhas de segurança da gama BMW M

Trabalho Prático 1 da unidade curricular de Integração de Sistemas de Informação, Licenciatura em Engenharia de Sistemas Informáticos, IPCA/EST, ano letivo 2026/2027.

O projeto implementa uma pipeline ETL em Pentaho Data Integration (PDI/Kettle) que integra especificações automóveis fornecidas num CSV local com contagens de campanhas de segurança devolvidas pela API pública da NHTSA. O resultado é consolidado em CSV, carregado em PostgreSQL e exportado em JSON e XML.

> O campo `recalls_por_100hp` é um indicador exploratório criado para o exercício ETL. Não é uma métrica científica validada de fiabilidade mecânica e não permite inferir causalidade.

## Estado da revisão

- Fonte `specs.csv`: 29 registos, sem duplicados na chave `(make, model, year)`.
- Quarentena: 1 registo, BMW M3 E92 GTS (2010), por peso omisso.
- Dataset mecânico válido: 28 veículos.
- Última execução local de T1, T2 e T3 nesta revisão: concluída com PDI 10.2.0.0-222.
- NHTSA nessa execução: 15 respostas HTTP 200 válidas e 13 respostas HTTP 400. As respostas HTTP 400 ficaram com contagem e rácio nulos, não com zero.
- T4, T5 e `J_main` não foram executados nesta revisão porque não foi encontrada uma instância PostgreSQL local configurada e salvaguardada.
- Testes automáticos: 23 testes com sucesso através da biblioteca standard de Python.
- Vídeo e QR Code: ação manual ainda necessária.
- PDF técnico revisto: `output/pdf/relatorio_final_revisao.pdf`; falta inserir o QR Code do vídeo para obter a versão de entrega.

O registo detalhado encontra-se em [docs/REVISAO_FINAL.md](docs/REVISAO_FINAL.md).

## Arquitetura

```text
data/raw ──T1──> data/processed/specs_limpas.csv
    │              └──> data/staging/rejeitados_specs.csv
    │
    └── NHTSA ──T2──> data/processed/nhtsa_recalls.csv
                           │
specs_limpas.csv ──────────┴──T3──> bmw_m_performance_fiabilidade.csv
                                         │
                                         T4
                                         ▼
                                  PostgreSQL carros_etl
                                         │
                                         T5
                              ┌──────────┴──────────┐
                              ▼                     ▼
                         catálogo JSON         resumo XML
```

O job `kettle/jobs/J_main.kjb` preserva a sequência T1 → T2 → T3 → T4 → T5 e encaminha falhas das transformações para a entrada `Abortar por Erro`.

## Transformações

### T1 — especificações e qualidade de dados

`kettle/transformations/T1_extract_specs.ktr`:

- lê `data/raw/specs.csv` e `data/raw/series_lookup.csv`;
- normaliza `make` e `model`;
- extrai `versao` e `model_prefix` por expressão regular;
- rejeita peso nulo, zero ou negativo, potência não positiva, cilindrada não positiva e ano fora de 1886–2100;
- mantém `Sort Rows` + `Unique Rows` na chave `(make, model, year)`;
- calcula `peso_ton`, `litros`, `hp_por_tonelada` e `hp_por_litro`;
- valida a correspondência de `series` e `body_type` após o `Stream Lookup`;
- escreve 28 linhas válidas e mantém o M3 E92 GTS na quarentena, sem imputar peso.

### T2 — API NHTSA

`kettle/transformations/T2_extract_nhtsa.ktr` envia exatamente:

```text
GET https://api.nhtsa.gov/recalls/recallsByVehicle
    ?make=<make>
    &model=<model_prefix>
    &modelYear=<year>
```

Exemplo: `BMW M3 E46 CSL (2003)` é consultado como `make=BMW`, `model=M3`, `modelYear=2003`. A resposta é, portanto, relativa à combinação genérica marca/modelo/ano disponível na NHTSA e não prova a aplicabilidade de cada campanha à variante E46 CSL.

O tratamento distingue:

- `OK`: HTTP 2xx, JSON válido e `Count` inteiro positivo;
- `OK_ZERO`: HTTP 2xx, JSON válido e `Count = 0`;
- `ERRO_HTTP_<código>`: resposta HTTP fora de 2xx;
- `JSON_INVALIDO`: corpo não analisável;
- `COUNT_AUSENTE`: propriedade `Count` em falta;
- `COUNT_INVALIDO`: valor negativo, fracionário ou não numérico;
- timeout/erro de transporte: falha do step REST e, por consequência, falha de T2/J_main.

`data/processed/nhtsa_recalls.csv` conserva `nhtsa_query_status` e `nhtsa_http_status`. Respostas inválidas são registadas sem credenciais e ficam com `nhtsa_recalls_count` nulo.

### T3 — consolidação

`kettle/transformations/T3_consolidate_metrics.ktr` efetua um `LEFT OUTER JOIN` pela chave `(make, model_prefix, year) = (make, model, year)`. A transformação não converte contagens ausentes em zero. O rácio só é calculado quando existe contagem válida:

```text
recalls_por_100hp = nhtsa_recalls_count / engine_hp × 100
```

O CSV final mantém 18 campos; os metadados HTTP permanecem no ficheiro intermédio de T2.

### T4 — PostgreSQL

`kettle/transformations/T4_load_postgres.ktr` usa `Insert/Update` com a chave `(make, model, year)`. Esta estratégia evita a eliminação prévia de dados e permite reexecução sem duplicar as linhas existentes. Não é uma transação atómica para o dataset completo e não remove linhas antigas que já não existam na fonte.

### T5 — JSON e XML

`kettle/transformations/T5_export_reports.ktr`:

- mantém `engine_hp` inteiro no catálogo JSON;
- cria `engine_hp_agregacao` com `CAST(... AS NUMERIC(10,2))` para impedir truncagem da média;
- formata `media_hp` com duas casas decimais;
- acrescenta `modelos_com_resposta_nhtsa` ao XML, tornando visível a cobertura válida por série;
- só abre os ficheiros de saída quando recebe a primeira linha, evitando substituir relatórios válidos por ficheiros vazios se a leitura PostgreSQL falhar antes de produzir dados.

Médias de potência esperadas:

| Série | Média (hp) |
|---|---:|
| Série 2 M | 422.50 |
| Série 3 M | 395.00 |
| Série 4 M | 487.75 |
| Série 5 M | 503.75 |
| Série 6 M | 533.50 |
| Série 8 M | 600.00 |

## Requisitos

Versões confirmadas no computador usado na revisão:

- Pentaho Data Integration 10.2.0.0-222;
- Java 21.0.12.1;
- Python 3.14.5;
- Git 2.45.0.windows.1.

É ainda necessário:

- PostgreSQL compatível com o DDL em `sql/01_schema.sql`;
- driver JDBC PostgreSQL disponível no PDI;
- acesso HTTPS a `api.nhtsa.gov`.

O projeto não depende de bibliotecas Python externas para executar os testes.

## Configurar PostgreSQL e o PDI

1. Criar uma base de dados vazia, sem apagar uma base já existente:

   ```powershell
   createdb -h localhost -p 5432 -U postgres carros_etl
   psql -h localhost -p 5432 -U postgres -d carros_etl -f .\sql\01_schema.sql
   ```

2. Copiar o exemplo de propriedades para a configuração local do Kettle:

   ```powershell
   New-Item -ItemType Directory -Force "$env:USERPROFILE\.kettle" | Out-Null
   Copy-Item .\config\kettle.properties.example "$env:USERPROFILE\.kettle\kettle.properties"
   notepad "$env:USERPROFILE\.kettle\kettle.properties"
   ```

3. Preencher localmente `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD`. O ficheiro real está ignorado pelo Git. Reiniciar o Spoon depois de alterar o ficheiro, porque o PDI lê estas propriedades no arranque.

   > No PDI 10.2 testado, definir apenas variáveis de ambiente na sessão PowerShell não as tornou automaticamente disponíveis como variáveis Kettle. Usar `kettle.properties` evita essa ambiguidade.

4. No Spoon, abrir T4 ou T5, editar a ligação `Postgres_Carros` e usar **Test**. A password não deve ser guardada no repositório.

## Executar

### Spoon

1. Abrir `kettle/jobs/J_main.kjb`.
2. Confirmar as variáveis PostgreSQL e a existência da tabela.
3. Executar com nível de log `Basic`.
4. Confirmar o caminho de sucesso e rever mensagens NHTSA; respostas HTTP inválidas ficam nulas e registadas.

### Kitchen no Windows

```powershell
& "C:\caminho\para\data-integration\Kitchen.bat" `
  /file:"$PWD\kettle\jobs\J_main.kjb" `
  /level:Basic
```

Para executar apenas uma transformação:

```powershell
& "C:\caminho\para\data-integration\Pan.bat" `
  /file:"$PWD\kettle\transformations\T1_extract_specs.ktr" `
  /level:Basic
```

## Testes

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam dados existentes, fórmulas, nulos, JSON/XML, estrutura Kettle, ausência de segredos e respostas NHTSA simuladas. Não equivalem a uma nova execução de T4/T5/PostgreSQL.

## Estrutura do repositório

```text
config/                   exemplo de configuração sem segredos
data/raw/                 fontes CSV locais
data/staging/             quarentena
data/processed/           artefactos intermédios e consolidado
data/output/              JSON e XML finais
docs/                     relatório, decisões, revisão e guião
docs/diagramas/           capturas reais existentes
kettle/transformations/   T1 a T5
kettle/jobs/              J_main
sql/                      DDL PostgreSQL
tests/                    testes standard library e fixtures locais
```

## Limitações conhecidas

- As especificações históricas em `specs.csv` não têm fonte externa documentada; são dados de entrada do projeto, não dados oficiais BMW verificados.
- A NHTSA cobre campanhas de segurança do mercado dos EUA e a consulta usa o prefixo genérico do modelo.
- Uma resposta HTTP inválida não é interpretada como `Count = 0`.
- O `Insert/Update` de T4 não garante atomicidade global e não elimina linhas obsoletas.
- Nesta instalação, `Pan.bat` devolveu código de processo 0 mesmo quando o log continha um erro de ligação; em automatizações deve validar-se também o resultado/log do PDI, preferencialmente através do job e dos respetivos hops de erro.
- As capturas existentes foram obtidas antes de algumas correções finais; devem ser atualizadas antes da entrega quando mostrarem steps entretanto alterados.
- O vídeo obrigatório e o respetivo QR Code ainda têm de ser produzidos manualmente.

## Documentação

- Relatório: [docs/relatorio_final.md](docs/relatorio_final.md)
- PDF técnico revisto: [output/pdf/relatorio_final_revisao.pdf](output/pdf/relatorio_final_revisao.pdf)
- Decisões ETL: [docs/decisoes_etl.md](docs/decisoes_etl.md)
- Guião do vídeo: [docs/GUIAO_VIDEO.md](docs/GUIAO_VIDEO.md)
- Checklist da demonstração: [docs/CHECKLIST_DEMONSTRACAO.md](docs/CHECKLIST_DEMONSTRACAO.md)
- Revisão final: [docs/REVISAO_FINAL.md](docs/REVISAO_FINAL.md)
- Inventário visual: [docs/diagramas/README.md](docs/diagramas/README.md)
