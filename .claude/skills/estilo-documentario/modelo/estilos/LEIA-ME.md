# Estilos (peles)

O `index.html` do modelo já vem no estilo **mesa de arquivo** (madeira, papel envelhecido, luz quente).
Um estilo é só CSS: as posições, os ids e o `plano.json` não mudam. Por isso dá para testar o mesmo vídeo em outro visual sem refazer nada.

## cordel (xilogravura)
Papel creme, tinta preta chapada, vermelho de impressão, tipos de madeira (Inter Display Black), sombras duras e bordas ásperas.

Para usar, adicione ao `index.html`:
1. No `<head>`, depois do `<style>`: `<link rel="stylesheet" href="estilos/cordel.css">`
2. Logo antes de `<div id="tremor">`, o filtro de borda áspera:
```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="aspero" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="r"/>
  <feDisplacementMap in="SourceGraphic" in2="r" scale="7" xChannelSelector="R" yChannelSelector="G"/></filter></svg>
```

As regras específicas de elementos da Cena 5 (bandeira, mapas, retrato) servem de exemplo: adapte os seletores para os elementos de cada vídeo.

**Cuidados aprendidos:**
- Contorno preto em `svg path` sobrescreve o `stroke` de faixas coloridas (o arco-íris ficou preto). Reponha as cores com `:nth-child`.
- Alto contraste em pintura escura vira um borrão preto. Use `grayscale(1) brightness(2.1) contrast(1.9)`.
