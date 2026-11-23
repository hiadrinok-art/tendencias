# Réu por um discurso? (colagem)

- `index.html`: a colagem inteira. `render(t)` desenha o quadro do segundo `t`, e as legendas saem de `NARR`.
- `render.js`: grava os quadros a 12 fps (`node render.js <pasta com index.html>`).
- `sfx.py`: gera os efeitos de papel e a batida de fundo a partir do `sfx.json` (`python3 sfx.py sfx.json audio.wav`).
- Montagem: `ffmpeg -framerate 12 -i frames/f%05d.jpg -i audio.wav -vf "fps=30,format=yuv420p" -c:v libx264 -crf 25 -c:a aac -shortest saida.mp4`
