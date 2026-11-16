import hashlib
import hmac
import json
from datetime import date

import httpx
import pytest

from radar import banco, monitor, notificacoes

from .conftest import SENHA, criar_conta
from .test_editais import bruto, gravar

ID = "07722779000106-1-000149/2026"


# ------------------------------------------------------------ telefone

def test_normalizar_telefone():
    assert notificacoes.normalizar_telefone("(11) 98765-4321") == "5511987654321"
    assert notificacoes.normalizar_telefone("+55 11 98765 4321") == "5511987654321"
    assert notificacoes.normalizar_telefone("11 3333-4444") is None   # fixo não tem WhatsApp garantido
    assert notificacoes.normalizar_telefone("123") is None
    assert notificacoes.mascarar_telefone("5511987654321") == "+55 (11) *****-4321"


def test_cadastro_e_confirmacao_do_numero(cliente, novo_cliente):
    criar_conta(cliente)
    assert cliente.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": False}).status_code == 422
    r = cliente.post("/alertas/telefone", json={"telefone": "(11) 98765-4321", "consentimento": True}).json()
    assert r["telefone"] == "+55 (11) *****-4321" and len(r["codigo_teste"]) == 6
    errado = "000000" if r["codigo_teste"] != "000000" else "111111"
    assert cliente.post("/alertas/telefone/confirmar", json={"codigo": errado}).status_code == 422
    assert cliente.post("/alertas/telefone/confirmar", json={"codigo": r["codigo_teste"]}).status_code == 200
    cfg = cliente.get("/alertas/config").json()
    assert cfg["verificado"] and cfg["canal"] == "simulado"
    assert "98765" not in json.dumps(cfg)  # número aparece mascarado

    outro = novo_cliente("203.0.113.77")
    criar_conta(outro, email="outro@empresa.com.br")
    r2 = outro.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": True}).json()
    assert outro.post("/alertas/telefone/confirmar", json={"codigo": r2["codigo_teste"]}).status_code == 409


def test_codigo_bloqueia_apos_5_erros_e_limita_envios(cliente):
    criar_conta(cliente)
    r = cliente.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": True}).json()
    errado = "000000" if r["codigo_teste"] != "000000" else "111111"
    for _ in range(5):
        cliente.post("/alertas/telefone/confirmar", json={"codigo": errado})
    assert cliente.post("/alertas/telefone/confirmar", json={"codigo": r["codigo_teste"]}).status_code == 429
    cliente.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": True})
    cliente.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": True})
    assert cliente.post("/alertas/telefone", json={"telefone": "11987654321", "consentimento": True}).status_code == 429


def _verificar(cliente, telefone="11987654321"):
    r = cliente.post("/alertas/telefone", json={"telefone": telefone, "consentimento": True}).json()
    assert cliente.post("/alertas/telefone/confirmar", json={"codigo": r["codigo_teste"]}).status_code == 200


def test_remover_numero_e_excluir_conta_apagam_dados(cliente, consultar):
    criar_conta(cliente)
    _verificar(cliente)
    assert cliente.delete("/alertas/telefone").status_code == 200
    assert consultar("SELECT telefone FROM alertas_config")[0][0] is None
    _verificar(cliente)
    assert cliente.get("/eu/dados").json()["alertas"]["telefone"] == "5511987654321"
    cliente.request("DELETE", "/eu", json={"senha": SENHA})
    assert consultar("SELECT COUNT(*) FROM alertas_config")[0][0] == 0
    assert consultar("SELECT COUNT(*) FROM mensagens_simuladas")[0][0] == 0


# ------------------------------------------------------------- webhook

def test_webhook_verificacao_e_sair(cliente, monkeypatch, consultar):
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "token-do-webhook")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "segredo-do-app")
    r = cliente.get("/webhook/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "token-do-webhook",
                                                 "hub.challenge": "12345"})
    assert r.status_code == 200 and r.text == "12345"
    assert cliente.get("/webhook/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "x",
                                                    "hub.challenge": "1"}).status_code == 403

    criar_conta(cliente)
    _verificar(cliente)
    corpo = json.dumps({"entry": [{"changes": [{"value": {"messages": [
        {"from": "5511987654321", "type": "text", "text": {"body": " SAIR "}}]}}]}]}).encode()
    cliente.cookies.clear()
    falsa = cliente.post("/webhook/whatsapp", content=corpo, headers={"X-Hub-Signature-256": "sha256=00"})
    assert falsa.status_code == 403
    assinatura = "sha256=" + hmac.new(b"segredo-do-app", corpo, hashlib.sha256).hexdigest()
    ok = cliente.post("/webhook/whatsapp", content=corpo,
                      headers={"X-Hub-Signature-256": assinatura, "Content-Type": "application/json"})
    assert ok.status_code == 200
    assert consultar("SELECT telefone_verificado FROM alertas_config")[0][0] == 0


