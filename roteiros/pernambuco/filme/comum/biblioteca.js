/* biblioteca.js — peças reutilizáveis do documentário (geram HTML/SVG). Cada cena usa B.* em cena.js. */
(function () {
  const px = (v) => (typeof v === "number" ? v + "px" : v);
  const estilo = (o) => Object.entries(o).filter(([, v]) => v !== undefined && v !== null)
    .map(([k, v]) => `${k}:${px(v)}`).join(";");
  const CIRC = "M8,55 C6,20 40,6 62,8 C88,10 98,35 95,58 C92,85 60,96 38,93 C14,90 4,72 10,48 C14,36 22,28 30,24";
  const ESTRELA = "M0,-50 L12,-15 L48,-15 L19,6 L30,41 L0,20 L-30,41 L-19,6 L-48,-15 L-12,-15 Z";

  const B = {
    ESTRELA,
    mundo(w, h, html, classe) {
      const m = document.getElementById("mundo");
      m.style.width = w + "px"; m.style.height = h + "px";
      if (classe) m.classList.add(...classe.split(" "));
      m.innerHTML = html;
    },
    // folha de papel (ou outra peça) posicionada no mundo
    folha({ id, x, y, w, h, rot = 0, html = "", classe = "papel", foco = false, extra = {} }) {
      return `<div ${id ? `id="${id}"` : ""} class="peca ${classe}${foco ? " foco" : ""}" style="${estilo({ left: x, top: y, width: w, height: h, transform: `rotate(${rot}deg)`, ...extra })}">${html}</div>`;
    },
    // texto que será datilografado (data-texto) — centralizado na folha
    datil({ id, texto, size = 120, top = 0, classe = "datil", foco = true, extra = {} }) {
      return `<div id="${id}" class="centro ${classe}${foco ? " foco" : ""}" data-texto="${texto}" style="${estilo({ top, "font-size": size, ...extra })}"></div>`;
    },
    texto({ id, html, size = 60, top = 0, left, right, classe = "serif", foco = false, extra = {} }) {
      const pos = left !== undefined ? { left, right: right ?? 0, "text-align": "left" } : {};
      return `<div ${id ? `id="${id}"` : ""} class="centro ${classe}${foco ? " foco" : ""}" style="${estilo({ top, "font-size": size, ...pos, ...extra })}">${html}</div>`;
    },
    circ(id, palavra, cor = "#b0161e") {
      return `<span class="circ">${palavra}<svg viewBox="0 0 100 100" preserveAspectRatio="none"><path id="${id}" class="traco" d="${CIRC}" stroke="${cor}" stroke-width="2.4" stroke-linecap="round"/></svg></span>`;
    },
    sub(id, palavra, cor = "#b0161e") {
      return `<span class="sub">${palavra}<svg viewBox="0 0 100 10" preserveAspectRatio="none"><path id="${id}" class="traco" d="M2,6 C30,3 70,8 98,4" stroke="${cor}" stroke-width="2.2" stroke-linecap="round"/></svg></span>`;
    },
    carimbo({ id, texto, x, y, size = 96, rot = -5, foco = true }) {
      return `<div id="${id}" class="carimbo${foco ? " foco" : ""}" style="${estilo({ left: x, top: y, "font-size": size, transform: `rotate(${rot}deg)` })}">${texto}</div>`;
    },
    foto({ id, src, x, y, w, rot = 0, legenda = "", foco = true, extra = {} }) {
      return `<div id="${id}" class="foto${foco ? " foco" : ""}" style="${estilo({ left: x, top: y, width: w, transform: `rotate(${rot}deg)`, ...extra })}"><img src="${src}" alt="${legenda}">${legenda ? `<div class="legenda">${legenda}</div>` : ""}</div>`;
    },
    rotulo({ texto, x, y, size = 48, extra = {} }) {
      return `<div class="rotulo" style="${estilo({ left: x, top: y, "font-size": size, ...extra })}">${texto}</div>`;
    },
    // SVG solto no mundo (para desenhos em traço)
    svg({ id, x, y, w, h, vb, html, foco = true, classe = "" }) {
      return `<div ${id ? `id="${id}"` : ""} class="solto ${classe}${foco ? " foco" : ""}" style="${estilo({ left: x, top: y, width: w, height: h })}"><svg viewBox="${vb || `0 0 ${w} ${h}`}" width="100%" height="100%" style="overflow:visible">${html}</svg></div>`;
    },
    estrela(x, y, s = 1, cor = "#f2c230", extra = "") {
      return `<path transform="translate(${x},${y}) scale(${s})" fill="${cor}" d="${ESTRELA}" ${extra}/>`;
    },
    // Mapa de estados (fonte: @svg-maps/brazil, CC BY 4.0). Recorta o viewBox nos estados pedidos.
    // estados: [{uf, fill, stroke, id, classe}], recorte: lista de UFs para o enquadramento (padrão: todos os pedidos)
    mapa({ id, x, y, w, h, estados, recorte, margem = 0.08, fundo = "", foco = false, extraSvg = "" }) {
      const vbId = `vb-${id}`;
      const paths = estados.map((e) => `<path ${e.id ? `id="${e.id}"` : ""} class="${e.classe || ""}" data-uf="${e.uf}" d="${GEO.estados[e.uf].d}" fill="${e.fill || "rgba(160,60,40,.18)"}" stroke="${e.stroke || "#5a2a1a"}" stroke-width="${e.sw || 1.2}" stroke-linejoin="round" vector-effect="non-scaling-stroke" style="stroke-width:${e.swpx || 6}px"/>`).join("");
      B._pendentes.push({ id: vbId, recorte: recorte || estados.map((e) => e.uf), margem });
      return `<div ${id ? `id="${id}"` : ""} class="peca mapa ${fundo}${foco ? " foco" : ""}" style="${estilo({ left: x, top: y, width: w, height: h })}"><svg id="${vbId}" viewBox="${GEO.viewBox}" preserveAspectRatio="xMidYMid meet" width="100%" height="100%">${paths}${extraSvg}</svg></div>`;
    },
    _pendentes: [],
    // Depois do HTML estar no DOM: ajusta viewBox dos mapas ao recorte pedido.
    finalizar() {
      for (const p of B._pendentes) {
        const svg = document.getElementById(p.id); if (!svg) continue;
        let x0 = 1e9, y0 = 1e9, x1 = -1e9, y1 = -1e9;
        svg.querySelectorAll("path[data-uf]").forEach((el) => {
          if (!p.recorte.includes(el.dataset.uf)) return;
          const bb = el.getBBox(); x0 = Math.min(x0, bb.x); y0 = Math.min(y0, bb.y); x1 = Math.max(x1, bb.x + bb.width); y1 = Math.max(y1, bb.y + bb.height);
        });
        const mx = (x1 - x0) * p.margem, my = (y1 - y0) * p.margem;
        svg.setAttribute("viewBox", `${x0 - mx} ${y0 - my} ${x1 - x0 + 2 * mx} ${y1 - y0 + 2 * my}`);
        svg.dataset.bbox = JSON.stringify([x0, y0, x1, y1]);
      }
      B._pendentes = [];
    },
    // ponto (em coordenadas do SVG do mapa) por fração da caixa de um estado: fx 0..1 (oeste→leste), fy 0..1 (norte→sul)
    pontoEstado(svgId, uf, fx, fy) {
      const el = document.querySelector('#' + svgId + ' path[data-uf="' + uf + '"]'); const bb = el.getBBox();
      return [bb.x + bb.width * fx, bb.y + bb.height * fy];
    },
    // ponto mais a LESTE do contorno do estado na altura fy (0 = norte, 1 = sul): serve para cidades do litoral
    costaLeste(svgId, uf, fy) {
      const el = document.querySelector('#' + svgId + ' path[data-uf="' + uf + '"]'); const bb = el.getBBox();
      const alvo = bb.y + bb.height * fy, tol = bb.height * 0.015, L = el.getTotalLength();
      let melhor = null;
      for (let i = 0; i <= 4000; i++) { const q = el.getPointAtLength(L * i / 4000);
        if (Math.abs(q.y - alvo) < tol && (!melhor || q.x > melhor.x)) melhor = { x: q.x, y: q.y }; }
      return [melhor.x, melhor.y];
    },
    // coordenadas do SVG do mapa -> pixels dentro da div do mapa (respeita viewBox + preserveAspectRatio meet)
    svgParaDiv(svgId, [sx, sy]) {
      const svg = document.getElementById(svgId); const [vx, vy, vw, vh] = svg.getAttribute("viewBox").split(/[ ,]+/).map(Number);
      const W = svg.clientWidth || svg.parentNode.clientWidth, H = svg.clientHeight || svg.parentNode.clientHeight;
      const k = Math.min(W / vw, H / vh), ox = (W - vw * k) / 2, oy = (H - vh * k) / 2;
      return [ox + (sx - vx) * k, oy + (sy - vy) * k];
    },
    // posiciona um elemento (já no DOM, dentro da div do mapa) num ponto do mapa; ancora = centro
    colocarNoMapa(elId, svgId, ponto, dx = 0, dy = 0) {
      const [x, y] = B.svgParaDiv(svgId, ponto); const el = document.getElementById(elId);
      el.style.left = (x + dx) + "px"; el.style.top = (y + dy) + "px";
    },
  };
  window.B = B;
})();
