#!/usr/bin/env python3
"""conferir_av.py — mede a sincronia REAL entre imagem e som no vídeo renderizado.

Uso: python3 conferir_av.py <projeto> <cena> <video_da_cena.mp4>

Para cada destaque de IMPACTO (carimbar, cair, alfinete) com som:
  - imagem: quadro de maior mudança (diferença entre quadros) numa janela de ±0,5 s do destaque
  - som: PICO do efeito (o impacto) na trilha só de efeitos (efeitos_stem.wav gerado pelo mix_final.py)
Mostra a diferença som − imagem. Até ±1 quadro (33 ms) é imperceptível; acima de 80 ms é atraso visível.

ATENÇÃO: a "imagem" é o quadro de maior mudança, e um movimento grande de câmera pode enganar o detector.
Por isso o script também grava, em <projeto>/conf/av/<cena>_<beat>.png, uma tira de quadros de t-0,2 s a t+0,17 s
com o tempo de cada quadro e o quadro do ataque do som marcado com ♪ — confira olhando.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

proj, cena, video = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
C = json.loads((proj / "cenas.json").read_text())[cena]
P = json.loads((proj / "cenas" / cena / "plano.resolvido.json").read_text())
FPS, W, H = 30, 320, 180
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
dif = np.r_[0, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))]

SR = 48000
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(proj / "efeitos_stem.wav"), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                     capture_output=True, check=True).stdout
efx = np.abs(np.frombuffer(pcm, np.float32))

ruins = 0
print(f"{'beat':>5} {'gatilho':14} {'ação':12} {'imagem':>8} {'som':>8} {'som−img':>8}")
for b in sorted(P["beats"], key=lambda b: b["t"]):
    if not b.get("som") or b["acao"] not in ("carimbar", "cair", "alfinete"): continue
    t = b["t"]; a, z = max(1, int((t - 0.5) * FPS)), min(len(dif) - 1, int((t + 0.5) * FPS))
    img = (a + int(np.argmax(dif[a:z + 1]))) / FPS
    g0 = int((C["ini"] + t - 0.3) * SR); g1 = int((C["ini"] + t + 0.5) * SR); seg = efx[g0:g1]
    if seg.size == 0 or seg.max() < 1e-4: print(f"{b['id']:>5} {b['gatilho'][:14]:14} {b['acao']:12} {img:8.3f}    (sem som)"); continue
    env = np.convolve(seg, np.ones(240) / 240, mode="same")   # pico do som (o impacto)
    som = (g0 + int(np.argmax(env))) / SR - C["ini"]
    d = som - img; flag = "" if abs(d) <= 0.08 else "  <-- conferir na tira"
    from PIL import Image, ImageDraw
    pasta = proj / "conf" / "av"; pasta.mkdir(parents=True, exist_ok=True)
    q0 = int(round((t - 0.2) * FPS)); qs = [q for q in range(q0, q0 + 12) if 0 <= q < len(fr)]
    tira = Image.new("L", (W * 6, H * 2)); dr = ImageDraw.Draw(tira); qsom = int(round(som * FPS))
    for i, q in enumerate(qs):
        im = Image.fromarray(fr[q].astype(np.uint8)); tira.paste(im, ((i % 6) * W, (i // 6) * H))
        dr.text(((i % 6) * W + 6, (i // 6) * H + 4), f"{q / FPS:.3f}s" + ("  ♪ SOM" if q == qsom else ""), fill=255)
    tira.save(pasta / f"{cena}_{b['id']}.png")
    ruins += bool(flag)
    print(f"{b['id']:>5} {b['gatilho'][:14]:14} {b['acao']:12} {img:8.3f} {som:8.3f} {d*1000:+7.0f} ms{flag}")
print("SINCRONIA OK" if not ruins else f"{ruins} destaque(s) para conferir nas tiras em conf/av/")
