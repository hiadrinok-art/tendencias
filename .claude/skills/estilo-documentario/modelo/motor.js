/* motor.js — motor genérico do estilo documentário para HyperFrames.
 *
 * Lê window.PLANO (gerado de plano.json por montar.py) e monta UMA timeline GSAP pausada:
 *   - câmera contínua (spline Catmull-Rom não uniforme pelos keyframes do plano, sem paradas secas);
 *   - um destaque aceso por vez (os anteriores apagam para OPACIDADE_APAGADO);
 *   - ações disparadas no tempo exato da palavra-gatilho (+ atraso_narracao);
 *   - grão de filme e tremor de câmera determinísticos.
 * Ao final escreve window.__linhaDoTempo (lista de eventos) para conferir_sincronia.py.
 */
(function () {
  const OPACIDADE_APAGADO = 0.38;
  const PASSO_CAMERA = 1 / 15;     // amostragem da spline (s)
  const W = 1920, H = 1080;

  // ---------- utilidades ----------
  function semente(s) { return function () { s = (s * 1664525 + 1013904223) % 4294967296; return s / 4294967296; }; }
  const $ = (id) => document.getElementById(id);

  // Catmull-Rom não uniforme (Barry–Goldman) sobre knots = tempos.
  function splineAt(ts, vs, t) {
    const n = ts.length;
    if (t <= ts[0]) return vs[0];
    if (t >= ts[n - 1]) return vs[n - 1];
    let i = 0; while (ts[i + 1] < t) i++;
    const t1 = ts[i], t2 = ts[i + 1];
    const p1 = vs[i], p2 = vs[i + 1];
    const t0 = i > 0 ? ts[i - 1] : t1 - (t2 - t1), p0 = i > 0 ? vs[i - 1] : p1 - (p2 - p1);
    const t3 = i + 2 < n ? ts[i + 2] : t2 + (t2 - t1), p3 = i + 2 < n ? vs[i + 2] : p2 + (p2 - p1);
    const L = (a, b, ta, tb) => (tb - t) / (tb - ta) * a + (t - ta) / (tb - ta) * b;
    const a1 = L(p0, p1, t0, t1), a2 = L(p1, p2, t1, t2), a3 = L(p2, p3, t2, t3);
    const b1 = L(a1, a2, t0, t2), b2 = L(a2, a3, t1, t3);
    return L(b1, b2, t1, t2);
  }

  function prepararTracos(el) {
    const tracos = el.matches && el.matches(".traco") ? [el] : Array.from(el.querySelectorAll(".traco"));
    tracos.forEach((p) => {
      const len = Math.ceil(p.getTotalLength ? p.getTotalLength() : 1000) + 2;
      p.style.strokeDasharray = len; p.style.strokeDashoffset = len; p.dataset.len = len;
    });
    return tracos;
  }

  function prepararLetras(el) {
    const txt = el.dataset.texto != null ? el.dataset.texto : null;
    if (txt == null) return [];
    el.textContent = "";
    return Array.from(txt).map((c) => { const s = document.createElement("span"); s.className = "letra"; s.textContent = c; el.appendChild(s); return s; });
  }

  function letrasDeTexto(el) {
    // Para elementos com HTML interno (ex.: palavra circulada): envolve cada caractere de nós de texto.
    const letras = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const nos = []; while (walker.nextNode()) nos.push(walker.currentNode);
    nos.forEach((n) => {
      if (n.parentNode.closest("svg")) return;
      const frag = document.createDocumentFragment();
      Array.from(n.textContent).forEach((c) => { const s = document.createElement("span"); s.className = "letra"; s.textContent = c; frag.appendChild(s); letras.push(s); });
      n.parentNode.replaceChild(frag, n);
    });
    return letras;
  }

  // ---------- montagem ----------
  function montar(P) {
    const tl = gsap.timeline({ paused: true });
    const off = P.atraso_narracao || 0;
    const eventos = [];
    const acesos = [];   // elementos que já apareceram

    // ---- câmera
    const ks = P.camera;
    const ts = ks.map((k) => k[0] + off);
    const xs = ks.map((k) => k[1]), ys = ks.map((k) => k[2]), zs = ks.map((k) => Math.log(k[3]));
    const mundo = $("mundo");
    const posCam = (t) => { const z = Math.exp(splineAt(ts, zs, t)); return { x: W / 2 - splineAt(ts, xs, t) * z, y: H / 2 - splineAt(ts, ys, t) * z, scale: z }; };
    tl.set(mundo, Object.assign({ transformOrigin: "0 0" }, posCam(0)), 0);
    for (let t = 0; t < P.duracao - 1e-6; t += PASSO_CAMERA) {
      const t2 = Math.min(P.duracao, t + PASSO_CAMERA);
      tl.to(mundo, Object.assign({ duration: t2 - t, ease: "none" }, posCam(t2)), t);
    }

    // ---- foco: um destaque aceso por vez
    function focar(el, t) {
      acesos.filter((o) => o !== el).forEach((o) => tl.to(o, { opacity: OPACIDADE_APAGADO, duration: 0.45, ease: "sine.out" }, t));
      if (!acesos.includes(el)) acesos.push(el);
      eventos.push({ t: +t.toFixed(3), tipo: "foco", alvo: el.id });
    }

    // ---- ações
    const acoes = {
      datilografar(b, el, t) {
        let letras = el.dataset.texto != null ? prepararLetras(el) : letrasDeTexto(el);
        const dt = Math.min(0.07, 0.9 / Math.max(1, letras.length));
        tl.set(el, { opacity: 1 }, t);
        letras.forEach((s, i) => tl.set(s, { opacity: 1 }, t + i * dt));
      },
      cair(b, el, t) {
        const r = gsap.getProperty(el, "rotation") || 0;
        tl.fromTo(el, { opacity: 0, y: -140, scale: 1.25, rotation: r + 7 },
                      { opacity: 1, y: 0, scale: 1, rotation: r, duration: 0.55, ease: "power3.out" }, t - 0.25);
      },
      alfinete(b, el, t) {
        const cab = el.querySelector(".cabeca"), nome = el.querySelector("[data-texto]");
        tl.set(el, { opacity: 1 }, t - 0.2);
        tl.fromTo(cab, { scale: 2.6, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.25, ease: "power4.in" }, t - 0.2);
        if (nome) { const ls = prepararLetras(nome); ls.forEach((s, i) => tl.set(s, { opacity: 1 }, t + 0.15 + i * 0.05)); }
      },
      desenhar(b, el, t) {
        const tracos = prepararTracos(el);
        tl.set(el, { opacity: 1 }, t);
        const dur = Math.max(0.5, Math.min(1.8, (b.fim || t + 1.6) - t));
        tracos.forEach((p, i) => tl.to(p, { strokeDashoffset: 0, duration: dur * 0.6, ease: "sine.inOut" }, t + i * (dur * 0.4 / Math.max(1, tracos.length))));
      },
      circular(b, el, t) {
        const c = $(b.circulo); prepararTracos(c);
        tl.to(c, { strokeDashoffset: 0, duration: 0.55, ease: "power2.out" }, t);
      },
      carimbar(b, el, t) {
        // o impacto acontece exatamente em t
        tl.fromTo(el, { opacity: 0, scale: 2.4, rotation: 4 }, { opacity: 1, scale: 1, rotation: -6, duration: 0.18, ease: "power4.in" }, t - 0.18);
        const tr = $("tremor");
        [[14, -9], [-11, 7], [7, -4], [-3, 2], [0, 0]].forEach(([x, y], i) => tl.to(tr, { x, y, duration: 0.045, ease: "none" }, t + i * 0.045));
      },
      congelar(b, el, t) {
        tl.fromTo(el, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "sine.out" }, t - 0.1);
      },
      acender(b, el, t) {
        const pre = b.pre != null ? b.pre + off : t - 0.7;
        const tracos = prepararTracos(el);
        tl.set(el, { opacity: 1 }, pre);
        tracos.forEach((p, i) => tl.to(p, { strokeDashoffset: 0, duration: 0.5, ease: "sine.out" }, pre + (i / tracos.length) * Math.max(0.2, t - pre - 0.4)));
        const nos = el.querySelectorAll(".no-luz");
        nos.forEach((n, i) => tl.fromTo(n, { opacity: 0, scale: 0.4, transformOrigin: "50% 50%" }, { opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)" }, t + i * 0.025));
      },
      reacender(b, el, t) {
        tl.fromTo(el, { opacity: OPACIDADE_APAGADO }, { opacity: 1, duration: 0.5, ease: "sine.out" }, t);
        if (b.circulo) {
          const c = $(b.circulo);
          tl.set(c, { strokeDashoffset: c.dataset.len }, t);
          tl.to(c, { strokeDashoffset: 0, duration: 0.6, ease: "power2.out" }, t + 0.1);
        }
      },
    };

    // fim de cada beat = início do próximo
    const bs = P.beats.slice().sort((a, b) => a.t - b.t);
    bs.forEach((b, i) => { b.fim = (i + 1 < bs.length ? bs[i + 1].t : P.duracao - off) + off; });

    bs.forEach((b) => {
      const el = $(b.alvo); const t = b.t + off;
      if (!el) throw new Error("alvo não encontrado: " + b.alvo);
      if (!acoes[b.acao]) throw new Error("ação desconhecida: " + b.acao);
      if (b.acao !== "circular") focar(el, t);
      acoes[b.acao](b, el, t);
      eventos.push({ t: +t.toFixed(3), tipo: b.acao, alvo: b.alvo, beat: b.id, gatilho: b.gatilho });
    });

    // ---- grão e cintilação (determinísticos)
    const rnd = semente(7);
    for (let t = 0; t < P.duracao; t += 1 / 12) {
      tl.set("#grao", { x: Math.floor(rnd() * 200 - 100), y: Math.floor(rnd() * 200 - 100) }, t);
      const f = rnd();
      if (t > 0.65 && t < P.duracao - 0.85) tl.set("#pisca", { opacity: 0.02 + f * 0.05 }, t);
    }
    // fade de entrada e saída
    tl.fromTo("#pisca", { opacity: 1 }, { opacity: 0.04, duration: 0.6, ease: "sine.out" }, 0);
    tl.to("#pisca", { opacity: 1, duration: 0.8, ease: "sine.in" }, P.duracao - 0.8);

    window.__timelines = window.__timelines || {};
    window.__timelines["root"] = tl;
    window.__linhaDoTempo = eventos;
    return tl;
  }

  window.Documentario = { montar, OPACIDADE_APAGADO };
})();
