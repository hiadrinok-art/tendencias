import json
from datetime import datetime, timedelta

from radar import banco, coletor
from radar.classificador import classificar

from .conftest import CONTA, ORIGEM, criar_conta


def bruto(**mudancas):
    """Registro no formato da API do PNCP (campos reais de um pregão da UFABC)."""
    base = {
        "numeroControlePNCP": "07722779000106-1-000149/2026",
        "orgaoEntidade": {"cnpj": "07722779000106", "razaoSocial": "FUNDACAO UNIVERSIDADE FEDERAL DO ABC - UFABC"},
        "unidadeOrgao": {"ufSigla": "SP", "municipioNome": "Santo André", "nomeUnidade": "FUNDAÇÃO UNIVERSIDADE FEDERAL DO ABC"},
        "objetoCompra": "Aquisição de solução de backup em disco, incluindo software de backup",
        "valorTotalEstimado": 1018253.63,
        "dataAberturaProposta": "2026-11-12T09:00:00",
        "dataEncerramentoProposta": (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%dT10:00:00"),
        "dataPublicacaoPncp": "2026-11-12T04:03:09",
        "anoCompra": 2026, "sequencialCompra": 149,
        "linkSistemaOrigem": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/acompanhamento-compra?compra=1",
    }
    base.update(mudancas)
    return base


def gravar(caminho, *registros):
    banco.preparar(caminho)
    conexao = banco.conectar(caminho)
    coletor.gravar(conexao, [coletor.converter(r, 6) for r in registros])
    conexao.close()


def test_classificador():
    assert classificar("Aquisição de solução de backup e licenças de software") == ["ti"]
    assert "obra" in classificar("Obras de pavimentação asfáltica")
    assert "obra" not in classificar("Fornecimento de mão-de-obra terceirizada de limpeza")
    assert classificar("Aquisição de gêneros alimentícios") == ["alim"]


def test_converter_limpa_dados_do_pncp():
    linha = coletor.converter(bruto(), 6)
    assert linha["uf"] == "SP" and linha["valor_estimado"] == 1018253.63
    assert linha["link_pncp"] == "https://pncp.gov.br/app/editais/07722779000106/2026/149"
    assert json.loads(linha["ramos"]) == ["ti"]


def test_converter_recusa_links_perigosos():
    for url in ["javascript:alert(1)", "http://compras.gov.br/x", "https://site-falso.com/gov.br",
                "https://gov.br.atacante.com/x", "data:text/html,<script>"]:
        assert coletor.converter(bruto(linkSistemaOrigem=url), 6)["link_origem"] is None, url
    assert coletor.converter(bruto(linkSistemaOrigem="https://www.gov.br/compras"), 6)["link_origem"]


def test_converter_descarta_registros_invalidos():
    assert coletor.converter(bruto(unidadeOrgao={"ufSigla": "XX"}), 6) is None
    assert coletor.converter(bruto(orgaoEntidade={"cnpj": "123"}), 6) is None
    assert coletor.converter(bruto(objetoCompra=""), 6) is None
    assert coletor.converter(bruto(valorTotalEstimado="abc"), 6)["valor_estimado"] is None
    assert coletor.converter(bruto(objetoCompra="x\u0000" + "a" * 5000), 6)["objeto"] == "x" + "a" * 1999


def test_painel_mostra_so_ramo_uf_e_prazo_aberto(cliente, caminho_banco):
    gravar(caminho_banco,
           bruto(),
           bruto(numeroControlePNCP="A-1", sequencialCompra=1, objetoCompra="Material de limpeza"),
           bruto(numeroControlePNCP="A-2", sequencialCompra=2, unidadeOrgao={"ufSigla": "RJ"}),
           bruto(numeroControlePNCP="A-3", sequencialCompra=3, dataEncerramentoProposta="2020-01-01T10:00:00"),
           bruto(numeroControlePNCP="A-4", sequencialCompra=4, objetoCompra="Locação de veículos com backup de motorista"))
    criar_conta(cliente)  # ramo TI, UF SP, palavra-chave "backup"
    dados = cliente.get("/editais").json()
    ids = [e["id"] for e in dados["editais"]]
    assert ids[0] == "07722779000106-1-000149/2026"
    assert "A-4" in ids                     # entrou pela palavra-chave
    assert not {"A-1", "A-2", "A-3"} & set(ids)  # outro ramo, outra UF, prazo vencido
    assert dados["resumo"]["total"] == 2
    assert dados["editais"][0]["dias_restantes"] == 9
    assert cliente.get("/editais?filtro=grandes").json()["editais"][0]["valor_estimado"] > 100_000


def test_editais_exigem_login(cliente):
    assert cliente.get("/editais").status_code == 401
    assert cliente.get("/edital?id=x").status_code == 401


def test_detalhe_e_avaliacao(cliente, caminho_banco, consultar):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)
    id_ = "07722779000106-1-000149/2026"
    e = cliente.get("/edital", params={"id": id_}).json()
    assert e["avaliacao"] is None and e["ramos"] == ["TI e software"]
    assert cliente.post("/edital/avaliacao", json={"id": id_, "serve": False}).status_code == 200
    assert cliente.get("/edital", params={"id": id_}).json()["avaliacao"] is False
    assert cliente.post("/edital/avaliacao", json={"id": "nao-existe", "serve": True}).status_code == 404
    assert cliente.get("/edital", params={"id": "nao-existe"}).status_code == 404


def test_paginas_do_site_com_csp_restrita(cliente):
    for caminho in ["/", "/cadastro", "/entrar", "/painel", "/ver"]:
        r = cliente.get(caminho)
        assert r.status_code == 200 and "text/html" in r.headers["content-type"], caminho
        csp = r.headers["content-security-policy"]
        assert "script-src 'self'" in csp and "unsafe-inline" not in csp and "frame-ancestors 'none'" in csp
    assert cliente.get("/static/app.js").status_code == 200


def test_paginas_sem_script_ou_estilo_inline():
    from pathlib import Path
    import re
    for arquivo in (Path(__file__).parent.parent / "radar" / "site").rglob("*.html"):
        html = arquivo.read_text()
        assert not re.search(r"<script(?![^>]*\bsrc=)", html), arquivo
        assert " style=" not in html and "<style" not in html, arquivo
        assert not re.search(r"\son[a-z]+=", html), arquivo


def test_csrf_aceita_mesma_origem_e_recusa_outra(app):
    from fastapi.testclient import TestClient
    with TestClient(app, base_url="https://radar.app.br") as c:
        assert c.post("/conta", json=CONTA, headers={"Origin": ORIGEM}).status_code == 201
        assert c.post("/edital/avaliacao", json={"id": "x", "serve": True},
                      headers={"Origin": "https://radar.app.br"}).status_code == 404  # passou do CSRF
        assert c.post("/edital/avaliacao", json={"id": "x", "serve": True},
                      headers={"Origin": "https://radar.app.br.evil.com"}).status_code == 403
