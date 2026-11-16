"use strict";

const ETAPAS = [["interesse", "Tenho interesse"], ["preparando", "Preparando proposta"], ["enviada", "Proposta enviada"],
  ["ganhou", "Ganhou"], ["perdeu", "Não ganhou"]];

function cartao(e, recarregar) {
  const { el } = Radar;
  const seletor = el("select", { "aria-label": "Mudar etapa" },
    ETAPAS.map(([v, n]) => el("option", { value: v, selected: v === e.status }, n)),
    el("option", { value: "" }, "Deixar de acompanhar"));
  seletor.addEventListener("change", async () => {
    try {
      if (seletor.value) await Radar.api("/funil", { metodo: "PUT", corpo: { id: e.id, status: seletor.value, nota: e.nota } });
      else await Radar.api("/funil?id=" + encodeURIComponent(e.id), { metodo: "DELETE" });
      recarregar();
    } catch (falha) { Radar.mostrarErro(document.getElementById("erro"), falha); }
  });
  return el("article", { class: "cartao-funil" },
    el("a", { href: "/ver?id=" + encodeURIComponent(e.id) }, Radar.legivel(e.objeto).slice(0, 110)),
    el("span", { class: "miudo" }, `${Radar.legivel(e.orgao)} · ${e.uf}`),
    el("span", {}, `Prazo: ${Radar.dataCurta(e.encerramento)} ${e.dias_restantes !== null ? "· " + Radar.emDias(e.dias_restantes) : ""}`),
    el("strong", {}, Radar.dinheiro(e.valor_estimado)),
    e.nota ? el("span", { class: "nota" }, e.nota) : null,
    seletor);
}

async function carregar() {
  const caixa = document.getElementById("funil");
  try {
    const { etapas } = await Radar.api("/funil");
    caixa.replaceChildren(...etapas.map(et => Radar.el("section", { class: "etapa", "aria-label": et.nome },
      Radar.el("h2", {}, Radar.el("span", {}, et.nome), Radar.el("span", {}, String(et.editais.length))),
      et.editais.length ? et.editais.map(e => cartao(e, carregar)) : Radar.el("p", { class: "miudo" }, "Nenhum edital aqui."))));
  } catch (falha) {
    if (falha.status === 401) return Radar.irPara("/entrar");
    Radar.mostrarErro(document.getElementById("erro"), falha);
  }
}

document.addEventListener("DOMContentLoaded", () => { Radar.ligarSair(); carregar(); });
