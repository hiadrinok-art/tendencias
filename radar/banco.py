"""Banco SQLite do MVP. Todas as consultas usam parâmetros (sem SQL montado com texto).

Cada requisição abre a própria conexão (``conectar``). Uma conexão única
compartilhada entre threads misturava as transações de pedidos simultâneos:
um pedido podia desfazer a gravação de outro, e a maioria recebia erro 500.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager

ESPERA_BANCO_OCUPADO = 10  # segundos esperando outra escrita terminar

ESQUEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    cnpj TEXT NOT NULL,
    ramos TEXT NOT NULL DEFAULT '[]',
    ufs TEXT NOT NULL DEFAULT '[]',
    palavras_chave TEXT NOT NULL DEFAULT '[]',
    termos_versao TEXT NOT NULL,
    termos_aceitos_em TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessoes (
    token_hash TEXT PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    criada TEXT NOT NULL,
    ultimo_uso TEXT NOT NULL,
    expira TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS sessoes_usuario ON sessoes(usuario_id);
CREATE TABLE IF NOT EXISTS auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quando TEXT NOT NULL,
    evento TEXT NOT NULL,
    usuario TEXT,
    email TEXT,
    ip TEXT,
    detalhe TEXT
);
"""


def conectar(caminho: str) -> sqlite3.Connection:
    """Abre uma conexão nova. Use uma por requisição e feche ao final."""
    conexao = sqlite3.connect(caminho, timeout=ESPERA_BANCO_OCUPADO, isolation_level=None,
                              check_same_thread=False)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute(f"PRAGMA busy_timeout = {ESPERA_BANCO_OCUPADO * 1000}")
    return conexao


def preparar(caminho: str) -> None:
    """Cria as tabelas e liga o modo WAL (leituras não esperam escritas)."""
    conexao = conectar(caminho)
    try:
        conexao.execute("PRAGMA journal_mode = WAL")
        conexao.executescript(ESQUEMA)
    finally:
        conexao.close()


@contextmanager
def transacao(conexao: sqlite3.Connection):
    conexao.execute("BEGIN IMMEDIATE")
    try:
        yield conexao
    except BaseException:
        conexao.execute("ROLLBACK")
        raise
    else:
        conexao.execute("COMMIT")
