"""Sessões no servidor: o token vai para o usuário, só o hash dele fica no banco.

Vantagens sobre um token assinado (JWT): dá para encerrar uma sessão na hora
(logout, troca de senha, exclusão da conta) e um vazamento do banco não
entrega tokens válidos.
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

DURACAO_MAXIMA = timedelta(days=7)
INATIVIDADE_MAXIMA = timedelta(hours=12)


def _agora() -> datetime:
    return datetime.now(timezone.utc)


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def criar(conexao, usuario_id: int) -> str:
    token = secrets.token_urlsafe(32)
    agora = _agora()
    conexao.execute(
        "INSERT INTO sessoes (token_hash, usuario_id, criada, ultimo_uso, expira) VALUES (?, ?, ?, ?, ?)",
        (_hash(token), usuario_id, agora.isoformat(), agora.isoformat(),
         (agora + DURACAO_MAXIMA).isoformat()),
    )
    return token


def validar(conexao, token: str | None) -> int | None:
    """Devolve o ID do usuário dono do token, ou None se inválido/expirado."""
    if not token or len(token) > 100:
        return None
    linha = conexao.execute(
        "SELECT usuario_id, ultimo_uso, expira FROM sessoes WHERE token_hash = ?", (_hash(token),)
    ).fetchone()
    if linha is None:
        return None
    agora = _agora()
    if agora >= datetime.fromisoformat(linha["expira"]) or \
            agora - datetime.fromisoformat(linha["ultimo_uso"]) >= INATIVIDADE_MAXIMA:
        encerrar(conexao, token)
        return None
    conexao.execute(
        "UPDATE sessoes SET ultimo_uso = ? WHERE token_hash = ?", (agora.isoformat(), _hash(token))
    )
    return linha["usuario_id"]


def encerrar(conexao, token: str) -> None:
    conexao.execute("DELETE FROM sessoes WHERE token_hash = ?", (_hash(token),))


def encerrar_todas(conexao, usuario_id: int) -> None:
    conexao.execute("DELETE FROM sessoes WHERE usuario_id = ?", (usuario_id,))
