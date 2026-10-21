# Dashboard local — BMW M Performance e Fiabilidade

Visualização dos resultados exportados pelo ETL, em PT-PT. HTML, CSS e JavaScript nativo, sem instalação de dependências, bibliotecas, CDN ou acesso à internet. Python serve apenas os ficheiros locais; não existe backend de aplicação.

## Abrir no Windows

1. Abra o PowerShell e entre na raiz do repositório original:

   ```powershell
   Set-Location 'C:\Users\gfcco\OneDrive\Documentos\isi-tp1-performance-fiabilidade'
   ```

2. Inicie o servidor, limitado ao próprio computador:

   ```powershell
   python -m http.server 8000 --bind 127.0.0.1
   ```

   Python 3.14.5 foi confirmado neste PC. Se `python` deixar de estar disponível no PATH, use o executável identificado:

   ```powershell
   & 'C:\Users\gfcco\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m http.server 8000 --bind 127.0.0.1
   ```

3. Mantenha o terminal aberto e visite **http://localhost:8000/dashboard/** no navegador.
4. Para parar o servidor, prima **Ctrl+C** no terminal.

Não abra `index.html` por duplo clique: `fetch` precisa do servidor HTTP local. O servidor parte da raiz para disponibilizar as exportações em `data/output/`. Se a porta 8000 já estiver ocupada por outro programa, use 8001 no comando e no endereço.

## Utilizar e demonstrar

- Mostre os quatro indicadores e os gráficos de veículos por série e cobertura NHTSA.
- Filtre a tabela por série e pesquise modelo, versão ou ano. Os filtros afetam apenas a tabela; os indicadores e gráficos são globais.
- Use **Limpar filtros** para voltar ao catálogo completo.
- Depois de executar o ETL e exportar novamente, prima **Atualizar dados** ou atualize a página. O JSON é lido com `cache: "no-store"`. O botão não executa o ETL, não consulta a API e não altera ficheiros.
- A hora apresentada é a hora de leitura local, não a hora de execução do ETL.
- Para gravar em 1080p, use o navegador maximizado e zoom a 100%. Desloque a página para mostrar a tabela e a nota de fontes.

## Dados e significado dos indicadores

A fonte única dos indicadores, gráficos e tabela é [`../data/output/bmw_m_catalogo_completo.json`](../data/output/bmw_m_catalogo_completo.json), na lista `catalogo_bmw_m`. O [XML por série](../data/output/bmw_m_resumo_series.xml) fica acessível para consulta e comparação, sem duplicar a agregação no frontend.

- **Veículos:** número de registos da lista.
- **Séries:** valores distintos de `series`.
- **Com resposta NHTSA:** `nhtsa_recalls_count` inteiro não negativo, incluindo zero. A validade da resposta HTTP é estabelecida pelo ETL; o JSON não exporta o estado HTTP.
- **Sem dados NHTSA:** `nhtsa_recalls_count` igual a `null`. Nunca é convertido em zero. Campo ausente, texto ou contagem negativa provoca erro explícito de formato.
- **Cobertura:** veículos com resposta / total de veículos. Catálogo vazio apresenta zero registos e percentagem indisponível.
- Potência, peso, potência/peso e aceleração usam os campos exportados, com unidades hp, kg, hp/t e segundos de 0–60 mph. Não se converte 0–60 mph em 0–100 km/h.

Na exportação inspecionada em 21/10/2026: 28 veículos, 6 séries, 15 com resposta e 13 sem dados; cobertura de 53,6%. Estes valores são uma referência de verificação, não constantes da aplicação.

A NHTSA cobre campanhas de segurança dos EUA e a consulta do ETL usa modelo genérico e ano. Não confirma aplicação por variante ou VIN. Ausência de dados não significa ausência de campanhas. Nem zero campanhas comprova fiabilidade mecânica. Não são apresentados rankings de recalls, rácios de recalls por potência ou taxas de fiabilidade. As especificações locais não são apresentadas como oficialmente verificadas pela BMW.

## Verificação rápida

1. Abra a página e confirme os indicadores com a exportação atual.
2. Selecione M3: a exportação acima contém 9 veículos. Pesquise `CSL`: fica M3 E46 CSL.
3. Limpe os filtros e procure `M5 E34`: a cobertura deve aparecer como **Sem dados · NULL**.
4. Pesquise um termo inexistente: deve surgir a mensagem de ausência de resultados.
5. Atualize os dados e confirme que a página continua funcional. Uma falha de leitura apresenta erro e oculta os indicadores, evitando mostrar dados antigos como atuais.
6. Verifique também numa janela estreita: os cartões reorganizam-se e a tabela permite deslocamento horizontal.

O enunciado original não foi encontrado no repositório; a dashboard implementa o critério de visualização descrito no pedido. A aceitação formal deve ser confirmada com o enunciado/docente.