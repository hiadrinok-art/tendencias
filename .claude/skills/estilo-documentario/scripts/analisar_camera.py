#!/usr/bin/env python3
"""Mede o movimento global da câmera quadro a quadro e aponta trancos.

Uso: python3 analisar_camera.py video.mp4 [--limiar 3.0]
Requer: opencv-python, numpy.
Saída: camera_velocidade.csv e camera_velocidade.png (picos em vermelho).
"""
import argparse, csv
import cv2, numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--limiar", type=float, default=3.0,
    help="pico = aceleração maior que N desvios-padrão da mediana")
a = ap.parse_args()

cap = cv2.VideoCapture(a.video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
ok, prev = cap.read(); prev = cv2.cvtColor(cv2.resize(prev, (480, 270)), cv2.COLOR_BGR2GRAY)
vel = []
diag = float(np.hypot(480, 270))

def movimento(a, b):
    """Movimento global entre dois quadros: translação + zoom + rotação, em px (480x270)."""
    pts = cv2.goodFeaturesToTrack(a, 400, 0.01, 8)
    if pts is None or len(pts) < 8:
        return 0.0
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(a, b, pts, None)
    ok = st.ravel() == 1
    if ok.sum() < 8:
        return 0.0
    M, _ = cv2.estimateAffinePartial2D(pts[ok], nxt[ok])
    if M is None:
        return 0.0
    escala = float(np.hypot(M[0, 0], M[1, 0]))
    rot = float(np.arctan2(M[1, 0], M[0, 0]))
    return float(np.hypot(M[0, 2], M[1, 2]) + abs(escala - 1) * diag / 2 + abs(rot) * diag / 2)

while True:
    ok, f = cap.read()
    if not ok: break
    g = cv2.cvtColor(cv2.resize(f, (480, 270)), cv2.COLOR_BGR2GRAY)
    vel.append(movimento(prev, g)); prev = g
v = np.array(vel); acc = np.abs(np.diff(v, prepend=v[:1]))
med, sd = np.median(acc), acc.std() or 1e-9
picos = np.where(acc > med + a.limiar * sd)[0]
with open("camera_velocidade.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["quadro", "tempo_s", "velocidade", "aceleracao", "tranco"])
    for i, (x, y) in enumerate(zip(v, acc)):
        w.writerow([i + 1, round((i + 1) / fps, 3), round(x, 4), round(y, 4), int(i in set(picos))])
paradas = np.where(v < 0.05)[0]
print(f"{len(picos)} trancos:", ", ".join(f"{(i+1)/fps:.2f}s" for i in picos[:30]))
print(f"{len(paradas)} quadros com câmera praticamente parada (verifique se é intencional).")
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    t = np.arange(1, len(v) + 1) / fps
    plt.figure(figsize=(12, 3)); plt.plot(t, v, lw=1)
    plt.scatter(t[picos], v[picos], c="red", s=12); plt.xlabel("s"); plt.ylabel("px/quadro")
    plt.tight_layout(); plt.savefig("camera_velocidade.png", dpi=120)
except ImportError:
    pass
