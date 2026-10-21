# Checklist da demonstração

**Auditoria das capturas — 21/10/2026:** [evidências essenciais disponíveis](diagramas/README.md). Não foi executado Pentaho nesta auditoria. O envio foi confirmado pelo utilizador com password manual; ${SMTP_PASSWORD} falhou com 535. Rever passwords guardadas, caminho absoluto preexistente de T6 e ausência de hop de falha de Mail antes de fechar a entrega.

## Antes de gravar

- [ ] PostgreSQL instalado e acessível.
- [ ] Base `carros_etl` nova ou salvaguardada.
- [ ] `sql/01_schema.sql` executado sem erros.
- [ ] Resolver passwords PostgreSQL ofuscadas já guardadas em T4/T5/T6 e confirmar configuração local sem expor segredos.
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
- [x] Capturas finais auditadas e sincronizadas em 21/10/2026; ver inventário.

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
- [ ] Mostrar a carga Table Output com TRUNCATE e 18 mapeamentos em PostgreSQL.
- [ ] Mostrar JSON e XML.
- [ ] Mostrar a correção da média de potência.
- [ ] Mostrar J_main com T1–T6 e Mail bem-sucedido, variáveis no parent job e email 28/15/13/6. Se executar novamente, usar ambiente preparado e preservar credenciais.
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
