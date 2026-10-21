# Relatório ETL por email — configuração e validação

## Atualização por evidência — 21/10/2026

A configuração e os testes abaixo ficam preservados como registo histórico; não descrevem integralmente o job original atual. A [execução final](diagramas/J_main_metricas_execucao.png) mostra sucesso de T1–T6 e Mail; o [email recebido](diagramas/T6_email_recebido.png) mostra 28/15/13/6. São evidências existentes: esta auditoria não executou Pentaho nem enviou email.

O utilizador confirmou sucesso apenas com introdução manual da password. ${SMTP_PASSWORD} falhou com erro 535; não considerar funcional o procedimento por variável descrito abaixo. O [SMTP capturado](diagramas/T6_config_mail.png) mostra smtp.office365.com, 587 e TLS, com password vazia. O job guardado também tem password Mail vazia.

No job atual não existe a entrada Carregar configuracao externa nem hop de falha de Mail. T6 tem caminho absoluto local preexistente. T4/T5/T6 têm campos de password PostgreSQL ofuscados e não vazios, a resolver antes da entrega; nenhum valor foi reproduzido, decifrado ou alterado. Ver [inventário final](diagramas/README.md) para a seleção de capturas e limites.

## Registo histórico anterior

## Alterações

Fluxo de sucesso: T1 → T2 → T3 → T4 → T5 → Carregar configuracao externa → T6 - Preparar Email → Mail - Relatorio ETL → Sucesso ETL.

- Corrigido o caminho da T6 para ser relativo ao job. Removidas apenas as duas entradas vazias e o hop entre elas.
- Mantidos os hops de falha de T1–T5. A configuração externa, a T6 e Mail também encaminham falhas para `Abortar por Erro`.
- A entrada de configuração importa apenas `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_TO`, `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` e `PGPASSWORD` do ambiente do processo Windows para o job. Não regista os valores. É necessária porque as variáveis PDI 10.2 não importam automaticamente o ambiente Windows.
- A T6 mantém a consulta SQL existente, que produz uma linha com totais de veículos, séries, contagens NHTSA válidas e contagens ausentes. A ligação PostgreSQL da T6 passa a usar configuração externa; não contém a password anterior.
- `COUNT(nhtsa_recalls_count)` inclui zero e exclui NULL. As contagens referem-se aos veículos presentes na tabela, não ao número de pedidos HTTP nem apenas às linhas desta execução.
- As quatro estatísticas são publicadas com âmbito `PARENT_JOB`. Executar a T6 isoladamente continua a produzir o erro de job pai ausente. Executar através de `J_main.kjb`.
- O Mail envia o relatório no corpo da mensagem, sem anexos e sem incluir automaticamente o log. Usa `smtp.office365.com`, porta `587`, autenticação e `TLS` (STARTTLS), UTF-8 e referências `${SMTP_*}`.
- HTTP inválido já tratado pela T2 conserva a contagem nula e aparece como ausência de dados. Não é usado para decidir se o job falhou. Uma falha real de transformação, PostgreSQL ou SMTP continua a abortar o job.
- T1–T5 não foram editadas. Alterações anteriores do utilizador foram preservadas. Não foi feito commit, push ou merge.

## Configuração Windows sem guardar passwords

Fechar todas as instâncias do Spoon antes de iniciar com este ambiente. Preservar primeiro qualquer trabalho por guardar. O `J_main` aberto durante a intervenção tinha alterações não guardadas: não guardar essa versão antiga sobre o ficheiro corrigido. Guardar trabalho pendente com outro nome, se necessário, e reabrir o job corrigido.

Numa nova sessão PowerShell, definir os valores não secretos e pedir as passwords com entrada oculta. Substituir os endereços de exemplo e o caminho de instalação. O código abaixo pode ser guardado porque não contém passwords; as passwords introduzidas ficam apenas na memória e no ambiente do processo.

