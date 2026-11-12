# Renderização

## Preferência: HyperFrames
HyperFrames é um framework de código aberto que renderiza composições em HTML/CSS/JS animadas em MP4. Antes de usar:
1. Confira a documentação/README atual do HyperFrames (comandos e API mudam) e instale conforme indicado.
2. Monte a composição em HTML: o "mundo" é um contêiner grande e a câmera é a transformação desse contêiner, animada numa timeline (ex.: GSAP).
3. Renderize em 1920×1080 a 30 fps e adicione o áudio (narração + trilha + SFX mixados).

## Alternativa sem HyperFrames
1. Página HTML com a mesma composição e uma função `seek(t)` determinística (timeline pausada).
2. Playwright: para cada quadro `i`, chame `seek(i/30)` e tire um screenshot PNG a 1920×1080.
3. ffmpeg: `ffmpeg -framerate 30 -i quadros/%05d.png -i mix.wav -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -shortest saida/documentario.mp4`

## Mixagem
`ffmpeg -i narracao.wav -i trilha.wav -i sfx.wav -filter_complex "[1]volume=-20dB[m];[0][m][2]amix=inputs=3:normalize=0" mix.wav`
Use automação de volume (filtro `volume` com expressão de tempo ou `afade`) para fazer a música morrer e voltar nos pontos do plano.
