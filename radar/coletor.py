"""Coletor do PNCP: baixa editais publicados, limpa os dados e grava no banco.

Uso:
    RADAR_BANCO=radar.db python -m radar.coletor --dias 3

Os dados do PNCP vêm de fora e são tratados como não confiáveis: textos são
limpos e cortados, números e datas validados, e só links https para domínios
conhecidos são guardados (um link "javascript:" no portal viraria um ataque
XSS no painel).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
from datetime import date, datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx

from . import banco
from .classificador import classificar
from .seguranca.validacao import cnpj_valido, limpar_texto, so_digitos

log = logging.getLogger("radar.coletor")

URL_PNCP = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MODALIDADES = {6: "Pregão eletrônico", 4: "Concorrência eletrônica"}
TAMANHO_PAGINA = 50
UFS = {"AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
       "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"}
# Domínios de sistemas de compras aceitos como link de origem.
DOMINIOS_LINK = ("gov.br", "serpro.gov.br", "bll.org.br", "bnc.org.br", "licitanet.com.br",
                 "portaldecompraspublicas.com.br", "bbmnet.com.br", "comprasbr.com.br")


def link_seguro(url: str | None) -> str | None:
    if not url or len(url) > 500:
        return None
    partes = urlparse(url.strip())
    host = (partes.hostname or "").lower()
    if partes.scheme != "https" or not any(host == d or host.endswith("." + d) for d in DOMINIOS_LINK):
        return None
    return url.strip()


def _data(texto: str | None) -> str | None:
    if not texto:
        return None
    try:
        return datetime.fromisoformat(texto[:19]).isoformat()
    except ValueError:
        return None


def _valor(numero) -> float | None:
    try:
        v = float(numero)
    except (TypeError, ValueError):
        return None
    return v if 0 < v < 1e13 else None


def converter(bruto: dict, modalidade: int) -> dict | None:
    """Transforma um registro do PNCP numa linha limpa, ou None se inválido."""
    orgao = bruto.get("orgaoEntidade") or {}
    unidade = bruto.get("unidadeOrgao") or {}
    cnpj = so_digitos(orgao.get("cnpj", ""))
    controle = limpar_texto(bruto.get("numeroControlePNCP", ""), 60)
    uf = (unidade.get("ufSigla") or "").upper()
    objeto = limpar_texto(bruto.get("objetoCompra", ""), 2000)
    try:
        ano, sequencial = int(bruto["anoCompra"]), int(bruto["sequencialCompra"])
    except (KeyError, TypeError, ValueError):
        return None
    if not controle or not objeto or uf not in UFS or not cnpj_valido(cnpj):
        return None
    return {
        "id": controle,
        "orgao": limpar_texto(orgao.get("razaoSocial", ""), 200),
        "orgao_cnpj": cnpj,
        "unidade": limpar_texto(unidade.get("nomeUnidade", ""), 200),
        "municipio": limpar_texto(unidade.get("municipioNome", ""), 100),
        "uf": uf,
        "modalidade": MODALIDADES.get(modalidade, limpar_texto(bruto.get("modalidadeNome", ""), 60)),
        "objeto": objeto,
        "valor_estimado": _valor(bruto.get("valorTotalEstimado")),
        "abertura": _data(bruto.get("dataAberturaProposta")),
        "encerramento": _data(bruto.get("dataEncerramentoProposta")),
        "publicado": _data(bruto.get("dataPublicacaoPncp")),
        "link_origem": link_seguro(bruto.get("linkSistemaOrigem")),
        "link_pncp": f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{sequencial}",
        "ramos": json.dumps(classificar(objeto)),
    }


def gravar(conexao, linhas: list[dict]) -> int:
    if not linhas:
        return 0
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    colunas = list(linhas[0].keys()) + ["coletado_em"]
    sql = (f"INSERT INTO editais ({', '.join(colunas)}) VALUES ({', '.join('?' * len(colunas))}) "
           f"ON CONFLICT(id) DO UPDATE SET " +
           ", ".join(f"{c} = excluded.{c}" for c in colunas if c != "id"))
    with banco.transacao(conexao):
        conexao.executemany(sql, [[l[c] for c in colunas[:-1]] + [agora] for l in linhas])
    return len(linhas)


def _pagina(cliente: httpx.Client, params: dict, tentativas: int = 4) -> dict:
    for tentativa in range(tentativas):
        try:
            r = cliente.get(URL_PNCP, params=params)
            if r.status_code == 204:
                return {"data": [], "totalPaginas": 0}
            r.raise_for_status()
            return r.json()
        except (httpx.HTTPError, ValueError) as erro:
            espera = 2 ** tentativa
            log.warning("PNCP falhou (%s), tentando de novo em %ss", erro, espera)
            time.sleep(espera)
    raise RuntimeError("PNCP indisponível depois de várias tentativas")


def coletar(caminho_banco: str, dias: int = 3, max_paginas: int = 100) -> int:
    banco.preparar(caminho_banco)
    conexao = banco.conectar(caminho_banco)
    fim = date.today()
    inicio = fim - timedelta(days=dias)
    total = 0
    with httpx.Client(timeout=60, headers={"User-Agent": "radar-de-editais/0.1"}) as cliente:
        for modalidade in MODALIDADES:
            pagina, total_paginas = 1, 1
            while pagina <= min(total_paginas, max_paginas):
                dados = _pagina(cliente, {
                    "dataInicial": inicio.strftime("%Y%m%d"), "dataFinal": fim.strftime("%Y%m%d"),
                    "codigoModalidadeContratacao": modalidade, "pagina": pagina,
                    "tamanhoPagina": TAMANHO_PAGINA,
                })
                total_paginas = int(dados.get("totalPaginas") or 0)
                linhas = [l for l in (converter(b, modalidade) for b in dados.get("data") or []) if l]
                total += gravar(conexao, linhas)
                log.info("modalidade %s, página %s/%s: %s editais", modalidade, pagina, total_paginas, len(linhas))
                pagina += 1
    conexao.close()
    return total


def reclassificar(caminho_banco: str) -> int:
    """Refaz a classificação de todos os editais (depois de mudar o classificador)."""
    conexao = banco.conectar(caminho_banco)
    try:
        linhas = conexao.execute("SELECT id, objeto FROM editais").fetchall()
        with banco.transacao(conexao):
            conexao.executemany("UPDATE editais SET ramos = ? WHERE id = ?",
                                [(json.dumps(classificar(l["objeto"])), l["id"]) for l in linhas])
        return len(linhas)
    finally:
        conexao.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    p = argparse.ArgumentParser(description="Coleta editais do PNCP")
    p.add_argument("--dias", type=int, default=3)
    p.add_argument("--max-paginas", type=int, default=100)
    p.add_argument("--reclassificar", action="store_true", help="só refaz a classificação por ramo")
    args = p.parse_args()
    if args.reclassificar:
        log.info("%s editais reclassificados.", reclassificar(os.environ.get("RADAR_BANCO", "radar.db")))
        return
    n = coletar(os.environ.get("RADAR_BANCO", "radar.db"), args.dias, args.max_paginas)
    log.info("Pronto: %s editais gravados ou atualizados.", n)


if __name__ == "__main__":
    main()
