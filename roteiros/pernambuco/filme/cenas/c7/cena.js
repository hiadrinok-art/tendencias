/* Cena 7 — Do mar ao sertão (cordel) */
(function () {
  const T = "#15120f", V = "#b3201c", A = "#e8b230", G = "#2f7d3a", Z = "#1f4f9c", P = "#f1e7d0";
  const tr = (w = 22) => `stroke="${T}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"`;
  const pe = GEO.estados.pe.d;

  const canavial = Array.from({ length: 9 }, (_, i) => { const x = 120 + i * 150;
    return `<path class="traco" d="M${x},1500 L${x},${300 + (i % 3) * 60} M${x},${700 + (i % 2) * 80} C${x - 90},${640 + (i % 2) * 80} ${x - 140},${600} ${x - 170},${620} M${x},${500 + (i % 3) * 40} C${x + 90},${430} ${x + 140},${420} ${x + 170},${440}" ${tr(18)}/>`; }).join("");
  const feira = `<path class="traco" d="M150,500 L850,250 L1550,500 Z M200,500 L200,1300 M1500,500 L1500,1300 M120,1300 L1580,1300" ${tr()}/>
      <path class="traco" d="M330,1300 L330,950 L700,950 L700,1300 M900,1300 L900,1000 L1350,1000 L1350,1300" ${tr()}/>
      <circle cx="430" cy="900" r="55" fill="${A}" stroke="${T}" stroke-width="12"/><circle cx="560" cy="900" r="55" fill="${V}" stroke="${T}" stroke-width="12"/>
      <circle cx="1030" cy="950" r="50" fill="${G}" stroke="${T}" stroke-width="12"/><circle cx="1180" cy="950" r="50" fill="${A}" stroke="${T}" stroke-width="12"/>`;
  const caatinga = `<circle cx="1250" cy="330" r="210" fill="${A}" stroke="${T}" stroke-width="16"/>
      <path class="traco" d="M700,1500 L700,450 C700,380 800,380 800,450 L800,1500 M700,900 L500,900 L500,650 C500,600 580,600 580,650 L580,830 M800,1050 L1000,1050 L1000,760 C1000,710 1080,710 1080,760 L1080,980" ${tr()}/>
      <path class="traco" d="M100,1500 L1600,1500 M200,1500 C260,1380 320,1420 360,1500 M1200,1500 C1260,1400 1340,1420 1380,1500" ${tr()}/>`;
  const rio = `<path class="traco" d="M200,100 C700,300 100,600 600,800 C1100,1000 400,1250 900,1500" stroke="${Z}" stroke-width="70" stroke-linecap="round" fill="none"/>
      <path class="traco" d="M260,100 C760,300 160,600 660,800 C1160,1000 460,1250 960,1500" stroke="${T}" stroke-width="10" fill="none"/>`;
  const petrolina = `<g>${[[380, 520], [460, 520], [540, 520], [420, 600], [500, 600], [460, 680]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="52" fill="#6a2a6a" stroke="${T}" stroke-width="12"/>`).join("")}
      <path class="traco" d="M460,470 L460,360 L540,320" ${tr(16)}/></g>
      <path d="M900,700 C860,520 1000,420 1120,470 C1250,520 1280,700 1180,800 C1080,900 930,860 900,700 Z" fill="${A}" stroke="${T}" stroke-width="14"/><path class="traco" d="M1100,470 C1110,420 1150,390 1200,380" ${tr(14)}/>
      <path d="M1500,260 L1560,260 L1560,420 C1640,460 1660,520 1660,600 L1660,1000 L1400,1000 L1400,600 C1400,520 1420,460 1500,420 Z" fill="${V}" stroke="${T}" stroke-width="14"/>`;
  const leg = (txt) => `<div class="madeira" style="position:absolute;left:-200px;right:-200px;bottom:-150px;text-align:center;font-size:104px;white-space:nowrap">${txt}</div>`;

  B.mundo(12400, 8400, `
    ${B.mapa({ id: "mapa-c7", x: 400, y: 300, w: 11600, h: 2700, estados: [], fundo: "papel" })}
    ${B.folha({ id: "folha-recife", x: 500, y: 3500, w: 2400, h: 900, rot: -1, foco: true, html: `<div class="centro madeira" style="top:250px;font-size:300px;letter-spacing:6px"><span id="letras-ar">AR</span>RECIFE<span id="letra-s">S</span></div>` })}
    ${B.foto({ id: "foto-noronha", src: "img/noronha.jpg", x: 3300, y: 3400, w: 2000, rot: 2, legenda: "Fernando de Noronha" })}
    ${B.svg({ id: "canavial", x: 5800, y: 3500, w: 1500, h: 1600, vb: "0 0 1500 1600", html: canavial, classe: "gravura" })}
    ${B.svg({ id: "feira", x: 7700, y: 3600, w: 1700, h: 1400, vb: "0 0 1700 1400", html: feira, classe: "gravura" })}
    ${B.svg({ id: "caatinga", x: 9900, y: 3400, w: 1700, h: 1600, vb: "0 0 1700 1600", html: caatinga, classe: "gravura" })}
    ${B.svg({ id: "rio", x: 900, y: 5700, w: 1200, h: 1600, vb: "0 0 1100 1600", html: rio, classe: "gravura" })}
    ${B.svg({ id: "petrolina", x: 2800, y: 5900, w: 1900, h: 1200, vb: "0 0 1800 1100", html: petrolina, classe: "gravura" })}
  `, "zona-cordel");
  for (const [id, txt] of [["canavial", "ZONA DA MATA"], ["feira", "AGRESTE"], ["caatinga", "SERTÃO · CAATINGA"], ["rio", "RIO SÃO FRANCISCO"], ["petrolina", "PETROLINA"]])
    document.getElementById(id).insertAdjacentHTML("beforeend", leg(txt));

  // mapa: contorno real de PE entalhado + camada de cores do azul (litoral) ao dourado (sertão)
  const svg = document.querySelector("#mapa-c7 svg");
  svg.innerHTML = `<defs><linearGradient id="g7" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="${Z}"/><stop offset=".25" stop-color="${G}"/><stop offset=".6" stop-color="${A}"/><stop offset="1" stop-color="#c98a2a"/></linearGradient></defs>
    <path data-uf="pe" d="${pe}" fill="none" stroke="none"/>
    <path id="pe-cores7" class="foco" d="${pe}" fill="url(#g7)" opacity=".85"/>
    <path id="pe-xilo" class="traco" d="${pe}" stroke="${T}" stroke-width="1.6" stroke-linejoin="round" fill="none"/>`;
  B._pendentes.push({ id: svg.id, recorte: ["pe"], margem: 0.04 }); B.finalizar();
  // ondas nos arrecifes, junto ao litoral real
  const costa = B.costaLeste(svg.id, "pe", 0.35);
  svg.insertAdjacentHTML("beforeend", `<g id="ondas" class="foco" stroke="${Z}" stroke-width=".7" fill="none" stroke-linecap="round">
      ${[0, 1, 2].map((i) => `<path class="traco" d="M${costa[0] + 1.5},${costa[1] - 6 + i * 6} c1.5,-1.5 3,1.5 4.5,0 c1.5,-1.5 3,1.5 4.5,0"/>`).join("")}</g>`);
  document.getElementById("mapa-c7").insertAdjacentHTML("beforeend",
    `<div id="km700" class="madeira foco" data-texto="+700 km" style="position:absolute;left:0;right:0;bottom:-40px;text-align:center;font-size:520px;color:${V}"></div>`);
  window.Documentario.montar(window.PLANO);
})();
