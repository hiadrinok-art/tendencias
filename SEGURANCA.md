# Segurança do Radar de Editais

Este documento resume como a API protege as contas e os dados das empresas. O código fica em `radar/seguranca/`, e os testes em `tests/` comprovam cada item.

## O que está protegido

| Ameaça | Proteção | Onde |
| --- | --- | --- |
| Vazamento do banco expõe senhas | Senhas guardadas só como hash scrypt com sal único; parâmetros no hash permitem aumentar o custo depois | `seguranca/senhas.py` |
| Senhas fracas | Mínimo de 10 caracteres, bloqueio de senhas comuns e de senha que contém o e-mail | `seguranca/validacao.py` |
| Adivinhar senha (força bruta) | 20 tentativas por minuto por IP (IPv6 agrupado por /64); 5 erros no mesmo e-mail a partir do mesmo IP bloqueiam esse IP por 15 minutos; 20 erros no e-mail vindos de vários IPs bloqueiam navegadores desconhecidos | `seguranca/limite.py`, `seguranca/rede.py` |
| Estranho travar a conta do dono | O bloqueio por erros nunca vale para o navegador onde o dono já entrou (cookie de dispositivo assinado, ligado ao e-mail) | `seguranca/dispositivos.py` |
| Chutar a senha com uma sessão roubada | Troca de senha e exclusão de conta aceitam 5 senhas erradas a cada 15 minutos | `app.py` (`conferir_senha`) |
| Descobrir quem tem conta | Mesma mensagem e mesmo tempo de resposta para "e-mail não existe" e "senha errada" | `app.py` (`entrar`) |
| Roubo de sessão | Token aleatório de 256 bits em cookie `HttpOnly`, `Secure` e `SameSite=Strict`; banco guarda só o hash do token | `seguranca/sessoes.py` |
| Sessão esquecida aberta | Expira após 12 h sem uso ou 7 dias no total; logout encerra na hora; troca de senha derruba todas | `seguranca/sessoes.py` |
| CSRF (site falso agindo em nome do usuário) | Requisições que mudam dados com o cookie de sessão só são aceitas das origens configuradas | `seguranca/protecao_http.py` |
| XSS, clickjacking, vazamento de referer | Cabeçalhos CSP, `X-Frame-Options`, `nosniff`, `Referrer-Policy`, HSTS e `Cache-Control: no-store` | `seguranca/protecao_http.py` |
| Dados malformados ou maliciosos | CNPJ com dígito verificador, e-mail validado, ramos e UFs só de listas fechadas, palavras-chave limpas e limitadas | `seguranca/validacao.py`, `app.py` |
| Esgotar a memória com pedidos enormes | Corpo de até 64 KB, contado byte a byte (vale também para envio em pedaços, sem Content-Length) | `seguranca/protecao_http.py` |
| Esgotar a memória ou a CPU com milhões de e-mails inventados | Contadores vencidos são apagados; teto de 100 mil chaves por contador, com custo constante por operação | `seguranca/limite.py` |
| Pedidos simultâneos corrompendo dados | Uma conexão com o banco por pedido, espera de até 10 s quando o banco está ocupado, e-mail repetido vira 409 | `banco.py` |
| IP falso no cabeçalho | `X-Forwarded-For` só é aceito quando vem dos proxies listados em `RADAR_PROXIES` | `seguranca/rede.py` |
| SQL injection | Todas as consultas usam parâmetros, sem SQL montado com texto | `banco.py` |
| Senha devolvida em mensagem de erro | Erros de validação mostram só o campo e o motivo, nunca o valor enviado | `app.py` |
| Segredos no código | Configuração só por variáveis de ambiente; a API não sobe sem `RADAR_SEGREDO` forte | `config.py` |
| Rastreamento de incidentes | Log de auditoria de cadastro, login, falha, bloqueio, troca de senha, exportação e exclusão | `seguranca/auditoria.py` |
| Revelar a tecnologia usada | Erros no formato próprio `{"erro": ...}`; servidor iniciado sem o cabeçalho `Server` | `app.py` |

## LGPD

