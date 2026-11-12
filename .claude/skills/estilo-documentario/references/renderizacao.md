# Renderização (testado com hyperframes 0.9.39)

## HyperFrames
- Instalar: `npm i hyperframes` (Node >= 22 e ffmpeg). O render usou o Chromium do sistema sem configuração extra.
- Estrutura que o motor segue: um `#root` com `data-composition-id="root"`, `data-width`, `data-height`, `data-start="0"` e `data-duration`; uma timeline GSAP **pausada** registrada em `window.__timelines["root"]`.
- Áudio: um único `<audio src="audio/mix.wav" data-start="0" data-duration="...">`. A mixagem é feita antes, no `montar.py`, porque assim é determinística e fácil de medir.
- Fontes: só via `@font-face` com arquivo local (`assets/fontes`). Fonte de sistema reprova no lint e cai para genérica no render.
- GSAP: use a cópia local `assets/gsap.min.js` (o render não depende de CDN).
- Comandos úteis:
  - `npx hyperframes lint <dir>`
  - `npx hyperframes check <dir>` (layout, contraste, áudio)
  - `npx hyperframes snapshot <dir> --at 1.5,3.8 -o <saida> --no-end` (gera a folha de contato)
  - `npx hyperframes render <dir> -o saida.mp4`
  - `npx hyperframes audio <arquivo>` (onsets, picos e volume)
- Tempo: 27 s a 1080p30 levaram ~2,5 min em CPU (captura beginframe).

## Alternativa sem HyperFrames
1. A mesma página expõe `window.__timelines.root` (timeline pausada).
2. Playwright: para cada quadro `i`, chame `tl.seek(i/30)` e tire um screenshot de 1920×1080.
3. `ffmpeg -framerate 30 -i q/%05d.png -i audio/mix.wav -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -shortest saida.mp4`
