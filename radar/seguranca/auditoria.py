"""Registro de eventos de segurança sem expor dados pessoais (LGPD).

E-mails e IPs são mascarados antes de ir para o log; o ID do usuário é
guardado como hash para que o histórico continue útil mesmo após a conta ser
excluída, sem permitir identificar a pessoa.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
import logging
from datetime import datetime, timezone

log = logging.getLogger("radar.auditoria")


def mascarar_email(email: str) -> str:
    if "@" not in (email or ""):
        return "***"
    usuario, dominio = email.split("@", 1)
    nome_dom, _, tld = dominio.partition(".")
    return f"{usuario[:1]}***@{nome_dom[:1]}***.{tld}" if tld else f"{usuario[:1]}***@***"


def mascarar_ip(ip: str) -> str:
    try:
        endereco = ipaddress.ip_address(ip)
    except ValueError:
        return "desconhecido"
    prefixo = 24 if endereco.version == 4 else 48
    return str(ipaddress.ip_network(f"{ip}/{prefixo}", strict=False))


def id_anonimo(usuario_id: int | str | None, segredo: str) -> str | None:
    if usuario_id is None:
        return None
    return hashlib.sha256(f"{segredo}:{usuario_id}".encode()).hexdigest()[:16]


def registrar(conexao, evento: str, *, segredo: str, usuario_id=None, email: str = "",
              ip: str = "", detalhe: str = "") -> None:
    linha = {
        "quando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "evento": evento,
        "usuario": id_anonimo(usuario_id, segredo),
        "email": mascarar_email(email) if email else None,
        "ip": mascarar_ip(ip) if ip else None,
        "detalhe": detalhe[:200] or None,
    }
    conexao.execute(
        "INSERT INTO auditoria (quando, evento, usuario, email, ip, detalhe) VALUES (?, ?, ?, ?, ?, ?)",
        (linha["quando"], evento, linha["usuario"], linha["email"], linha["ip"], linha["detalhe"]),
    )
    log.info(json.dumps(linha, ensure_ascii=False))
