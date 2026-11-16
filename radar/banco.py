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
CREATE TABLE IF NOT EXISTS editais (
    id TEXT PRIMARY KEY,               -- número de controle do PNCP
    orgao TEXT NOT NULL,
    orgao_cnpj TEXT NOT NULL,
    unidade TEXT,
    municipio TEXT,
    uf TEXT NOT NULL,
    modalidade TEXT,
    objeto TEXT NOT NULL,
    valor_estimado REAL,
    abertura TEXT,
    encerramento TEXT,
    publicado TEXT,
    link_origem TEXT,
    link_pncp TEXT NOT NULL,
    ramos TEXT NOT NULL DEFAULT '[]',
    coletado_em TEXT NOT NULL,
    ano INTEGER,
    sequencial INTEGER
);
CREATE INDEX IF NOT EXISTS editais_encerramento ON editais(encerramento);
CREATE INDEX IF NOT EXISTS editais_uf ON editais(uf);
CREATE TABLE IF NOT EXISTS avaliacoes (
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    edital_id TEXT NOT NULL REFERENCES editais(id) ON DELETE CASCADE,
    serve INTEGER NOT NULL,
    quando TEXT NOT NULL,
    PRIMARY KEY (usuario_id, edital_id)
);
CREATE TABLE IF NOT EXISTS acompanhamentos (
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    edital_id TEXT NOT NULL REFERENCES editais(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    nota TEXT NOT NULL DEFAULT '',
    atualizado TEXT NOT NULL,
    PRIMARY KEY (usuario_id, edital_id)
);
CREATE TABLE IF NOT EXISTS detalhes_pncp (
    edital_id TEXT NOT NULL,
    tipo TEXT NOT NULL,               -- 'itens' ou 'arquivos'
    conteudo TEXT NOT NULL,           -- JSON já limpo
    buscado_em TEXT NOT NULL,
    PRIMARY KEY (edital_id, tipo)
);
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
        _migrar(conexao)
    finally:
        conexao.close()


def _migrar(conexao: sqlite3.Connection) -> None:
    """Acrescenta colunas novas em bancos criados por versões anteriores."""
    existentes = {linha["name"] for linha in conexao.execute("PRAGMA table_info(editais)")}
    for coluna, tipo in (("ano", "INTEGER"), ("sequencial", "INTEGER")):
        if coluna not in existentes:
            conexao.execute(f"ALTER TABLE editais ADD COLUMN {coluna} {tipo}")


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
