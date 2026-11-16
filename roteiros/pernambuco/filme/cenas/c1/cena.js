/* Cena 1 — A terra antes do nome (mesa de arquivo) */
(function () {
  // Pernambuco sem divisões internas: só a silhueta, e por cima uma camada litoral(azul) → sertão(ocre)
  const grad = `<defs><linearGradient id="g-faixa" x1="1" y1="0" x2="0" y2="0">
      <stop offset="0" stop-color="#3f6f9a" stop-opacity=".55"/><stop offset=".22" stop-color="#4f7d3a" stop-opacity=".5"/>
      <stop offset=".55" stop-color="#9a8a3a" stop-opacity=".5"/><stop offset="1" stop-color="#b8742a" stop-opacity=".6"/></linearGradient></defs>`;
  const pe = GEO.estados.pe.d;
  const silhueta = `<path id="pe-silhueta" class="foco" d="${pe}" fill="rgba(120,80,40,.16)" stroke="#5a3418" stroke-width="1" vector-effect="non-scaling-stroke" style="stroke-width:7px"/>
                    <path id="pe-cores" class="foco" d="${pe}" fill="url(#g-faixa)" stroke="none"/>`;

  // figuras rupestres genéricas em traço ocre (pessoas, cervo, ave, sol, mãos)
  const ocre = 'stroke="#a5481f" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" fill="none"';
  const figuras = `<g ${ocre}>
    <path class="traco" d="M200,260 L200,520 M200,330 L120,420 M200,330 L280,410 M200,520 L140,660 M200,520 L260,660"/><circle class="traco" cx="200" cy="215" r="42"/>
    <path class="traco" d="M420,280 L420,540 M420,350 L340,300 M420,350 L510,300 M420,540 L370,680 M420,540 L470,680"/><circle class="traco" cx="420" cy="235" r="42"/>
    <path class="traco" d="M640,300 L640,540 M640,360 L560,440 M640,360 L720,430 M640,540 L590,680 M640,540 L700,680"/><circle class="traco" cx="640" cy="255" r="42"/>
    <path class="traco" d="M900,460 C960,400 1120,400 1180,460 L1220,420 M900,460 L880,600 M960,470 L950,610 M1120,470 L1130,610 M1180,460 L1190,600 M1220,420 L1260,340 M1240,380 L1300,330"/>
    <path class="traco" d="M1350,250 L1450,200 L1550,250 M1450,200 L1450,330 M1400,280 L1500,280"/>
    <circle class="traco" cx="1500" cy="560" r="80"/><path class="traco" d="M1500,450 L1500,420 M1500,700 L1500,670 M1390,560 L1360,560 M1640,560 L1610,560 M1425,485 L1405,465 M1575,635 L1595,655"/>
  </g>`;

  B.css(`
    .pedra { background: radial-gradient(ellipse at 40% 35%, #d9b48a, #b98a5c 60%, #9a6c44); border-radius: 40px 70px 50px 90px; }
    .pedra::after { content: ""; position: absolute; inset: 0; border-radius: inherit; opacity: .35;
      background: repeating-radial-gradient(circle at 30% 40%, rgba(80,40,20,.25) 0 2px, transparent 2px 14px); }`);
  B.mundo(7400, 4300, `
    ${B.mapa({ id: "mapa-pe", x: 300, y: 700, w: 4400, h: 1900, estados: [], fundo: "mapa-papel" })}
    ${B.foto({ id: "foto-catimbau", src: "img/catimbau.jpg", x: 4950, y: 450, w: 1900, rot: 2.5, legenda: "Vale do Catimbau" })}
    ${B.folha({ id: "pedra", x: 4900, y: 2550, w: 2050, h: 1200, rot: -1.5, classe: "pedra",
        html: `<div style="position:absolute;inset:80px 60px 60px 60px">${B.svg({ id: "figuras", x: 0, y: 0, w: "100%", h: "100%", vb: "0 0 1700 800", html: figuras })}</div>` })}
  `);
  // o mapa é montado à mão aqui (silhueta + gradiente), mantendo o viewBox recortado em PE
  const svg = document.querySelector("#mapa-pe svg");
  svg.innerHTML = grad + `<path data-uf="pe" d="${pe}" fill="none" stroke="none"/>` + silhueta;
  B._pendentes.push({ id: svg.id, recorte: ["pe"], margem: 0.05 });
  B.finalizar();

  // nomes dos povos, escritos à mão sobre o mapa (posições aproximadas, sem fronteiras)
  const div = document.getElementById("mapa-pe");
  const nomes = [["nome-caetes", "Caetés", 0.86, 0.62], ["nome-potiguaras", "Potiguaras", 0.80, 0.14], ["nome-tabajaras", "Tabajaras", 0.55, 0.30]];
  for (const [id, txt, fx, fy] of nomes) {
    div.insertAdjacentHTML("beforeend", `<div id="${id}" class="serif foco" data-texto="${txt}" style="position:absolute;font-size:120px;font-style:italic;color:#4a2a14;white-space:nowrap"></div>`);
    B.colocarNoMapa(id, svg.id, B.pontoEstado(svg.id, "pe", fx, fy));
    gsap.set("#" + id, { xPercent: -50, yPercent: -50 });
  }
  window.Documentario.montar(window.PLANO);
})();
