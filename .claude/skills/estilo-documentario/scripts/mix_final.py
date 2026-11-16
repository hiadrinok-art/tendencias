#!/usr/bin/env python3
"""mix_final.py — mixagem ÚNICA do documentário inteiro (todas as cenas), com sincronia conferida.

Uso: python3 mix_final.py <pasta_do_projeto>

Lê:
  narracao_total.wav, cenas.json, cenas/<cena>/plano.resolvido.json
  trilhas.json   [{"arquivo": "trilhas/x.mp3", "ini": "<cena>@<t>" ou segundos globais, "fim": ...,
                   "abaixo_da_voz": 14, "fade_in": 1.0, "fade_out": 2.0,
                   "envelope": [["c5@14.2", -60], ...]}]   (desvio em dB; 0 = normal)
  efeitos/<nome>.mp3|wav
Gera:
  mix.wav (48 kHz estéreo, -16 LUFS, linear) e sincronia.txt

Sincronia dos efeitos: cada arquivo de efeito tem o silêncio inicial MEDIDO (primeira amostra acima de
-30 dB do pico) e descontado, para o ataque cair exatamente no tempo do destaque.
"""
import json, subprocess, sys, re
from pathlib import Path
import numpy as np

SR = 48000
proj = Path(sys.argv[1]).resolve()
C = json.loads((proj / "cenas.json").read_text(encoding="utf-8"))
ordem = list(C.keys())

def ler(arq, canais=2):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arq), "-f", "f32le", "-ac", str(canais), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, canais).copy()

def tglobal(v):
    if isinstance(v, (int, float)): return float(v)
    c, t = v.split("@"); return C[c]["ini"] + float(t)

def env_db(x, passo=0.5):
    m = x.mean(axis=1) if x.ndim == 2 else x
    n = int(SR * passo); k = len(m) // n
    return 20 * np.log10(np.sqrt(np.mean(m[:k * n].reshape(k, n) ** 2, axis=1) + 1e-12))

voz = ler(proj / "narracao_total.wav", 1)[:, 0]
N = len(voz)
mix = np.zeros((N, 2), np.float32); mix += voz[:, None]
ev = env_db(voz); nivel_voz = float(np.mean(ev[ev > -45]))

# ---- trilhas (niveladas sob a voz, com envelope de desvio)
for tr in json.loads((proj / "trilhas.json").read_text(encoding="utf-8")):
    x = ler(proj / tr["arquivo"]); ini = tglobal(tr["ini"]); fim = tglobal(tr["fim"])
    x = x[: int((fim - ini) * SR)]
    t = np.arange(len(x)) / SR
    e = env_db(x); suave = np.convolve(e, np.ones(7) / 7, mode="same")
    base_db = np.clip((nivel_voz - tr.get("abaixo_da_voz", 14)) - suave, -40, 12)
    g_db = np.interp(t, (np.arange(len(base_db)) + 0.5) * 0.5, base_db)
    pts = sorted([[tglobal(a) - ini, d] for a, d in tr.get("envelope", [])])
    if pts: g_db = g_db + np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
    g = 10 ** (g_db / 20)
    fi, fo = tr.get("fade_in", 1.0), tr.get("fade_out", 2.0)
    g *= np.clip(t / max(fi, 1e-3), 0, 1) * np.clip((t[-1] - t) / max(fo, 1e-3), 0, 1)
    a = int(ini * SR); b = min(N, a + len(x)); mix[a:b] += (x[: b - a] * g[: b - a, None])

# ---- efeitos de todas as cenas
cache, linhas = {}, []
def efeito(nome):
    if nome in cache: return cache[nome]
    arq = next((proj / "efeitos").glob(nome + ".*"))
    x = ler(arq); amp = np.abs(x).max(axis=1); pico = amp.max()
    ataque = int(np.argmax(amp > pico * 10 ** (-30 / 20)))
    cache[nome] = (x[ataque:], ataque / SR); return cache[nome]
GANHO = {"carimbo": 1.0, "papel": 0.55, "maquina": 0.45, "pena": 0.5}
for c in ordem:
    P = json.loads((proj / "cenas" / c / "plano.resolvido.json").read_text(encoding="utf-8"))
    eventos = [(b["t"], b["som"], f"beat {b['id']} '{b['gatilho']}'", b["acao"]) for b in P["beats"] if b.get("som")]
    eventos += [(t, s, "extra", "") for t, s in P.get("sons_extras", [])]
    for t, som, rot, acao in eventos:
        x, corte = efeito(som); tg = C[c]["ini"] + t
        a = int(round(tg * SR)); b = min(N, a + len(x))
        if a < N: mix[a:b] += x[: b - a] * GANHO.get(som, 0.6)
        linhas.append(f"{c:8s} {rot:34s} {som:10s} destaque {tg:8.3f}s  ataque do som {tg:8.3f}s  (silêncio inicial removido: {corte*1000:4.0f} ms)")

bruto = proj / "_mix_bruto.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", str(bruto)],
               input=mix.astype(np.float32).tobytes(), check=True)
alvo = "I=-16:TP=-1.5:LRA=20"
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(bruto), "-af", f"loudnorm={alvo}:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
seg = (f"loudnorm={alvo}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}"
       f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-af", seg + ",aresample=48000", "-ar", "48000", str(proj / "mix.wav")], check=True)
bruto.unlink()
(proj / "sincronia.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8")
print(f"mix.wav pronto ({N/SR:.2f} s); {len(linhas)} efeitos posicionados; relatório em sincronia.txt")
