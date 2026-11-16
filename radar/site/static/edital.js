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
