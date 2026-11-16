// Demonstração estática do Radar (GitHub Pages): sem contas e sem servidor.
// A escolha de ramo/estados fica só no localStorage do visitante.
"use strict";

const UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
  "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"];
const CHAVE = "radar-demo-filtros";
const { el } = Radar;

function agoraBrasilia() {
  const partes = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Sao_Paulo", year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23",
  }).formatToParts(new Date()).map(p => [p.type, p.value]));
  return `${partes.year}-${partes.month}-${partes.day}T${partes.hour}:${partes.minute}:${partes.second}`;
}

function diasAte(encerramento, hoje) {
  if (!encerramento) return null;
  const ms = Date.parse(encerramento.slice(0, 10)) - Date.parse(hoje.slice(0, 10));
  return Math.max(0, Math.round(ms / 864e5));
}

function semAcento(t) {
  return (t || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[\s\-_/]+/g, " ");
}

function linkSeguro(url) {
  try { return new URL(url).protocol === "https:" ? url : null; } catch (e) { return null; }
}

async function carregarDados() {
  const resposta = await fetch("dados/editais.json", { cache: "no-cache" });
  if (!resposta.ok) throw new Error("Não foi possível carregar os editais.");
  const dados = await resposta.json();
  const hoje = agoraBrasilia();
  dados.editais = dados.editais
    .filter(e => e.encerramento && e.encerramento > hoje)
    .map(e => ({ ...e, dias_restantes: diasAte(e.encerramento, hoje) }));
  dados.nomeRamo = Object.fromEntries(dados.ramos.map(r => [r.id, r.nome]));
  return dados;
}

function lerFiltros(ramosValidos) {
  let salvo = {};
  try { salvo = JSON.parse(localStorage.getItem(CHAVE) || "{}"); } catch (e) { salvo = {}; }
  const ramos = Array.isArray(salvo.ramos) ? salvo.ramos.filter(r => ramosValidos.includes(r)) : [];
  const ufs = Array.isArray(salvo.ufs) ? salvo.ufs.filter(u => UFS.includes(u)) : [];
  return {
    ramos: ramos.length ? ramos : ["ti"],
    ufs: ufs.length ? ufs : ["SP"],
    palavras: typeof salvo.palavras === "string" ? salvo.palavras.slice(0, 200) : "",
  };
}

function salvarFiltros(f) {
  try { localStorage.setItem(CHAVE, JSON.stringify(f)); } catch (e) { /* modo privado: segue sem salvar */ }
}

// ------------------------------------------------------------------ painel

function opcao(nome, valor, rotulo, marcado, classe = "") {
  return el("label", { class: `opcao ${classe}` },
    el("input", { type: "checkbox", name: nome, value: valor, checked: marcado }),
    el("span", {}, rotulo));
}

function linhaEdital(e) {
  const urgente = e.dias_restantes !== null && e.dias_restantes <= 3;
  const local = [Radar.legivel(e.orgao), [e.municipio, e.uf].filter(Boolean).join(", ")].filter(Boolean).join(" · ");
  return el("a", { class: "linha-edital", href: "edital.html?id=" + encodeURIComponent(e.id) },
    el("span", { class: "linha-edital__prazo" },
      el("strong", {}, Radar.dataCurta(e.encerramento)),
      el("span", { class: urgente ? "urgente" : null }, Radar.emDias(e.dias_restantes))),
    el("span", { class: "linha-edital__objeto" }, el("strong", {}, Radar.legivel(e.objeto)), el("span", {}, local)),
    el("span", { class: "linha-edital__valor" }, Radar.dinheiro(e.valor_estimado)));
}

