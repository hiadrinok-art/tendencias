/* Cena 2 — O açúcar (mesa de arquivo) */
(function () {
  const srcEngenho = "img/engenho.jpg"; // TROCAR por engenho2.jpg quando baixar

  B.css(`
    .livro { background: linear-gradient(90deg, #e8d7b4 0 49.6%, #b49a6c 49.6% 50.4%, #e8d7b4 50.4%); border-radius: 10px; }
    .livro .pag { position: absolute; top: 120px; bottom: 90px; }
    .livro .linha { height: 18px; margin: 0 0 46px; border-radius: 9px; background: rgba(60,40,25,.28); }
    .livro .cab { position: absolute; top: 40px; left: 0; right: 0; text-align: center; font-size: 46px; letter-spacing: 8px; color: rgba(60,40,25,.6); }
    .livro .palavra { font-family: "Serifa", serif; font-style: italic; font-size: 92px; color: #2a1f16; }
  `);

  const linhas = (n, larguras) => Array.from({ length: n }, (_, i) => `<div class="linha" style="width:${larguras[i % larguras.length]}%"></div>`).join("");
  const livro = `
    <div class="cab datil">LIVRO DE REGISTRO · ENGENHO</div>
    <div class="pag" style="left:90px;width:calc(50% - 150px)">${linhas(14, [96, 88, 92, 70, 95, 84])}</div>
    <div class="pag" style="left:calc(50% + 60px);width:calc(50% - 150px)">
      ${linhas(5, [92, 86, 95, 78, 90])}
      <div style="margin:-10px 0 40px"><span id="marca-escr" class="sub palavra">escravizados<svg viewBox="0 0 100 10" preserveAspectRatio="none"><path id="sub-escr" class="traco" d="M2,6 C30,3 70,8 98,4" stroke="#b0161e" stroke-width="2.2" stroke-linecap="round"/></svg></span></div>
      ${linhas(7, [88, 94, 80, 91, 70, 86, 93])}
    </div>`;

  const caravela = `<g stroke="#e9dcc0" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none">
      <path class="traco" d="M120,640 L1480,640 L1300,820 L300,820 Z"/>
      <path class="traco" d="M620,640 L620,120 M1020,640 L1020,220"/>
      <path class="traco" d="M640,160 C860,220 880,440 640,560 M1040,250 C1220,300 1240,470 1040,560"/>
      <path class="traco" d="M620,120 L760,150 L620,180"/>
      <path class="traco" d="M40,900 C260,860 420,940 640,900 C860,860 1040,940 1260,900 C1400,875 1500,890 1580,900"/>
    </g>`;
  const cana = `<g stroke="#4f6a2a" stroke-width="18" stroke-linecap="round" fill="none">
      <path class="traco" d="M450,1500 L450,100"/><path class="traco" d="M410,1150 L490,1150 M410,800 L490,800 M410,450 L490,450"/>
      <path class="traco" d="M450,1150 C300,1050 180,980 80,1000"/><path class="traco" d="M450,800 C620,700 760,660 860,690"/>
      <path class="traco" d="M450,450 C300,330 200,280 110,290"/><path class="traco" d="M450,160 C560,60 660,20 760,30"/></g>`;
  const torrao = `<g stroke="#e9dcc0" stroke-width="16" stroke-linejoin="round" fill="none">
      <path class="traco" d="M150,260 L420,140 L640,260 L370,380 Z"/><path class="traco" d="M150,260 L150,560 L370,680 L370,380"/>
      <path class="traco" d="M370,680 L640,560 L640,260"/></g>
      <g fill="#f4ecdc" opacity=".7"><circle cx="300" cy="300" r="10"/><circle cx="460" cy="250" r="8"/><circle cx="250" cy="470" r="9"/><circle cx="520" cy="430" r="7"/></g>`;
  const rota = `<g fill="none" stroke-linecap="round">
      <path class="traco" d="M200,1200 C700,900 1500,500 2950,260" stroke="#7a2a14" stroke-width="14" stroke-dasharray="1 0"/>
      <path class="traco" d="M200,1200 C800,1000 1700,700 2950,560" stroke="#7a2a14" stroke-width="14"/></g>
      <g fill="#7a2a14"><circle cx="200" cy="1200" r="34"/><circle cx="2950" cy="260" r="30"/><circle cx="2950" cy="560" r="30"/></g>`;

  const mapaPe = B.mapa({ id: "mapa-c2", x: 6100, y: 2450, w: 2400, h: 1050, estados: [{ uf: "pe", fill: "rgba(120,80,40,.16)", stroke: "#5a3418", swpx: 6 }], fundo: "mapa-papel" });

  B.mundo(9600, 5500, `
    ${B.folha({ id: "folha-1535", x: 400, y: 500, w: 1500, h: 560, rot: -1.2, html: B.datil({ id: "data1535", texto: "1535", size: 300, top: 110 }) })}
    ${B.svg({ id: "caravela", x: 300, y: 1350, w: 1700, h: 1000, vb: "0 0 1600 960", html: caravela })}
    ${B.foto({ id: "foto-olinda", src: "img/olinda.jpg", x: 2300, y: 380, w: 2100, rot: 2, legenda: "Olinda · Frans Post" })}
    ${B.svg({ id: "cana", x: 2600, y: 2400, w: 900, h: 1550, vb: "0 0 900 1550", html: cana })}
    ${B.foto({ id: "foto-engenho", src: srcEngenho, x: 3700, y: 2300, w: 2100, rot: -2, legenda: "Engenho · Frans Post" })}
    ${B.svg({ id: "torrao", x: 4700, y: 600, w: 760, h: 760, vb: "0 0 800 800", html: torrao })}
    ${B.folha({ id: "livro", x: 5600, y: 450, w: 3200, h: 1650, rot: 1, classe: "livro", foco: true, html: livro })}
    ${mapaPe}
    ${B.folha({ id: "carta", x: 5900, y: 3800, w: 3300, h: 1400, rot: -0.8, classe: "mapa-papel", html: B.svg({ id: "rota", x: 150, y: 60, w: 2600, h: 1150, vb: "0 0 3200 1400", html: rota }) })}
  `);
  // rótulos da rota (texto fixo, aparece com a rota)
  document.getElementById("rota").insertAdjacentHTML("beforeend", `
    <div class="rotulo" style="left:40px;top:1000px;font-size:58px">RECIFE</div>
    <div class="rotulo" style="left:2440px;top:150px;font-size:58px">AMSTERDÃ</div>
    <div class="rotulo" style="left:2440px;top:420px;font-size:58px">LISBOA</div>`);
  B.finalizar();
  // nomes dos povos (da Cena 1) já escritos no mapa — vão se apagar em "terras"
  const svgId = "vb-mapa-c2", div = document.getElementById("mapa-c2");
  div.insertAdjacentHTML("beforeend", `<div id="nomes-povos" style="position:absolute;inset:0"></div>`);
  const g = document.getElementById("nomes-povos");
  for (const [txt, fx, fy] of [["Caetés", 0.86, 0.62], ["Potiguaras", 0.80, 0.14], ["Tabajaras", 0.55, 0.30]]) {
    const [x, y] = B.svgParaDiv(svgId, B.pontoEstado(svgId, "pe", fx, fy));
    g.insertAdjacentHTML("beforeend", `<div class="serif" style="position:absolute;left:${x}px;top:${y}px;transform:translate(-50%,-50%);font-size:76px;font-style:italic;color:#4a2a14;white-space:nowrap">${txt}</div>`);
  }
  window.Documentario.montar(window.PLANO);
})();
