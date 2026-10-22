# Entrega do relatório final ISI TP1

Data da revisão: 22 de outubro de 2026.

## Documentos preparados

- `docs/relatorio_final.md`: fonte textual revista e completa.
- `docs/relatorio_final.docx`: documento editável com índice, 17 páginas e 16 figuras.
- `output/pdf/relatorio_final.pdf`: versão para leitura e entrega, exportada do Word e revista visualmente em todas as páginas.
- `docs/enunciado_tp1_2026_2027.pdf`: cópia do enunciado fornecido.
- `docs/diagramas/dashboard_relatorio_final.png`: nova captura real da dashboard local.

O relatório cobre os oito componentes exigidos, relaciona a implementação com as três fases ETL e mantém T1–T6, J_main, PostgreSQL, JSON/XML, email e dashboard. O link e o QR do vídeo estão incluídos. O texto conclui explicitamente que recalls não são medida comprovada de fiabilidade mecânica, que recalls_por_100hp não tem justificação técnica forte para esse fim e que não se podem identificar os BMW M mais fiáveis.

## Verificações realizadas

- Leitura das cinco páginas do enunciado, dos seis KTR, de J_main, do DDL e da documentação existente.
- 18 verificações dos artefactos concluídas: 29 entradas; 1 rejeitado; 28 veículos; 18 campos; ausência de duplicados; igualdade CSV/JSON; 15 OK/200; 13 ERRO/400; 13 contagens e rácios NULL; preço M5 E34 NULL; 6 séries e médias coerentes; cálculo do rácio e destino do QR.
- Dashboard aberta sobre cópia dos ficheiros atuais: 28 veículos, 6 séries, 15 respostas válidas, 13 sem dados, 53,6% de cobertura; filtro M3 e pesquisa CSL devolvem um veículo.
- Capturas existentes de execução e email incorporadas com os seus limites identificados. Não se atribuiu uma nova execução Pentaho a esta revisão.
- PDF e Word revistos visualmente; índice e ligações do vídeo presentes.

## Preservação

Não foram alterados KTR/KJB, SQL, dados, credenciais, código da dashboard ou configurações de execução. As alterações que já existiam nesses ficheiros foram preservadas. Não foi executado Pentaho, alterado PostgreSQL, enviada uma mensagem ou publicado o repositório. Não houve commit, push ou submissão no e-learning.

README, decisões ETL, inventário das capturas e documentação da dashboard foram atualizados para apontar ao relatório atual. O histórico das decisões foi mantido e identificado como histórico. O gerador PDF antigo não foi alterado; a versão final entregue foi exportada do Word. Para alterações de apresentação, editar o DOCX e voltar a exportar PDF.

## Pendências antes da entrega

1. Confirmar que o vídeo abre e reproduz numa janela privada. O QR foi validado, mas a consulta automática ao YouTube não permitiu verificar reprodução ou permissões.
2. Rever as credenciais PostgreSQL ofuscadas antes de publicar ou entregar os KTR. O relatório não reproduz passwords. Esta revisão documental não altera a configuração funcional existente.
3. Para executar noutro computador, adaptar o caminho absoluto de T6 e configurar PostgreSQL/SMTP. O envio validado exige password manual; SMTP_PASSWORD não está validada.
4. Confirmar o registo do tema, plataforma, email e repositório na folha partilhada indicada no enunciado.
5. Colocar os materiais finais no repositório Git e submeter no e-learning até 22/10/2026, conforme o enunciado. Confirmar com o docente a data da defesa individual.

## Limites já assumidos no relatório

Mail não possui hop de falha explícito. A carga usa TRUNCATE e não demonstra rollback global. A revisão não verificou o esquema da base em execução, falhas SMTP ou novas respostas da API. A dashboard não é streaming. As especificações não têm fonte externa individual documentada. Estas condições não foram escondidas nem apresentadas como funcionalidades concluídas.
