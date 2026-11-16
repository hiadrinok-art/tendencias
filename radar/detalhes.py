"""Itens e documentos de um edital, buscados no PNCP sob demanda (com cache).

O endereço consultado é montado só com dados do nosso banco (CNPJ, ano e
sequencial já validados na coleta), nunca com texto vindo do usuário, então a
API não pode ser usada para acessar endereços arbitrários (SSRF).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import httpx

from .seguranca.validacao import limpar_texto

URL_BASE = "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}"
VALIDADE_CACHE = timedelta(hours=6)
MAX_ITENS = 300
TIPOS = ("itens", "arquivos")


class PncpIndisponivel(RuntimeError):
    pass


def _numero(valor) -> float | None:
    try:
        v = float(valor)
    except (TypeError, ValueError):
        return None
    return v if 0 <= v < 1e13 else None


def _link_pncp(url) -> str | None:
    if isinstance(url, str) and url.startswith("https://pncp.gov.br/") and len(url) < 400:
        return url
    return None


def limpar_itens(brutos: list) -> list[dict]:
    itens = []
    for b in brutos[:MAX_ITENS]:
        if not isinstance(b, dict):
            continue
        beneficio = limpar_texto(b.get("tipoBeneficioNome") or "", 80)
        itens.append({
            "numero": b.get("numeroItem") if isinstance(b.get("numeroItem"), int) else None,
            "descricao": limpar_texto(b.get("descricao") or "", 500),
            "quantidade": _numero(b.get("quantidade")),
            "unidade": limpar_texto(b.get("unidadeMedida") or "", 40),
            "valor_unitario": _numero(b.get("valorUnitarioEstimado")),
            "valor_total": _numero(b.get("valorTotal")),
            "tipo": limpar_texto(b.get("materialOuServicoNome") or "", 20),
            "beneficio": beneficio,
            "exclusivo_me_epp": "exclusiva" in beneficio.lower(),
            "situacao": limpar_texto(b.get("situacaoCompraItemNome") or "", 40),
        })
    return itens


def limpar_arquivos(brutos: list) -> list[dict]:
    arquivos = []
    for b in brutos[:100]:
        if not isinstance(b, dict) or b.get("statusAtivo") is False:
            continue
        url = _link_pncp(b.get("url"))
        if not url:
            continue
        arquivos.append({
            "titulo": limpar_texto(b.get("titulo") or "Documento", 200),
            "tipo": limpar_texto(b.get("tipoDocumentoNome") or "", 80),
            "publicado": limpar_texto(b.get("dataPublicacaoPncp") or "", 19),
            "url": url,
        })
    return arquivos


def _baixar(edital, tipo: str, cliente: httpx.Client | None) -> list:
    url = URL_BASE.format(cnpj=edital["orgao_cnpj"], ano=int(edital["ano"]), seq=int(edital["sequencial"]))
    url += "/itens" if tipo == "itens" else "/arquivos"
    params = {"pagina": 1, "tamanhoPagina": MAX_ITENS} if tipo == "itens" else None
    dono = cliente is None
    cliente = cliente or httpx.Client(timeout=20, headers={"User-Agent": "radar-de-editais/0.1"})
    try:
        r = cliente.get(url, params=params)
        if r.status_code in (204, 404):
            return []
        r.raise_for_status()
        dados = r.json()
        return dados if isinstance(dados, list) else []
    except (httpx.HTTPError, ValueError) as erro:
        raise PncpIndisponivel(str(erro)) from erro
    finally:
        if dono:
            cliente.close()


def obter(conexao, edital, tipo: str, cliente: httpx.Client | None = None) -> list[dict]:
    """Devolve itens ou arquivos do edital, do cache ou do PNCP."""
    if tipo not in TIPOS:
        raise ValueError(tipo)
    if edital["ano"] is None or edital["sequencial"] is None:
        return []
    agora = datetime.now(timezone.utc)
    cache = conexao.execute(
        "SELECT conteudo, buscado_em FROM detalhes_pncp WHERE edital_id = ? AND tipo = ?",
        (edital["id"], tipo)).fetchone()
    if cache and agora - datetime.fromisoformat(cache["buscado_em"]) < VALIDADE_CACHE:
        return json.loads(cache["conteudo"])

    brutos = _baixar(edital, tipo, cliente)
    limpos = limpar_itens(brutos) if tipo == "itens" else limpar_arquivos(brutos)
    conexao.execute(
        "INSERT INTO detalhes_pncp (edital_id, tipo, conteudo, buscado_em) VALUES (?, ?, ?, ?) "
        "ON CONFLICT(edital_id, tipo) DO UPDATE SET conteudo = excluded.conteudo, buscado_em = excluded.buscado_em",
        (edital["id"], tipo, json.dumps(limpos, ensure_ascii=False), agora.isoformat(timespec="seconds")))
    return limpos
