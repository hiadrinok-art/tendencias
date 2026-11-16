import pytest
from fastapi.testclient import TestClient

from radar import banco
from radar.app import criar_app
from radar.config import Config

ORIGEM = "https://radar.exemplo"
SENHA = "Radar-de-editais-2026"
CONTA = {
    "email": "compras@empresa.com.br",
    "senha": SENHA,
    "cnpj": "07.722.779/0001-06",
    "ramos": ["ti"],
    "ufs": ["SP"],
    "palavras_chave": ["backup"],
    "aceite_termos": True,
}


@pytest.fixture
def caminho_banco(tmp_path):
    return str(tmp_path / "t.db")


@pytest.fixture
def app(caminho_banco):
    # "testclient" é o IP que o TestClient usa; tratá-lo como proxy confiável
    # permite simular visitantes de IPs diferentes com X-Forwarded-For.
    config = Config(segredo="s" * 40, banco=caminho_banco, https=False, origens=[ORIGEM],
                    proxies_confiaveis=["testclient"])
    return criar_app(config)


@pytest.fixture
def cliente(app):
    with TestClient(app, headers={"Origin": ORIGEM}) as c:
        yield c


@pytest.fixture
def novo_cliente(app):
    """Fábrica de clientes independentes (cada um com seus cookies), vindos do IP dado."""
    abertos = []

    def fabricar(ip="203.0.113.1"):
        c = TestClient(app, headers={"Origin": ORIGEM, "X-Forwarded-For": ip})
        abertos.append(c)
        return c

    yield fabricar
    for c in abertos:
        c.close()


@pytest.fixture
def consultar(caminho_banco):
    def executar(sql, *params):
        conexao = banco.conectar(caminho_banco)
        try:
            return conexao.execute(sql, params).fetchall()
        finally:
            conexao.close()
    return executar


def criar_conta(cliente, **mudancas):
    return cliente.post("/conta", json={**CONTA, **mudancas})
