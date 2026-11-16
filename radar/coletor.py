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
# Modalidades em que fornecedores disputam (códigos do PNCP).
MODALIDADES = {
    6: "Pregão eletrônico",
    4: "Concorrência eletrônica",
    8: "Dispensa de licitação",
    5: "Concorrência presencial",
    7: "Pregão presencial",
    12: "Credenciamento",
}
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
        "ano": ano,
        "sequencial": sequencial,
    }


def gravar(conexao, linhas: list[dict]) -> int:
    linhas = [l for l in linhas if l]
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


class PncpFalhou(RuntimeError):
    pass


PAUSA_ENTRE_PAGINAS = 0.4   # segundos; evita o bloqueio "429 Too Many Requests" do PNCP
ESPERA_MAXIMA = 90          # segundos numa única espera


def _espera(resposta: httpx.Response | None, tentativa: int) -> float:
    """Usa o Retry-After do PNCP quando vier; senão, espera crescente (2, 4, 8... s)."""
    if resposta is not None:
        pedido = resposta.headers.get("retry-after", "")
        if pedido.isdigit():
            return min(int(pedido), ESPERA_MAXIMA)
    return min(2 ** (tentativa + 1), ESPERA_MAXIMA)


def _pagina(cliente: httpx.Client, params: dict, tentativas: int = 7, dormir=time.sleep, url: str = URL_PNCP) -> dict:
    for tentativa in range(tentativas):
        resposta = None
        try:
            resposta = cliente.get(url, params=params)
            if resposta.status_code == 204:
                return {"data": [], "totalPaginas": 0}
            resposta.raise_for_status()
            return resposta.json()
        except (httpx.HTTPError, ValueError) as erro:
            espera = _espera(resposta, tentativa)
            log.warning("PNCP falhou (%s), tentando de novo em %ss", type(erro).__name__, espera)
            dormir(espera)
    raise PncpFalhou(f"PNCP não respondeu à página {params.get('pagina')} depois de {tentativas} tentativas")


def coletar(caminho_banco: str, dias: int = 3, max_paginas: int = 100, dormir=time.sleep,
            cliente: httpx.Client | None = None, limite_segundos: float | None = None,
            relogio=time.monotonic) -> int:
    """Coleta todas as modalidades. Uma página que falhe é pulada (e registrada), sem
    perder o resto; só falha de vez se nada for coletado. Com ``limite_segundos``,
    para ao atingir o tempo e fica com o que já coletou (as modalidades mais
    importantes vêm primeiro em MODALIDADES)."""
    inicio_relogio = relogio()
    banco.preparar(caminho_banco)
    conexao = banco.conectar(caminho_banco)
    fim = date.today()
    inicio = fim - timedelta(days=dias)
    total, falhas = 0, 0
    dono = cliente is None
    cliente = cliente or httpx.Client(timeout=60, headers={"User-Agent": "radar-de-editais/0.1"})
    try:
        for modalidade in MODALIDADES:
            pagina, total_paginas = 1, 1
            while pagina <= min(total_paginas, max_paginas):
                if limite_segundos is not None and relogio() - inicio_relogio > limite_segundos:
                    log.warning("Limite de tempo atingido: parando com %s editais.", total)
                    return _encerrar(total, falhas)
                try:
                    dados = _pagina(cliente, {
                        "dataInicial": inicio.strftime("%Y%m%d"), "dataFinal": fim.strftime("%Y%m%d"),
                        "codigoModalidadeContratacao": modalidade, "pagina": pagina,
                        "tamanhoPagina": TAMANHO_PAGINA,
                    }, dormir=dormir)
                except PncpFalhou as erro:
                    falhas += 1
                    log.error("%s (modalidade %s). Pulando.", erro, modalidade)
                    if pagina == 1:
                        break  # sem a 1ª página não sabemos quantas existem
                    pagina += 1
                    continue
                total_paginas = int(dados.get("totalPaginas") or 0)
                linhas = [l for l in (converter(b, modalidade) for b in dados.get("data") or []) if l]
                total += gravar(conexao, linhas)
                log.info("modalidade %s, página %s/%s: %s editais", modalidade, pagina, total_paginas, len(linhas))
                pagina += 1
                dormir(PAUSA_ENTRE_PAGINAS)
    finally:
        conexao.close()
        if dono:
            cliente.close()
    return _encerrar(total, falhas)


def _encerrar(total: int, falhas: int) -> int:
    if total == 0 and falhas:
        raise PncpFalhou("Nenhum edital coletado: o PNCP não respondeu.")
    if falhas:
        log.warning("Coleta terminou com %s página(s) puladas.", falhas)
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
