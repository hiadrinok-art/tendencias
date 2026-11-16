---
name: estilo-documentario
description: Cria minidocumentários animados feitos 100% em código (sem gerador de vídeo por IA e sem banco de imagens), com uma câmera contínua sobre um "mundo" grande, fotos reais com licença livre, destaques sincronizados palavra a palavra com a narração e efeitos sonoros reais. Use quando o usuário pedir um "documentário", "vídeo estilo documentário", "vídeo explicativo histórico", "mapa/linha do tempo animada" ou entregar uma narração + tema para virar vídeo.
---

# Estilo documentário

Transforma **narração + tema** em um MP4 1920×1080 a 30 fps em que cada quadro é desenhado em código e renderizado no **HyperFrames** (`npx hyperframes`, HTML + GSAP → MP4).
O fluxo foi testado de ponta a ponta: 27 s renderizados em ~2,5 min em CPU.

## Regras inegociáveis
1. **Nada de vídeo gerado por IA nem banco de imagens/vídeos.** Todo quadro é código (HTML/CSS/SVG + GSAP).
2. **Uma câmera só, um mundo só.** Um plano-sequência contínuo sobre uma grande cena (mesa, mapa, linha do tempo). Sem cortes, sem parada seca: o `motor.js` interpola a câmera com spline.
3. **Regras de leitura** (`references/regras-de-estilo.md`): uma ideia por frase, **um destaque aceso por vez**, cada frase aparece uma única vez, e o visual entra **na palavra falada**.
4. **Imagens só com licença livre e documentada** (Wikimedia Commons, domínio público, CC), com uma linha por arquivo em `creditos.csv`. Sem foto com licença? **Desenhe em SVG** (prédios, mapas, objetos).
5. **Sons reais.** Use o pacote do usuário. Sem pacote, gere efeitos e trilha no ElevenLabs (se o conector existir) ou use fontes livres, sempre registrando nos créditos.

## O que tem aqui
| Caminho | Para quê |
|---|---|
| `modelo/` | Projeto inicial pronto: `index.html` (mundo e elementos), `motor.js` (câmera, foco, ações, grão: **genérico, não editar por vídeo**), `cena.js` (desenhos gerados por código do vídeo atual), `plano.json` (exemplo completo), fontes e GSAP locais |
| `scripts/transcrever.py` | narração → `palavras.json` com o tempo de cada palavra (faster-whisper) |
| `scripts/montar.py` | `plano.json` → `plano.js` + `audio/mix.wav` (narração, trilha com envelope, efeitos no beat, normalização a -16 LUFS) |
| `scripts/conferir_sincronia.py` | confere se cada beat cai na palavra-gatilho (tolerância 80 ms) e se há destaques colados |
| `scripts/conferir_video.sh` | quadros a cada 0,5 s, folhas de contato e RMS por 0,5 s |
| `scripts/analisar_camera.py` | velocidade da câmera quadro a quadro e trancos |
| `modelo/estilos/` | peles visuais trocáveis só por CSS (padrão: mesa de arquivo; `cordel.css`: xilogravura). Veja o LEIA-ME |
| `references/` | regras de estilo, modelo de tabela e notas de renderização |

## Fluxo

### 0. Preparar o ambiente (uma vez por sessão)
```bash
mkdir -p ~/hf && cd ~/hf && npm init -y >/dev/null && npm i hyperframes   # Node >= 22 e ffmpeg
pip install faster-whisper opencv-python-headless matplotlib
cp -r <skill>/modelo  <projeto>/cena
```
Hosts que a rede precisa liberar: `upload.wikimedia.org` e `commons.wikimedia.org` (fotos) e `elevenlabsusercontent.com` (baixar áudio gerado).

### 1. Narração e transcrição
- Se o usuário só tiver o roteiro, gere a voz (ElevenLabs: `creative_list_voices` com `languages=["pt"]`, e um narrador de documentário de sotaque pt-BR funciona bem com `eleven_multilingual_v2`).
- `python3 scripts/transcrever.py cena/audio/narracao.mp3 trabalho/palavras.json`

### 2. Fotos e direção de arte
- Busque só em fontes com licença livre, pesquisando em inglês. **A API do Commons limita requisições (HTTP 429) em IPs compartilhados**: baixe direto de `upload.wikimedia.org/wikipedia/commons/<h>/<hh>/<Arquivo>` (h = md5 do nome do arquivo) e confirme a licença na página quando possível.
- Referências de estilo só inspiram, nunca entram no vídeo.

### 3. Plano em tabela, ANTES de qualquer código
- Monte a tabela (`references/modelo-plano.md`) e **pergunte as ambiguidades**. Padrão: destaques em sequência, um aceso por vez, e a foto apaga quando a ideia entra.
- **Pare e peça aprovação.** Depois passe a tabela para `cena/plano.json`:
  - `beats[]`: `t` = início da palavra-gatilho (de `palavras.json`), `acao`, `alvo` (id do elemento), `som`;
  - `camera[]`: `[t, x, y, zoom]` em coordenadas do mundo; o motor passa uma spline por eles;
  - `audio.trilha_abaixo_da_voz`: ex. `14`. O `montar.py` mede a trilha a cada 0,5 s e a mantém 14 dB abaixo da fala, compensando o crescendo da música. **Use sempre.**
  - `audio.trilha_envelope`: `[t, dB]` como **desvio** (0 = normal, -60 = silêncio, +9 = subir no fim). Faça a música **morrer no impacto** e voltar na virada.
