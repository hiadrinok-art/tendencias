"use strict";

const ICONES = { prazo: "Prazo", situacao: "Situação", documento: "Documento", resultado: "Resultado",
  ata_processo: "Ata", atas_ramo: "Atas do ramo", novos_editais: "Editais novos" };
const WHATS = { enviado: "Enviado no WhatsApp", simulado: "WhatsApp (teste)", erro: "Falha no envio",
  limite: "Limite diário atingido", pendente: "Envio pendente" };

function dataHoraUtc(iso) {
  return new Date(iso).toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit",
    hour: "2-digit", minute: "2-digit" });
}

async function carregarEventos() {
  const { el } = Radar;
  const lista = document.getElementById("eventos");
  const { eventos } = await Radar.api("/alertas/eventos");
  if (!eventos.length) {
    lista.replaceChildren(el("li", { class: "miudo" },
      "Nenhum alerta ainda. Acompanhe editais (botão Acompanhar no edital) e o Radar avisa quando algo mudar."));
    return;
  }
  lista.replaceChildren(...eventos.map(e => el("li", { class: e.lido ? "evento" : "evento evento--novo" },
    el("div", { class: "evento__topo" },
      el("span", { class: "etiqueta etiqueta--teal" }, ICONES[e.tipo] || e.tipo),
      el("span", { class: "miudo" }, dataHoraUtc(e.criado))),
    el("strong", {}, e.titulo),
    el("p", { class: "texto-2" }, Radar.legivel(e.texto)),
    el("div", { class: "evento__topo" },
      e.link && e.link.startsWith("/") ? el("a", { href: e.link }, "Abrir") : el("span"),
      e.whatsapp ? el("span", { class: "miudo" }, WHATS[e.whatsapp] || "") : null))));
}

async function carregarSimuladas() {
  const { mensagens } = await Radar.api("/alertas/simuladas");
  const sec = document.getElementById("sec-simuladas");
  sec.classList.toggle("oculto", !mensagens.length);
  document.getElementById("simuladas").replaceChildren(...mensagens.map(m =>
    Radar.el("li", { class: "evento evento--whats" }, Radar.el("span", { class: "miudo" }, dataHoraUtc(m.criado)),
      Radar.el("p", { class: "mensagem" }, m.conteudo))));
}

async function carregarConfig() {
  const cfg = await Radar.api("/alertas/config");
  document.getElementById("modo-teste").classList.toggle("oculto", cfg.canal !== "simulado");
  document.getElementById("whats-ok").classList.toggle("oculto", !cfg.verificado);
  document.getElementById("form-numero").classList.toggle("oculto", cfg.verificado);
  if (cfg.verificado) {
    document.getElementById("numero").textContent = cfg.telefone;
    document.getElementById("form-codigo").classList.add("oculto");
  }
  const prefs = document.getElementById("form-prefs");
  for (const [nome, valor] of Object.entries(cfg.preferencias)) prefs.elements[nome].checked = valor;
}

document.addEventListener("DOMContentLoaded", async () => {
  Radar.ligarSair();
  const erro = document.getElementById("erro");
  const msg = document.getElementById("whats-msg");
  try {
    await Promise.all([carregarConfig(), carregarEventos(), carregarSimuladas()]);
  } catch (e) {
    if (e.status === 401) return Radar.irPara("/entrar");
    return Radar.mostrarErro(erro, e);
  }

  document.getElementById("form-numero").addEventListener("submit", async ev => {
    ev.preventDefault();
    msg.textContent = "Enviando código…";
    try {
      const r = await Radar.api("/alertas/telefone", { metodo: "POST", corpo: {
        telefone: document.getElementById("telefone").value,
        consentimento: document.getElementById("consentimento").checked } });
      document.getElementById("form-codigo").classList.remove("oculto");
      document.getElementById("codigo-info").textContent = r.codigo_teste
        ? `Modo de teste: o código é ${r.codigo_teste}.`
        : `Enviamos um código para ${r.telefone}. Ele vale por 10 minutos.`;
      msg.textContent = "";
      document.getElementById("codigo").focus();
    } catch (e) { msg.textContent = e.message; }
  });

  document.getElementById("form-codigo").addEventListener("submit", async ev => {
    ev.preventDefault();
    try {
      await Radar.api("/alertas/telefone/confirmar", { metodo: "POST",
        corpo: { codigo: document.getElementById("codigo").value.trim() } });
      msg.textContent = "Número confirmado. Você vai receber os alertas no WhatsApp.";
      await carregarConfig();
    } catch (e) { msg.textContent = e.message; }
  });

  document.getElementById("remover").addEventListener("click", async () => {
    await Radar.api("/alertas/telefone", { metodo: "DELETE" });
    msg.textContent = "Pronto: você não vai mais receber alertas no WhatsApp.";
    await carregarConfig();
  });

  document.getElementById("form-prefs").addEventListener("submit", async ev => {
    ev.preventDefault();
    const f = ev.target.elements;
    try {
      await Radar.api("/alertas/preferencias", { metodo: "PUT", corpo: {
        novos_editais: f.novos_editais.checked, processos: f.processos.checked,
        atas_ramo: f.atas_ramo.checked, atas_processos: f.atas_processos.checked } });
      document.getElementById("prefs-msg").textContent = "Preferências salvas.";
    } catch (e) { document.getElementById("prefs-msg").textContent = e.message; }
  });

  document.getElementById("marcar-lidos").addEventListener("click", async () => {
    await Radar.api("/alertas/eventos/lidos", { metodo: "POST" });
    carregarEventos();
  });
});
