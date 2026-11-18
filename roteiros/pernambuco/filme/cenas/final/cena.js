/* Final — O que é ser pernambucano (cordel, fechando na mesa de arquivo) */
(function () {
  const T = "#15120f", V = "#b3201c", A = "#e8b230", G = "#2f7d3a", Z = "#1f4f9c", P = "#f1e7d0";
  const tr = (w = 22) => `stroke="${T}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"`;

  const gomos = [V, A, G, Z, V, A, G, Z];
  const somb = gomos.map((c, i) => { const a0 = Math.PI + i * Math.PI / 8, a1 = a0 + Math.PI / 8, r = 640;
    return `<path d="M800,700 L${800 + r * Math.cos(a0)},${700 + r * Math.sin(a0)} A${r},${r} 0 0,1 ${800 + r * Math.cos(a1)},${700 + r * Math.sin(a1)} Z" fill="${c}" stroke="${T}" stroke-width="14"/>`; }).join("")
    + `<path d="M800,700 L800,1350 C800,1430 700,1430 690,1360" ${tr()}/>`;
  const alfaia = `<ellipse cx="600" cy="260" rx="420" ry="110" fill="${P}" stroke="${T}" stroke-width="18"/>
      <path d="M180,260 L180,860 C180,940 1020,940 1020,860 L1020,260" fill="${V}" stroke="${T}" stroke-width="18"/>
      <path d="M180,300 L400,860 L600,300 L800,860 L1020,300" fill="none" stroke="${P}" stroke-width="16"/>`;
  const sanfona = `<path d="M220,300 L520,160 L520,660 L220,800 Z" fill="${V}" stroke="${T}" stroke-width="18"/><path d="M1080,160 L1380,300 L1380,800 L1080,660 Z" fill="${V}" stroke="${T}" stroke-width="18"/>
      <path d="M520,160 L1080,160 L1080,660 L520,660 Z" fill="${P}" stroke="${T}" stroke-width="18"/>
      ${Array.from({ length: 6 }, (_, i) => `<path d="M${600 + i * 80},160 L${600 + i * 80},660" stroke="${T}" stroke-width="16"/>`).join("")}`;
  // bandeira atual de Pernambuco (uma estrela), com contorno de xilogravura
  const bandeira = `<rect x="0" y="0" width="1700" height="700" fill="${Z}" stroke="${T}" stroke-width="18"/>
      <rect x="0" y="700" width="1700" height="450" fill="${P}" stroke="${T}" stroke-width="18"/>
      <path d="M470,640 A380,380 0 0 1 1230,640" stroke="#c8202a" stroke-width="48" fill="none"/>
      <path d="M518,640 A332,332 0 0 1 1182,640" stroke="${A}" stroke-width="48" fill="none"/>
      <path d="M566,640 A284,284 0 0 1 1134,640" stroke="${G}" stroke-width="48" fill="none"/>
      <circle cx="850" cy="560" r="78" fill="${A}" stroke="${T}" stroke-width="8"/>
      <path transform="translate(850,150) scale(1.3)" fill="${A}" stroke="${T}" stroke-width="6" d="${B.ESTRELA}"/>
      <path d="M820,760 h60 v110 h110 v60 h-110 v200 h-60 v-200 h-110 v-60 h110 z" fill="#c8202a" stroke="${T}" stroke-width="8"/>`;
  const ufs = Object.keys(GEO.estados);
  const mapa = B.mapa({ id: "mapa-br2", x: 400, y: 3900, w: 3300, h: 2300, fundo: "papel", margem: 0.03,
    estados: ufs.map((uf) => ({ uf, fill: "none", stroke: T, swpx: 3 })) });

  B.mundo(13000, 8200, `
    ${B.folha({ id: "lembra-1817", x: 300, y: 7350, w: 2000, h: 640, rot: -2, html: B.texto({ html: "6 de março de 1817", size: 120, top: 220, classe: "datil" }) })}
    ${B.foto({ id: "lembra-caneca", src: "img/caneca.jpg", x: 10600, y: 7150, w: 1400, rot: 3, legenda: "Frei Caneca", foco: false })}
    ${B.foto({ id: "lembra-olinda", src: "img/olinda.jpg", x: 2800, y: 7250, w: 1500, rot: -1.5, legenda: "Olinda", foco: false })}
    <div id="folheto" class="peca zona-cordel fundo-cordel" style="left:1000px;top:500px;width:11000px;height:6600px;box-shadow:0 60px 120px rgba(0,0,0,.6)">
      ${B.folha({ id: "capa-final", x: 400, y: 300, w: 3100, h: 1400, rot: -1, html: B.datil({ id: "txt-capa", texto: "o que é ser pernambucano?", size: 150, top: 520, classe: "madeira" }) })}
      ${B.folha({ id: "folha-datas", x: 3800, y: 350, w: 3400, h: 900, rot: 1, html: B.datil({ id: "txt-datas", texto: "1535 · 1630 · 1654 · 1695 · 1817 · 1824", size: 130, top: 340 }) })}
      ${B.folha({ id: "folha-rep", x: 7500, y: 300, w: 3100, h: 1200, rot: -1.2, html: B.carimbo({ id: "carimbo-rep2", texto: "REPÚBLICA", x: 380, y: 330, size: 300, rot: -5 }) })}
      ${B.foto({ id: "foto-serra2", src: "img/serra_barriga.jpg", x: 400, y: 1900, w: 2300, rot: 1.5, legenda: "Palmares · Serra da Barriga" })}
      <div id="trio" style="position:absolute;left:3100px;top:2000px;width:5000px;height:1600px">
        ${B.svg({ id: "somb2", x: 0, y: 0, w: 1500, h: 1400, vb: "0 0 1600 1450", html: somb, classe: "gravura" })}
        ${B.svg({ id: "alfaia2", x: 1750, y: 250, w: 1300, h: 1050, vb: "0 0 1200 960", html: alfaia, classe: "gravura" })}
        ${B.svg({ id: "sanfona2", x: 3300, y: 250, w: 1600, h: 1000, vb: "0 0 1600 960", html: sanfona, classe: "gravura" })}
      </div>
      ${B.folha({ id: "folha-dor", x: 8300, y: 2100, w: 2400, h: 1300, rot: 1, html: B.datil({ id: "txt-dor", texto: "dor em música, luta em memória", size: 140, top: 300, extra: { padding: "0 120px", "line-height": "1.4" } }) })}
      ${mapa}
      ${B.svg({ id: "bandeira-pe", x: 4300, y: 3700, w: 3000, h: 2030, vb: "0 0 1700 1150", html: bandeira, classe: "gravura" })}
    </div>`);
  // PE aceso no mapa do Brasil
  B.finalizar();
  const svg = document.getElementById("vb-mapa-br2");
  svg.insertAdjacentHTML("beforeend", `<path id="pe-acesa" class="foco" d="${GEO.estados.pe.d}" fill="${V}" stroke="${T}" stroke-width="1" vector-effect="non-scaling-stroke" style="stroke-width:5px"/>`);
  document.getElementById("bandeira-pe").insertAdjacentHTML("beforeend", `
    <div style="position:absolute;left:-700px;right:-700px;top:2080px;text-align:center">
      <div class="madeira" style="font-size:260px;letter-spacing:20px">PERNAMBUCO</div>
      <div id="txt-povo" class="madeira verm foco" data-texto="Uma história que vive em seu povo." style="font-size:120px;margin-top:10px"></div></div>`);
  window.Documentario.montar(window.PLANO);
})();
