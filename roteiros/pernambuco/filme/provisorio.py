#!/usr/bin/env python3
"""Enquanto não há narração: usa t_prov dos beats e dur_prov do plano para pré-visualizar a cena."""
import json, re, sys
from pathlib import Path
proj, cena = Path(sys.argv[1]), sys.argv[2]
P = json.loads((proj / "cenas" / cena / "plano.json").read_text(encoding="utf-8"))
tempos = {}
for b in P["beats"]:
    b["t"] = b["t_prov"]; tempos[str(b["id"])] = b["t"]
def tempo(v):
    if isinstance(v, (int, float)): return float(v)
    m = re.fullmatch(r"@([\w.]+)\s*([+-]\s*[\d.]+)?", v.strip()); ref, d = m.group(1), float((m.group(2) or "0").replace(" ", ""))
    return d if ref == "ini" else (P["dur_prov"] + d if ref == "fim" else tempos[ref] + d)
P["camera"] = sorted([[round(tempo(k[0]), 3)] + k[1:] for k in P["camera"]], key=lambda k: k[0])
P["sons_extras"] = [[tempo(t), s] for t, s in P.get("sons_extras", [])]
P["duracao"] = P["dur_prov"]; P["atraso_narracao"] = 0.0
(proj / "cenas" / cena / "plano.js").write_text("window.PLANO = " + json.dumps(P, ensure_ascii=False) + ";\n", encoding="utf-8")
(proj / "cenas" / cena / "plano.resolvido.json").write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[{cena}] PROVISÓRIO: {len(P['beats'])} beats, {P['duracao']} s")
