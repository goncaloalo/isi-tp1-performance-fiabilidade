# Revisão final do projeto

Data da revisão: 20/10/2026

Branch: `fix/revisao-final-isi-tp1`
Prazo indicado: 22/10/2026

## A. Alterações implementadas

| Estado | Alteração |
|---|---|
| CONCLUÍDO | Reforço das validações de T1 para peso, potência, cilindrada, ano e lookup de séries. |
| CONCLUÍDO | Preservação do M3 E92 GTS na quarentena, sem imputação. |
| CONCLUÍDO | Manutenção de `Sort Rows` + `Unique Rows` e teste com duplicado artificial. |
| CONCLUÍDO | Validação explícita de HTTP, JSON e `Count` em T2. |
| CONCLUÍDO | Metadados `nhtsa_query_status` e `nhtsa_http_status` no ficheiro intermédio. |
| CONCLUÍDO | Remoção da conversão de contagens NHTSA nulas em zero em T3. |
| CONCLUÍDO | Substituição de credenciais PostgreSQL por variáveis locais. |
| CONCLUÍDO | Substituição de `TRUNCATE + Table Output` por `Insert/Update`. |
| CONCLUÍDO | Restrições adicionais e chave única alinhada no DDL. |
| CONCLUÍDO | Correção da média de potência em T5 através de um campo decimal dedicado. |
| CONCLUÍDO | Inclusão de cobertura NHTSA por série no XML. |
| CONCLUÍDO | Abertura diferida dos ficheiros JSON/XML para não apagar relatórios válidos quando a origem falha antes da primeira linha. |
| CONCLUÍDO | Criação de 23 testes automáticos e fixtures locais. |
| CONCLUÍDO | Revisão do README, relatório, decisões ETL e inventário de imagens. |
| CONCLUÍDO | Criação do guião de vídeo e checklist de demonstração. |

## B. Problemas corrigidos

| Estado | Problema | Correção |
|---|---|---|
| CONCLUÍDO | Médias `422`, `487`, `503` e `533` truncadas no XML. | `CAST(engine_hp AS NUMERIC(10,2))`, agregação no novo campo e formato `0.00`. |
| CONCLUÍDO | Erro documental sobre duplicado BMW M3. | Documentado que a fonte tem 29 registos únicos e um rejeitado por peso omisso. |
| CONCLUÍDO | HTTP 400 com corpo `Count=0` tratado como zero. | Estado de erro explícito e contagem nula. |
| CONCLUÍDO | Ausência de correspondência em T3 convertida em zero. | Step de imputação removido; nulos propagados. |
| CONCLUÍDO | Recalls apresentados como fiabilidade mecânica. | Terminologia e conclusões revistas; indicador classificado como exploratório. |
| CONCLUÍDO | Credencial reversível nos KTR. | Ligação parametrizada; exemplo sem segredo. |
| CONCLUÍDO | `TRUNCATE` descrito como atomicamente seguro. | Removido da transformação e da documentação. |
| CONCLUÍDO | Inventário com imagens inexistentes. | Inventário sincronizado e faltas assinaladas. |
| CONCLUÍDO | T5 criava ficheiros JSON/XML vazios quando a leitura PostgreSQL falhava na inicialização. | Ativada a opção `DoNotOpenNewFileInit` em ambos os outputs e acrescentado teste estrutural. |

## C. Problemas ainda por resolver

| Estado | Problema |
|---|---|
| PENDENTE DE VALIDAÇÃO | T4 e T5 ainda não foram executadas contra PostgreSQL após as alterações. |
| PENDENTE DE VALIDAÇÃO | `J_main` ainda não foi executado ponta a ponta após a revisão. |
| PENDENTE DE VALIDAÇÃO | Confirmar em PDI o resultado de `SUM` quando todos os valores NHTSA de uma série são nulos. |
| AÇÃO MANUAL NECESSÁRIA | Atualizar capturas do Spoon que antecedem a revisão. |
| AÇÃO MANUAL NECESSÁRIA | Gravar, publicar e testar o vídeo demonstrativo. |
| AÇÃO MANUAL NECESSÁRIA | Criar QR Code apenas depois de existir URL real. |
| AÇÃO MANUAL NECESSÁRIA | Inserir o QR Code no PDF técnico revisto e voltar a validar a versão definitiva. |
| NÃO CONCLUÍDO | Validação das especificações históricas contra fontes primárias; não existem fontes documentadas no repositório. |

