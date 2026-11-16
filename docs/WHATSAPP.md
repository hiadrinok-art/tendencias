# Alertas no WhatsApp: como conectar

O Radar envia alertas pela **API oficial do WhatsApp (WhatsApp Cloud API, da Meta)**. Sem a configuração abaixo, tudo funciona em **modo de teste**: nenhuma mensagem sai do servidor, e a página Alertas mostra o que teria sido enviado.

## O que o Radar avisa

| Alerta | Quando | Para quem |
| --- | --- | --- |
| Prazo de propostas alterado | O encerramento mudou no PNCP | Quem acompanha o edital |
| Situação mudou | Por exemplo: suspensa, revogada, homologada | Quem acompanha o edital |
| Novo documento | Retificação, esclarecimento, resposta a impugnação etc. | Quem acompanha o edital |
| Resultado publicado | Vencedor e valor de cada item | Quem acompanha o edital |
| Ata assinada | Ata de registro de preço do processo | Quem acompanha o edital |
| Atas novas do ramo | Resumo diário com exemplos | Quem tem o ramo |
| Editais novos do ramo | Resumo diário | Quem tem o ramo e as UFs |

Cada usuário liga ou desliga cada tipo e recebe no máximo 15 mensagens por dia. Tudo também fica na página **Alertas**.

## Passo a passo na Meta

1. Crie uma conta no **Meta Business** (business.facebook.com) e um app do tipo **Business** em developers.facebook.com, com o produto **WhatsApp**.
2. Cadastre e **verifique o número** da empresa que vai enviar. A verificação da empresa é exigida para enviar em volume.
3. Gere um **token permanente** (usuário do sistema com permissão `whatsapp_business_messaging`) e anote o **Phone number ID**.
4. Crie e envie para aprovação os **2 modelos de mensagem** abaixo, em português (pt_BR).
5. Em **Webhooks**, use a URL `https://SEU-SITE/webhook/whatsapp`, o *verify token* que você escolher e assine o campo **messages**. É por aí que chega o "SAIR".
6. No servidor (no Render: *Environment*), preencha as variáveis abaixo e reinicie.

| Variável | O que é |
| --- | --- |
| `WHATSAPP_TOKEN` | Token permanente da API (segredo) |
| `WHATSAPP_PHONE_ID` | Phone number ID do número que envia |
| `WHATSAPP_APP_SECRET` | App secret do app da Meta, usado para validar o webhook (segredo) |
| `WHATSAPP_VERIFY_TOKEN` | Texto que você escolheu no passo 5 |
| `WHATSAPP_MODELO_CODIGO` | Nome do modelo de código (padrão `radar_codigo`) |
| `WHATSAPP_MODELO_ALERTA` | Nome do modelo de alerta (padrão `radar_alerta`) |
| `WHATSAPP_API_VERSAO` | Versão da Graph API (padrão `v21.0`; confira a atual na Meta) |
| `RADAR_SITE` | Endereço público do site, para os links das mensagens |

Nunca coloque o token ou o app secret no código ou no GitHub.

## Modelos de mensagem para aprovar

**`radar_codigo`**, categoria **Autenticação**, com botão "Copiar código". A Meta gera o texto padrão, algo como "*{{1}}* é seu código de verificação."

**`radar_alerta`**, categoria **Utilidade**, com 3 variáveis:

```
Radar de Editais: {{1}}

{{2}}

Ver no Radar: {{3}}

Responda SAIR para parar de receber.
```

Exemplo: {{1}} = "Prazo de propostas alterado"; {{2}} = "Solução de backup em disco. De 25/11/2026 às 10:00 para 28/11/2026 às 10:00."; {{3}} = link do edital.

## Regras que o Radar já cumpre

- **Consentimento:** o número só é usado depois que a pessoa marca a autorização e confirma o código de 6 dígitos (vale 10 minutos, 5 tentativas, 3 envios por hora).
- **Saída fácil:** "Parar de receber" na página, ou responder SAIR, PARAR ou STOP. O webhook só é aceito com a assinatura da Meta.
- **LGPD:** o número aparece mascarado e entra na exportação de dados. Ele é apagado quando a pessoa sai ou exclui a conta.
- **Custo:** a Meta cobra por conversa iniciada pela empresa. O limite de 15 mensagens por dia por usuário evita surpresas. Confira os preços atuais na Meta.