# ------------------------------------------------------ WhatsApp Cloud

def test_envio_pela_api_da_meta_monta_o_modelo():
    pedidos = []

    def meta(pedido):
        pedidos.append(pedido)
        return httpx.Response(200, json={"messages": [{"id": "wamid.x"}]})
    n = notificacoes.NotificadorWhatsAppCloud("TOKEN", "123", "radar_codigo", "radar_alerta",
                                             cliente=httpx.Client(transport=httpx.MockTransport(meta)))
    assert n.enviar_alerta(None, 1, "5511987654321", "Prazo alterado", "linha 1\nlinha 2\t fim", "https://x/ver") == "enviado"
    p = pedidos[0]
    assert str(p.url) == "https://graph.facebook.com/v21.0/123/messages"
    assert p.headers["authorization"] == "Bearer TOKEN"
    corpo = json.loads(p.content)
    assert corpo["template"]["name"] == "radar_alerta" and corpo["template"]["language"]["code"] == "pt_BR"
    textos = [x["text"] for x in corpo["template"]["components"][0]["parameters"]]
    assert all("\n" not in t and "\t" not in t for t in textos)


def test_falha_da_meta_vira_erro_controlado():
    n = notificacoes.NotificadorWhatsAppCloud("T", "1", "a", "b", cliente=httpx.Client(
        transport=httpx.MockTransport(lambda r: httpx.Response(400, json={"error": {"code": 131026}}))))
    with pytest.raises(notificacoes.FalhaEnvio, match="131026"):
        n.enviar_alerta(None, 1, "5511987654321", "t", "x", "l")


# --------------------------------------------------------------- monitor

def pncp_falso(estado):
    """Simula o PNCP para um edital (compra, documentos, itens, resultados) e as atas."""
    def responder(pedido):
        url = str(pedido.url)
        if "/atas/atualizacao" in url:
            return httpx.Response(200, json={"data": estado["atas"], "totalPaginas": 1})
        if url.endswith("/arquivos"):
            return httpx.Response(200, json=estado["arquivos"])
        if "/resultados" in url:
            return httpx.Response(200, json=[{"nomeRazaoSocialFornecedor": "EMPRESA VENCEDORA LTDA",
                                               "valorTotalHomologado": 900000.0}])
        if "/itens" in url:
            return httpx.Response(200, json=[{"numeroItem": 1}])
        if "/compras/2026/149" in url:
            return httpx.Response(200, json=estado["compra"])
        return httpx.Response(204)
    return httpx.Client(transport=httpx.MockTransport(responder))


def documento(seq, titulo, tipo="Edital"):
    return {"sequencialDocumento": seq, "titulo": titulo, "tipoDocumentoNome": tipo, "statusAtivo": True,
            "url": f"https://pncp.gov.br/pncp-api/v1/orgaos/07722779000106/compras/2026/149/arquivos/{seq}"}