- Ações do motor: `datilografar`, `cair`, `alfinete`, `desenhar` (traços `.traco` de SVG), `circular`, `carimbar` (impacto exato em `t` + tremor), `congelar`, `acender` (traços + nós `.no-luz`), `reacender`, `mover` (`para: {x, y, rotation}`), `apagar`.
  - `foco` (opcional) diz qual elemento fica aceso, quando não é o próprio alvo (ex.: circular palavras de um documento).
  - `sons_extras: [[t, som]]` para sons sem destaque (sino, salva).
- `python3 scripts/conferir_sincronia.py cena/plano.json trabalho/palavras.json`

### 4. Construir o mundo
- Em `index.html`, posicione os elementos no mundo (`#mundo`, ~8800×4320 px). Todo elemento destacável leva `class="foco"` e um `id` usado no plano.
- Desenhos gerados (rede neural, gráficos) ficam em `cena.js`.
- **Garanta que a câmera nunca mostre a borda do mundo**: com centro `x` e zoom `z`, a área visível vai de `x - 960/z` a `x + 960/z`.
- `python3 scripts/montar.py cena`

### 5. Autoverificação (obrigatória, antes de mostrar ao usuário)
1. `npx hyperframes lint cena`: precisa dar 0 erros (fontes sempre via `@font-face` local).
2. `npx hyperframes check cena`: os avisos `canvas_covered #mundo`, `text_occluded` sob `#luz` e `canvas_overflow` fora da câmera são **falsos positivos** deste estilo (as camadas já levam `data-layout-ignore` e `data-layout-allow-overflow`). Leia o resto.
3. `npx hyperframes snapshot cena --at <meio de cada beat> -o conf/snap --no-end` e **olhe a folha de contato**. Procure: borda do mundo à mostra, desenho cortado, câmera saindo antes do destaque terminar, traço que não fecha, texto pequeno.
4. Corrija, repita o snapshot só nos tempos problemáticos e renderize: `npx hyperframes render cena -o saida/documentario.mp4`.
5. `scripts/analisar_camera.py`: trancos no fade de entrada e saída são normais. "Câmera parada" sobre áreas lisas (madeira escura) pode ser falso positivo, porque o detector precisa de textura.
6. `scripts/conferir_video.sh`: revise as folhas (a cada 0,5 s) procurando trechos vazios de mais de 1 s.
7. Volume: `ffmpeg -i video.mp4 -af ebur128 -f null -` deve dar de -14 a -18 LUFS.

### 6. Entregar e iterar
- Entregue o MP4, a tabela final, `creditos.csv` e a lista do que a autoverificação corrigiu e do que ficou pendente.
- Ajustes do usuário mudam primeiro o `plano.json`/tabela, depois o código. Rode a autoverificação de novo.

## Lições do primeiro teste
- `vector-effect="non-scaling-stroke"` quebra a animação de traço: o comprimento não bate e o círculo nunca fecha. Não use.
- A câmera precisa **segurar** no destaque até ele terminar: ponha um keyframe extra antes de sair.
- Trechos de câmera viajando sobre a mesa vazia por mais de ~0,7 s ficam fracos: ponha objetos no caminho ou encurte a viagem.
- Cartões vazios esperando um carimbo por segundos parecem erro: faça o cartão entrar junto com o destaque ou tenha conteúdo nele.
- **Câmera (piloto Pernambuco):** a spline Catmull-Rom passava do ponto quando uma viagem longa vinha logo depois de um trecho parado, mostrando a borda preta do mundo. O motor agora usa PCHIP (cúbica monotônica), que nunca passa do keyframe.
- **Wikimedia:** a API e o upload.wikimedia.org dão 429 em IP compartilhado. Tente de novo depois de alguns minutos e use uma silhueta provisória enquanto isso.
- **Direito autoral de pinturas:** confira a data de morte do artista (no Brasil, 70 anos). Ex.: Parreiras (1937) é domínio público; Murillo La Greca (1985) não.
- **Foco em elementos aninhados:** nunca dê foco a um filho de um elemento que já foi aceso (ex.: nomes dentro de um mapa). Apagar o pai apaga o filho junto. Use `"foco": "<id do pai>"` nesses beats.
- **HyperFrames remove `<style id>` do modelo**: injete CSS da cena por código (`B.css(...)`).
- **Rode `hyperframes validate`** em toda cena: ele acusa erros de JavaScript e imagens faltando (ex.: um 429 do Wikimedia salvo como `.jpg`).
- Narração do ElevenLabs sai baixa na mixagem (cerca de -28 LUFS); o `montar.py` normaliza para -16 em **duas passadas lineares**. A de uma passada comprime e desfaz o envelope.
- Para medir música × voz, use as pausas reais da narração (`silencedetect`), não os tempos do Whisper: as palavras podem estar adiantadas.
- `data-duration` do `#root` e do `<audio>` precisa ser igual a `duracao` do plano, senão o render sai com tela preta no fim.
- Piloto de 80 s: ~1,5 h no total; render de 6,5 min.
