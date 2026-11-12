---
name: estilo-documentario
description: Cria minidocumentários animados feitos 100% em código (sem gerador de vídeo por IA e sem banco de imagens), com uma câmera contínua sobre um "mundo" grande, fotos reais com licença livre, destaques sincronizados palavra a palavra com a narração e efeitos sonoros reais. Use quando o usuário pedir um "documentário", "vídeo estilo documentário", "vídeo explicativo histórico", "mapa/linha do tempo animada" ou entregar uma narração + tema para virar vídeo.
---

# Estilo documentário

Transforma **narração + tema** em um MP4 1920×1080 a 30 fps em que cada quadro é desenhado em código.

## Regras inegociáveis
1. **Nada de vídeo gerado por IA nem banco de imagens.** Todo quadro é código (HTML/CSS/SVG/Canvas + animação), renderizado no HyperFrames ou, se ele não estiver disponível, num renderizador próprio (ver `references/renderizacao.md`).
2. **Uma câmera só, um mundo só.** O vídeo inteiro é um movimento de câmera contínuo sobre uma grande cena (mesa, mapa, linha do tempo). Sem cortes nem troca de slide: a câmera desliza, aproxima, recua, viaja e mergulha de novo, sempre com easing e nunca com parada seca.
3. **Regras de leitura** (detalhes em `references/regras-de-estilo.md`):
   - uma ideia por frase e **um destaque aceso por vez**;
   - cada frase aparece na tela **uma única vez**, curta, em letra grande;
   - o visual entra **exatamente na palavra falada** (o círculo é desenhado quando a palavra é dita).
4. **Imagens só com licença livre e documentada** (Wikimedia Commons / Wikipedia, domínio público, CC). Cada arquivo ganha uma linha em `creditos.csv`.
5. **Sons reais.** Use os efeitos e trilhas da pasta do usuário (máquina de escrever, carimbo, papel, textura de filme antigo). Não sintetize sons se houver material profissional.

## Entradas esperadas (uma pasta)
| Pasta | Conteúdo | Obrigatório |
|---|---|---|
| `narracao/` | áudio da voz (wav/mp3) e, se houver, o roteiro em texto | sim |
| `fotos/` | fotos reais com licença livre + `creditos.csv` | não: a skill busca |
| `referencias/` | imagens de estilo (Pinterest etc.), **só inspiração, nunca entram no vídeo** | não |
| `efeitos/` | trilhas, SFX, texturas | recomendado |

Se faltar algo, siga o fluxo mesmo assim e avise o que foi substituído.

## Fluxo

### 1. Preparar e transcrever
- Transcreva a narração **com tempos por palavra** (ex.: Whisper com `word_timestamps=True`). Salve em `trabalho/palavras.json`.
- Olhe as referências e descreva a direção de arte em 5 a 8 linhas: paleta, luz, materiais (papel, filme, madeira) e tipografia.

### 2. Buscar fotos (se o usuário não entregou todas)
- Identifique pessoas, lugares e objetos citados.
- Busque **só** em fontes com licença livre (Wikimedia Commons primeiro). Pesquise em **inglês**.
- Para cada foto, registre em `fotos/creditos.csv`: `arquivo,titulo,autor,licenca,url_fonte`. Sem licença clara, não use.
- Referências de estilo (Pinterest) só inspiram e não são baixadas para o vídeo.

### 3. Plano em tabela, ANTES de qualquer código
Monte a tabela de beats (modelo em `references/modelo-plano.md`):

| # | início–fim (s) | fala | palavra-gatilho | único destaque na tela | texto na tela | câmera | som |
|---|---|---|---|---|---|---|---|

- Um beat por ideia. Cada destaque é casado com a palavra-gatilho (tempo exato do `palavras.json`).
- **Liste as ambiguidades e pergunte ao usuário** (ex.: "nome + idade: dois destaques em sequência ou um só?"; "a foto sai quando a ideia entra?"). Padrão quando o usuário não responder: em sequência, um aceso por vez, e a foto apaga quando a ideia entra.
- **Pare e peça aprovação da tabela.** Mudar a tabela é muito mais barato do que mudar o vídeo pronto.

### 4. Construir o mundo e a câmera
- Monte um único "mundo" grande (ex.: 8000×5000 px) com todos os elementos posicionados: fotos "caindo na mesa", mapa, carimbos, anotações.
- A câmera é uma transformação (translate/scale/rotate leve) animada por keyframes com easing suave (`power2.inOut`/`sine.inOut`). Entre beats a câmera **sempre se move** (drift lento), nunca congela.
- Cada destaque é disparado no tempo da palavra-gatilho: círculo desenhado (stroke-dashoffset), sublinhado, carimbo ou foto entrando.
- Textura de filme antigo/grão e vinheta por cima de tudo.

### 5. Autoverificação (obrigatória, antes de mostrar ao usuário)
Rode `scripts/conferir_video.sh <video.mp4>` e analise:
- **Quadros parados por beat:** extraia o quadro do meio de cada beat e confira contra a direção de arte (ex.: "claro demais, cara de pergaminho sem a luz das referências" → corrigir luz e contraste).
- **Velocidade da câmera:** `scripts/analisar_camera.py` mede o deslocamento quadro a quadro. Picos = trancos. Suavize keyframes até não haver picos acima do limiar.
- **Varredura a cada 0,5 s:** procure texto cortado, elemento pequeno demais (rosto com menos de ~25% da altura quando for o destaque), sobreposição, mais de um destaque aceso, tela vazia ou ruído/"chuvisco".
- **Áudio:** meça a trilha (volume RMS/onsets com ffmpeg ou librosa). Escolha uma trilha que cresça com a narrativa, faça a música **morrer no golpe de efeito** (ex.: carimbo) e voltar no momento de virada (ex.: "a luz acende"). Narração sempre inteligível (música por volta de −18 a −22 dB sob a voz).
- Corrija sozinho o que encontrar e repita a verificação.

### 6. Entregar
- Renderize o MP4 1920×1080 a 30 fps com a narração sincronizada.
- Entregue: o vídeo, a tabela final, `creditos.csv` e uma lista curta do que foi corrigido na autoverificação.
- Peça feedback explícito. Problemas comuns da 1ª versão: **fotos pequenas demais, personagem que quase não aparece, final confuso**. Não pare na primeira versão.

### 7. Iterar
O usuário pode mandar ajustes por áudio ou texto. Transforme cada ajuste em mudança na **tabela** primeiro e só depois no código. Renderize de novo e repita o passo 5.

## Estrutura de trabalho sugerida
```
projeto/
  narracao/ fotos/ referencias/ efeitos/
  trabalho/palavras.json  trabalho/plano.md  trabalho/direcao-de-arte.md
  cena/ (código do mundo e da câmera)
  saida/documentario.mp4  saida/creditos.csv
```
