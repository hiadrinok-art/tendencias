/* cena.js — o que é específico DESTE documentário: desenhos gerados por código. Depois chama o motor. */
(function () {
  // Rede neural: camadas de nós ligados por traços (desenhados) e nós que "acendem".
  const svg = document.getElementById("rede-svg");
  const NS = "http://www.w3.org/2000/svg";
  const camadas = [4, 6, 6, 3];
  const W = 1700, H = 1100, mx = 180, my = 140;
  const pos = camadas.map((n, i) => Array.from({ length: n }, (_, j) => [mx + i * (W - 2 * mx) / (camadas.length - 1), my + (j + 0.5) * (H - 2 * my) / n]));
  const gL = document.createElementNS(NS, "g");
  gL.setAttribute("stroke", "#e9dcc0"); gL.setAttribute("stroke-width", "3"); gL.setAttribute("opacity", ".8");
  for (let i = 0; i < pos.length - 1; i++) pos[i].forEach((a) => pos[i + 1].forEach((b) => {
    const p = document.createElementNS(NS, "path"); p.setAttribute("class", "traco"); p.setAttribute("d", `M${a[0]},${a[1]} L${b[0]},${b[1]}`); gL.appendChild(p);
  }));
  svg.appendChild(gL);
  pos.flat().forEach(([x, y]) => {
    const base = document.createElementNS(NS, "circle");
    base.setAttribute("cx", x); base.setAttribute("cy", y); base.setAttribute("r", 34);
    base.setAttribute("fill", "#2a1a10"); base.setAttribute("stroke", "#e9dcc0"); base.setAttribute("stroke-width", 4);
    svg.appendChild(base);
    const g = document.createElementNS(NS, "g"); g.setAttribute("class", "no-luz");
    const halo = document.createElementNS(NS, "circle"); halo.setAttribute("cx", x); halo.setAttribute("cy", y); halo.setAttribute("r", 70); halo.setAttribute("fill", "rgba(255,200,110,.28)");
    const nucleo = document.createElementNS(NS, "circle"); nucleo.setAttribute("cx", x); nucleo.setAttribute("cy", y); nucleo.setAttribute("r", 30); nucleo.setAttribute("fill", "#ffd27a");
    g.appendChild(halo); g.appendChild(nucleo); svg.appendChild(g);
  });

  window.Documentario.montar(window.PLANO);
})();