async function iniciarPainel() {
  let dados;
  try {
    dados = await carregarDados();
  } catch (e) {
    document.getElementById("lista").replaceChildren(el("p", { class: "vazio" }, e.message));
    return;
  }
  const ramosValidos = dados.ramos.map(r => r.id);
  const filtros = lerFiltros(ramosValidos);
  let aba = "todos";

  const caixaRamos = document.getElementById("ramos");
  dados.ramos.forEach(r => caixaRamos.append(opcao("ramo", r.id, r.nome, filtros.ramos.includes(r.id))));
  const caixaUfs = document.getElementById("ufs");
  UFS.forEach(u => caixaUfs.append(opcao("uf", u, u, filtros.ufs.includes(u), "opcao--uf")));
  const palavras = document.getElementById("palavras");
  palavras.value = filtros.palavras;

  const gerado = new Date(dados.gerado_em);
  document.getElementById("atualizado").textContent =
    `Dados do PNCP atualizados em ${gerado.toLocaleDateString("pt-BR", { timeZone: "America/Sao_Paulo" })} às ${gerado.toLocaleTimeString("pt-BR", { timeZone: "America/Sao_Paulo", hour: "2-digit", minute: "2-digit" })}`;

  function marcados(nome) {
    return [...document.querySelectorAll(`input[name="${nome}"]:checked`)].map(i => i.value);
  }

  function desenhar() {
    filtros.ramos = marcados("ramo");
    filtros.ufs = marcados("uf");
    filtros.palavras = palavras.value.slice(0, 200);
    salvarFiltros(filtros);

    const ramos = new Set(filtros.ramos);
    const ufs = new Set(filtros.ufs);
    const termos = filtros.palavras.split(",").map(semAcento).map(t => t.trim()).filter(Boolean);
    const todos = dados.editais.filter(e => ufs.has(e.uf) &&
      (e.ramos.some(r => ramos.has(r)) || (termos.length && termos.some(t => semAcento(e.objeto).includes(t)))));

    const nomes = filtros.ramos.map(r => dados.nomeRamo[r]);
    const textoUfs = filtros.ufs.length === 27 ? "Todo o Brasil" : filtros.ufs.join(", ");
    document.getElementById("perfil").textContent =
      `${nomes.join(", ") || "Nenhum ramo"} · ${textoUfs || "nenhum estado"}`;

    const prazo = todos.filter(e => e.dias_restantes !== null && e.dias_restantes <= 10);
    const grandes = todos.filter(e => (e.valor_estimado || 0) >= 100000);
    document.getElementById("ind-total").textContent = todos.length.toLocaleString("pt-BR");
    document.getElementById("ind-valor").textContent = Radar.dinheiroCurto(todos.reduce((s, e) => s + (e.valor_estimado || 0), 0));
    document.getElementById("ind-prazo").textContent = todos.length
      ? `${Radar.dataCurta(todos[0].encerramento).split(",")[0]} · ${Radar.emDias(todos[0].dias_restantes)}` : "—";
    const rotulos = { todos: `Todos (${todos.length})`, prazo: `Prazo em até 10 dias (${prazo.length})`,
      grandes: `Acima de R$ 100 mil (${grandes.length})` };
    document.querySelectorAll(".aba").forEach(a => { a.textContent = rotulos[a.dataset.filtro]; });

    const visiveis = { todos, prazo, grandes }[aba];
    const lista = document.getElementById("lista");
    if (!filtros.ramos.length && !termos.length) {
      lista.replaceChildren(el("div", { class: "vazio" }, el("strong", {}, "Escolha pelo menos um ramo acima.")));
    } else if (!filtros.ufs.length) {
      lista.replaceChildren(el("div", { class: "vazio" }, el("strong", {}, "Escolha pelo menos um estado acima.")));
    } else if (!visiveis.length) {
      lista.replaceChildren(el("div", { class: "vazio" },
        el("strong", {}, "Nenhum edital aberto com esses filtros agora."),
        el("span", {}, "Tente incluir mais estados ou palavras-chave.")));
    } else {
      lista.replaceChildren(...visiveis.slice(0, 200).map(linhaEdital));
    }
    document.getElementById("rodape-lista").textContent = visiveis.length > 200
      ? `Mostrando os 200 com prazo mais próximo, de ${visiveis.length}.` : "";
  }

  caixaRamos.addEventListener("change", desenhar);
  caixaUfs.addEventListener("change", desenhar);
  let espera;
  palavras.addEventListener("input", () => { clearTimeout(espera); espera = setTimeout(desenhar, 250); });
  document.getElementById("todas-ufs").addEventListener("click", () => {
    caixaUfs.querySelectorAll("input").forEach(i => { i.checked = true; }); desenhar();
  });
  document.getElementById("nenhuma-uf").addEventListener("click", () => {
    caixaUfs.querySelectorAll("input").forEach(i => { i.checked = false; }); desenhar();
  });
  document.querySelectorAll(".aba").forEach(botao => botao.addEventListener("click", () => {
    aba = botao.dataset.filtro;
    document.querySelectorAll(".aba").forEach(a => a.setAttribute("aria-selected", String(a === botao)));
    desenhar();
  }));
  desenhar();
}

// ------------------------------------------------------------------ edital

async function iniciarEdital() {
  const erro = document.getElementById("erro");
  const id = new URLSearchParams(location.search).get("id") || "";
  let e;
  try {
    const dados = await carregarDados();
    e = dados.editais.find(x => x.id === id);
    if (!e) throw new Error("Edital não encontrado ou já encerrado.");
    e.nomesRamos = e.ramos.map(r => dados.nomeRamo[r]).filter(Boolean);
  } catch (falha) {
    document.getElementById("carregando").classList.add("oculto");
    return Radar.mostrarErro(erro, falha);
  }
  const texto = (alvo, valor) => { document.getElementById(alvo).textContent = valor; };
  const objeto = Radar.legivel(e.objeto);
  document.title = `${objeto.slice(0, 60)} — Radar de Editais`;
  const etiquetas = document.getElementById("etiquetas");
  [...e.nomesRamos.map(r => [r, "etiqueta etiqueta--teal"]), [e.modalidade, "etiqueta"]]
    .filter(([t]) => t).forEach(([t, c]) => etiquetas.append(el("span", { class: c }, t)));
  texto("titulo", objeto.length > 140 ? objeto.slice(0, 137).trimEnd() + "…" : objeto);
  texto("orgao", [Radar.legivel(e.orgao), e.unidade && e.unidade !== e.orgao && e.unidade !== "Unidade Única" ? Radar.legivel(e.unidade) : null,
    [e.municipio, e.uf].filter(Boolean).join(", ")].filter(Boolean).join(" · "));
  texto("objeto", objeto);
  texto("valor", Radar.dinheiro(e.valor_estimado));
  texto("publicado", Radar.dataHora(e.publicado));
  texto("abertura", Radar.dataHora(e.abertura));
  texto("encerramento", `${Radar.dataHora(e.encerramento)} · ${Radar.emDias(e.dias_restantes)}`);
  texto("controle", `Nº PNCP ${e.id}`);
  const origem = linkSeguro(e.link_origem);
  if (origem) {
    const a = document.getElementById("link-origem");
    a.href = origem;
    a.classList.remove("oculto");
  }
  const pncp = linkSeguro(e.link_pncp);
  if (pncp) document.getElementById("link-pncp").href = pncp;
  document.getElementById("carregando").classList.add("oculto");
  document.getElementById("conteudo").classList.remove("oculto");
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("ramos")) iniciarPainel();
  else if (document.getElementById("conteudo")) iniciarEdital();
});