def test_monitor_avisa_mudancas_no_processo_e_ata(cliente, caminho_banco, consultar):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)
    _verificar(cliente)
    cliente.put("/funil", json={"id": ID, "status": "enviada"})
    estado = {"compra": {"situacaoCompraNome": "Divulgada no PNCP", "dataEncerramentoProposta": "2026-11-25T10:00:00",
                         "existeResultado": False},
              "arquivos": [documento(1, "Edital.pdf")], "atas": []}
    sem_espera = dict(dormir=lambda s: None, notificador=notificacoes.NotificadorSimulado())

    primeira = monitor.rodar(caminho_banco, cliente=pncp_falso(estado), **sem_espera)
    assert primeira["processos"] == 0  # 1ª vez só guarda o estado

    estado["compra"].update(dataEncerramentoProposta="2026-11-28T10:00:00", situacaoCompraNome="Homologada",
                            existeResultado=True)
    estado["arquivos"].append(documento(2, "Resposta a esclarecimento.pdf", "Outros"))
    estado["atas"] = [{"numeroControlePNCPAta": ID + "-000001", "numeroControlePNCPCompra": ID,
                       "cnpjOrgao": "07722779000106", "nomeOrgao": "UFABC", "cancelado": False,
                       "objetoContratacao": "Solução de backup em disco", "vigenciaInicio": "2026-12-01",
                       "vigenciaFim": "2027-12-01", "dataPublicacaoPncp": date.today().isoformat()}]
    segunda = monitor.rodar(caminho_banco, cliente=pncp_falso(estado), **sem_espera)
    tipos = {e["tipo"]: e for e in cliente.get("/alertas/eventos").json()["eventos"]}
    assert {"prazo", "situacao", "documento", "resultado", "ata_processo", "atas_ramo"} <= set(tipos)
    assert "28/11/2026" in tipos["prazo"]["texto"]
    assert "EMPRESA VENCEDORA LTDA" in tipos["resultado"]["texto"]
    assert "vencedor: EMPRESA VENCEDORA LTDA, R$ 900.000,00" in tipos["atas_ramo"]["texto"]
    assert segunda["envio"]["simulado"] >= 6
    assert consultar("SELECT encerramento FROM editais WHERE id = ?", ID)[0][0] == "2026-11-28T10:00:00"

    # Rodar de novo não repete alertas
    monitor.rodar(caminho_banco, cliente=pncp_falso(estado), **sem_espera)
    assert len(cliente.get("/alertas/eventos").json()["eventos"]) == len(tipos)
    mensagens = cliente.get("/alertas/simuladas").json()["mensagens"]
    assert any("Prazo de propostas alterado" in m["conteudo"] for m in mensagens)


def test_preferencia_desligada_nao_gera_alerta(cliente, caminho_banco):
    gravar(caminho_banco, bruto())
    criar_conta(cliente)
    cliente.put("/alertas/preferencias", json={"novos_editais": False, "processos": False,
                                               "atas_ramo": False, "atas_processos": False})
    cliente.put("/funil", json={"id": ID, "status": "interesse"})
    estado = {"compra": {"situacaoCompraNome": "A", "dataEncerramentoProposta": "2026-11-25T10:00:00"},
              "arquivos": [], "atas": []}
    kw = dict(dormir=lambda s: None, notificador=notificacoes.NotificadorSimulado())
    monitor.rodar(caminho_banco, cliente=pncp_falso(estado), **kw)
    estado["compra"]["situacaoCompraNome"] = "Suspensa"
    monitor.rodar(caminho_banco, cliente=pncp_falso(estado), **kw)
    assert cliente.get("/alertas/eventos").json()["eventos"] == []


def test_sem_whatsapp_alerta_fica_so_no_site(cliente, caminho_banco, consultar):
    gravar(caminho_banco, bruto(dataPublicacaoPncp=date.today().isoformat() + "T08:00:00"))
    criar_conta(cliente)  # não cadastrou WhatsApp
    monitor.rodar(caminho_banco, cliente=pncp_falso({"compra": {}, "arquivos": [], "atas": []}),
                  dormir=lambda s: None, notificador=notificacoes.NotificadorSimulado())
    eventos = cliente.get("/alertas/eventos").json()["eventos"]
    assert eventos and eventos[0]["tipo"] == "novos_editais" and eventos[0]["whatsapp"] is None
    assert consultar("SELECT COUNT(*) FROM mensagens_simuladas")[0][0] == 0


def test_limite_diario_de_mensagens(cliente, caminho_banco):
    banco.preparar(caminho_banco)
    criar_conta(cliente)
    _verificar(cliente)
    conexao = banco.conectar(caminho_banco)
    uid = conexao.execute("SELECT id FROM usuarios").fetchone()[0]
    for i in range(monitor.MAX_WHATSAPP_POR_DIA + 5):
        monitor.criar_evento(conexao, uid, f"teste:{i}", "documento", f"Evento {i}", "texto")
    contagem = monitor.enviar_pendentes(conexao, notificacoes.NotificadorSimulado())
    conexao.close()
    assert contagem["simulado"] == monitor.MAX_WHATSAPP_POR_DIA and contagem["limite"] == 5
