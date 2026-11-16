"""Cookie de "dispositivo confiável", contra o bloqueio de contas por terceiros.

Antes, 5 senhas erradas para um e-mail bloqueavam a conta para todo mundo,
inclusive para o dono com a senha certa. Agora:

- erros vindos de um IP bloqueiam só aquele IP para aquele e-mail;
- um bloqueio geral do e-mail (ataque distribuído) não vale para o
  navegador onde o dono já entrou antes, identificado por este cookie.

O cookie é assinado com HMAC e amarrado ao e-mail: não dá para forjar nem
reaproveitar em outra conta. Técnica recomendada pela OWASP ("device cookies").
"""

from __future__ import annotations

import hashlib
import hmac
import secrets

NOME_COOKIE = "radar_dispositivo"
DURACAO_SEGUNDOS = 180 * 24 * 3600


def _assinatura(segredo: str, email: str, nonce: str) -> str:
    return hmac.new(segredo.encode(), f"dispositivo|{email}|{nonce}".encode(), hashlib.sha256).hexdigest()


def emitir(segredo: str, email: str) -> str:
    nonce = secrets.token_urlsafe(16)
    return f"{nonce}.{_assinatura(segredo, email, nonce)}"


def confiavel(segredo: str, email: str, valor: str | None) -> bool:
    if not valor or "." not in valor or len(valor) > 200:
        return False
    nonce, assinatura = valor.split(".", 1)
    return hmac.compare_digest(assinatura, _assinatura(segredo, email, nonce))
