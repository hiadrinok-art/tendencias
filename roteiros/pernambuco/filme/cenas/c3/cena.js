/* Cena 3 — Palmares (mesa de arquivo) */
(function () {
  // Pernambuco e Alagoas com a mesma cor: até 1817 Alagoas era uma comarca de Pernambuco
  const cor = "rgba(150,70,40,.20)";
  const mapa = B.mapa({ id: "mapa-c3", x: 300, y: 450, w: 4300, h: 2500, fundo: "mapa-papel", margem: 0.06,
    estados: [{ uf: "pe", fill: cor, stroke: "#5a3418", swpx: 6 }, { uf: "al", fill: cor, stroke: "rgba(90,52,24,.55)", swpx: 4 }] });

  const ocre = 'stroke="#e9dcc0" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  const palicada = `<g ${ocre}>
      ${Array.from({ length: 9 }, (_, i) => `<path class="traco" d="M${1300 + i * 95},980 L${1300 + i * 95},420 L${1325 + i * 95},360 L${1350 + i * 95},420 L${1350 + i * 95},980"/>`).join("")}
      <path class="traco" d="M1260,560 L2180,560 M1260,820 L2180,820"/>
    </g>
    <g stroke="#c0392b" stroke-width="16" stroke-linecap="round" fill="none">
      <path class="traco" d="M80,500 L1150,560 M1100,520 L1150,560 L1100,600"/>
      <path class="traco" d="M80,700 L1150,700 M1100,660 L1150,700 L1100,740"/>
      <path class="traco" d="M80,900 L1150,840 M1100,800 L1150,840 L1100,880"/>
    </g>`;

  B.mundo(9200, 5000, `
    ${mapa}
    ${B.foto({ id: "foto-serra", src: "img/serra_barriga.jpg", x: 5000, y: 350, w: 2200, rot: 2, legenda: "Serra da Barriga" })}
    ${B.svg({ id: "palicada", x: 6100, y: 2950, w: 2700, h: 1300, vb: "0 0 2300 1100", html: palicada })}
    ${B.folha({ id: "folha-zumbi", x: 500, y: 3250, w: 2600, h: 1100, rot: -1.2, html: `
        ${B.datil({ id: "nome-zumbi", texto: "ZUMBI", size: 260, top: 160 })}
        ${B.datil({ id: "data-zumbi", texto: "20 de novembro de 1695", size: 120, top: 640 })}` })}
    ${B.folha({ id: "folha-consc", x: 3200, y: 3300, w: 2600, h: 1100, rot: 1.2, html: `
        ${B.carimbo({ id: "carimbo-nov", texto: "20 DE NOVEMBRO", x: 330, y: 150, size: 140, rot: -5 })}
        ${B.datil({ id: "txt-consc", texto: "Dia da Consciência Negra", size: 120, top: 700, classe: "serif" })}` })}
  `);
  B.finalizar();
  const sv = "vb-mapa-c3", div = document.getElementById("mapa-c3");
  // pontos reais: Recife no litoral de PE; Serra da Barriga (União dos Palmares, ~9°10' S, 36°03' O) dentro de Alagoas
  const recife = B.costaLeste(sv, "pe", 0.35), serra = B.pontoEstado(sv, "al", 0.71, 0.21);
  const svg = document.getElementById(sv);
  svg.insertAdjacentHTML("beforeend", `<path id="linha-resist" class="traco foco" d="M${recife[0]},${recife[1]} Q${(recife[0] + serra[0]) / 2 + 8},${recife[1] + 6} ${serra[0]},${serra[1]}" fill="none" stroke="#b0161e" stroke-width="1.6" stroke-linecap="round"/>
    <circle cx="${serra[0]}" cy="${serra[1]}" r="1.6" fill="#b0161e"/>`);
  div.insertAdjacentHTML("beforeend", `
    <div id="rot-serra" class="rotulo" style="font-size:64px">SERRA DA BARRIGA</div>
    <div id="rot-pe" class="rotulo" style="font-size:72px">PERNAMBUCO · ATÉ 1817</div>`);
  B.colocarNoMapa("rot-serra", sv, serra, 30, 20);
  const peBB = document.querySelector('#vb-mapa-c3 path[data-uf="pe"]').getBBox();
  B.colocarNoMapa("rot-pe", sv, [peBB.x + peBB.width * 0.18, peBB.y + peBB.height * 0.25]);
  window.Documentario.montar(window.PLANO);
})();
