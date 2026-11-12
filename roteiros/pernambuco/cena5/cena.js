/* cena.js — Cena 5 (1817): desenhos gerados por código. Depois chama o motor. */
(function () {
  // 75 traços de calendário (um por dia da república), desenhados em sequência.
  const g = document.getElementById("tracos75");
  const NS = "http://www.w3.org/2000/svg";
  for (let i = 0; i < 75; i++) {
    const x = 120 + i * (1560 / 74);
    const p = document.createElementNS(NS, "path");
    p.setAttribute("class", "traco");
    p.setAttribute("d", `M${x.toFixed(1)},${i % 5 === 4 ? 230 : 255} L${x.toFixed(1)},${i % 5 === 4 ? 350 : 325}`);
    g.appendChild(p);
  }
  window.Documentario.montar(window.PLANO);
})();
