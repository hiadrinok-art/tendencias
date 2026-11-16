# Segurança do Radar de Editais

Este documento resume como a API protege as contas e os dados das empresas. O código fica em `radar/seguranca/`, e os testes em `tests/` comprovam cada item.

## O que está protegido

| Ameaça | Proteção | Onde |
| --- | --- | --- |
| Vazamento do banco expõe senhas | Senhas guardadas só como hash scrypt com sal único; parâmetros no hash permitem aumentar o custo depois | `seguranca/senhas.py` |
| Senhas fracas | Mínimo de 10 caracteres, bloqueio de senhas comuns e de senha que contém o e-mail | `seguranca/validacao.py` |
| Adivinhar senha (força bruta) | 20 tentativas por minuto por IP; 5 erros no mesmo e-mail bloqueiam por 15 minutos | `seguranca/limite.py` |
| Descobrir quem tem conta | Mesma mensagem e mesmo tempo de resposta para "e-mail não existe" e "senha errada" | `app.py` (`entrar`) |
| Roubo de sessão | Token aleatório de 256 bits em cookie `HttpOnly`, `Secure` e `SameSite=Strict`; banco guarda só o hash do token | `seguranca/sessoes.py` |
| Sessão esquecida aberta | Expira após 12 h sem uso ou 7 dias no total; logout encerra na hora; troca de senha derruba todas | `seguranca/sessoes.py` |
| CSRF (site falso agindo em nome do usuário) | Requisições que mudam dados com o cookie de sessão só são aceitas das origens configuradas | `seguranca/protecao_http.py` |
| XSS, clickjacking, vazamento de referer | Cabeçalhos CSP, `X-Frame-Options`, `nosniff`, `Referrer-Policy`, HSTS e `Cache-Control: no-store` | `seguranca/protecao_http.py` |
| Dados malformados ou maliciosos | CNPJ com dígito verificador, e-mail validado, ramos e UFs só de listas fechadas, palavras-chave limpas e limitadas, corpo de até 64 KB | `seguranca/validacao.py`, `app.py` |
| SQL injection | Todas as consultas usam parâmetros, sem SQL montado com texto | `banco.py` |
| Senha devolvida em mensagem de erro | Erros de validação mostram só o campo e o motivo, nunca o valor enviado | `app.py` |
| Segredos no código | Configuração só por variáveis de ambiente; a API não sobe sem `RADAR_SEGREDO` forte | `config.py` |
| Rastreamento de incidentes | Log de auditoria de cadastro, login, falha, bloqueio, troca de senha, exportação e exclusão | `seguranca/auditoria.py` |

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
uvicorn radar.app:app --reload
python -m pytest -q                            # testes
```

## Antes de ir para produção

- [ ] Servir só por HTTPS (`RADAR_HTTPS=1`, o padrão) e configurar `RADAR_ORIGENS` com o domínio real.
- [ ] Trocar os contadores em memória por Redis se houver mais de uma instância da API.
- [ ] Atrás de proxy ou CDN, ler o IP real do cabeçalho do proxy confiável, ou o limite por IP valerá para todos.
- [ ] Confirmação de e-mail no cadastro e recuperação de senha por link de uso único.
- [ ] Checar senhas contra vazamentos conhecidos (Have I Been Pwned, consulta k-anonymity).
- [ ] Backup criptografado do banco e política de retenção dos logs de auditoria.
- [ ] Termos de uso e política de privacidade publicados, com encarregado (DPO) definido.
- [ ] Autenticação em dois fatores para o plano de licenças (consultorias).