- **Consentimento:** o cadastro exige aceite dos termos; a versão e a data ficam salvas.
- **Minimização:** guardamos só e-mail, CNPJ, ramos, UFs e palavras-chave.
- **Acesso (art. 18):** `GET /eu/dados` devolve tudo o que temos da conta.
- **Eliminação (art. 18):** `DELETE /eu`, com confirmação de senha, apaga a conta e as sessões.
- **Logs sem dados pessoais:** e-mail mascarado (`c***@e***.com.br`), IP cortado em /24 e usuário como hash.

## Rotas

| Método | Rota | Login? | O que faz |
| --- | --- | --- | --- |
| POST | `/conta` | Não | Cria a conta e já abre sessão |
| POST | `/sessao` | Não | Login |
| DELETE | `/sessao` | Sim | Logout |
| GET | `/eu` | Sim | Perfil e filtros |
| PUT | `/eu/senha` | Sim | Troca a senha e encerra as outras sessões |
| GET | `/eu/dados` | Sim | Exporta os dados (LGPD) |
| DELETE | `/eu` | Sim | Exclui a conta (LGPD) |

## Como rodar

```bash
pip install -r requirements.txt
export RADAR_SEGREDO="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export RADAR_ORIGENS="http://localhost:3000"   # endereço do painel web
export RADAR_HTTPS=0                           # só em desenvolvimento local
export RADAR_PROXIES=""                         # IPs do proxy/balanceador, se houver
uvicorn radar.app:app --reload --no-server-header --no-proxy-headers
python -m pytest -q                            # testes
```

## Antes de ir para produção

- [ ] Servir só por HTTPS (`RADAR_HTTPS=1`, o padrão) e configurar `RADAR_ORIGENS` com o domínio real.
- [ ] Trocar os contadores em memória por Redis se houver mais de uma instância da API.
- [ ] Atrás de proxy ou CDN, preencher `RADAR_PROXIES` com os IPs dele (senão todos os usuários parecem um só IP).
- [ ] Avisar o dono por e-mail quando a conta dele for bloqueada por tentativas erradas.
- [ ] Confirmação de e-mail no cadastro e recuperação de senha por link de uso único.
- [ ] Checar senhas contra vazamentos conhecidos (Have I Been Pwned, consulta k-anonymity).
- [ ] Backup criptografado do banco e política de retenção dos logs de auditoria.
- [ ] Termos de uso e política de privacidade publicados, com encarregado (DPO) definido.
- [ ] Autenticação em dois fatores para o plano de licenças (consultorias).

## Teste de segurança de 16/11/2026

A API foi atacada ao vivo com 20 ataques. Os 5 problemas mais graves e as falhas 7 (em parte) e 9 foram corrigidos e retestados ao vivo. Cada um ganhou um teste automático em `tests/test_ataques.py`, para não voltar.

| # | Falha | Gravidade | Situação |
| --- | --- | --- | --- |
| 1 | Pedidos simultâneos davam erro 500 (9 de 10 cadastros) | Alta | Corrigida |
| 2 | 5 senhas erradas de um estranho travavam o dono | Alta | Corrigida |
| 3 | Corpo em pedaços (chunked) passava do limite de 64 KB | Média | Corrigida |
| 4 | Contadores de tentativa cresciam sem fim (172 MB com 200 mil e-mails) | Média | Corrigida |
| 5 | Chutes ilimitados da senha em troca de senha e exclusão | Média | Corrigida |
| 6 | Qualquer pessoa cadastra o CNPJ de outra empresa | Média | Aberta: exige verificação de vínculo |
| 7 | Limite por IP frágil (IPv6, proxy, spray de senha) | Média | Em parte: IPv6 /64 e proxies confiáveis corrigidos; spray segue limitado só por IP |
| 8 | Cadastro revela se o e-mail já tem conta | Baixa | Aberta: resolver junto com a confirmação de e-mail |
| 9 | Servidor revela a tecnologia usada | Baixa | Corrigida |
| 10 | Falha nova, achada no reteste: acima de 100 mil chaves, a limpeza dos contadores travava a CPU | Média | Corrigida |
