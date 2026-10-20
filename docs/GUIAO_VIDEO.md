# Guião de Gravação do Vídeo Demonstrativo (3 a 5 Minutos)

- **Unidade Curricular:** Integração de Sistemas de Informação (ISI) — IPCA / EST
- **Trabalho Prático 1:** Pipeline ETL — Performance vs. Fiabilidade da Gama BMW M
- **Estudante:** Gonçalo Correia (n.º 22840)
- **Duração Estimada:** 4 minutos e 30 segundos (intervalo permitido: 3 a 5 minutos)
- **Formato:** Gravação de ecrã com voz, resolução 1080p, texto do Pentaho Spoon perfeitamente legível

---

## 1. Preparação Prévia à Gravação

Antes de iniciar a gravação:
1. Abrir o **Pentaho Spoon** com as transformações `T1` a `T5` e o Job `J_main.kjb` abertos em separadores.
2. Abrir o **pgAdmin** (ou terminal com `psql`) ligado à base de dados `carros_etl`.
3. Abrir o **VS Code** na raiz do repositório, com a pasta `data/` visível no explorador.
4. Fechar janelas com dados pessoais, notificações ou palavras-passe.
5. Testar o microfone para garantir áudio limpo e sem ruído de fundo.

---

## 2. Cronograma e Guião Passo a Passo

### 0:00 – 0:30 | Introdução e Enquadramento do Problema
* **Ecrã:** Mostrar a página principal do repositório no GitHub ou o ficheiro `README.md` no editor.
* **O que dizer:**
  > "Olá, o meu nome é Gonçalo Correia, número 22840, aluno do 3.º ano de Engenharia de Sistemas Informáticos no IPCA.
  > Neste Trabalho Prático 1 de Integração de Sistemas de Informação, desenvolvi um pipeline completo de ETL no Pentaho Data Integration.
  > O objetivo foi cruzar dados de especificações de modelos desportivos BMW M com dados oficiais de chamadas à oficina (*recalls*) da agência norte-americana NHTSA, para perceber se o aumento de cavalos e rendimento por litro ao longo dos anos prejudicou a fiabilidade dos veículos."

---

### 0:30 – 1:15 | Transformação T1: Limpeza, Regex, Quarentena e Métricas
* **Ecrã:** Mudar para o Pentaho Spoon e mostrar o canvas da transformação `T1_extract_specs.ktr`.
* **O que fazer no ecrã:**
  - Fazer duplo clique no step `Filter rows` (`Validar peso`) e no step `Rejeitados`.
  - Abrir brevemente o `Regex evaluation` (`Extrair versao via Regex`) e o `Calculator`.
* **O que dizer:**
  > "Na transformação T1, lemos o CSV de especificações em bruto com 29 veículos.
  > Limpamos os textos com o *String operations* e aplicamos um filtro de validação de peso: o modelo M3 E92 GTS não tinha peso registado, pelo que foi isolado no ficheiro de quarentena `rejeitados_specs.csv`, evitando divisões por zero ou estimativas falsas.
  > Extraímos a versão especial e o prefixo do modelo usando Expressões Regulares, removemos um registo duplicado e calculámos os rácios de cavalos por tonelada e por litro no *Calculator*, apoiados numa constante de 1000.
  > Por fim, fizemos um *Stream lookup* com a tabela de séries, gerando o ficheiro limpo `specs_limpas.csv` com 28 modelos válidos."

---

### 1:15 – 1:55 | Transformação T2: Ingestão de Dados via API REST NHTSA
* **Ecrã:** No Spoon, mudar para o separador `T2_extract_nhtsa.ktr`.
* **O que fazer no ecrã:**
  - Mostrar o step `Modified JavaScript value` e o step `REST client`.
  - Abrir o step `JSON input` evidenciando o campo `$.Count`.
* **O que dizer:**
  > "Na transformação T2, consumimos a API pública da NHTSA.
  > Removemos combinações duplicadas de modelo e ano para não sobrecarregar o serviço com pedidos repetidos.
  > Através de um script JavaScript com `encodeURIComponent`, montamos o URL dinâmico por marca, modelo e ano.
  > O operador *REST client* faz o pedido HTTP GET e o *JSON input* extrai o número total de recalls através da expressão `$.Count`.
  > O resultado é guardado no ficheiro `nhtsa_recalls.csv` com as contagens obtidas para os 28 veículos."

---

### 1:55 – 2:35 | Transformação T3: Consolidação e Rácio de Fiabilidade
* **Ecrã:** No Spoon, mudar para o separador `T3_consolidate_metrics.ktr`.
* **O que fazer no ecrã:**
  - Mostrar o step `Merge join` e destacar a opção `LEFT OUTER JOIN`.
  - Mostrar o step `Calculator` com o cálculo de `recalls_por_100hp`.
