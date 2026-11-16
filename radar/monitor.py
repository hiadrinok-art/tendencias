"""Monitor diário: mudanças nos processos acompanhados, atas novas e resumos.

Uso (depois da coleta de editais):
    RADAR_BANCO=dados/radar.db python -m radar.monitor

Gera "eventos" (que aparecem na página Alertas) e envia pelo WhatsApp os de
quem confirmou o número e ligou aquele tipo de alerta.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import time
from datetime import date, datetime, timedelta, timezone

import httpx

from . import banco, notificacoes
from .classificador import RAMOS, classificar
from .coletor import _pagina as pagina_consulta  # mesma política de espera do coletor
from .detalhes import limpar_arquivos
from .seguranca.validacao import cnpj_valido, limpar_texto, so_digitos

log = logging.getLogger("radar.monitor")

URL_COMPRA = "https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}"
URL_ARQUIVOS = "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos"
URL_ITENS = "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens"
URL_RESULTADOS = "https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens/{item}/resultados"
URL_ATAS = "https://pncp.gov.br/api/consulta/v1/atas/atualizacao"

MAX_WHATSAPP_POR_DIA = 15
SITE = os.environ.get("RADAR_SITE", "").rstrip("/")


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _link(caminho: str) -> str:
    return f"{SITE}{caminho}" if SITE else caminho


def _dinheiro(valor) -> str:
    if valor is None:
        return "valor não informado"
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def _plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def _data(iso: str | None) -> str:
    if not iso:
        return "sem data"
    d, _, h = iso.partition("T")
    ano, mes, dia = d.split("-")
    return f"{dia}/{mes}/{ano}" + (f" às {h[:5]}" if h else "")


def criar_evento(conexao, usuario_id: int, chave: str, tipo: str, titulo: str, texto: str,
                 link: str | None = None, edital_id: str | None = None) -> bool:
    """Grava o evento se for novo para o usuário. Devolve True se gravou."""
    cursor = conexao.execute(
        "INSERT OR IGNORE INTO eventos (usuario_id, chave, tipo, edital_id, titulo, texto, link, criado, whatsapp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendente')",
        (usuario_id, chave[:200], tipo, edital_id, limpar_texto(titulo, 200), texto[:1500], link, _agora()))
    return cursor.rowcount == 1


# ------------------------------------------------------------- processos

def _get(cliente: httpx.Client, url: str, params=None):
    r = cliente.get(url, params=params)
    if r.status_code in (204, 404):
        return None
    r.raise_for_status()
    return r.json()


def _resumo_resultados(cliente, edital) -> str:
    base = dict(cnpj=edital["orgao_cnpj"], ano=edital["ano"], seq=edital["sequencial"])
    itens = _get(cliente, URL_ITENS.format(**base), {"pagina": 1, "tamanhoPagina": 50}) or []
    linhas = []
    for item in itens[:5]:
        numero = item.get("numeroItem")
        if not isinstance(numero, int):
            continue
        resultados = _get(cliente, URL_RESULTADOS.format(**base, item=numero)) or []
        for r in resultados[:1]:
            nome = limpar_texto(r.get("nomeRazaoSocialFornecedor") or "fornecedor não informado", 80)
            linhas.append(f"Item {numero}: {nome}, {_dinheiro(r.get('valorTotalHomologado'))}")
    if len(itens) > 5:
        linhas.append(f"e mais {len(itens) - 5} itens")
    return "; ".join(linhas) or "Veja os vencedores no PNCP."


def verificar_processos(conexao, cliente: httpx.Client, dormir=time.sleep) -> int:
    """Compara cada edital acompanhado com a última verificação e gera eventos."""
    editais = conexao.execute(
        "SELECT DISTINCT e.* FROM editais e JOIN acompanhamentos a ON a.edital_id = e.id "
        "WHERE a.status NOT IN ('ganhou', 'perdeu') AND e.ano IS NOT NULL").fetchall()
    gerados = 0
    for e in editais:
        base = dict(cnpj=e["orgao_cnpj"], ano=e["ano"], seq=e["sequencial"])
        try:
            compra = _get(cliente, URL_COMPRA.format(**base)) or {}
            documentos = limpar_arquivos(_get(cliente, URL_ARQUIVOS.format(**base)) or [])
        except (httpx.HTTPError, ValueError) as erro:
            log.warning("Não deu para verificar %s: %s", e["id"], type(erro).__name__)
            continue
        situacao = limpar_texto(compra.get("situacaoCompraNome") or "", 60) or None
        encerramento = (compra.get("dataEncerramentoProposta") or "")[:19] or e["encerramento"]
        tem_resultado = bool(compra.get("existeResultado"))
        titulos = sorted({f"{d['tipo']}|{d['titulo']}" for d in documentos})
        antes = conexao.execute("SELECT * FROM processos_estado WHERE edital_id = ?", (e["id"],)).fetchone()

        eventos = []  # (chave, tipo, titulo, texto)
        objeto = e["objeto"][:90]
        if antes is not None:
            if situacao and antes["situacao"] and situacao != antes["situacao"]:
                eventos.append((f"situacao:{e['id']}:{situacao}", "situacao", f"Situação mudou: {situacao}",
                                f"{objeto} ({e['orgao'][:60]}). Antes: {antes['situacao']}."))
            if encerramento and antes["encerramento"] and encerramento != antes["encerramento"]:
                eventos.append((f"prazo:{e['id']}:{encerramento}", "prazo", "Prazo de propostas alterado",
                                f"{objeto}. De {_data(antes['encerramento'])} para {_data(encerramento)}."))
            novos = [t for t in titulos if t not in set(json.loads(antes["documentos"]))]
            for t in novos[:5]:
                tipo_doc, _, nome = t.partition("|")
                eventos.append((f"doc:{e['id']}:{t}", "documento", f"Novo documento: {tipo_doc or 'Documento'}",
                                f"{nome} — {objeto}."))
            if tem_resultado and not antes["tem_resultado"]:
                try:
                    resumo = _resumo_resultados(cliente, e)
                except (httpx.HTTPError, ValueError):
                    resumo = "Veja os vencedores no PNCP."
                eventos.append((f"resultado:{e['id']}", "resultado", "Resultado publicado", f"{objeto}. {resumo}"))

        conexao.execute(
            "INSERT INTO processos_estado (edital_id, situacao, encerramento, documentos, tem_resultado, verificado_em) "
            "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(edital_id) DO UPDATE SET situacao = excluded.situacao, "
            "encerramento = excluded.encerramento, documentos = excluded.documentos, "
            "tem_resultado = excluded.tem_resultado, verificado_em = excluded.verificado_em",
            (e["id"], situacao, encerramento, json.dumps(titulos, ensure_ascii=False), int(tem_resultado), _agora()))
        if encerramento != e["encerramento"]:
            conexao.execute("UPDATE editais SET encerramento = ? WHERE id = ?", (encerramento, e["id"]))

        if eventos:
            seguidores = conexao.execute(
                "SELECT a.usuario_id FROM acompanhamentos a LEFT JOIN alertas_config c ON c.usuario_id = a.usuario_id "
                "WHERE a.edital_id = ? AND COALESCE(c.processos, 1) = 1", (e["id"],)).fetchall()
            for s in seguidores:
                for chave, tipo, titulo, texto in eventos:
                    gerados += criar_evento(conexao, s["usuario_id"], chave, tipo, titulo, texto,
                                            _link("/ver?id=" + e["id"]), e["id"])
        dormir(0.3)
    return gerados


# ------------------------------------------------------------------ atas

def converter_ata(bruto: dict) -> dict | None:
    if not isinstance(bruto, dict) or bruto.get("cancelado"):
        return None
    cnpj = so_digitos(bruto.get("cnpjOrgao") or "")
    ata_id = limpar_texto(bruto.get("numeroControlePNCPAta") or "", 80)
    compra_id = limpar_texto(bruto.get("numeroControlePNCPCompra") or "", 60)
    objeto = limpar_texto(bruto.get("objetoContratacao") or "", 1000)
    if not ata_id or not compra_id or not objeto or not cnpj_valido(cnpj):
        return None
    return {
        "id": ata_id, "compra_id": compra_id,
        "numero": limpar_texto(bruto.get("numeroAtaRegistroPreco") or "", 40),
        "orgao": limpar_texto(bruto.get("nomeOrgao") or "", 200), "orgao_cnpj": cnpj, "objeto": objeto,
        "vigencia_inicio": (bruto.get("vigenciaInicio") or "")[:10] or None,
        "vigencia_fim": (bruto.get("vigenciaFim") or "")[:10] or None,
        "publicado": (bruto.get("dataPublicacaoPncp") or "")[:10] or None,
        "ramos": json.dumps(classificar(objeto)),
    }


def coletar_atas(conexao, cliente: httpx.Client, dias: int = 1, max_paginas: int = 60, dormir=time.sleep) -> list[dict]:
    """Atas publicadas nos últimos ``dias`` (o PNCP lista por atualização; filtramos pela publicação)."""
    fim = date.today()
    inicio = fim - timedelta(days=dias)
    novas, pagina, total_paginas = [], 1, 1
    while pagina <= min(total_paginas, max_paginas):
        try:
            dados = pagina_consulta(cliente, {"dataInicial": inicio.strftime("%Y%m%d"),
                                              "dataFinal": fim.strftime("%Y%m%d"),
                                              "pagina": pagina, "tamanhoPagina": 50},
                                    dormir=dormir, url=URL_ATAS)
        except RuntimeError as erro:
            log.error("Atas: %s", erro)
            break
        total_paginas = int(dados.get("totalPaginas") or 0)
        for b in dados.get("data") or []:
            ata = converter_ata(b)
            if ata and ata["publicado"] and ata["publicado"] >= inicio.isoformat():
                novas.append(ata)
        pagina += 1
        dormir(0.4)
    agora = _agora()
    with banco.transacao(conexao):
        for a in novas:
            conexao.execute(
                "INSERT INTO atas (id, compra_id, numero, orgao, orgao_cnpj, objeto, vigencia_inicio, vigencia_fim, "
                "publicado, ramos, coletado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING",
                (a["id"], a["compra_id"], a["numero"], a["orgao"], a["orgao_cnpj"], a["objeto"],
                 a["vigencia_inicio"], a["vigencia_fim"], a["publicado"], a["ramos"], agora))
    return novas


def _vencedor(cliente: httpx.Client, compra_id: str, cache: dict) -> str | None:
    """Vencedor e valor do item 1 da compra que gerou a ata (ex.: "EMPRESA X, R$ 1.234,00")."""
    if compra_id in cache:
        return cache[compra_id]
    resultado = None
    partes = re.fullmatch(r"(\d{14})-\d+-(\d+)/(\d{4})", compra_id)
    if partes and cliente is not None:
        cnpj, seq, ano = partes.group(1), int(partes.group(2)), int(partes.group(3))
        try:
            r = _get(cliente, URL_RESULTADOS.format(cnpj=cnpj, ano=ano, seq=seq, item=1)) or []
            if r and isinstance(r, list):
                nome = limpar_texto(r[0].get("nomeRazaoSocialFornecedor") or "", 60)
                if nome:
                    resultado = f"{nome}, {_dinheiro(r[0].get('valorTotalHomologado'))}"
        except (httpx.HTTPError, ValueError):
            pass
    cache[compra_id] = resultado
    return resultado


def eventos_de_atas(conexao, novas: list[dict], cliente: httpx.Client | None = None) -> int:
    gerados = 0
    vencedores: dict = {}
    hoje = date.today().isoformat()
    # 1) Ata de um processo que o usuário acompanha
    for a in novas:
        seguidores = conexao.execute(
            "SELECT a.usuario_id FROM acompanhamentos a LEFT JOIN alertas_config c ON c.usuario_id = a.usuario_id "
            "WHERE a.edital_id = ? AND COALESCE(c.atas_processos, 1) = 1", (a["compra_id"],)).fetchall()
        for s in seguidores:
            gerados += criar_evento(
                conexao, s["usuario_id"], f"ata:{a['id']}", "ata_processo", "Ata de registro de preço assinada",
                f"{a['objeto'][:120]} ({a['orgao'][:60]}). Vigência de {_data(a['vigencia_inicio'])} "
                f"a {_data(a['vigencia_fim'])}.", _link("/ver?id=" + a["compra_id"]), a["compra_id"])
    # 2) Resumo diário das atas novas do ramo
    usuarios = conexao.execute(
        "SELECT u.id, u.ramos FROM usuarios u LEFT JOIN alertas_config c ON c.usuario_id = u.id "
        "WHERE COALESCE(c.atas_ramo, 1) = 1").fetchall()
    for u in usuarios:
        ramos = set(json.loads(u["ramos"]))
        do_ramo, compras_vistas = [], set()
        for a in novas:
            if ramos & set(json.loads(a["ramos"])):
                do_ramo.append(a)
        unicas = []
        for a in do_ramo:  # uma compra pode gerar várias atas: um exemplo por compra
            if a["compra_id"] not in compras_vistas:
                compras_vistas.add(a["compra_id"])
                unicas.append(a)
        if not do_ramo:
            continue
        partes = []
        for a in unicas[:3]:
            vencedor = _vencedor(cliente, a["compra_id"], vencedores)
            partes.append(f"{a['objeto'][:70]} ({a['orgao'][:40]})" + (f" — vencedor: {vencedor}" if vencedor else ""))
        exemplos = "; ".join(partes)
        nomes = ", ".join(RAMOS[r] for r in sorted(ramos) if r in RAMOS)
        gerados += criar_evento(
            conexao, u["id"], f"atas_ramo:{hoje}", "atas_ramo",
            f"{_plural(len(do_ramo), 'ata nova', 'atas novas')} em {nomes}", f"Exemplos: {exemplos}.", _link("/alertas"))
    return gerados


# --------------------------------------------------------- novos editais

def eventos_de_novos_editais(conexao) -> int:
    """Um resumo por dia: editais publicados desde o último resumo, no ramo e nas UFs do usuário."""
    gerados = 0
    hoje = date.today().isoformat()
    agora_local = datetime.now(timezone(timedelta(hours=-3))).replace(tzinfo=None).isoformat(timespec="seconds")
    usuarios = conexao.execute(
        "SELECT u.id, u.ramos, u.ufs, c.ultimo_resumo FROM usuarios u LEFT JOIN alertas_config c ON c.usuario_id = u.id "
        "WHERE COALESCE(c.novos_editais, 1) = 1").fetchall()
    for u in usuarios:
        desde = u["ultimo_resumo"] or (date.today() - timedelta(days=1)).isoformat()
        ufs = json.loads(u["ufs"])
        ramos = set(json.loads(u["ramos"]))
        linhas = conexao.execute(
            f"SELECT id, objeto, encerramento, valor_estimado, ramos FROM editais WHERE publicado >= ? "
            f"AND encerramento > ? AND uf IN ({','.join('?' * len(ufs))}) ORDER BY encerramento",
            (desde, agora_local, *ufs)).fetchall()
        novos = [l for l in linhas if ramos & set(json.loads(l["ramos"]))]
        if novos:
            exemplos = "; ".join(f"{l['objeto'][:60]} (até {_data(l['encerramento'])[:5]})" for l in novos[:3])
            gerados += criar_evento(conexao, u["id"], f"novos:{hoje}", "novos_editais",
                                    f"{_plural(len(novos), 'edital novo', 'editais novos')} no seu ramo",
                                    f"Mais urgentes: {exemplos}.", _link("/painel"))
        conexao.execute(
            "INSERT INTO alertas_config (usuario_id, ultimo_resumo) VALUES (?, ?) "
            "ON CONFLICT(usuario_id) DO UPDATE SET ultimo_resumo = excluded.ultimo_resumo", (u["id"], hoje))
    return gerados


# ---------------------------------------------------------------- envio

def enviar_pendentes(conexao, notificador: notificacoes.Notificador) -> dict:
    """Envia pelo WhatsApp os eventos pendentes de quem confirmou o número."""
    contagem = {"enviado": 0, "simulado": 0, "erro": 0, "limite": 0, "sem_whatsapp": 0}
    hoje = date.today().isoformat()
    pendentes = conexao.execute(
        "SELECT ev.*, c.telefone, c.telefone_verificado FROM eventos ev "
        "LEFT JOIN alertas_config c ON c.usuario_id = ev.usuario_id "
        "WHERE ev.whatsapp = 'pendente' ORDER BY ev.id").fetchall()
    for ev in pendentes:
        if not ev["telefone_verificado"] or not ev["telefone"]:
            conexao.execute("UPDATE eventos SET whatsapp = NULL WHERE id = ?", (ev["id"],))
            contagem["sem_whatsapp"] += 1
            continue
        enviados_hoje = conexao.execute(
            "SELECT COUNT(*) FROM eventos WHERE usuario_id = ? AND whatsapp IN ('enviado', 'simulado') "
            "AND whatsapp_em >= ?", (ev["usuario_id"], hoje)).fetchone()[0]
        if enviados_hoje >= MAX_WHATSAPP_POR_DIA:
            situacao = "limite"
        else:
            try:
                situacao = notificador.enviar_alerta(conexao, ev["usuario_id"], ev["telefone"],
                                                     ev["titulo"], ev["texto"], ev["link"] or _link("/alertas"))
            except notificacoes.FalhaEnvio as erro:
                log.warning("Envio falhou (evento %s): %s", ev["id"], erro)
                situacao = "erro"
        conexao.execute("UPDATE eventos SET whatsapp = ?, whatsapp_em = ? WHERE id = ?", (situacao, _agora(), ev["id"]))
        contagem[situacao] += 1
    return contagem


def rodar(caminho_banco: str, cliente: httpx.Client | None = None, notificador=None, dormir=time.sleep,
          dias_atas: int = 1) -> dict:
    banco.preparar(caminho_banco)
    conexao = banco.conectar(caminho_banco)
    dono = cliente is None
    cliente = cliente or httpx.Client(timeout=30, headers={"User-Agent": "radar-de-editais/0.1"})
    notificador = notificador or notificacoes.do_ambiente()
    try:
        resumo = {"processos": verificar_processos(conexao, cliente, dormir=dormir)}
        novas = coletar_atas(conexao, cliente, dias=dias_atas, dormir=dormir)
        resumo["atas_novas"] = len(novas)
        resumo["eventos_atas"] = eventos_de_atas(conexao, novas, cliente)
        resumo["eventos_novos_editais"] = eventos_de_novos_editais(conexao)
        resumo["envio"] = enviar_pendentes(conexao, notificador)
        resumo["canal"] = notificador.nome
        return resumo
    finally:
        conexao.close()
        if dono:
            cliente.close()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    p = argparse.ArgumentParser(description="Monitor de processos, atas e alertas")
    p.add_argument("--dias-atas", type=int, default=1)
    args = p.parse_args()
    resumo = rodar(os.environ.get("RADAR_BANCO", "radar.db"), dias_atas=args.dias_atas)
    log.info("Monitor: %s", json.dumps(resumo, ensure_ascii=False))


if __name__ == "__main__":
    main()
