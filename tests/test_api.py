import pytest

from radar.config import Config

from .conftest import CONTA, SENHA, criar_conta


def test_cadastro_login_e_perfil(cliente):
    assert criar_conta(cliente).status_code == 201
    cliente.cookies.clear()
    assert cliente.get("/eu").status_code == 401
    r = cliente.post("/sessao", json={"email": CONTA["email"], "senha": SENHA})
    assert r.status_code == 200
    cookie = r.headers["set-cookie"].lower()
    assert "httponly" in cookie and "samesite=strict" in cookie
    assert cliente.get("/eu").json()["cnpj"] == "07722779000106"


def test_cabecalhos_de_seguranca(cliente):
    r = cliente.get("/saude")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["x-frame-options"] == "DENY"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert r.headers["cache-control"] == "no-store"


def test_dados_invalidos_sao_recusados(cliente):
    assert criar_conta(cliente, cnpj="07.722.779/0001-07").status_code == 422
    assert criar_conta(cliente, senha="12345678").status_code == 422
    assert criar_conta(cliente, aceite_termos=False).status_code == 422
    assert criar_conta(cliente, ramos=["ti", "invasao"]).status_code == 422
    assert criar_conta(cliente, ufs=["XX"]).status_code == 422


def test_erro_de_validacao_nao_devolve_a_senha(cliente):
    r = criar_conta(cliente, senha="segredo-" * 30)
    assert r.status_code == 422
    assert "segredo-" not in r.text


def test_email_repetido(cliente):
    criar_conta(cliente)
    assert criar_conta(cliente).status_code == 409


def test_login_errado_tem_mesma_mensagem_com_ou_sem_conta(cliente):
    criar_conta(cliente)
    cliente.cookies.clear()
    senha_errada = cliente.post("/sessao", json={"email": CONTA["email"], "senha": "errada-123456"})
    sem_conta = cliente.post("/sessao", json={"email": "ninguem@x.com", "senha": "errada-123456"})
    assert senha_errada.status_code == sem_conta.status_code == 401
    assert senha_errada.json() == sem_conta.json()


def test_bloqueio_apos_5_tentativas(cliente):
    criar_conta(cliente)
    cliente.cookies.clear()
    for _ in range(5):
        assert cliente.post("/sessao", json={"email": CONTA["email"], "senha": "errada-123456"}).status_code == 401
    r = cliente.post("/sessao", json={"email": CONTA["email"], "senha": SENHA})
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > 0


def test_csrf_origem_estranha_e_recusada(cliente):
    criar_conta(cliente)
    r = cliente.request("DELETE", "/eu", json={"senha": SENHA}, headers={"Origin": "https://site-malicioso.com"})
    assert r.status_code == 403
    assert cliente.get("/eu").status_code == 200


def test_logout_encerra_a_sessao(cliente):
    criar_conta(cliente)
    token = cliente.cookies.get("radar_sessao")
    cliente.delete("/sessao")
    cliente.cookies.clear()
    assert cliente.get("/eu", headers={"Authorization": f"Bearer {token}"}).status_code == 401


def test_troca_de_senha_derruba_outras_sessoes(cliente):
    criar_conta(cliente)
    token_antigo = cliente.cookies.get("radar_sessao")
    r = cliente.put("/eu/senha", json={"senha_atual": SENHA, "senha_nova": "Nova-senha-forte-2026"})
    assert r.status_code == 200
    assert cliente.get("/eu", headers={"Authorization": f"Bearer {token_antigo}"}).status_code == 401
    assert cliente.get("/eu").status_code == 200


def test_lgpd_exportar_e_excluir(cliente, consultar):
    criar_conta(cliente)
    dados = cliente.get("/eu/dados").json()
    assert dados["email"] == CONTA["email"] and "senha_hash" not in dados
    assert dados["termos_versao"]

    assert cliente.request("DELETE", "/eu", json={"senha": "errada-123456"}).status_code == 401
    assert cliente.request("DELETE", "/eu", json={"senha": SENHA}).status_code == 200
    assert cliente.get("/eu").status_code == 401

    assert consultar("SELECT COUNT(*) FROM usuarios")[0][0] == 0
    assert consultar("SELECT COUNT(*) FROM sessoes")[0][0] == 0
    logs = " ".join(str(tuple(l)) for l in consultar("SELECT * FROM auditoria"))
    assert CONTA["email"] not in logs and "c***@e***.com.br" in logs


def test_corpo_grande_demais(cliente):
    r = cliente.post("/sessao", content=b"x" * 70_000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_sem_segredo_nao_sobe(monkeypatch):
    from radar.config import ConfiguracaoInvalida
    monkeypatch.setenv("RADAR_SEGREDO", "curto")
    with pytest.raises(ConfiguracaoInvalida):
        Config.do_ambiente()
