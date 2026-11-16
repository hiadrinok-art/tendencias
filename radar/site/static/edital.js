"use strict";

function texto(id, valor) { document.getElementById(id).textContent = valor; }

// Só abre links https para pncp.gov.br ou que a API já validou (ver coletor.link_seguro).
function linkSeguro(url) {
  try { return new URL(url).protocol === "https:" ? url : null; } catch (e) { return null; }
}

function marcarVoto(serve) {
  document.getElementById("voto-sim").setAttribute("aria-pressed", String(serve === true));
  document.getElementById("voto-nao").setAttribute("aria-pressed", String(serve === false));
  if (serve !== null) texto("h-voto", "Obrigado! Isso vai afinar os próximos editais que mostramos.");
}

function iniciarAcompanhamento(e) {
  const status = document.getElementById("status");
  const nota = document.getElementById("nota");
  const msg = document.getElementById("acomp-msg");
  if (e.acompanhamento) {
    status.value = e.acompanhamento.status;
    nota.value = e.acompanhamento.nota;
  }
  document.getElementById("salvar-acomp").addEventListener("click", async () => {
    msg.textContent = "Salvando…";
    try {
      if (status.value) {
        await Radar.api("/funil", { metodo: "PUT", corpo: { id: e.id, status: status.value, nota: nota.value } });
        msg.textContent = "Salvo. Veja em Acompanhando.";
      } else {
        await Radar.api("/funil?id=" + encodeURIComponent(e.id), { metodo: "DELETE" });
        msg.textContent = "Você deixou de acompanhar este edital.";
      }
    } catch (falha) {
      msg.textContent = falha.message;
    }
  });
}

async function carregarItens(id) {
  const caixa = document.getElementById("itens");
  try {
    const { lista } = await Radar.api("/edital/detalhes?tipo=itens&id=" + encodeURIComponent(id));
    if (!lista.length) { caixa.replaceChildren(Radar.el("p", { class: "miudo" }, "O PNCP não traz itens para este edital.")); return; }
    const { el } = Radar;
    const qtd = n => n === null ? "—" : n.toLocaleString("pt-BR");
    caixa.replaceChildren(el("table", { class: "tabela-itens" },
      el("thead", {}, el("tr", {}, el("th", {}, "Nº"), el("th", {}, "Descrição"), el("th", { class: "num" }, "Qtd."),
        el("th", { class: "num" }, "Valor unitário"), el("th", { class: "num" }, "Total"))),
      el("tbody", {}, lista.map(i => el("tr", {},
        el("td", {}, i.numero ?? ""),
        el("td", {}, Radar.legivel(i.descricao), i.exclusivo_me_epp ? el("div", {}, el("span", { class: "selo-me" }, "Exclusivo ME/EPP")) : null),
        el("td", { class: "num" }, `${qtd(i.quantidade)} ${i.unidade}`.trim()),
        el("td", { class: "num" }, Radar.dinheiro(i.valor_unitario)),
        el("td", { class: "num" }, Radar.dinheiro(i.valor_total)))))));
  } catch (falha) {
    caixa.replaceChildren(Radar.el("p", { class: "miudo" }, falha.message));
  }
}

async function carregarDocumentos(id) {
  const lista = document.getElementById("documentos");
  try {
    const { lista: docs } = await Radar.api("/edital/detalhes?tipo=arquivos&id=" + encodeURIComponent(id));
    if (!docs.length) { lista.replaceChildren(Radar.el("li", { class: "miudo" }, "Nenhum documento publicado no PNCP.")); return; }
    lista.replaceChildren(...docs.map(d => {
      const url = linkSeguro(d.url);
      return Radar.el("li", {},
        url ? Radar.el("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, d.titulo) : d.titulo,
        Radar.el("span", { class: "miudo" }, d.tipo));
    }));
  } catch (falha) {
    lista.replaceChildren(Radar.el("li", { class: "miudo" }, falha.message));
  }
}

document.addEventListener("DOMContentLoaded", async () => {
  Radar.ligarSair();
  const erro = document.getElementById("erro");
  const id = new URLSearchParams(location.search).get("id") || "";
  let e;
  try {
    e = await Radar.api("/edital?id=" + encodeURIComponent(id));
  } catch (falha) {
    if (falha.status === 401) return Radar.irPara("/entrar");
    document.getElementById("carregando").classList.add("oculto");
    return Radar.mostrarErro(erro, falha);
  }

  document.title = `${e.objeto.slice(0, 60)} — Radar de Editais`;
  const etiquetas = document.getElementById("etiquetas");
  [...e.ramos.map(r => [r, "etiqueta etiqueta--teal"]), [e.modalidade, "etiqueta"]]
    .filter(([t]) => t).forEach(([t, c]) => etiquetas.append(Radar.el("span", { class: c }, t)));

  const objeto = Radar.legivel(e.objeto);
  const titulo = objeto.length > 140 ? objeto.slice(0, 137).trimEnd() + "…" : objeto;
  texto("titulo", titulo);
  texto("orgao", [Radar.legivel(e.orgao), e.unidade && e.unidade !== e.orgao && e.unidade !== "Unidade Única" ? Radar.legivel(e.unidade) : null, [e.municipio, e.uf].filter(Boolean).join(", ")]
    .filter(Boolean).join(" · "));
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

  marcarVoto(e.avaliacao);
  document.getElementById("link-agenda").href = "/edital/agenda.ics?id=" + encodeURIComponent(e.id);
  iniciarAcompanhamento(e);
  carregarItens(e.id);
  carregarDocumentos(e.id);
  for (const [botao, serve] of [["voto-sim", true], ["voto-nao", false]]) {
    document.getElementById(botao).addEventListener("click", async () => {
      try {
        await Radar.api("/edital/avaliacao", { metodo: "POST", corpo: { id: e.id, serve } });
        marcarVoto(serve);
      } catch (falha) {
        Radar.mostrarErro(erro, falha);
      }
    });
  }

  document.getElementById("carregando").classList.add("oculto");
  document.getElementById("conteudo").classList.remove("oculto");
});
