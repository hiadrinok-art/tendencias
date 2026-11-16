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
CREATE TABLE IF NOT EXISTS alertas_config (
    usuario_id INTEGER PRIMARY KEY REFERENCES usuarios(id) ON DELETE CASCADE,
    telefone TEXT,                     -- E.164 sem "+", ex.: 5511987654321
    telefone_verificado INTEGER NOT NULL DEFAULT 0,
    consentimento_em TEXT,             -- quando aceitou receber no WhatsApp
    codigo_hash TEXT,
    codigo_expira TEXT,
    codigo_tentativas INTEGER NOT NULL DEFAULT 0,
    novos_editais INTEGER NOT NULL DEFAULT 1,
    processos INTEGER NOT NULL DEFAULT 1,
    atas_ramo INTEGER NOT NULL DEFAULT 1,
    atas_processos INTEGER NOT NULL DEFAULT 1,
    ultimo_resumo TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS alertas_telefone ON alertas_config(telefone) WHERE telefone_verificado = 1;
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    chave TEXT NOT NULL,               -- evita alerta repetido
    tipo TEXT NOT NULL,                -- prazo, situacao, documento, resultado, ata_processo, atas_ramo, novos_editais
    edital_id TEXT,
    titulo TEXT NOT NULL,
    texto TEXT NOT NULL,
    link TEXT,
    criado TEXT NOT NULL,
    lido INTEGER NOT NULL DEFAULT 0,
    whatsapp TEXT,                     -- NULL = não enviar; pendente, enviado, erro, limite, simulado
    whatsapp_em TEXT,
    UNIQUE (usuario_id, chave)
);
CREATE INDEX IF NOT EXISTS eventos_usuario ON eventos(usuario_id, criado);
CREATE TABLE IF NOT EXISTS processos_estado (
    edital_id TEXT PRIMARY KEY,
    situacao TEXT,
    encerramento TEXT,
    documentos TEXT NOT NULL DEFAULT '[]',
    tem_resultado INTEGER NOT NULL DEFAULT 0,
    verificado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS atas (
    id TEXT PRIMARY KEY,               -- número de controle PNCP da ata
    compra_id TEXT NOT NULL,
    numero TEXT,
    orgao TEXT NOT NULL,
    orgao_cnpj TEXT NOT NULL,
    objeto TEXT NOT NULL,
    vigencia_inicio TEXT,
    vigencia_fim TEXT,
    publicado TEXT,
    ramos TEXT NOT NULL DEFAULT '[]',
    coletado_em TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS atas_compra ON atas(compra_id);
CREATE TABLE IF NOT EXISTS mensagens_simuladas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,  -- some com a conta (LGPD)
    telefone TEXT NOT NULL,
    conteudo TEXT NOT NULL,
    criado TEXT NOT NULL
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