```powershell
$env:SMTP_USER = 'conta@dominio.pt'
$env:SMTP_FROM = $env:SMTP_USER
$env:SMTP_TO = 'destinatario@dominio.pt'
$env:PGHOST = 'localhost'
$env:PGPORT = '5432'
$env:PGDATABASE = 'carros_etl'
$env:PGUSER = 'postgres'

$smtpSecret = Read-Host 'SMTP_PASSWORD' -AsSecureString
$pgSecret = Read-Host 'PGPASSWORD' -AsSecureString
try {
    $env:SMTP_PASSWORD = [System.Net.NetworkCredential]::new('', $smtpSecret).Password
    $env:PGPASSWORD = [System.Net.NetworkCredential]::new('', $pgSecret).Password
    & 'C:\Users\gfcco\OneDrive\Documentos\pdi-ce-10.2.0.0-222\data-integration\Spoon.bat'
}
finally {
    Remove-Item Env:SMTP_PASSWORD, Env:PGPASSWORD -ErrorAction SilentlyContinue
    $smtpSecret.Dispose()
    $pgSecret.Dispose()
}
```

O Spoon iniciado herda uma cópia desse ambiente; a entrada de configuração publica as variáveis no job. Limpar o ambiente da shell não remove a cópia do Spoon: fechar o Spoon depois da execução. Não usar `setx` para passwords, não colocar passwords na linha de comandos, em `.env`, `kettle.properties`, KTR/KJB, capturas ou Git. Não executar com log Debug/Rowlevel nem exportar a lista de variáveis com segredos carregados.

A conta Microsoft 365 precisa de permitir SMTP AUTH e o método de autenticação por utilizador/password usado pela entrada Mail. O remetente deve ser a própria conta ou ter autorização Send As. Uma password de aplicação não contorna uma política que bloqueie esse método. Não alterar políticas da organização para este teste. A Microsoft mantém o comportamento de Basic SMTP AUTH até dezembro de 2026 e prevê alterações aos valores por omissão no fim desse mês; confirmar com o administrador a disponibilidade na conta.

Fontes: [configuração Microsoft 365](https://learn.microsoft.com/en-gb/Exchange/mail-flow-best-practices/how-to-set-up-a-multifunction-device-or-application-to-send-email-using-microsoft-365-or-office-365) e [calendário de autenticação](https://techcommunity.microsoft.com/blog/exchange/updated-exchange-online-smtp-auth-basic-authentication-deprecation-timeline/4489835).

## Validação realizada e limitações

- XML e grafo verificados: 11 entradas, 17 hops, referências coerentes e caminhos de falha preservados.
- Job e T6 carregados pelas classes da instalação PDI 10.2.0.0-222. Confirmada a classe `JobEntryMail` e a leitura/gravação das opções de servidor, porta, TLS, autenticação e referência externa da password.
- Importação das variáveis externas verificada com valores sintéticos, sem enviar email.
- Teste efetivo no Spoon com uma cópia temporária `START → T6 → Sucesso/Abortar`, sem Mail: falhou na ligação PostgreSQL porque o Spoon aberto não tinha as variáveis `PGHOST`, `PGPORT` e `PGDATABASE`. O log mostrou a URL com placeholders não resolvidos e confirmou execução de `Abortar por Erro`, `result=false`. Este teste ocorreu antes de acrescentar a entrada de importação do ambiente.
- Não foi confirmado sucesso da consulta na T6, do job completo, da autenticação SMTP ou da entrega do email. Não foi enviado email real.
- Os 23 testes existentes apresentavam 21 aprovações e duas falhas antes da correção: quantidade fixa de seis ficheiros Kettle (já existem sete com a T6) e expectativas de configuração externa na T5 que não correspondem à T5 local. Não foram alterados esses testes nem T1–T5.

## Passos manuais pendentes no Spoon

1. Iniciar o Spoon pelo PowerShell acima com configuração real externa e reabrir o `kettle/jobs/J_main.kjb` corrigido.
2. Confirmar visualmente o fluxo final, o caminho relativo da T6 e as ligações de falha. Não executar a T6 isoladamente.
3. Executar o job localmente, com log `Basic`. Confirmar `result=true` até à T6, uma linha consultada e uma linha recebida por `Set variables`, sem erros.
4. Confirmar `result=true` no Mail, `Sucesso ETL` e receção na caixa do destinatário. Comparar os quatro totais com a consulta SQL da T6. Não devem aparecer `${ETL_*}` na mensagem recebida.
5. Confirmar que veículos sem dados NHTSA são reportados como ausentes e não como zero recalls ou falha do job.
6. Numa cópia de teste, provocar falha PostgreSQL e falha SMTP (por exemplo, porta local sem serviço). Confirmar aborto e ausência de sucesso. Restaurar a configuração correta; não simular falhas alterando T1–T5.

Só depois destes passos se pode declarar validado o envio de ponta a ponta.
