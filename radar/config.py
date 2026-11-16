"""Configuração lida de variáveis de ambiente. Nenhum segredo fica no código."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


class ConfiguracaoInvalida(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    segredo: str
    banco: str = "radar.db"
    https: bool = True
    origens: list[str] = field(default_factory=list)
    nome_cookie: str = "radar_sessao"
    versao_termos: str = "2026-11"

    @classmethod
    def do_ambiente(cls) -> "Config":
        segredo = os.environ.get("RADAR_SEGREDO", "")
        if len(segredo) < 32:
            raise ConfiguracaoInvalida(
                "Defina RADAR_SEGREDO com pelo menos 32 caracteres aleatórios "
                "(ex.: python -c 'import secrets; print(secrets.token_urlsafe(48))')."
            )
        origens = [o.strip() for o in os.environ.get("RADAR_ORIGENS", "").split(",") if o.strip()]
        return cls(
            segredo=segredo,
            banco=os.environ.get("RADAR_BANCO", "radar.db"),
            https=os.environ.get("RADAR_HTTPS", "1") != "0",
            origens=origens,
        )
