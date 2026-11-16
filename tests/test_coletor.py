import httpx

from radar import banco, coletor

from .test_editais import bruto


def transporte(roteiro):
    """Simula o PNCP: roteiro[(modalidade, pagina)] = lista de respostas em sequência."""
    chamadas = []

    def responder(pedido):
        m = int(pedido.url.params["codigoModalidadeContratacao"])
        p = int(pedido.url.params["pagina"])
        chamadas.append((m, p))
        fila = roteiro.get((m, p))
        if not fila:
            return httpx.Response(204)
        return fila.pop(0) if len(fila) > 1 else fila[0]
    return httpx.MockTransport(responder), chamadas


def pagina(*registros, total=2):
    return httpx.Response(200, json={"data": list(registros), "totalPaginas": total})


def test_429_espera_o_retry_after_e_continua(tmp_path):
    esperas = []
    t, _ = transporte({
        (6, 1): [httpx.Response(429, headers={"Retry-After": "7"}), pagina(bruto())],
        (6, 2): [pagina(bruto(numeroControlePNCP="B-2", sequencialCompra=2))],
    })
    n = coletor.coletar(str(tmp_path / "t.db"), dormir=esperas.append, cliente=httpx.Client(transport=t))
    assert n == 2
    assert 7 in esperas  # respeitou o Retry-After


def test_pagina_que_sempre_falha_e_pulada_sem_perder_o_resto(tmp_path):
    t, _ = transporte({
        (6, 1): [pagina(bruto(), total=3)],
        (6, 2): [httpx.Response(429)],
        (6, 3): [pagina(bruto(numeroControlePNCP="B-3", sequencialCompra=3), total=3)],
    })
    caminho = str(tmp_path / "t.db")
    n = coletor.coletar(caminho, dormir=lambda s: None, cliente=httpx.Client(transport=t))
    assert n == 2
    c = banco.conectar(caminho)
    assert c.execute("SELECT ano, sequencial FROM editais WHERE id = 'B-3'").fetchone()[:] == (2026, 3)


def test_nada_coletado_e_erro(tmp_path):
    t, _ = transporte({(m, 1): [httpx.Response(503)] for m in coletor.MODALIDADES})
    import pytest
    with pytest.raises(coletor.PncpFalhou):
        coletor.coletar(str(tmp_path / "t.db"), dormir=lambda s: None, cliente=httpx.Client(transport=t))


def test_banco_antigo_ganha_colunas_novas(tmp_path):
    import sqlite3
    caminho = str(tmp_path / "velho.db")
    c = sqlite3.connect(caminho)
    c.execute("CREATE TABLE editais (id TEXT PRIMARY KEY, orgao TEXT NOT NULL, orgao_cnpj TEXT NOT NULL, unidade TEXT,"
              " municipio TEXT, uf TEXT NOT NULL, modalidade TEXT, objeto TEXT NOT NULL, valor_estimado REAL,"
              " abertura TEXT, encerramento TEXT, publicado TEXT, link_origem TEXT, link_pncp TEXT NOT NULL,"
              " ramos TEXT NOT NULL DEFAULT '[]', coletado_em TEXT NOT NULL)")
    c.commit(); c.close()
    banco.preparar(caminho)
    colunas = {l[1] for l in sqlite3.connect(caminho).execute("PRAGMA table_info(editais)")}
    assert {"ano", "sequencial"} <= colunas
