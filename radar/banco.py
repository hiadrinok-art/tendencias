"""Banco SQLite do MVP. Todas as consultas usam parâmetros (sem SQL montado com texto)."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager

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
    conexao = sqlite3.connect(caminho, check_same_thread=False, isolation_level=None)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")
    conexao.execute("PRAGMA journal_mode = WAL")
    conexao.executescript(ESQUEMA)
    return conexao


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
