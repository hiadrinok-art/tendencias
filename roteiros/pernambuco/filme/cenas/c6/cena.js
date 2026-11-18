/* Cena 6 — A cultura que ferve: a virada da mesa de arquivo para o CORDEL.
   O mundo é a mesa; sobre ela, um grande folheto (.zona-cordel) com capa. A capa sai e a câmera mergulha. */
(function () {
  const T = "#15120f", V = "#b3201c", A = "#e8b230", G = "#2f7d3a", Z = "#1f4f9c", P = "#f1e7d0";
  const tr = `stroke="${T}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round" fill="none"`;

  // sombrinha de frevo (gomos coloridos com contorno preto) + cabo
  const gomos = [V, A, G, Z, V, A, G, Z];
  const somb = gomos.map((c, i) => { const a0 = Math.PI + i * Math.PI / 8, a1 = a0 + Math.PI / 8, r = 640;
    return `<path d="M800,700 L${800 + r * Math.cos(a0)},${700 + r * Math.sin(a0)} A${r},${r} 0 0,1 ${800 + r * Math.cos(a1)},${700 + r * Math.sin(a1)} Z" fill="${c}" stroke="${T}" stroke-width="14"/>`; }).join("")
    + `<path d="M800,700 L800,1350 C800,1430 700,1430 690,1360" ${tr}/><circle cx="800" cy="52" r="26" fill="${T}"/>`;
  // cortejo de maracatu: estandarte, rei, rainha (figuras de xilogravura, genéricas)
  const fig = (x, coroa) => `<path class="traco" d="M${x},430 L${x - 120},980 L${x + 120},980 Z M${x - 60},560 L${x - 170},700 M${x + 60},560 L${x + 170},700" ${tr}/>
      <circle class="traco" cx="${x}" cy="360" r="70" ${tr}/>${coroa ? `<path class="traco" d="M${x - 70},290 L${x - 50},220 L${x - 20},270 L${x},210 L${x + 20},270 L${x + 50},220 L${x + 70},290" ${tr}/>` : ""}`;
  const cortejo = `<path class="traco" d="M180,980 L180,140 M180,160 L480,160 L480,520 L330,440 L180,520" ${tr}/>${fig(800, true)}${fig(1260, true)}
      <path class="traco" d="M80,1060 L1520,1060" ${tr}/>`;
  const alfaia = `<ellipse cx="600" cy="260" rx="420" ry="110" fill="${P}" stroke="${T}" stroke-width="18"/>
      <path d="M180,260 L180,860 C180,940 1020,940 1020,860 L1020,260" fill="${V}" stroke="${T}" stroke-width="18"/>
      <path d="M180,300 L400,860 L600,300 L800,860 L1020,300" fill="none" stroke="${P}" stroke-width="16"/>
      <path d="M1100,80 L760,300 M1180,160 L860,330" stroke="${T}" stroke-width="22" stroke-linecap="round"/>`;
  const bandeirinhas = Array.from({ length: 12 }, (_, i) => `<path d="M${80 + i * 140},${200 + (i % 2) * 20} l120,0 l0,140 l-60,-50 l-60,50 z" fill="${[V, A, G, Z][i % 4]}" stroke="${T}" stroke-width="10"/>`).join("");
  const saojoao = `<path class="traco" d="M40,190 C600,260 1200,260 1780,190" ${tr}/>${bandeirinhas}
      <path class="traco" d="M700,1250 L1100,950 M700,950 L1100,1250 M760,1250 L1040,1250" ${tr}/>
      <path d="M900,1000 C760,860 880,780 860,640 C980,760 1000,700 1000,600 C1100,760 1080,880 900,1000 Z" fill="${V}" stroke="${T}" stroke-width="14"/>`;
  const barro = `<path d="M600,250 C680,250 720,320 700,400 L780,420 C860,440 880,620 820,900 L380,900 C320,620 340,440 420,420 L500,400 C480,320 520,250 600,250 Z" fill="#a8562a" stroke="${T}" stroke-width="18"/>
      <path d="M470,600 L330,760 M730,600 L870,760" stroke="${T}" stroke-width="22" stroke-linecap="round"/><path d="M380,900 L340,1080 L860,1080 L820,900" fill="#8c4420" stroke="${T}" stroke-width="18"/>
      <ellipse cx="600" cy="230" rx="170" ry="40" fill="#8c4420" stroke="${T}" stroke-width="14"/>`;
  // sanfona + chapéu de couro (sem retrato do artista)
  const gonzaga = `<path class="traco" d="M220,700 L520,560 L520,1060 L220,1200 Z M520,560 L1080,560 L1080,1060 L520,1060 M1080,560 L1380,700 L1380,1200 L1080,1060" ${tr}/>
      ${Array.from({ length: 6 }, (_, i) => `<path class="traco" d="M${600 + i * 80},560 L${600 + i * 80},1060" ${tr}/>`).join("")}
      <path class="traco" d="M330,330 C420,140 1180,140 1270,330 C1350,380 1450,420 1500,470 C1100,420 500,420 100,470 C150,420 250,380 330,330 Z" ${tr}/>
      <path class="traco" d="M420,330 L600,250 L800,330 L1000,250 L1180,330" ${tr}/>`;
  const mangue = `<path class="traco" d="M500,700 C500,480 1100,480 1100,700 C1100,900 500,900 500,700 Z" ${tr}/>
      <path class="traco" d="M520,640 L300,520 L180,600 M510,720 L280,720 M520,800 L300,900 M1080,640 L1300,520 L1420,600 M1090,720 L1320,720 M1080,800 L1300,900" ${tr}/>
      <path class="traco" d="M700,520 L640,300 M900,520 L960,300 M640,300 L560,200 M960,300 L1040,200 M800,500 L800,180 M740,220 L860,220 M760,260 L840,260" ${tr}/>`;
  const museu = `<path class="traco" d="M200,150 L1500,150 L1500,1050 L200,1050 Z M300,250 L1400,250 L1400,950 L300,950 Z" ${tr}/>
      <path class="traco" d="M200,150 L300,250 M1500,150 L1400,250 M200,1050 L300,950 M1500,1050 L1400,950" ${tr}/>`;
  const capa = `<div style="position:absolute;inset:0;background:${P};border:40px solid ${T};box-sizing:border-box"></div>
      <div style="position:absolute;left:900px;right:900px;top:700px;bottom:1900px;border:30px solid ${T};background:repeating-linear-gradient(45deg,${T} 0 18px,transparent 18px 60px)"></div>
      <div class="madeira" style="position:absolute;left:0;right:0;top:4300px;text-align:center;font-size:560px;color:${T};letter-spacing:18px">PERNAMBUCO</div>
      <div class="madeira verm" style="position:absolute;left:0;right:0;top:4950px;text-align:center;font-size:280px;letter-spacing:10px">A CULTURA QUE FERVE</div>`;

  const pos = (x, y, w, h) => ({ x, y, w, h });
  B.mundo(11000, 6600, `
    <div id="folheto" class="peca zona-cordel fundo-cordel" style="left:900px;top:300px;width:9200px;height:6000px;box-shadow:0 60px 120px rgba(0,0,0,.6)">
      <div id="folheto-miolo" style="position:absolute;left:600px;top:600px;width:8000px;height:4800px">
        ${B.folha({ id: "folha-frevo", x: 200, y: 200, w: 1700, h: 1050, rot: -1, html: `${B.datil({ id: "data1907", texto: "1907", size: 220, top: 70 })}
            ${B.carimbo({ id: "bloco-frevo", texto: "FREVO", x: 330, y: 470, size: 300, rot: -4 })}` })}
        ${B.folha({ id: "folha-ferver", x: 200, y: 1400, w: 1700, h: 520, rot: 1, html: B.datil({ id: "txt-ferver", texto: "frever = ferver", size: 140, top: 150 }) })}
        ${B.svg({ id: "sombrinha", x: 2150, y: 150, w: 1700, h: 1500, vb: "0 0 1600 1450", html: somb, classe: "gravura" })}
        ${B.folha({ id: "folha-unesco", x: 4250, y: 350, w: 1700, h: 900, rot: -1.5, html: B.carimbo({ id: "selo-unesco", texto: "UNESCO · 2012", x: 190, y: 290, size: 150, rot: -5 }) })}
        ${B.svg({ id: "cortejo", x: 6150, y: 150, w: 1700, h: 1300, vb: "0 0 1600 1150", html: cortejo, classe: "gravura" })}
        ${B.svg({ id: "alfaia", x: 200, y: 2300, w: 1500, h: 1100, vb: "0 0 1200 960", html: alfaia, classe: "gravura" })}
        ${B.svg({ id: "saojoao", x: 2150, y: 2050, w: 1800, h: 1400, vb: "0 0 1820 1300", html: saojoao, classe: "gravura" })}
        ${B.svg({ id: "barro", x: 4400, y: 2150, w: 1300, h: 1300, vb: "0 0 1200 1150", html: barro, classe: "gravura" })}
        ${B.svg({ id: "gonzaga", x: 6150, y: 2000, w: 1700, h: 1400, vb: "0 0 1600 1250", html: gonzaga, classe: "gravura" })}
        ${B.svg({ id: "mangue", x: 400, y: 3600, w: 1700, h: 1100, vb: "0 0 1600 1000", html: mangue, classe: "gravura" })}
        ${B.svg({ id: "museu", x: 2300, y: 3550, w: 1700, h: 1150, vb: "0 0 1700 1150", html: museu, classe: "gravura" })}
      </div>
      <div id="capa" style="position:absolute;inset:0">${capa}</div>
    </div>`);
  // legendas em tipo de madeira, dentro das próprias peças (aparecem junto com elas)
  const leg = (id, txt, top) => document.getElementById(id).insertAdjacentHTML("beforeend",
    `<div class="madeira" style="position:absolute;left:-100px;right:-100px;top:${top}px;text-align:center;font-size:96px;color:${T};white-space:nowrap">${txt}</div>`);
  leg("cortejo", "MARACATU", 1300); leg("alfaia", "ALFAIA", 1100); leg("saojoao", "CARUARU · SÃO JOÃO", 1400); leg("barro", "ALTO DO MOURA", 1300);
  leg("gonzaga", "LUIZ GONZAGA · EXU", 1400); leg("mangue", "MANGUEBEAT", 1100); leg("sombrinha", "CARNAVAL", 1500);
  window.Documentario.montar(window.PLANO);
})();
