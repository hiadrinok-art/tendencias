// checar_enquadramento.js — confere, para CADA destaque do plano, se o elemento aceso está na tela.
// Uso: node checar_enquadramento.js <cena>/index.html
// Para cada beat mede o elemento de foco (b.foco || b.alvo) em t+0.4 s e em t+1.2 s (ou pouco antes do próximo beat):
//   - visível < 85% da área  -> "CORTADO / FORA DO QUADRO"
//   - altura < 12% da tela    -> "PEQUENO DEMAIS"
//   - fica na tela < 1,0 s    -> "SAI CEDO DEMAIS"
// Sai com código 1 se houver problema.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  const erros = []; p.on('pageerror', e => erros.push('ERRO JS: ' + e.message));
  await p.goto('file://' + require('path').resolve(process.argv[2])); await p.waitForTimeout(1200);
  const rel = await p.evaluate(() => {
    const tl = window.__timelines.root, P = window.PLANO, root = document.getElementById('root').getBoundingClientRect();
    const beats = P.beats.slice().sort((a, b) => a.t - b.t), out = [];
    // caixa da peça INCLUINDO o que transborda dela (legendas, notas presas): uma legenda cortada também é erro
    const caixa = (el) => { let r = el.getBoundingClientRect(), L = r.left, T = r.top, R = r.right, Bt = r.bottom;
      el.querySelectorAll("*").forEach((c) => { const q = c.getBoundingClientRect(); if (q.width * q.height < 4) return;
        const st = getComputedStyle(c); if (st.opacity === "0" || st.visibility === "hidden") return;
        L = Math.min(L, q.left); T = Math.min(T, q.top); R = Math.max(R, q.right); Bt = Math.max(Bt, q.bottom); });
      return { left: L, top: T, right: R, bottom: Bt, width: R - L, height: Bt - T }; };
    const medir = (el) => { const r = caixa(el);
      const ix = Math.max(0, Math.min(r.right, root.right) - Math.max(r.left, root.left)), iy = Math.max(0, Math.min(r.bottom, root.bottom) - Math.max(r.top, root.top));
      const cobre = (ix * iy) / (root.width * root.height);   // close-up: o elemento ocupa a tela
      return { vis: cobre >= 0.55 ? 1 : (ix * iy) / Math.max(1, r.width * r.height), alt: r.height / root.height, larg: r.width / root.width }; };
    // peça que de fato anima: o círculo (circular), o foco (apagar), ou o próprio alvo; elementos sem tamanho usam o 1º filho com tamanho
    const peca = (bt) => { let el = bt.acao === "circular" ? document.getElementById(bt.circulo)
        : bt.acao === "apagar" ? document.getElementById(bt.foco || bt.alvo) : document.getElementById(bt.alvo);
      if (el && el.getBoundingClientRect().width * el.getBoundingClientRect().height < 100)
        el = [...el.querySelectorAll("*")].find((c) => c.getBoundingClientRect().width * c.getBoundingClientRect().height >= 100) || el;
      return el; };
    // foco aninhado: um destaque DENTRO de outro que já acendeu faz o de fora apagar levando o de dentro junto
    const acesos = [];
    beats.forEach((bt) => { const f = document.getElementById(bt.foco || bt.alvo); if (!f || ["circular", "apagar"].includes(bt.acao) && !bt.foco) return;
      for (const a of acesos) if (a !== f && a.contains(f)) out.push(`beat ${bt.id} '${bt.gatilho}': FOCO ANINHADO — #${f.id} está dentro de #${a.id}, que já acendeu (use "foco": "${a.id}" ou outro elemento)`);
      if (!acesos.includes(f)) acesos.push(f); });
    beats.forEach((bt, i) => {
      const el = peca(bt), id = el ? (el.id || bt.alvo) : bt.alvo; if (!el) { out.push(`beat ${bt.id}: elemento de ${bt.alvo} não existe`); return; }
      const prox = i + 1 < beats.length ? beats[i + 1].t : P.duracao;
      const t1 = bt.t + 0.4, t2 = Math.min(bt.t + 1.2, prox - 0.1); let fica = 0;
      for (let t = bt.t; t < Math.min(prox, bt.t + 3) ; t += 0.1) { tl.seek(t); if (medir(el).vis >= 0.85) fica += 0.1; }
      if (bt.panoramica) return;   // percurso proposital por um elemento grande (ex.: mapa do litoral ao sertão)
      for (const t of [t1, t2]) { tl.seek(t); const m = medir(el);
        // todo TEXTO dentro do destaque precisa estar ≥ 90% visível (legenda cortada é erro)
        for (const c of [el, ...el.querySelectorAll("*")]) {
          if (![...c.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) continue;
          const st = getComputedStyle(c); if (st.opacity === "0") continue;
          const q = c.getBoundingClientRect(); if (q.width * q.height < 50) continue;
          const ix = Math.max(0, Math.min(q.right, root.right) - Math.max(q.left, root.left)), iy = Math.max(0, Math.min(q.bottom, root.bottom) - Math.max(q.top, root.top));
          const v = (ix * iy) / (q.width * q.height);
          if (v > 0 && v < 0.9) { out.push(`beat ${bt.id} '${bt.gatilho}' em ${t.toFixed(2)}s: TEXTO CORTADO "${c.textContent.trim().slice(0, 30)}" (${Math.round(v * 100)}% visível)`); break; }
        }
        if (m.vis < 0.85) out.push(`beat ${bt.id} '${bt.gatilho}' #${id} em ${t.toFixed(2)}s: CORTADO/FORA (${Math.round(m.vis * 100)}% visível)`);
        else if (m.alt < 0.12 && m.larg < 0.12) out.push(`beat ${bt.id} '${bt.gatilho}' #${id} em ${t.toFixed(2)}s: PEQUENO DEMAIS (${Math.round(m.alt * 100)}% da altura)`); }
      if (fica < Math.min(1.0, prox - bt.t - 0.15)) out.push(`beat ${bt.id} '${bt.gatilho}' #${id}: SAI CEDO DEMAIS (só ${fica.toFixed(1)} s na tela)`);
    });
    return out;
  });
  const tudo = erros.concat(rel);
  console.log(tudo.length ? tudo.join('\n') : 'enquadramento OK: todos os destaques inteiros, legíveis e na tela por tempo suficiente');
  await b.close(); process.exit(tudo.length ? 1 : 0);
})();