## D. Testes realizados e resultados

### Execuções Pentaho

| Estado | Execução | Resultado real |
|---|---|---|
| CONCLUÍDO | T1 antes da revisão | código 0; 29 linhas, 1 rejeitada, 28 válidas. |
| CONCLUÍDO | T2 antes da revisão | código 0; 28 linhas; aceitava HTTP 400 como zero. |
| CONCLUÍDO | T3 antes da revisão | código 0; 28 linhas. |
| CONCLUÍDO | T1 após a revisão | código 0; 29 linhas, 1 rejeitada, 28 válidas, 0 falhas de lookup. |
| CONCLUÍDO | T2 após a revisão | código 0; 28 pedidos e 28 linhas; 15 `OK`, 13 `ERRO_HTTP_400`. |
| CONCLUÍDO | T3 após a revisão | código 0; 28 linhas; 13 contagens e rácios nulos. |
| PENDENTE DE VALIDAÇÃO | T4 | não executada contra uma base funcional; a resolução de propriedades foi verificada com um endpoint fictício que recusou a ligação. |
| PENDENTE DE VALIDAÇÃO | T5 | não executada contra uma base funcional. |
| CONCLUÍDO | Falha controlada de T5 | propriedades resolvidas por `kettle.properties`; ligação fictícia `127.0.0.1:1` recusada; hashes dos JSON/XML permaneceram inalterados após ativar a abertura diferida. Não constitui execução funcional de T5. |
| PENDENTE DE VALIDAÇÃO | J_main | não executado após a revisão. |

### Testes automáticos

Comando:

```powershell
python -m unittest discover -s tests -v
```

Resultado: **CONCLUÍDO — 23 testes executados, 23 com sucesso**.

Os testes validam CSV, contagens, modelos, quarentena, duplicados, campos obrigatórios, fórmulas, nulos, JSON, XML, médias decimais, estrutura Kettle, configuração PostgreSQL e respostas NHTSA simuladas.

### Outras validações

| Estado | Validação | Resultado |
|---|---|---|
| CONCLUÍDO | Parsing XML de 5 KTR e 1 KJB | todos bem formados. |
| CONCLUÍDO | Hops de transformações | todas as origens e destinos correspondem a steps existentes. |
| CONCLUÍDO | CSV consolidado | 28 linhas e 18 campos. |
| CONCLUÍDO | Séries no XML | 6. |
| CONCLUÍDO | Médias de potência | 422.50, 395.00, 487.75, 503.75, 533.50 e 600.00. |
| CONCLUÍDO | Consistência CSV/JSON/XML | validada pelos testes. |
| CONCLUÍDO | Preservação de `price_usd = NULL` no M5 E34 | validada. |
| PENDENTE DE VALIDAÇÃO | Resolução das propriedades PostgreSQL | o PDI 10.2 leu um `kettle.properties` isolado e tentou ligar ao endpoint fictício `127.0.0.1:1`; a recusa esperada confirmou a substituição das variáveis sem tocar numa BD real, mas não valida a carga. |

Os testes de artefactos não substituem uma nova execução de T4/T5. O JSON e XML foram alinhados deterministicamente com o CSV e verificados, mas não são apresentados como produtos de uma execução recente de T5.

Na falha controlada, `Pan.bat` terminou com código de processo 0 apesar do erro registado pelo step PostgreSQL. Por isso, uma automatização não deve usar apenas esse código como prova de sucesso; deve validar o log/resultado Kettle ou executar o job com os caminhos de erro configurados.

## E. Ferramentas indisponíveis

