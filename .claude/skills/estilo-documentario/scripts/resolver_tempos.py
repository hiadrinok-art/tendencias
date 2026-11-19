#!/usr/bin/env python3
"""resolver_tempos.py — transforma palavras-gatilho em tempos exatos, para uma cena de um projeto multi-cena.

Uso: python3 resolver_tempos.py <pasta_do_projeto> <cena>

Lê <projeto>/cenas/<cena>/plano.json, <projeto>/palavras.json e <projeto>/cenas.json e escreve
<projeto>/cenas/<cena>/plano.js com tempos LOCAIS da cena (0 = início da cena).

No plano:
  beats[].gatilho       palavra falada (acentos/pontuação ignorados; aceita grafia próxima; alternativas com "|", ex.: "setenta|75")
  beats[].n             qual ocorrência dessa palavra na cena (1 = primeira). Sem "n", vale a 1ª ocorrência
                        DEPOIS do beat anterior (na ordem dos ids), então palavras repetidas não roubam o beat
  beats[].desloc        ajuste fino em s (ex.: -0.1 para o impacto cair um pouco antes)
  camera[i][0]          número (s locais) ou texto "@<id>", "@<id>+0.4", "@<id>-0.6", "@fim-1.5", "@ini+0.2"
  audio.trilha_envelope e sons_extras aceitam o mesmo formato de tempo.
Se uma palavra não for encontrada, o script PARA com erro: nada é chutado.
"""
import difflib, json, re, sys, unicodedata
from pathlib import Path

proj, cena = Path(sys.argv[1]).resolve(), sys.argv[2]
P = json.loads((proj / "cenas" / cena / "plano.json").read_text(encoding="utf-8"))
W = [w for w in json.loads((proj / "palavras.json").read_text(encoding="utf-8")) if w["cena"] == cena]
C = json.loads((proj / "cenas.json").read_text(encoding="utf-8"))[cena]

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(ch for ch in s if unicodedata.category(ch) != "Mn"))

def achar(gatilho, n, depois=None):
    # alternativas com "|": a transcrição pode escrever números por extenso ou em algarismos ("setenta|75")
    hits = []
    for alt in gatilho.split("|"):
        alvo = norm(alt)
        hits = [w for w in W if norm(w["w"]) == alvo] or \
               [w for w in W if difflib.SequenceMatcher(None, norm(w["w"]), alvo).ratio() >= 0.75]
        if len(hits) >= n: break
    # sem "n" explícito: a 1ª ocorrência DEPOIS do beat anterior (uma palavra repetida antes não rouba o beat)
    if depois is not None:
        hits = [w for w in hits if w["ini"] - C["ini"] >= depois - 0.05] or hits
    if len(hits) < n:
        raise SystemExit(f"[{cena}] gatilho '{gatilho}' (ocorrência {n}) não encontrado. Palavras da cena: "
                         + " ".join(w["w"] for w in W))
    return hits[n - 1]["ini"] - C["ini"]

tempos = {}; ant = 0.0
for b in sorted(P["beats"], key=lambda b: float(b["id"])):   # beats na ordem da fala (id 10.1 vem antes de 11)
    bruto = achar(b["gatilho"], b.get("n", 1), None if "n" in b else ant)
    b["t"] = round(bruto + b.get("desloc", 0.0), 3); ant = bruto
    tempos[str(b["id"])] = b["t"]

def tempo(v):
    if isinstance(v, (int, float)): return float(v)
    m = re.fullmatch(r"@([\w.]+)\s*([+-]\s*[\d.]+)?", v.strip())
    if not m: raise SystemExit(f"[{cena}] tempo inválido: {v}")
    ref, d = m.group(1), float((m.group(2) or "0").replace(" ", ""))
    if ref == "ini": return d
    if ref == "fim": return C["dur"] + d
    if ref not in tempos: raise SystemExit(f"[{cena}] beat '{ref}' não existe (usado em {v})")
    return tempos[ref] + d

P["camera"] = [[round(tempo(k[0]), 3)] + k[1:] for k in P["camera"]]
P["camera"].sort(key=lambda k: k[0])
for a, b in zip(P["camera"], P["camera"][1:]):
    if b[0] - a[0] < 0.05: raise SystemExit(f"[{cena}] keyframes de câmera colados: {a[0]} e {b[0]}")
if "audio" in P and "trilha_envelope" in P["audio"]:
    P["audio"]["trilha_envelope"] = sorted([[round(tempo(t), 3), v] for t, v in P["audio"]["trilha_envelope"]])
P["sons_extras"] = [[round(tempo(t), 3), s] for t, s in P.get("sons_extras", [])]
P["duracao"] = C["dur"]; P["atraso_narracao"] = 0.0; P["cena"] = cena; P["ini_global"] = C["ini"]
(proj / "cenas" / cena / "plano.js").write_text("window.PLANO = " + json.dumps(P, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
(proj / "cenas" / cena / "plano.resolvido.json").write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"[{cena}] {len(P['beats'])} beats resolvidos; duração {C['dur']:.3f} s ({C['quadros']} quadros)")
