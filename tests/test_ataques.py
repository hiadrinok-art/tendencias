"""Testes de regressão: cada teste repete um ataque do teste de segurança de 16/11/2026
e confirma que a falha encontrada continua corrigida."""

import concurrent.futures as cf

from radar.seguranca import dispositivos, rede
from radar.seguranca.limite import JanelaDeslizante

from .conftest import CONTA, SENHA, criar_conta

ERRADA = "errada-123456"


# Falha 1: conexão única com o banco quebrava pedidos simultâneos (erro 500).
def test_cadastros_simultaneos_nao_dao_erro(novo_cliente, consultar):
    def cadastrar(i):
        c = novo_cliente(f"198.51.100.{i}")
        return criar_conta(c, email=f"pessoa{i}@empresa.com.br").status_code

    with cf.ThreadPoolExecutor(10) as pool:
        codigos = list(pool.map(cadastrar, range(10)))
    assert codigos == [201] * 10
    assert consultar("SELECT COUNT(*) FROM usuarios")[0][0] == 10


def test_mesmo_email_em_paralelo_cria_uma_conta_so(novo_cliente, consultar):
    def cadastrar(i):
        return criar_conta(novo_cliente(f"198.51.100.{i}")).status_code

    with cf.ThreadPoolExecutor(8) as pool:
        codigos = sorted(pool.map(cadastrar, range(8)))
    assert codigos == [201] + [409] * 7
    assert consultar("SELECT COUNT(*) FROM usuarios")[0][0] == 1


# Falha 2: um estranho travava a conta do dono com 5 senhas erradas.
def test_erros_de_um_ip_nao_travam_o_dono_em_outro_ip(novo_cliente):
    criar_conta(novo_cliente("203.0.113.10"))
    atacante = novo_cliente("198.51.100.66")
    for _ in range(5):
        assert atacante.post("/sessao", json={"email": CONTA["email"], "senha": ERRADA}).status_code == 401
    assert atacante.post("/sessao", json={"email": CONTA["email"], "senha": ERRADA}).status_code == 429

    dono = novo_cliente("203.0.113.10")
    assert dono.post("/sessao", json={"email": CONTA["email"], "senha": SENHA}).status_code == 200


def test_ataque_distribuido_nao_trava_o_dispositivo_do_dono(novo_cliente):
    dono = novo_cliente("203.0.113.10")
    criar_conta(dono)  # este navegador ganha o cookie de dispositivo confiável
    dono.delete("/sessao")

    for i in range(25):  # 25 IPs diferentes, 1 erro cada
        novo_cliente(f"198.51.100.{i}").post("/sessao", json={"email": CONTA["email"], "senha": ERRADA})

    desconhecido = novo_cliente("192.0.2.50")
    assert desconhecido.post("/sessao", json={"email": CONTA["email"], "senha": SENHA}).status_code == 429
    assert dono.post("/sessao", json={"email": CONTA["email"], "senha": SENHA}).status_code == 200


def test_cookie_de_dispositivo_nao_serve_para_outra_conta():
    cookie = dispositivos.emitir("segredo" * 6, "dono@empresa.com.br")
    assert dispositivos.confiavel("segredo" * 6, "dono@empresa.com.br", cookie)
    assert not dispositivos.confiavel("segredo" * 6, "outro@empresa.com.br", cookie)
    assert not dispositivos.confiavel("segredo" * 6, "dono@empresa.com.br", cookie[:-1] + "0")
    assert not dispositivos.confiavel("segredo" * 6, "dono@empresa.com.br", None)


