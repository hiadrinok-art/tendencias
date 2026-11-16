"""Validação de dados vindos do usuário: CNPJ, e-mail, senha e palavras-chave."""

from __future__ import annotations

import re
import unicodedata

_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,24}$")

# Pequena lista das senhas mais vazadas. Em produção, complementar com a
# consulta k-anonymity do Have I Been Pwned.
SENHAS_COMUNS = {
    "123456", "123456789", "12345678", "1234567890", "senha123", "password",
    "qwerty123", "abc123456", "11111111", "00000000", "senha1234", "mudar123",
    "brasil123", "admin123", "iloveyou", "1q2w3e4r", "1q2w3e4r5t", "123mudar",
}

TAMANHO_MIN_SENHA = 10
TAMANHO_MAX_SENHA = 128


def so_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def cnpj_valido(cnpj: str) -> bool:
    """Confere os dois dígitos verificadores do CNPJ (formato numérico)."""
    d = so_digitos(cnpj)
    if len(d) != 14 or d == d[0] * 14:
        return False

    def digito(base: str, pesos: list[int]) -> str:
        resto = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    dv1 = digito(d[:12], pesos1)
    dv2 = digito(d[:12] + dv1, pesos2)
    return d[12:] == dv1 + dv2


def normalizar_email(email: str) -> str:
    return (email or "").strip().lower()


def email_valido(email: str) -> bool:
    email = normalizar_email(email)
    return len(email) <= 254 and bool(_EMAIL.match(email))


def problemas_da_senha(senha: str, email: str = "") -> list[str]:
    """Lista os motivos de recusa da senha (vazia = senha aceita)."""
    problemas = []
    if len(senha) < TAMANHO_MIN_SENHA:
        problemas.append(f"Use pelo menos {TAMANHO_MIN_SENHA} caracteres.")
    if len(senha) > TAMANHO_MAX_SENHA:
        problemas.append(f"Use no máximo {TAMANHO_MAX_SENHA} caracteres.")
    if senha.lower() in SENHAS_COMUNS:
        problemas.append("Essa senha é muito comum e aparece em vazamentos.")
    if len(set(senha)) < 4:
        problemas.append("Use mais variedade de caracteres.")
    usuario = normalizar_email(email).split("@")[0]
    if len(usuario) >= 4 and usuario in senha.lower():
        problemas.append("A senha não pode conter o seu e-mail.")
    return problemas


def limpar_texto(texto: str, tamanho_max: int) -> str:
    """Remove caracteres de controle e espaços repetidos; corta no tamanho máximo."""
    texto = unicodedata.normalize("NFC", texto or "")
    texto = "".join(" " if c.isspace() else c for c in texto)
    texto = "".join(c for c in texto if unicodedata.category(c)[0] != "C")
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:tamanho_max]


def limpar_palavras_chave(palavras: list[str], maximo: int = 10, tamanho: int = 40) -> list[str]:
    vistas: list[str] = []
    for p in palavras:
        p = limpar_texto(p, tamanho).lower()
        if p and p not in vistas:
            vistas.append(p)
        if len(vistas) == maximo:
            break
    return vistas
