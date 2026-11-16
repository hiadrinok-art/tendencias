"""Hash e verificação de senhas com scrypt (biblioteca padrão do Python).

Formato salvo no banco: ``scrypt$<n>$<r>$<p>$<sal_b64>$<hash_b64>``.
Os parâmetros ficam junto do hash para permitir aumentar o custo no futuro
sem invalidar senhas antigas (ver ``precisa_rehash``).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

N = 2**14
R = 8
P = 1
TAMANHO_SAL = 16
TAMANHO_HASH = 32
_MAXMEM = 64 * 1024 * 1024


def _b64(dados: bytes) -> str:
    return base64.urlsafe_b64encode(dados).decode().rstrip("=")


def _unb64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


def _derivar(senha: str, sal: bytes, n: int, r: int, p: int) -> bytes:
    return hashlib.scrypt(
        senha.encode("utf-8"), salt=sal, n=n, r=r, p=p, maxmem=_MAXMEM, dklen=TAMANHO_HASH
    )


def gerar_hash(senha: str) -> str:
    sal = secrets.token_bytes(TAMANHO_SAL)
    chave = _derivar(senha, sal, N, R, P)
    return f"scrypt${N}${R}${P}${_b64(sal)}${_b64(chave)}"


def verificar(senha: str, hash_salvo: str) -> bool:
    try:
        algoritmo, n, r, p, sal, chave = hash_salvo.split("$")
        if algoritmo != "scrypt":
            return False
        calculada = _derivar(senha, _unb64(sal), int(n), int(r), int(p))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(calculada, _unb64(chave))


def precisa_rehash(hash_salvo: str) -> bool:
    try:
        _, n, r, p, _, _ = hash_salvo.split("$")
    except ValueError:
        return True
    return (int(n), int(r), int(p)) != (N, R, P)


# Hash de uma senha aleatória, usado para gastar o mesmo tempo quando o
# e-mail não existe. Assim o tempo de resposta não revela quem tem conta.
HASH_FICTICIO = gerar_hash(secrets.token_urlsafe(16))
