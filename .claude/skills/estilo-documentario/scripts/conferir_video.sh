#!/usr/bin/env bash
# Uso: conferir_video.sh video.mp4 [pasta_saida]
# Gera quadros a cada 0,5 s, folhas de contato e um resumo de volume do áudio.
set -euo pipefail
V="$1"; OUT="${2:-conferencia}"
mkdir -p "$OUT/quadros"
ffmpeg -loglevel error -y -i "$V" -vf "fps=2,scale=480:-1" "$OUT/quadros/q_%04d.png"
ffmpeg -loglevel error -y -i "$V" -vf "fps=2,scale=320:-1,tile=6x5" "$OUT/folha_%02d.png"
# RMS (dB) em blocos de 0,5 s: tempo_s,rms_db
SR=48000
ffmpeg -hide_banner -nostats -i "$V" -vn -af "aresample=$SR,asetnsamples=n=$((SR/2)):p=0,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null - 2>/dev/null \
  | awk -F'[ :=]+' '/pts_time/{t=$NF} /RMS_level/{print t","$NF}' > "$OUT/rms_por_0.5s.txt" || true
echo "Quadros: $OUT/quadros  |  Folhas de contato: $OUT/folha_*.png  |  RMS: $OUT/rms_por_0.5s.txt"
echo "Agora rode: python3 $(dirname "$0")/analisar_camera.py $V"
