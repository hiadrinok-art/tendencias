#!/usr/bin/env python3
"""conferir_sincronia.py — confere se cada destaque do plano cai na palavra falada.

Uso: python3 conferir_sincronia.py plano.json palavras.json [--tolerancia 0.08]
Para cada beat, procura a palavra-gatilho (sem acento/pontuação) em palavras.json perto de t
e mostra a diferença. Também acusa dois destaques com menos de 0,35 s entre si (risco de dois acesos).
Sai com código 1 se algo estiver fora da tolerância.
"""
import argparse, difflib, json, sys, unicodedata, re

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

ap = argparse.ArgumentParser()
ap.add_argument("plano"); ap.add_argument("palavras"); ap.add_argument("--tolerancia", type=float, default=0.08)
a = ap.parse_args()
P = json.load(open(a.plano, encoding="utf-8")); W = json.load(open(a.palavras, encoding="utf-8"))
ruim = 0
print(f"{'beat':>5}  {'gatilho':<12} {'plano':>7} {'fala':>7} {'dif':>6}")
for b in sorted(P["beats"], key=lambda b: b["t"]):
    alvo = norm(b["gatilho"])
    # aceita grafias próximas da transcrição (ex.: "Frey" para "Frei")
    cands = [w for w in W if norm(w["w"]) == alvo or difflib.SequenceMatcher(None, norm(w["w"]), alvo).ratio() >= 0.75]
    if not cands:
        print(f"{b['id']:>5}  {b['gatilho']:<12} {b['t']:7.2f}   (palavra não encontrada)"); ruim += 1; continue
    w = min(cands, key=lambda w: abs(w["ini"] - b["t"]))
    d = b["t"] - w["ini"]
    flag = "" if abs(d) <= a.tolerancia else "  <-- fora"
    ruim += bool(flag)
    print(f"{b['id']:>5}  {b['gatilho']:<12} {b['t']:7.2f} {w['ini']:7.2f} {d:+6.2f}{flag}")
ts = sorted((b["t"], b["id"]) for b in P["beats"] if b.get("acao") not in ("circular",))
for (t1, i1), (t2, i2) in zip(ts, ts[1:]):
    if t2 - t1 < 0.35:
        print(f"aviso: beats {i1} e {i2} com {t2-t1:.2f}s de distância (dois destaques quase juntos)"); ruim += 1
print("OK" if not ruim else f"{ruim} problema(s)")
sys.exit(1 if ruim else 0)
