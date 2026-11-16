/* Abertura — 6 de março de 1817 (mesa de arquivo) */
(function () {
  const ufs = Object.keys(GEO.estados);
  const estados = ufs.map((uf) => uf === "pe"
    ? { uf, fill: "rgba(176,22,30,.32)", stroke: "#6e1a12", swpx: 7 }
    : { uf, fill: "rgba(120,80,40,.10)", stroke: "rgba(90,55,25,.55)", swpx: 4 });

  const coroa = `
    <g stroke="#8a5a1a" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" fill="none">
      <path class="traco" d="M200,720 L1400,720"/>
      <path class="traco" d="M220,720 L160,300 L480,520 L800,180 L1120,520 L1440,300 L1380,720"/>
      <path class="traco" d="M800,180 L800,40 M730,100 L870,100"/>
      <path class="traco" d="M260,620 L1340,620"/>
    </g>
    <g fill="#8a5a1a"><circle cx="160" cy="300" r="34"/><circle cx="480" cy="520" r="26"/><circle cx="1120" cy="520" r="26"/><circle cx="1440" cy="300" r="34"/></g>`;

  const faixa = `<svg viewBox="0 0 1700 520" width="100%" height="100%" style="position:absolute;inset:0;overflow:visible">
      <g id="faixa-tracos" stroke="#2a1f16" stroke-width="10" stroke-linecap="round">
        <path class="traco" d="M220,300 L1480,300"/>
        <path class="traco" d="M220,250 L220,350"/><path class="traco" d="M1480,250 L1480,350"/>
      </g></svg>
    <div class="rotulo" style="left:120px;top:370px;font-size:84px;color:#2a1f16">1817</div>
    <div class="rotulo" style="left:1380px;top:370px;font-size:84px;color:#2a1f16">1822</div>
    ${B.datil({ id: "anos-txt", texto: "5 anos", size: 110, top: 90 })}`;

  B.mundo(9000, 5200, `
    ${B.folha({ id: "folha-data", x: 500, y: 1900, w: 1700, h: 640, rot: -1.5,
      html: B.datil({ id: "data1817", texto: "6 de março de 1817", size: 140, top: 190 }) })}
    ${B.mapa({ id: "mapa-br", x: 2650, y: 250, w: 4200, h: 4400, estados, margem: 0.03, fundo: "mapa-papel",
      extraSvg: "" })}
    ${B.svg({ id: "coroa", x: 3850, y: 1150, w: 1900, h: 950, vb: "0 0 1600 800", html: coroa })}
    ${B.folha({ id: "faixa-tempo", x: 500, y: 3050, w: 1700, h: 520, rot: 1.2, html: faixa })}
    ${B.folha({ id: "titulo", x: 2850, y: 1650, w: 3800, h: 1700, rot: -1.2, foco: true, html: `
      ${B.texto({ html: "PERNAMBUCO", size: 430, top: 300, classe: "serif", extra: { "font-weight": "bold", "letter-spacing": "24px" } })}
      ${B.datil({ id: "subtitulo", texto: "Terra de História, Coragem e Revolução", size: 118, top: 1080 })}` })}
  `);

  // alfinete do Recife e carimbo dentro da div do mapa
  document.getElementById("mapa-br").insertAdjacentHTML("beforeend", `
    <div id="pino-recife" class="pino foco"><div class="cabeca"></div><div class="nome" data-texto="RECIFE" style="font-size:34px;top:30px;right:30px"></div></div>
    <div id="carimbo-rep" class="carimbo foco" style="font-size:150px;transform:rotate(-7deg)">REPÚBLICA</div>`);
  B.finalizar();
  // Recife: litoral de PE a ~35% da altura do estado (lat. 8°03' S num estado que vai de ~7°15' a ~9°29' S)
  B.colocarNoMapa("pino-recife", "vb-mapa-br", B.costaLeste("vb-mapa-br", "pe", 0.35));
  const pe = document.querySelector('#vb-mapa-br path[data-uf="pe"]').getBBox();
  B.colocarNoMapa("carimbo-rep", "vb-mapa-br", [pe.x + pe.width * 0.5, pe.y + pe.height * 0.5]);
  gsap.set("#carimbo-rep", { xPercent: -50, yPercent: -50 });
  // o nome do Recife fica à esquerda do alfinete (à direita é mar)
  document.getElementById("pino-recife").classList.add("nome-esq");

  window.Documentario.montar(window.PLANO);
})();
