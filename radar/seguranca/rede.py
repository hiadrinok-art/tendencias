"""Descobre o IP real do cliente e a chave usada nos limites por IP.

- ``X-Forwarded-For`` só é lido quando o pedido vem de um proxy configurado
  como confiável (``RADAR_PROXIES``). Sem isso, atrás de um proxy todos os
  usuários pareceriam um só IP; e, confiando em qualquer um, o atacante
  inventaria um IP novo a cada tentativa.
- IPv6 é agrupado por /64: uma única conexão doméstica recebe trilhões de
  endereços, que de outra forma burlariam o limite por IP.
"""

from __future__ import annotations

import ipaddress


def ip_real(ip_conexao: str, x_forwarded_for: str | None, proxies_confiaveis: set[str]) -> str:
    entradas = [p.strip() for p in (x_forwarded_for or "").split(",") if p.strip()]
    if "*" in proxies_confiaveis:
        # Hospedagens como o Render: o app só é alcançável pelo proxy da
        # plataforma, cujos IPs mudam. Vale o último IP da lista, que é o que
        # o proxy viu; o que o cliente escreveu fica à esquerda e é ignorado.
        return entradas[-1] if entradas else ip_conexao
    if ip_conexao not in proxies_confiaveis or not x_forwarded_for:
        return ip_conexao
    # Lê da direita para a esquerda: cada proxy acrescenta o IP de quem o chamou.
    for candidato in reversed([p.strip() for p in x_forwarded_for.split(",") if p.strip()]):
        if candidato not in proxies_confiaveis:
            return candidato
    return ip_conexao


def chave_de_limite(ip: str) -> str:
    try:
        endereco = ipaddress.ip_address(ip)
    except ValueError:
        return ip or "desconhecido"
    if endereco.version == 6:
        return str(ipaddress.ip_network(f"{ip}/64", strict=False))
    return ip
