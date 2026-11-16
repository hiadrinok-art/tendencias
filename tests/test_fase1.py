from radar import detalhes

from .conftest import criar_conta
from .test_editais import bruto, gravar

ID = "07722779000106-1-000149/2026"


def test_itens_e_documentos_limpos_e_em_cache(cliente, caminho_banco, monkeypatch):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)
    chamadas = []

    def falso_pncp(edital, tipo, cliente_http):
        chamadas.append((edital["orgao_cnpj"], edital["ano"], edital["sequencial"], tipo))
        if tipo == "itens":
            return [{"numeroItem": 1, "descricao": "Servidor rack\u0000", "quantidade": 2, "unidadeMedida": "Unidade",
                     "valorUnitarioEstimado": 371911.0, "valorTotal": 743822.0,
                     "tipoBeneficioNome": "Participação exclusiva para ME/EPP", "materialOuServicoNome": "Material"}]
        return [{"titulo": "Edital.pdf", "tipoDocumentoNome": "Edital", "statusAtivo": True,
                 "url": "https://pncp.gov.br/pncp-api/v1/orgaos/07722779000106/compras/2026/149/arquivos/1"},
                {"titulo": "Malicioso", "statusAtivo": True, "url": "javascript:alert(1)"},
                {"titulo": "Removido", "statusAtivo": False, "url": "https://pncp.gov.br/x"}]
    monkeypatch.setattr(detalhes, "_baixar", falso_pncp)

    itens = cliente.get("/edital/detalhes", params={"id": ID, "tipo": "itens"}).json()["lista"]
    assert itens[0]["descricao"] == "Servidor rack" and itens[0]["exclusivo_me_epp"] is True
    arquivos = cliente.get("/edital/detalhes", params={"id": ID, "tipo": "arquivos"}).json()["lista"]
    assert [a["titulo"] for a in arquivos] == ["Edital.pdf"]  # link perigoso e inativo descartados
    cliente.get("/edital/detalhes", params={"id": ID, "tipo": "itens"})
    assert chamadas == [("07722779000106", 2026, 149, "itens"), ("07722779000106", 2026, 149, "arquivos")]  # cache


def test_pncp_fora_do_ar_da_503(cliente, caminho_banco, monkeypatch):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)

    def falha(*a):
        raise detalhes.PncpIndisponivel("timeout")
    monkeypatch.setattr(detalhes, "_baixar", falha)
    r = cliente.get("/edital/detalhes", params={"id": ID})
    assert r.status_code == 503 and "PNCP" in r.json()["erro"]


def test_agenda_ics_escapa_texto(cliente, caminho_banco):
    gravar(caminho_banco, bruto(objetoCompra="Backup; teste, com\\barra\nEND:VCALENDAR"))
    criar_conta(cliente)
    r = cliente.get("/edital/agenda.ics", params={"id": ID})
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/calendar")
    linhas = r.text.split("\r\n")
    assert linhas.count("END:VCALENDAR") == 1  # texto do edital não injeta comandos
    assert any(l.startswith(r"SUMMARY:Fim das propostas: Backup\; teste\, com\\barra") for l in linhas)
    assert "TRIGGER:-P1D" in linhas


def test_funil_por_usuario(cliente, caminho_banco, novo_cliente):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)
    assert cliente.put("/funil", json={"id": ID, "status": "preparando", "nota": "Ligar\npara o órgão"}).status_code == 200
    etapas = {e["status"]: e for e in cliente.get("/funil").json()["etapas"]}
    assert etapas["preparando"]["editais"][0]["nota"] == "Ligar\npara o órgão"
    assert cliente.get("/edital", params={"id": ID}).json()["acompanhamento"]["status"] == "preparando"
    assert cliente.get("/editais").json()["editais"][0]["acompanhamento"] == "preparando"
    assert cliente.put("/funil", json={"id": ID, "status": "hackeado"}).status_code == 422

    outro = novo_cliente("203.0.113.99")
    criar_conta(outro, email="outra@empresa.com.br")
    assert all(not e["editais"] for e in outro.get("/funil").json()["etapas"])  # não vê o funil alheio

    assert cliente.delete("/funil", params={"id": ID}).status_code == 200
    assert all(not e["editais"] for e in cliente.get("/funil").json()["etapas"])


def test_busca_livre_ignora_ramo(cliente, caminho_banco):
    gravar(caminho_banco, bruto(),
           bruto(numeroControlePNCP="L-1", sequencialCompra=5, objetoCompra="Aquisição de uniformes escolares"))
    criar_conta(cliente)  # ramo TI
    ids = [e["id"] for e in cliente.get("/editais", params={"q": "UNIFORMES"}).json()["editais"]]
    assert ids == ["L-1"]
    assert cliente.get("/editais", params={"q": "uniformes backup"}).json()["editais"] == []
