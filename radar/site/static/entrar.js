"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form");
  const erro = document.getElementById("erro");
  const botao = document.getElementById("enviar");

  form.addEventListener("submit", async evento => {
    evento.preventDefault();
    erro.classList.add("oculto");
    botao.disabled = true;
    try {
      await Radar.api("/sessao", {
        metodo: "POST",
        corpo: { email: document.getElementById("email").value, senha: document.getElementById("senha").value },
      });
      Radar.irPara("/painel");
    } catch (e) {
      Radar.mostrarErro(erro, e);
      botao.disabled = false;
    }
  });
});
