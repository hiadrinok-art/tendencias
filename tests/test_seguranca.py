from radar.seguranca import auditoria, senhas, validacao
from radar.seguranca.limite import JanelaDeslizante


def test_hash_de_senha_confere_e_nao_guarda_texto():
    h = senhas.gerar_hash("uma senha bem longa")
    assert "uma senha" not in h
    assert senhas.verificar("uma senha bem longa", h)
    assert not senhas.verificar("outra senha qualquer", h)


def test_mesma_senha_gera_hashes_diferentes():
    assert senhas.gerar_hash("abcdefghij1") != senhas.gerar_hash("abcdefghij1")


def test_hash_corrompido_nao_quebra():
    assert not senhas.verificar("x", "lixo")
    assert not senhas.verificar("x", "bcrypt$1$2$3$a$b")
    assert senhas.precisa_rehash("scrypt$1024$8$1$a$b")


def test_cnpj():
    assert validacao.cnpj_valido("07.722.779/0001-06")  # UFABC, do PNCP
    assert validacao.cnpj_valido("33781055000135")      # Fiocruz, do PNCP
    assert not validacao.cnpj_valido("07.722.779/0001-07")
    assert not validacao.cnpj_valido("11111111111111")
    assert not validacao.cnpj_valido("123")


def test_email():
    assert validacao.email_valido("Contato@Empresa.com.br")
    assert not validacao.email_valido("sem-arroba")
    assert not validacao.email_valido("a@b")


def test_politica_de_senha():
    assert validacao.problemas_da_senha("curta")
    assert validacao.problemas_da_senha("1234567890")
    assert validacao.problemas_da_senha("aaaaaaaaaaaa")
    assert validacao.problemas_da_senha("joaosilva-2026!", "joaosilva@empresa.com")
    assert validacao.problemas_da_senha("Radar-de-editais-2026", "joao@empresa.com") == []


def test_palavras_chave_limpas():
    sujas = ["  Backup\u0000 ", "backup", "SaaS\n\tnuvem", "x" * 100] + [f"p{i}" for i in range(20)]
    limpas = validacao.limpar_palavras_chave(sujas)
    assert limpas[:2] == ["backup", "saas nuvem"]
    assert len(limpas[2]) == 40
    assert len(limpas) == 10


def test_janela_deslizante_bloqueia_e_libera():
    agora = [0.0]
    janela = JanelaDeslizante(limite=3, janela=60, relogio=lambda: agora[0])
    assert all(janela.permitir("ip") for _ in range(3))
    assert not janela.permitir("ip")
    assert janela.permitir("outro-ip")
    agora[0] = 61
    assert janela.permitir("ip")


def test_mascaras_de_auditoria():
    assert auditoria.mascarar_email("joao@empresa.com.br") == "j***@e***.com.br"
    assert auditoria.mascarar_ip("200.150.10.77") == "200.150.10.0/24"
    assert auditoria.mascarar_ip("lixo") == "desconhecido"
    assert auditoria.id_anonimo(7, "s") == auditoria.id_anonimo(7, "s") != auditoria.id_anonimo(8, "s")
