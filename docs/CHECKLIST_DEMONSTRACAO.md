# Checklist da demonstração

## Antes de gravar

- [ ] PostgreSQL instalado e acessível.
- [ ] Base `carros_etl` nova ou salvaguardada.
- [ ] `sql/01_schema.sql` executado sem erros.
- [ ] Variáveis PostgreSQL configuradas apenas localmente.
- [ ] Ligação `Postgres_Carros` testada no Spoon.
- [ ] Acesso a `https://api.nhtsa.gov` confirmado.
- [ ] T1 executada: 29 lidos, 1 rejeitado, 28 válidos.
- [ ] T2 executada e estados HTTP revistos.
- [ ] T3 executada: 28 linhas finais.
- [ ] T4 executada sem apagar dados não salvaguardados.
- [ ] T4 reexecutada e contagem mantida em 28.
- [ ] T5 executada: 28 objetos JSON e 6 séries XML.
- [ ] Médias XML confirmadas com duas casas decimais.
- [ ] `python -m unittest discover -s tests -v` sem falhas.
- [ ] Nenhuma password visível no ecrã ou nos logs.
- [ ] Capturas finais atualizadas.

## Durante a gravação

- [ ] Identificar UC, curso, autor e objetivo.
- [ ] Mostrar as duas fontes locais e a API.
- [ ] Explicar a quarentena do M3 E92 GTS.
- [ ] Explicar que a fonte atual não tem duplicados.
- [ ] Mostrar os operadores de deduplicação.
- [ ] Mostrar os parâmetros `make`, `model` e `modelYear`.
- [ ] Explicar a granularidade genérica da consulta NHTSA.
- [ ] Mostrar a distinção entre zero válido e erro HTTP.
- [ ] Mostrar o `LEFT OUTER JOIN` e a preservação de nulos.
- [ ] Mostrar a carga `Insert/Update` em PostgreSQL.
- [ ] Mostrar JSON e XML.
- [ ] Mostrar a correção da média de potência.
- [ ] Executar `J_main` e mostrar o resultado real.
- [ ] Mostrar os testes automáticos.
- [ ] Referir limitações e trabalhos futuros.

## Depois de gravar

- [ ] Rever áudio, resolução e legibilidade.
- [ ] Confirmar que não aparecem segredos ou dados pessoais.
- [ ] Publicar o vídeo.
- [ ] Testar o URL sem sessão iniciada.
- [ ] Criar o QR Code a partir do URL final.
- [ ] Testar o QR Code em pelo menos um telemóvel.
- [ ] Inserir URL e QR Code no Markdown e no PDF.
- [ ] Confirmar que o PDF mantém o QR Code legível.
- [ ] Atualizar `docs/REVISAO_FINAL.md` de “AÇÃO MANUAL NECESSÁRIA” para “CONCLUÍDO”.
