/* Cena 4 — Pernambuco disputado por impérios (mesa de arquivo) */
(function () {
  const creme = 'stroke="#e9dcc0" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  const navio = (dx, s) => `<g transform="translate(${dx},0) scale(${s})" ${creme}>
      <path class="traco" d="M40,420 L520,420 L460,500 L100,500 Z"/><path class="traco" d="M220,420 L220,80 M360,420 L360,140"/>
      <path class="traco" d="M232,100 C320,150 330,300 232,380 M372,160 C440,200 450,320 372,380"/></g>`;
  const frota = navio(0, 1) + navio(560, 0.8) + navio(1020, 0.65) +
    `<path class="traco" d="M0,560 C200,530 400,590 600,560 C800,530 1000,590 1200,560 C1350,540 1500,560 1600,560" ${creme}/>`;
  // ícones: pincel (pintores), luneta (cientistas), compasso (engenheiros)
  const icones = `<g ${creme}>
      <path class="traco" d="M160,620 L420,200 M420,200 C450,150 520,170 500,230 L470,280 M160,620 C120,680 70,700 60,640 C60,600 110,590 160,620"/>
      <path class="traco" d="M760,560 L1160,300 L1210,380 L810,640 Z M1160,300 L1250,250 L1300,330 L1210,380 M900,600 L860,760 M960,560 L1040,760"/>
      <path class="traco" d="M1700,180 L1560,720 M1700,180 L1840,720 M1700,180 m-34,0 a34,34 0 1,0 68,0 a34,34 0 1,0 -68,0 M1610,520 C1660,560 1740,560 1790,520"/></g>
      <g font-family="Datilo" font-size="60" fill="#e9dcc0" text-anchor="middle"><text x="280" y="840">pintores</text><text x="1030" y="840">cientistas</text><text x="1700" y="840">engenheiros</text></g>`;
  const ponte = `<g ${creme}>
      <path class="traco" d="M0,300 L1800,300"/><path class="traco" d="M100,300 C250,520 450,520 600,300 M600,300 C750,520 950,520 1100,300 M1100,300 C1250,520 1450,520 1600,300"/>
      <path class="traco" d="M0,600 C300,570 600,630 900,600 C1200,570 1500,630 1800,600"/></g>
      <g font-family="Datilo" font-size="56" fill="#e9dcc0"><text x="0" y="200">RECIFE</text><text x="1500" y="200">MAURÍCIA</text></g>`;
  // quatro figuras neutras, lado a lado, com legenda (sem caricatura)
  const pessoa = (x) => `<path class="traco" d="M${x},380 L${x},760 M${x},470 L${x - 90},620 M${x},470 L${x + 90},620 M${x},760 L${x - 70},980 M${x},760 L${x + 70},980"/><circle class="traco" cx="${x}" cy="320" r="58"/>`;
  const silhuetas = `<g ${creme}>${[250, 750, 1250, 1750].map(pessoa).join("")}<path class="traco" d="M120,1020 L1880,1020"/></g>
      <g font-family="Datilo" font-size="52" fill="#e9dcc0" text-anchor="middle"><text x="250" y="1110">senhores</text><text x="750" y="1110">soldados</text><text x="1250" y="1110">indígenas</text><text x="1750" y="1110">negros</text></g>`;

  const mapa = B.mapa({ id: "mapa-c4", x: 2500, y: 350, w: 3000, h: 1600, fundo: "mapa-papel", margem: 0.05,
    estados: [{ uf: "pe", fill: "rgba(120,80,40,.16)", stroke: "#5a3418", swpx: 6 }, { uf: "pb", fill: "rgba(120,80,40,.06)", stroke: "rgba(90,52,24,.4)", swpx: 3 }, { uf: "al", fill: "rgba(120,80,40,.06)", stroke: "rgba(90,52,24,.4)", swpx: 3 }],
    recorte: ["pe"] });

  B.mundo(12400, 6800, `
    ${B.folha({ id: "folha-1630", x: 300, y: 450, w: 1600, h: 560, rot: -1.2, html: B.datil({ id: "data1630", texto: "1630", size: 300, top: 110 }) })}
    ${B.svg({ id: "frota", x: 300, y: 1250, w: 1800, h: 700, vb: "0 0 1600 620", html: frota })}
    ${mapa}
    ${B.foto({ id: "foto-olinda", src: "img/olinda.jpg", x: 5800, y: 350, w: 2300, rot: 1.5, legenda: "Olinda · Frans Post" })}
    ${B.foto({ id: "mapa1647", src: "img/mapa1647.jpg", x: 8400, y: 300, w: 3500, rot: -1, legenda: "Brasilia qua parte paret Belgis · 1647" })}
    ${B.foto({ id: "retrato-nassau", src: "img/nassau.jpg", x: 300, y: 2400, w: 1500, rot: 2, legenda: "Maurício de Nassau · Jan de Baen" })}
    ${B.svg({ id: "icones", x: 2300, y: 2550, w: 2100, h: 1050, vb: "0 0 1900 900", html: icones })}
    ${B.svg({ id: "ponte", x: 2300, y: 3750, w: 2100, h: 800, vb: "0 0 1800 680", html: ponte })}
    ${B.foto({ id: "foto-sinagoga", src: "img/sinagoga.jpg", x: 5000, y: 2450, w: 1400, rot: -1.5, legenda: "Kahal Zur Israel · Recife" })}
    ${B.folha({ id: "folha-escr", x: 7100, y: 2600, w: 2300, h: 800, rot: 1, html: B.texto({ html:
        `os engenhos continuavam movidos pelo trabalho <span id="marca-escr4" class="sub">escravizado<svg viewBox="0 0 100 10" preserveAspectRatio="none"><path id="sub-escr4" class="traco" d="M2,6 C30,3 70,8 98,4" stroke="#b0161e" stroke-width="2.2" stroke-linecap="round"/></svg></span>`,
        size: 88, top: 170, classe: "serif", extra: { "font-style": "italic", padding: "0 120px", "line-height": "1.5" } }) })}
    ${B.folha({ id: "folha-1645", x: 9800, y: 2550, w: 2300, h: 1100, rot: -1, html: `
        ${B.datil({ id: "data1645", texto: "1645", size: 240, top: 90 })}
        ${B.carimbo({ id: "carimbo-insur", texto: "INSURREIÇÃO", x: 300, y: 560, size: 130, rot: -6 })}` })}
    ${B.svg({ id: "silhuetas", x: 300, y: 4700, w: 2400, h: 1350, vb: "0 0 2000 1150", html: silhuetas })}
    ${B.folha({ id: "folha-nomes", x: 3100, y: 4850, w: 2600, h: 1000, rot: 1.2, html: `
        ${B.datil({ id: "nome-hd", texto: "Henrique Dias", size: 150, top: 160 })}
        ${B.datil({ id: "nome-fc", texto: "Filipe Camarão", size: 150, top: 560 })}` })}
    ${B.foto({ id: "foto-guararapes", src: "img/guararapes.jpg", x: 6100, y: 4350, w: 3800, rot: -0.8, legenda: "Batalha dos Guararapes · Victor Meirelles",
        extra: {} })}
    ${B.folha({ id: "folha-1654", x: 10300, y: 4700, w: 1900, h: 1000, rot: 1.5, html: B.carimbo({ id: "carimbo-1654", texto: "1654", x: 380, y: 230, size: 260, rot: -6 }) })}
  `);
  // Olinda incendiada: escurecimento pelas bordas sobre a pintura
  document.querySelector("#foto-olinda").insertAdjacentHTML("beforeend",
    `<div id="queima" class="foco" style="position:absolute;inset:26px 26px 110px 26px;background:radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 30%, rgba(60,20,5,.55) 65%, rgba(10,4,0,.92) 100%), linear-gradient(0deg, rgba(200,70,10,.35), rgba(0,0,0,0) 45%)"></div>`);
  // anos sobre a pintura dos Guararapes
  document.querySelector("#foto-guararapes").insertAdjacentHTML("beforeend",
    `<div id="nota-guar" class="peca papel" style="right:-160px;bottom:-90px;width:1300px;height:420px;transform:rotate(3deg)"><div id="anos-guar" class="centro datil foco" data-texto="1648 · 1649" style="top:110px;font-size:170px"></div></div>`);
  B.finalizar();
  // ataque holandês: setas do mar até Olinda e Recife (pontos no litoral real de PE)
  const sv = "vb-mapa-c4", svg = document.getElementById(sv);
  const recife = B.costaLeste(sv, "pe", 0.35), olinda = B.costaLeste(sv, "pe", 0.32);
  const seta = (p, dy) => `<path class="traco" d="M${p[0] + 26},${p[1] + dy} L${p[0] + 3},${p[1]} M${p[0] + 7},${p[1] - 2} L${p[0] + 3},${p[1]} L${p[0] + 7},${p[1] + 2}" />`;
  svg.insertAdjacentHTML("beforeend", `<g id="setas-wic" class="foco" fill="none" stroke="#c8590f" stroke-width=".32" stroke-linecap="round">${seta(olinda, -4)}${seta(recife, 4)}</g>
     <g fill="#7a2a14"><circle cx="${olinda[0]}" cy="${olinda[1]}" r=".9"/><circle cx="${recife[0]}" cy="${recife[1]}" r=".9"/></g>`);
  const div = document.getElementById("mapa-c4");
  div.insertAdjacentHTML("beforeend", `<div id="rot-olinda" class="rotulo" style="font-size:54px">OLINDA</div><div id="rot-recife" class="rotulo" style="font-size:54px">RECIFE</div>`);
  B.colocarNoMapa("rot-olinda", sv, olinda, -330, -80); B.colocarNoMapa("rot-recife", sv, recife, -330, 30);
  // alvo de câmera para o close no litoral
  div.insertAdjacentHTML("beforeend", `<div id="costa-zoom" style="position:absolute;width:10px;height:10px"></div>`);
  B.colocarNoMapa("costa-zoom", sv, [(recife[0] + olinda[0]) / 2 - 12, (recife[1] + olinda[1]) / 2]);
  window.Documentario.montar(window.PLANO);
})();
