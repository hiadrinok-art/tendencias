# Documentário animado feito em código com o Claude

Fonte: https://youtu.be/J70PCpxWTFA (estudado pela legenda em português; as imagens do vídeo não foram vistas).

## Ideia central
Um minidocumentário (exemplo: história da IA, de Turing em 1950 a Dartmouth em 1956) feito **sem gerador de vídeo por IA nem banco de imagens**: cada quadro é desenhado em código e renderizado no **HyperFrames** (editor de vídeo de código aberto que aceita código). Do material entregue ao MP4 levou cerca de 1 hora.

## Materiais de entrada (uma pasta com 4 itens)
1. **Narração**: o áudio da voz.
2. **Fotos reais** de pessoas e lugares, só com licença livre (Wikipedia / Wikimedia Commons), com **a licença de cada foto anotada num arquivo**.
3. **Referências de estilo** (Pinterest), que servem só de inspiração e não entram no vídeo. Pesquisar em **inglês** ("3D documentary", "cinematic", "paper animation"...); dá para pedir ao Claude os termos certos.
4. **Pacote de efeitos profissional**: textura de filme antigo, trilhas, sons de papel, máquina de escrever e carimbo. Sons profissionais ficam melhores que os sons inventados pela IA.

## Estrutura do prompt
1. **Restrição técnica:** nada de vídeo por IA nem banco de imagens; tudo em código e renderizado no HyperFrames.
2. **Estilo:** o vídeo inteiro é **um único movimento de câmera sobre um "mundo" grande**, sem cortes e sem troca de slide. A câmera desliza, aproxima, recua, viaja e mergulha de novo, sempre fluida (keyframes suaves, nunca parada seca).
3. **Regras de leitura (as mais importantes):**
   - uma ideia por frase e **um destaque por vez**;
   - cada frase aparece na tela uma única vez, sem paredes de texto, em letra grande;
   - o visual cai **exatamente na palavra falada** (o círculo é desenhado quando a palavra é dita).

## Processo
1. **Pedir o plano antes de construir:** uma tabela com *tempo · fala · único destaque na tela · texto que aparece*, casada com a narração. O Claude fez perguntas de ambiguidade (ex.: "nome + idade são dois destaques ou um?", resposta: os dois em sequência, um aceso por vez, e a foto apaga quando a ideia entra). **Mudar a tabela sai muito mais barato do que mudar o vídeo pronto.**
2. **Autoverificação durante a construção:**
   - extrair quadros parados de cada beat e corrigir o visual (estava claro demais, "cara de pergaminho");
   - medir a velocidade da câmera quadro a quadro, achar os picos (trancos) e suavizar o caminho;
   - antes de renderizar, revisar um quadro a cada 0,5 s procurando elementos cortados, pequenos ou sobrepostos;
   - analisar as trilhas com uma ferramenta de áudio: escolher piano crescente, fazer a música morrer no golpe do carimbo e voltar quando a luz acende.
3. **Saída:** MP4 1920×1080, 30 fps, narração sincronizada.
4. **Iterar:** a primeira versão tinha fotos pequenas e um final com "chuvisco". O ajuste foi pedido por áudio (às vezes refinando o prompt em outra conversa). Não parar na primeira versão.
5. **Transformar em skill:** salvar o processo inteiro (prompt, tabela, busca de fotos com licença, câmera, som) numa skill ("estilo documentário"). Nas próximas vezes basta entregar narração e tema.

## Lições para aplicar
- Plano em tabela antes do código.
- Uma ideia e um destaque por vez, sincronizados com a palavra.
- Câmera contínua sobre um mundo único em vez de cortes.
- Imagens só com licença documentada.
- Efeitos sonoros reais e trilha casada com os momentos-chave.
- Verificação automática de quadros, movimento e áudio antes de entregar.
- Empacotar o fluxo que deu certo como skill reutilizável.

*(O final do vídeo é propaganda do curso/plataforma do autor; ficou de fora.)*
