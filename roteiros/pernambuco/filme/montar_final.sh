#!/usr/bin/env bash
# junta as cenas renderizadas (sem som) + créditos e coloca a mixagem única por cima
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p saida
: > render/lista.txt
for c in abertura c1 c2 c3 c4 c5 c6 c7 c8 final creditos; do echo "file '$PWD/render/$c.mp4'" >> render/lista.txt; done
ffmpeg -v error -y -f concat -safe 0 -i render/lista.txt -an -c:v copy render/_video.mp4
CRED=$(ffprobe -v error -show_entries format=duration -of csv=p=0 render/creditos.mp4)
ffmpeg -v error -y -i mix.wav -af "apad=pad_dur=$CRED" -ar 48000 render/_audio.wav
ffmpeg -v error -y -i render/_video.mp4 -i render/_audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart saida/pernambuco-documentario.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,nb_frames -of compact saida/pernambuco-documentario.mp4
