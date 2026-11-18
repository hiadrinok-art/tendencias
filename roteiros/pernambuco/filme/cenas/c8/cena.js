/* Cena 8 — O próximo capítulo (cordel) */
(function () {
  const T = "#15120f", V = "#b3201c", A = "#e8b230", Z = "#1f4f9c";
  const tr = (w = 22) => `stroke="${T}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" fill="none"`;
  // sobrado e casebre lado a lado (contraste, sem números)
  const casas = `<path class="traco" d="M150,1400 L150,500 L550,250 L950,500 L950,1400 Z M150,500 L950,500 M300,650 L300,850 L450,850 L450,650 Z M650,650 L650,850 L800,850 L800,650 Z M300,1000 L300,1200 L450,1200 L450,1000 Z M650,1000 L650,1400 L800,1400 L800,1000" ${tr()}/>
      <path class="traco" d="M1350,1400 L1350,1000 L1600,850 L1850,1000 L1850,1400 Z M1550,1400 L1550,1180 L1660,1180 L1660,1400" ${tr()}/>
      <path class="traco" d="M60,1400 L2000,1400" ${tr()}/>`;
  const cisterna = `<path class="traco" d="M300,700 L300,1350 C300,1450 1300,1450 1300,1350 L1300,700" ${tr()}/>
      <path class="traco" d="M250,700 C250,520 1350,520 1350,700 Z" ${tr()}/>
      ${[0, 1, 2, 3].map((i) => `<path class="traco" d="M300,${850 + i * 140} C600,${900 + i * 140} 1000,${900 + i * 140} 1300,${850 + i * 140}" ${tr(12)}/>`).join("")}
      <path d="M800,120 C740,240 700,300 700,360 C700,420 745,460 800,460 C855,460 900,420 900,360 C900,300 860,240 800,120 Z" fill="${Z}" stroke="${T}" stroke-width="14"/>`;
  const sinagoga = `<path class="traco" d="M100,1300 L100,400 L1300,400 L1300,1300 Z M100,400 L700,150 L1300,400" ${tr()}/>
      ${[0, 1, 2].map((i) => `<path class="traco" d="M${260 + i * 360},1300 L${260 + i * 360},850 C${260 + i * 360},730 ${440 + i * 360},730 ${440 + i * 360},850 L${440 + i * 360},1300" ${tr(16)}/>`).join("")}
      ${[0, 1, 2].map((i) => `<path class="traco" d="M${280 + i * 360},520 L${280 + i * 360},680 L${420 + i * 360},680 L${420 + i * 360},520 Z" ${tr(14)}/>`).join("")}`;
  const porto = `<path class="traco" d="M100,1400 L100,500 L600,500 L600,1400 M700,1400 L700,250 L1200,250 L1200,1400 M1300,1400 L1300,700 L1800,700 L1800,1400 M40,1400 L1860,1400" ${tr()}/>
      <path class="traco" d="M200,620 L500,620 L500,800 M350,800 L350,1000 L500,1000 M800,400 L1100,400 L1100,600 L950,600 L950,900 M800,1000 L1100,1000 M1400,850 L1700,850 L1700,1050 L1550,1050" stroke="${V}" stroke-width="14" stroke-linecap="round" fill="none"/>
      ${[[500, 800], [350, 1000], [1100, 600], [950, 900], [1700, 1050]].map(([x, y]) => `<circle cx="${x}" cy="${y}" r="26" fill="${A}" stroke="${T}" stroke-width="10"/>`).join("")}`;
  const pena = `<path class="traco" d="M1700,150 C1300,250 1000,600 900,1000 L960,1020 C1100,640 1400,330 1700,150 Z" ${tr(18)}/>
      <path class="traco" d="M930,1010 L880,1150" ${tr(14)}/>
      <path class="traco" d="M100,1200 C400,1170 600,1230 880,1170" stroke="${T}" stroke-width="16" stroke-linecap="round" fill="none"/>`;
  const leg = (txt) => `<div class="madeira" style="position:absolute;left:-200px;right:-200px;bottom:-150px;text-align:center;font-size:104px;white-space:nowrap">${txt}</div>`;

  B.mundo(9200, 5600, `
    ${B.folha({ id: "folha-desafios", x: 400, y: 400, w: 2700, h: 950, rot: -1, html: B.datil({ id: "txt-desafios", texto: "desafios antigos", size: 210, top: 300 }) })}
    ${B.svg({ id: "casas", x: 500, y: 1900, w: 2400, h: 1650, vb: "0 0 2060 1450", html: casas, classe: "gravura" })}
    ${B.svg({ id: "cisterna", x: 3600, y: 450, w: 1700, h: 1650, vb: "0 0 1600 1500", html: cisterna, classe: "gravura" })}
    <div id="bairro" style="position:absolute;left:3400px;top:2500px;width:4600px;height:2200px">
      ${B.svg({ id: "sinagoga-traco", x: 0, y: 200, w: 1600, h: 1550, vb: "0 0 1400 1350", html: sinagoga, classe: "gravura" })}
      ${B.svg({ id: "porto", x: 2100, y: 150, w: 2300, h: 1700, vb: "0 0 1900 1450", html: porto, classe: "gravura" })}
    </div>
    ${B.svg({ id: "pena", x: 5900, y: 400, w: 2600, h: 1600, vb: "0 0 1800 1250", html: pena, classe: "gravura" })}
  `, "zona-cordel");
  for (const [id, txt] of [["casas", "DESIGUALDADE"], ["cisterna", "SERTÃO · ÁGUA"], ["sinagoga-traco", "KAHAL ZUR ISRAEL · 1636"], ["porto", "PORTO DIGITAL"], ["pena", "O PRÓXIMO CAPÍTULO"]])
    document.getElementById(id).insertAdjacentHTML("beforeend", leg(txt));
  window.Documentario.montar(window.PLANO);
})();