# Falha 3: corpo enviado em pedaços (chunked) passava do limite de 64 KB.
def test_corpo_em_pedacos_acima_do_limite_e_recusado(cliente):
    def pedacos():
        for _ in range(200):
            yield b" " * 10_000

    r = cliente.post("/sessao", content=pedacos(), headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_corpo_em_pedacos_pequeno_funciona(cliente):
    criar_conta(cliente)
    cliente.cookies.clear()
    corpo = f'{{"email": "{CONTA["email"]}", "senha": "{SENHA}"}}'.encode()
    r = cliente.post("/sessao", content=iter([corpo[:10], corpo[10:]]),
                     headers={"Content-Type": "application/json"})
    assert r.status_code == 200


# Falha 4: contadores de tentativa nunca eram apagados (memória crescia sem fim).
def test_contadores_vencidos_sao_apagados():
    agora = [0.0]
    janela = JanelaDeslizante(5, 900, relogio=lambda: agora[0])
    for i in range(50_000):
        janela.registrar(f"inventado{i}@x.com")
    agora[0] = 10_000
    janela.registrar("um-novo@x.com")
    for _ in range(1000):  # dispara a varredura periódica
        janela.registrar("um-novo@x.com")
    assert len(janela) == 1


def test_contadores_respeitam_o_teto():
    janela = JanelaDeslizante(5, 900, max_chaves=1000)
    for i in range(5000):
        janela.registrar(f"k{i}")
    assert len(janela) <= 1000


def test_inundacao_de_chaves_nao_trava_a_cpu():
    # Achado no reteste: acima do teto, a limpeza varria todas as chaves a cada
    # operação (custo quadrático). 500 mil chaves levavam dezenas de segundos.
    import time
    janela = JanelaDeslizante(5, 900, max_chaves=50_000)
    inicio = time.perf_counter()
    for i in range(500_000):
        janela.registrar(f"k{i}")
    assert time.perf_counter() - inicio < 10
    assert len(janela) == 50_000


# Falha 5: sem limite para chutar a senha em /eu/senha e DELETE /eu.
def test_chutes_na_confirmacao_de_senha_sao_bloqueados(cliente):
    criar_conta(cliente)
    for i in range(5):
        r = cliente.put("/eu/senha", json={"senha_atual": f"chute-{i:06d}", "senha_nova": "Outra-senha-2026"})
        assert r.status_code == 401
    r = cliente.put("/eu/senha", json={"senha_atual": SENHA, "senha_nova": "Outra-senha-2026"})
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > 0
    assert cliente.request("DELETE", "/eu", json={"senha": SENHA}).status_code == 429


# Parte da falha 7: IP real atrás de proxy, sem confiar em cabeçalho forjado.
def test_ip_real_so_confia_em_proxy_configurado():
    proxies = {"10.0.0.1"}
    assert rede.ip_real("10.0.0.1", "203.0.113.7", proxies) == "203.0.113.7"
    assert rede.ip_real("10.0.0.1", "1.2.3.4, 203.0.113.7", proxies) == "203.0.113.7"
    assert rede.ip_real("10.0.0.1", "203.0.113.7, 10.0.0.1", proxies) == "203.0.113.7"
    assert rede.ip_real("198.51.100.9", "1.1.1.1", proxies) == "198.51.100.9"  # forjado
    assert rede.ip_real("10.0.0.1", None, proxies) == "10.0.0.1"


def test_ipv6_agrupado_por_64():
    a = rede.chave_de_limite("2001:db8:1:2:aaaa::1")
    b = rede.chave_de_limite("2001:db8:1:2:ffff::9")
    assert a == b == "2001:db8:1:2::/64"
    assert rede.chave_de_limite("2001:db8:1:3::1") != a
    assert rede.chave_de_limite("203.0.113.7") == "203.0.113.7"


def test_x_forwarded_for_forjado_nao_burla_limite(app):
    from fastapi.testclient import TestClient

    from .conftest import ORIGEM
    # Cliente vindo de um IP que NÃO é proxy confiável tenta mudar de IP a cada pedido.
    with TestClient(app, client=("198.51.100.200", 5000), headers={"Origin": ORIGEM}) as c:
        codigos = [c.post("/sessao", json={"email": f"u{i}@x.com", "senha": ERRADA},
                          headers={"X-Forwarded-For": f"1.1.1.{i}"}).status_code for i in range(25)]
    assert 429 in codigos


# Falha 9: erros não usam mais o formato padrão do framework.
def test_erros_no_formato_proprio(cliente):
    r = cliente.post("/sessao", json={"email": "a@b.com", "senha": "x"})
    assert r.status_code == 401
    assert r.json() == {"erro": "E-mail ou senha incorretos."}


def test_modo_hospedagem_usa_o_ip_visto_pelo_proxy():
    # Com RADAR_PROXIES="*", vale o último IP: o cliente não consegue forjar.
    assert rede.ip_real("10.1.2.3", "1.1.1.1, 203.0.113.7", {"*"}) == "203.0.113.7"
    assert rede.ip_real("10.1.2.3", None, {"*"}) == "10.1.2.3"
