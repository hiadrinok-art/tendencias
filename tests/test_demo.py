import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import gerar_demo  # noqa: E402

from .test_editais import bruto, gravar  # noqa: E402


def test_demo_publica_so_o_necessario(tmp_path):
    caminho = str(tmp_path / "t.db")
    gravar(caminho, bruto(), bruto(numeroControlePNCP="V-1", sequencialCompra=9,
                                   dataEncerramentoProposta="2020-01-01T10:00:00"))
    saida = tmp_path / "_site"
    assert gerar_demo.gerar(saida, caminho) == 1  # o encerrado fica de fora

    arquivos = sorted(str(p.relative_to(saida)) for p in saida.rglob("*") if p.is_file())
    assert arquivos == [".nojekyll", "dados/editais.json", "edital.html", "index.html", "painel.html",
                        "static/app.css", "static/app.js", "static/demo.js", "static/icone.svg"]

    dados = json.loads((saida / "dados" / "editais.json").read_text())
    assert set(dados["editais"][0]) == set(gerar_demo.CAMPOS)
    assert dados["editais"][0]["ramos"] == ["ti"]

    for pagina in ("index.html", "painel.html", "edital.html"):
        html = (saida / pagina).read_text()
        assert 'http-equiv="Content-Security-Policy"' in html and "unsafe-inline" not in html
        assert 'href="/' not in html and 'src="/' not in html  # tudo relativo (Pages fica em /tendencias/)
