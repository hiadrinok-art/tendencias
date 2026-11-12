#!/usr/bin/env python3
"""montar.py — transforma plano.json em plano.js (lido pela cena) e mixa o áudio final.

Uso: python3 montar.py <pasta_da_cena>   (a pasta que contém plano.json)

Mixagem (audio/mix.wav):
  - narração com atraso_narracao;
  - trilha com envelope de volume em dB (trilha_envelope: [[t, dB], ...], interpolação linear);
    com "trilha_abaixo_da_voz": N, a trilha é medida a cada 0,5 s e mantida N dB abaixo da fala
    (o envelope vira desvio relativo: 0 = normal, -60 = silêncio);
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

def aplicar_envelope(arquivo, pts, destino):
    """Aplica o envelope [[t, dB], ...] (t do plano; soma-se o atraso) nas amostras e grava WAV estéreo 48 kHz."""
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(arquivo), "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()
    t = np.arange(len(x)) / 48000.0
    ts = np.array([p[0] + off for p in pts]); db = np.array([p[1] for p in pts], dtype=np.float64)
    ganho = 10 ** (np.interp(t, ts, db) / 20)
    x *= ganho[:, None].astype(np.float32)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ac", "2", "-ar", "48000", "-i", "-", str(destino)],
                   input=x.tobytes(), check=True)

def rms_janelas(arquivo, passo=0.5):
    """RMS (dB) a cada `passo` segundos."""
    n = int(48000 * passo)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(arquivo), "-af",
                        f"aresample=48000,asetnsamples=n={n}:p=0,astats=metadata=1:reset=1,"
                        "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-", "-f", "null", "-"],
                       capture_output=True, text=True)
    vals = []
    for linha in r.stdout.splitlines():
        if "RMS_level=" in linha:
            v = linha.split("=")[-1]
            vals.append(-120.0 if "inf" in v else float(v))
    return vals

envelope = A["trilha_envelope"]
if A.get("trilha_abaixo_da_voz") is not None:
    # Modo automático: a trilha fica sempre `trilha_abaixo_da_voz` dB abaixo da fala,
    # compensando o crescendo da própria música. O envelope vira desvio relativo (0 = normal, -60 = silêncio).
    voz = [v for v in rms_janelas(base / A["narracao"]) if v > -45]
    nivel_voz = sum(voz) / len(voz)
    tri = rms_janelas(base / A["trilha"])
    suave = [sum(tri[max(0, i - 3):i + 4]) / len(tri[max(0, i - 3):i + 4]) for i in range(len(tri))]
    def desvio(t):
        pts = envelope
        if t <= pts[0][0]: return pts[0][1]
        for (t1, d1), (t2, d2) in zip(pts, pts[1:]):
            if t <= t2: return d1 + (d2 - d1) * (t - t1) / max(t2 - t1, 1e-3)
        return pts[-1][1]
    pontos, t = [], -off
    while t <= dur - off + 1e-6:
        i = min(int((t + off) / 0.5), len(suave) - 1)
        base_db = min(6.0, (nivel_voz - A["trilha_abaixo_da_voz"]) - suave[i])
        pontos.append([round(t, 3), round(base_db + desvio(t), 2)])
        t += 0.5
    # mantém os cantos exatos do envelope (cortes secos no carimbo etc.)
    for tt, _ in envelope:
        i = min(max(int((tt + off) / 0.5), 0), len(suave) - 1)
        pontos.append([tt, round(min(6.0, (nivel_voz - A["trilha_abaixo_da_voz"]) - suave[i]) + desvio(tt), 2)])
    envelope = sorted({p[0]: p for p in pontos}.values())

trilha_env = base / "audio" / "_trilha_env.wav"
aplicar_envelope(base / A["trilha"], envelope, trilha_env)
entradas = ["-i", str(base / A["narracao"]), "-i", str(trilha_env)]
filtros = [f"[0:a]aresample=48000,adelay={int(off*1000)}:all=1,apad[nar]",
           "[1:a]aresample=48000,apad[tri]"]
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

filtros.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{dur}[pre]")
saida = base / "audio" / "mix.wav"
bruto = base / "audio" / "_mix_bruto.wav"
subprocess.run(["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[pre]",
                "-ac", "2", "-ar", "48000", str(bruto)], check=True)

# Normalização em DUAS passadas e LINEAR (-16 LUFS, pico -1.5 dBTP).
# A de uma passada age como compressor dinâmico: sobe as partes baixas e desfaz o envelope da trilha.
alvo = "I=-16:TP=-1.5:LRA=20"
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(bruto), "-af", f"loudnorm={alvo}:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
med = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
seg = (f"loudnorm={alvo}:linear=true:measured_I={med['input_i']}:measured_TP={med['input_tp']}"
       f":measured_LRA={med['input_lra']}:measured_thresh={med['input_thresh']}:offset={med['target_offset']}")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(bruto), "-af", seg + ",aresample=48000", "-ar", "48000", str(saida)], check=True)
bruto.unlink()
trilha_env.unlink()
print("ok: plano.js e audio/mix.wav")
