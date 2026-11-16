"use strict";

const { el } = Radar;
const NOMES_RAMOS = {};
let resumo = null;
let busca = "";
const NOMES_STATUS = { interesse: "Tenho interesse", preparando: "Preparando proposta", enviada: "Proposta enviada",
  ganhou: "Ganhou", perdeu: "Não ganhou" };

function linhaEdital(e) {
  const urgente = e.dias_restantes !== null && e.dias_restantes <= 3;
  const local = [Radar.legivel(e.orgao), [e.municipio, e.uf].filter(Boolean).join(", ")].filter(Boolean).join(" · ");
  return el("a", { class: "linha-edital", href: "/ver?id=" + encodeURIComponent(e.id) },
    el("span", { class: "linha-edital__prazo" },
      el("strong", {}, Radar.dataCurta(e.encerramento)),
      el("span", { class: urgente ? "urgente" : null }, Radar.emDias(e.dias_restantes))),
    el("span", { class: "linha-edital__objeto" },
      el("strong", {}, Radar.legivel(e.objeto)),
      el("span", {}, local),
      e.acompanhamento ? el("span", { class: "selo-acomp" }, NOMES_STATUS[e.acompanhamento] || "") : null),
    el("span", { class: "linha-edital__valor" }, Radar.dinheiro(e.valor_estimado)));
}

function preencherResumo(r) {
  document.getElementById("ind-total").textContent = r.total.toLocaleString("pt-BR");
  document.getElementById("ind-valor").textContent = Radar.dinheiroCurto(r.valor_somado);
  document.getElementById("ind-prazo").textContent = r.proximo_prazo
    ? `${Radar.dataCurta(r.proximo_prazo).split(",")[0]} · ${Radar.emDias(r.proximo_em_dias)}`
    : "—";
  const rotulos = { todos: `Todos (${r.total})`, prazo: `Prazo em até 10 dias (${r.prazo_10_dias})`,
    grandes: `Acima de R$ 100 mil (${r.acima_100_mil})` };
  document.querySelectorAll(".aba").forEach(a => { a.textContent = rotulos[a.dataset.filtro]; });
}

async function carregar(filtro) {
  const lista = document.getElementById("lista");
  lista.replaceChildren(el("p", { class: "carregando vazio" }, "Buscando editais…"));
  try {
    const dados = await Radar.api("/editais?filtro=" + encodeURIComponent(filtro) + "&q=" + encodeURIComponent(busca));
    if (!resumo) { resumo = dados.resumo; preencherResumo(resumo); }
    document.querySelector(".cabeca-painel h1").textContent = busca
      ? `Resultados para “${busca}”` : "Editais abertos no seu ramo";
    if (!dados.editais.length) {
      lista.replaceChildren(el("div", { class: "vazio" },
        el("strong", {}, "Nenhum edital aberto com esses filtros agora."),
        el("span", {}, "Novos editais entram todos os dias. Você também pode incluir mais estados ou palavras-chave.")));
    } else {
      lista.replaceChildren(...dados.editais.map(linhaEdital));
    }
    const total = filtro === "todos" ? dados.resumo.total : dados.editais.length;
    document.getElementById("rodape-lista").textContent = total > dados.editais.length
      ? `Mostrando os ${dados.editais.length} com prazo mais próximo, de ${total}.` : "";
  } catch (e) {
    if (e.status === 401) return Radar.irPara("/entrar");
    Radar.mostrarErro(document.getElementById("erro"), e);
    lista.replaceChildren();
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  Radar.ligarSair();
  try {
    const [eu, ramos] = await Promise.all([Radar.api("/eu"), Radar.api("/ramos")]);
    ramos.forEach(r => { NOMES_RAMOS[r.id] = r.nome; });
    const ufs = eu.ufs.length === 27 ? "Todo o Brasil" : eu.ufs.join(", ");
    document.getElementById("perfil").textContent = `${eu.ramos.map(r => NOMES_RAMOS[r] || r).join(", ")} · ${ufs}`;
  } catch (e) {
    if (e.status === 401) return Radar.irPara("/entrar");
    Radar.mostrarErro(document.getElementById("erro"), e);
    return;
  }

  document.querySelectorAll(".aba").forEach(aba => aba.addEventListener("click", () => {
    document.querySelectorAll(".aba").forEach(a => a.setAttribute("aria-selected", String(a === aba)));
    carregar(aba.dataset.filtro);
  }));
  const campo = document.getElementById("q");
  const limpar = document.getElementById("limpar-busca");
  const recomecar = () => {
    resumo = null;
    document.querySelectorAll(".aba").forEach(a => a.setAttribute("aria-selected", String(a.dataset.filtro === "todos")));
    carregar("todos");
  };
  document.getElementById("busca").addEventListener("submit", evento => {
    evento.preventDefault();
    busca = campo.value.trim().slice(0, 100);
    limpar.classList.toggle("oculto", !busca);
    recomecar();
  });
  limpar.addEventListener("click", () => {
    campo.value = ""; busca = ""; limpar.classList.add("oculto"); recomecar();
  });
  carregar("todos");
});
