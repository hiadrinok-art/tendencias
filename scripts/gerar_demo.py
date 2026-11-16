"""Gera a versão de demonstração (site estático) para o GitHub Pages.

    python scripts/gerar_demo.py --saida _site            # coleta no PNCP e gera
    python scripts/gerar_demo.py --saida _site --banco dados/radar.db   # usa banco existente

A demonstração não tem contas: o visitante escolhe ramo e estados na tela e a
escolha fica só no navegador dele. Nada de dados pessoais é coletado. Só a
pasta gerada é publicada (nunca o repositório inteiro).
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from radar import banco, coletor  # noqa: E402
from radar.classificador import RAMOS  # noqa: E402

SITE = RAIZ / "radar" / "site"
DEMO = RAIZ / "demo"
CAMPOS = ["id", "orgao", "unidade", "municipio", "uf", "modalidade", "objeto", "valor_estimado",
          "abertura", "encerramento", "publicado", "link_origem", "link_pncp", "ramos"]

# Ajustes na landing do site completo para a versão de demonstração.
TROCAS_LANDING = [
    ('href="/static/', 'href="static/'),
    ('<a class="marca" href="/">', '<a class="marca" href="./">'),
    ('<a href="/entrar">Entrar</a>\n', ''),
    ('href="/cadastro">Cadastre seu ramo</a>', 'href="painel.html">Testar agora</a>'),
    ('href="/cadastro">Cadastre seu ramo — é grátis</a>', 'href="painel.html">Testar agora — sem cadastro</a>'),
    ('Protótipo em teste com empresas piloto. Sem cartão.',
     'Demonstração: sem cadastro, sem e-mail e sem senha. Editais reais do PNCP, atualizados todo dia.'),
    ('href="/cadastro">Começar grátis</a>', 'href="painel.html">Testar agora</a>'),
    ('href="/cadastro">Entrar na lista do Pro</a>', 'href="painel.html">Testar agora</a>'),
    ('href="/cadastro">Cadastrar meu ramo</a>', 'href="painel.html">Ver os editais do meu ramo</a>'),
    ('Cadastre seu ramo e veja os editais abertos ainda hoje.', 'Escolha seu ramo e veja os editais abertos agora.'),
]
CSP = ("default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
       "form-action 'none'; base-uri 'none'; object-src 'none'")


def exportar(caminho_banco: str) -> list[dict]:
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None).isoformat(timespec="seconds")
    conexao = banco.conectar(caminho_banco)
    try:
        linhas = conexao.execute(
            f"SELECT {', '.join(CAMPOS)} FROM editais WHERE encerramento > ? ORDER BY encerramento",
            (agora,)).fetchall()
    finally:
        conexao.close()
    saida = []
    for l in linhas:
        e = dict(l)
        e["ramos"] = json.loads(e["ramos"])
        saida.append(e)
    return saida


def gerar(saida: Path, caminho_banco: str) -> int:
    if saida.exists():
        shutil.rmtree(saida)
    (saida / "static").mkdir(parents=True)
    (saida / "dados").mkdir()

    for arquivo in ("app.css", "app.js", "icone.svg"):
        shutil.copy(SITE / "static" / arquivo, saida / "static" / arquivo)
    for arquivo in DEMO.glob("*.js"):
        shutil.copy(arquivo, saida / "static" / arquivo.name)
    for arquivo in DEMO.glob("*.html"):
        shutil.copy(arquivo, saida / arquivo.name)

    landing = (SITE / "index.html").read_text()
    for antes, depois in TROCAS_LANDING:
        if antes not in landing:
            raise SystemExit(f"Landing mudou; ajuste TROCAS_LANDING: {antes!r}")
        landing = landing.replace(antes, depois)
    landing = landing.replace('<meta charset="utf-8">',
                              f'<meta charset="utf-8">\n<meta http-equiv="Content-Security-Policy" content="{CSP}">', 1)
    (saida / "index.html").write_text(landing)

    editais = exportar(caminho_banco)
    dados = {
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ramos": [{"id": k, "nome": v} for k, v in RAMOS.items()],
        "editais": editais,
    }
    (saida / "dados" / "editais.json").write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
    (saida / ".nojekyll").write_text("")
    return len(editais)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--saida", default="_site")
    p.add_argument("--banco", help="banco já coletado; sem isso, coleta agora no PNCP")
    p.add_argument("--dias", type=int, default=4)
    args = p.parse_args()
    caminho = args.banco
    if not caminho:
        caminho = str(Path(tempfile.mkdtemp()) / "radar.db")
        coletor.coletar(caminho, dias=args.dias)
    n = gerar(Path(args.saida), caminho)
    print(f"Demonstração gerada em {args.saida} com {n} editais abertos.")


if __name__ == "__main__":
    main()
