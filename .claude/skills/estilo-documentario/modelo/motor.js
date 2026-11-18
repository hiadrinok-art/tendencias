/* motor.js — motor genérico do estilo documentário para HyperFrames.
 *
 * Lê window.PLANO (gerado de plano.json por montar.py) e monta UMA timeline GSAP pausada:
 *   - câmera contínua (cúbica monotônica PCHIP pelos keyframes do plano: suave e sem passar do ponto);
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

  // Interpolação cúbica monotônica (PCHIP, Fritsch–Carlson) com knots = tempos.
  // Suave (derivada contínua) e SEM overshoot: a câmera nunca passa do keyframe nem mostra a borda do mundo.
  function tangentes(ts, vs) {
    const n = ts.length, h = [], d = [], m = new Array(n).fill(0);
    for (let i = 0; i < n - 1; i++) { h[i] = ts[i + 1] - ts[i]; d[i] = (vs[i + 1] - vs[i]) / h[i]; }
    if (n === 2) { m[0] = m[1] = d[0]; return m; }
    for (let i = 1; i < n - 1; i++) {
      if (d[i - 1] * d[i] <= 0) { m[i] = 0; continue; }
      const w1 = 2 * h[i] + h[i - 1], w2 = h[i] + 2 * h[i - 1];
      m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
    }
    const ponta = (h0, h1, d0, d1) => { let v = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1);
      if (Math.sign(v) !== Math.sign(d0)) v = 0; else if (Math.sign(d0) !== Math.sign(d1) && Math.abs(v) > Math.abs(3 * d0)) v = 3 * d0; return v; };
    m[0] = ponta(h[0], h[1], d[0], d[1]);
    m[n - 1] = ponta(h[n - 2], h[n - 3], d[n - 2], d[n - 3]);
    return m;
  }
  const cacheTan = new Map();
  function splineAt(ts, vs, t) {
    const n = ts.length;
    if (t <= ts[0]) return vs[0];
    if (t >= ts[n - 1]) return vs[n - 1];
    let m = cacheTan.get(vs); if (!m) { m = tangentes(ts, vs); cacheTan.set(vs, m); }
    let i = 0; while (ts[i + 1] < t) i++;
    const h = ts[i + 1] - ts[i], u = (t - ts[i]) / h, u2 = u * u, u3 = u2 * u;
    return (2 * u3 - 3 * u2 + 1) * vs[i] + (u3 - 2 * u2 + u) * h * m[i] + (-2 * u3 + 3 * u2) * vs[i + 1] + (u3 - u2) * h * m[i + 1];
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
    // Keyframes podem mirar elementos: x/y = "#id" ou "#id+120" / "#id-80" (centro do elemento no mundo).
    function coord(v, eixo) {
      if (typeof v !== "string") return v;
      // 1º: o texto inteiro é um id existente (ex.: "#folha-1535"); 2º: "#id+120" / "#id-80" (deslocamento)
      let el = $(v.slice(1)), d = 0;
      if (!el) {
        const m = v.match(/^#([\w-]+?)\s*([+-]\s*\d+(?:\.\d+)?)$/);
        if (!m) throw new Error("câmera mira elemento inexistente: " + v);
        el = $(m[1]); d = parseFloat(m[2].replace(/\s/g, ""));
        if (!el) throw new Error("câmera mira elemento inexistente: " + v);
      }
      // posição de LAYOUT (offsetLeft/Top somados até o #mundo): não depende da escala da página nem de transforms
      let x = el.offsetWidth / 2, y = el.offsetHeight / 2, n = el;
      if (el instanceof SVGElement) {
        // coordenadas do desenho -> pixels da div que contém o <svg> (viewBox + preserveAspectRatio "meet")
        const svg = el.ownerSVGElement || el, bb = el.getBBox(), cont = svg.parentNode;
        const vb = (svg.getAttribute("viewBox") || `0 0 ${cont.offsetWidth} ${cont.offsetHeight}`).split(/[ ,]+/).map(Number);
        const W = cont.offsetWidth, H = cont.offsetHeight, k = Math.min(W / vb[2], H / vb[3]);
        x = (W - vb[2] * k) / 2 + (bb.x + bb.width / 2 - vb[0]) * k; y = (H - vb[3] * k) / 2 + (bb.y + bb.height / 2 - vb[1]) * k; n = cont;
      }
      while (n && n.id !== "mundo") { x += n.offsetLeft; y += n.offsetTop; n = n.offsetParent; }
      return (eixo === "x" ? x : y) + d;
    }
    const ks = P.camera.map((k) => [k[0], coord(k[1], "x"), coord(k[2], "y"), k[3]]);
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
    let focoAtual = null;
    function focar(el, t) {
      acesos.filter((o) => o !== el).forEach((o) => tl.to(o, { opacity: OPACIDADE_APAGADO, duration: 0.45, ease: "sine.out" }, t));
      // um destaque que JÁ foi aceso e depois apagado volta a 100% quando recebe o foco de novo
      if (acesos.includes(el) && focoAtual !== el) tl.to(el, { opacity: 1, duration: 0.45, ease: "sine.out" }, t);
      if (!acesos.includes(el)) acesos.push(el);
      focoAtual = el;
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
      mover(b, el, t) {
        // b.para = {x, y, rotation}: deslocamento relativo à posição atual
        const d = b.para || {};
        tl.set(el, { opacity: 1 }, t);
        tl.to(el, { x: "+=" + (d.x || 0), y: "+=" + (d.y || 0), rotation: "+=" + (d.rotation || 0), duration: b.duracao || 1.2, ease: "power2.inOut" }, t);
      },
      apagar(b, el, t) {
        tl.to(el, { opacity: 0, duration: b.duracao || 0.8, ease: "sine.inOut" }, t);
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
      // b.foco: qual elemento fica aceso (padrão: o próprio alvo). "circular" e "apagar" não mudam o foco sozinhos.
      const foco = b.foco ? $(b.foco) : ((b.acao === "circular" || b.acao === "apagar") ? null : el);
      if (foco) focar(foco, t);
      acoes[b.acao](b, el, t);
      eventos.push({ t: +t.toFixed(3), tipo: b.acao, alvo: b.alvo, beat: b.id, gatilho: b.gatilho });
    });

    // ---- grão e cintilação (determinísticos)
    // fades de entrada/saída configuráveis (filme em várias cenas: use valores curtos, ex. 0.4)
    const fi = P.fade_ini ?? 0.6, ff = P.fade_fim ?? 0.8;
    const rnd = semente(7);
    for (let t = 0; t < P.duracao; t += 1 / 12) {
      tl.set("#grao", { x: Math.floor(rnd() * 200 - 100), y: Math.floor(rnd() * 200 - 100) }, t);
      const f = rnd();
      if (t > fi + 0.05 && t < P.duracao - ff - 0.05) tl.set("#pisca", { opacity: 0.02 + f * 0.05 }, t);
    }
    // fade de entrada e saída
    if (fi > 0) tl.fromTo("#pisca", { opacity: 1 }, { opacity: 0.04, duration: fi, ease: "sine.out" }, 0);
    if (ff > 0) tl.to("#pisca", { opacity: 1, duration: ff, ease: "sine.in" }, P.duracao - ff);

    window.__timelines = window.__timelines || {};
    window.__timelines["root"] = tl;
    window.__linhaDoTempo = eventos;
    return tl;
  }

  window.Documentario = { montar, OPACIDADE_APAGADO };
})();
