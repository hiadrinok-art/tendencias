#!/usr/bin/env bash
# junta as cenas renderizadas (sem som) + créditos, encaixa os clipes de "pintura animada" (ia/*.mp4)
# e coloca a mixagem única por cima. Saída: saida/pernambuco-documentario.mp4 (H.264 CRF 20)
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p saida
: > render/lista.txt
for c in abertura c1 c2 c3 c4 c5 c6 c7 c8 final creditos; do echo "file '$PWD/render/$c.mp4'" >> render/lista.txt; done
ffmpeg -v error -y -f concat -safe 0 -i render/lista.txt -an -c:v copy render/_video.mp4
CRED=$(ffprobe -v error -show_entries format=duration -of csv=p=0 render/creditos.mp4)
ffmpeg -v error -y -i mix.wav -af "apad=pad_dur=$CRED" -ar 48000 render/_audio.wav
# pintura animada dos Guararapes: entra em c4@61.4 (palavra "Guararapes"), 5,04 s, com fusão de 0,8 s
T0=$(python3 -c "import json;print(json.load(open('cenas.json'))['c4']['ini']+61.4)")
FONTE="$PWD/comum/assets/fontes/Caladea-Italic.ttf"
ffmpeg -v error -y -i render/_video.mp4 -i ia/guararapes_vivo.mp4 -i render/_audio.wav -filter_complex "
 [1:v]fps=30,scale=1920:1080,format=yuva420p,fade=t=in:st=0:d=0.8:alpha=1,fade=t=out:st=4.24:d=0.8:alpha=1,
  drawtext=fontfile=$FONTE:text='Victor Meirelles, 1879 · pintura animada':fontsize=30:fontcolor=white@0.85:x=60:y=h-80:box=1:boxcolor=black@0.35:boxborderw=12,
  setpts=PTS+$T0/TB[c];
 [0:v][c]overlay=eof_action=pass:enable='between(t,$T0,$T0+5.04)'[v]" \
 -map "[v]" -map 2:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -r 30 -c:a aac -b:a 256k -shortest -movflags +faststart saida/pernambuco-documentario.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,nb_frames -of compact saida/pernambuco-documentario.mp4
