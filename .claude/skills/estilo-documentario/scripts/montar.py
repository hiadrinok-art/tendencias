#!/usr/bin/env python3
"""montar.py — transforma plano.json em plano.js (lido pela cena) e mixa o áudio final.

Uso: python3 montar.py <pasta_da_cena>   (a pasta que contém plano.json)

Mixagem (audio/mix.wav):
  - narração com atraso_narracao;
  - trilha com envelope de volume em dB (trilha_envelope: [[t, dB], ...], interpolação linear);
  - efeitos posicionados no tempo de cada beat que tem "som" (no impacto do carimbo, exatamente em t);
  - "sons_extras": [[t, som]] para sons que não pertencem a um destaque;
  - normalização final para -16 LUFS (padrão de redes/YouTube), pico máximo -1.5 dBTP.
"""
import json, subprocess, sys
from pathlib import Path

base = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
P = json.loads((base / "plano.json").read_text(encoding="utf-8"))
(base / "plano.js").write_text("window.PLANO = " + json.dumps(P, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")

A, off, dur = P["audio"], P.get("atraso_narracao", 0.0), P["duracao"]

def expr_envelope(pts):
    """Expressão ffmpeg (ganho linear) interpolando pontos [t, dB]; t do plano + atraso."""
    pts = [(t + off, db) for t, db in pts]
    g = lambda db: 10 ** (db / 20)
    e = f"{g(pts[-1][1]):.6f}"
    for (t1, d1), (t2, d2) in reversed(list(zip(pts, pts[1:]))):
        lin = f"({g(d1):.6f}+({g(d2):.6f}-{g(d1):.6f})*(t-{t1:.3f})/{max(t2 - t1, 1e-3):.3f})"
        e = f"if(lt(t,{t2:.3f}),{lin},{e})"
    return f"if(lt(t,{pts[0][0]:.3f}),{g(pts[0][1]):.6f},{e})"

entradas = ["-i", str(base / A["narracao"]), "-i", str(base / A["trilha"])]
filtros = [f"[0:a]aresample=48000,adelay={int(off*1000)}:all=1,apad[nar]",
           f"[1:a]aresample=48000,volume='{expr_envelope(A['trilha_envelope'])}':eval=frame,apad[tri]"]
mix = ["[nar]", "[tri]"]
idx = 2
for b in P["beats"]:
    som = b.get("som")
    if not som:
        continue
    t = b["t"] + off
    if b["acao"] == "carimbar":
        t -= 0.01                      # transiente do carimbo cai no quadro do impacto
    entradas += ["-i", str(base / A["efeitos"][som])]
    ganho = {"carimbo": 1.0, "papel": 0.55, "maquina": 0.45}.get(som, 0.6)
    filtros.append(f"[{idx}:a]aresample=48000,volume={ganho},adelay={int(max(t,0)*1000)}:all=1,apad[e{idx}]")
    mix.append(f"[e{idx}]"); idx += 1

# sons sem destaque próprio: "sons_extras": [[t, "nome"], ...]
for t, som in P.get("sons_extras", []):
    entradas += ["-i", str(base / A["efeitos"][som])]
    filtros.append(f"[{idx}:a]aresample=48000,volume=0.8,adelay={int(max(t + off, 0)*1000)}:all=1,apad[e{idx}]")
    mix.append(f"[e{idx}]"); idx += 1

filtros.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{dur},loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[out]")
cmd = ["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[out]", "-ac", "2", "-ar", "48000", str(base / "audio" / "mix.wav")]
subprocess.run(cmd, check=True)
print("ok: plano.js e audio/mix.wav")