* **O que dizer:**
  > "Na transformação T3, unificamos os dados mecânicos com os dados de segurança.
  > Ordenamos ambos os fluxos e usamos um *Merge join* configurado como *LEFT OUTER JOIN*. Isto garante que todos os modelos das especificações continuam presentes, mesmo que não tenham nenhum recall associado.
  > Removemos campos duplicados com o *Select values*, tratamos valores nulos substituindo-os por zero e calculamos a métrica de fiabilidade: o número de recalls a dividir pela potência, multiplicado por 100.
  > O resultado é o dataset consolidado `bmw_m_performance_fiabilidade.csv` com 18 colunas."

---

### 2:35 – 3:15 | Transformações T4 e T5: PostgreSQL, JSON e XML
* **Ecrã:** Mostrar `T4_load_postgres.ktr` no Spoon e mudar para o pgAdmin/terminal, seguido de `T5_export_reports.ktr`.
* **O que fazer no ecrã:**
  - Mostrar a opção *Truncate table* no step `Table output` de T4.
  - No pgAdmin/terminal, correr `SELECT COUNT(*) FROM bmw_m_performance_fiabilidade;` (mostra 28 linhas) e mostrar o M5 E34 com `price_usd` nulo.
  - Mostrar em T5 a bifurcação em fluxo e abrir rapidamente os ficheiros `data/output/bmw_m_catalogo_completo.json` e `bmw_m_resumo_series.xml`.
* **O que dizer:**
  > "Em T4, carregamos os dados para a tabela no PostgreSQL 18. Ativamos a opção *Truncate table* para que a carga seja idempotente, ou seja, podemos correr o pipeline as vezes que quisermos sem violar a restrição única de modelo e ano. O preço do M5 E34 de 1988 foi mantido como NULL, respeitando a ausência de dados na fonte.
  > Em T5, lemos a base de dados ordenada por série e duplicamos a stream em memória. O ramo JSON exporta os 28 modelos com todos os atributos. O ramo XML usa o step *GroupBy* para agregar os dados por série e calcular médias de potência, rácios e total de recalls para as 6 séries M."

---

### 3:15 – 4:00 | Job J_main: Orquestração e Mecanismo Fail-Fast
* **Ecrã:** No Spoon, abrir o Job `J_main.kjb`.
* **O que fazer no ecrã:**
  - Mostrar a linha verde sequencial (T1 a T5 e Sucesso) e os 5 hops vermelhos a convergir no step `Abortar por Erro`.
  - Clicar no botão **Run** e executar o Job ao vivo (ou mostrar o terminal com a execução via Kitchen).
* **O que dizer:**
  > "O Job principal `J_main.kjb` orquestra todo o processo de forma sequencial: T1, T2, T3, T4 e T5.
  > Todos os caminhos usam a variável relativa `${Internal.Entry.Current.Directory}`, o que garante que o projeto funciona em qualquer computador sem alterar caminhos absolutos.
  > Se alguma transformação falhar — por exemplo, por falta de internet em T2 ou erro de base de dados em T4 —, o fluxo segue pelo caminho vermelho para o step *Abortar por Erro*, interrompendo o pipeline de imediato para não propagar dados inconsistentes.
  > Ao executar o Job, vemos que em cerca de 10 segundos todo o pipeline é concluído com sucesso e zero erros."

---

### 4:00 – 4:35 | Resultados, Limitações e Conclusão
* **Ecrã:** Mostrar a tabela de resultados do XML ou a secção 4 do relatório final.
* **O que dizer:**
  > "Analisando os resultados obtidos:
  > A Série 3 M concentra 22 dos 36 recalls registados, mas os boletins da NHTSA mostram que isso se deve a componentes partilhados de grande volume, como airbags Takata e cablagens de sofagem, e não a avarias no motor.
  > As séries de topo, como a Série 5 e Série 6, apresentam praticamente zero recalls apesar de terem motores V8 e V10 acima dos 500 cavalos.
  > A Série 4 M atinge a maior potência específica média com 163 cavalos por litro, mantendo um rácio de recalls moderado, o que mostra que a sobrealimentação bi-turbo moderna não causou uma explosão de falhas de segurança.
  > Como limitações, recordo que a API da NHTSA consulta por modelo geral e foca-se no mercado dos EUA.
  > O projeto cumpriu todos os objetivos de ISI e está totalmente funcional. Obrigado pela atenção!"

---

## 3. Instruções Finais para Publicação

1. Rever a gravação completa para validar a qualidade do som e a nitidez do ecrã.
2. Confirmar que a duração total fica entre **3:00 e 5:00 minutos**.
3. Carregar o vídeo na plataforma indicada pelos docentes (ex.: YouTube em modo 'Não listado' ou plataforma de e-learning).
4. Gerar o QR Code para o URL definitivo e inseri-lo na secção 5 do relatório final.