| Estado | Ferramenta |
|---|---|
| CONCLUÍDO | Java 21.0.12.1 disponível. |
| CONCLUÍDO | PDI 10.2.0.0-222: Spoon, Pan e Kitchen disponíveis. |
| CONCLUÍDO | Python 3.14.5 disponível. |
| CONCLUÍDO | Git 2.45.0.windows.1 disponível. |
| NÃO CONCLUÍDO | `psql` e `pg_dump` não encontrados no `PATH`. |
| NÃO CONCLUÍDO | Serviço PostgreSQL local não identificado durante a auditoria. |
| NÃO CONCLUÍDO | Pandoc não encontrado no `PATH`. |
| NÃO CONCLUÍDO | Poppler (`pdftoppm`/`pdfinfo`) não encontrado no `PATH`. |
| CONCLUÍDO | PyMuPDF disponível e usado como alternativa para renderizar e rever as 11 páginas do PDF. |

## F. Artefactos gerados

| Estado | Artefacto |
|---|---|
| CONCLUÍDO | `tests/test_pipeline.py` e fixtures NHTSA. |
| CONCLUÍDO | `config/kettle.properties.example`. |
| CONCLUÍDO | `docs/GUIAO_VIDEO.md`. |
| CONCLUÍDO | `docs/CHECKLIST_DEMONSTRACAO.md`. |
| CONCLUÍDO | `docs/REVISAO_FINAL.md`. |
| CONCLUÍDO | CSV NHTSA e consolidado regenerados por T2/T3. |
| CONCLUÍDO | JSON/XML alinhados com os dados revistos e testes. |
| CONCLUÍDO | `output/pdf/relatorio_final_revisao.pdf`, com capa, paginação, imagens e referências; 11 páginas revistas visualmente. |
| AÇÃO MANUAL NECESSÁRIA | PDF final com QR Code real. |
| AÇÃO MANUAL NECESSÁRIA | Vídeo publicado. |

## G. Ações manuais necessárias

1. Instalar ou localizar PostgreSQL, `psql` e `pg_dump`.
2. Fazer backup se for usada uma base existente:

   ```powershell
   pg_dump -h localhost -p 5432 -U postgres -Fc -f .\backup_carros_etl.dump carros_etl
   ```

3. Numa base nova ou salvaguardada, executar:

   ```powershell
   psql -h localhost -p 5432 -U postgres -d carros_etl -f .\sql\01_schema.sql
   ```

4. Copiar `config/kettle.properties.example` para `%USERPROFILE%\.kettle\kettle.properties`, preencher localmente e reiniciar o Spoon. Não confiar apenas em variáveis da sessão PowerShell: esse mecanismo não foi resolvido automaticamente pelo PDI 10.2 testado.
5. Testar a ligação no Spoon.
6. Executar T4 duas vezes e confirmar `COUNT(*) = 28` nas duas execuções.
7. Executar T5 e voltar a correr os testes Python.
8. Executar `J_main` e guardar o log real.
9. Atualizar as capturas indicadas em `docs/diagramas/README.md`.
10. Gravar o vídeo com `docs/GUIAO_VIDEO.md`, publicar, testar o URL e criar o QR Code.
11. Inserir URL/QR no relatório e gerar o PDF final.

## H. Checklist da entrega de 22/10/2026

- [x] Branch de revisão criada sem alterar `master`.
- [x] Arquitetura T1–T5 preservada.
- [x] Dados brutos não adulterados.
- [x] 28 veículos válidos e rejeitado preservado.
- [x] Erro de duplicado corrigido na documentação.
- [x] Médias de potência corrigidas na configuração e nos artefactos.
- [x] Semântica NHTSA corrigida.
- [x] Credenciais removidas dos ficheiros Kettle.
- [x] Testes automáticos criados e executados.
- [x] README e relatório revistos.
- [x] Guião e checklist de vídeo criados.
- [ ] PostgreSQL/T4/T5 validados após revisão.
- [ ] J_main executado após revisão.
- [ ] Capturas finais atualizadas.
- [ ] Vídeo publicado e acessível.
- [ ] QR Code real inserido.
- [ ] PDF final revisto.
- [ ] Branch publicada no GitHub.
