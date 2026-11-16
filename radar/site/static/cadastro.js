"use strict";

const UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
  "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"];

function cnpjValido(texto) {
  const d = texto.replace(/\D/g, "");
  if (d.length !== 14 || /^(\d)\1+$/.test(d)) return false;
  const digito = (base, pesos) => {
    const resto = pesos.reduce((s, p, i) => s + Number(base[i]) * p, 0) % 11;
    return resto < 2 ? 0 : 11 - resto;
  };
  const p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
  const dv1 = digito(d, p1);
  const dv2 = digito(d.slice(0, 12) + dv1, [6, ...p1]);
  return d.endsWith(`${dv1}${dv2}`);
}

function mascaraCnpj(texto) {
  const d = texto.replace(/\D/g, "").slice(0, 14);
  return d.replace(/^(\d{2})(\d)/, "$1.$2").replace(/^(\d{2})\.(\d{3})(\d)/, "$1.$2.$3")
    .replace(/\.(\d{3})(\d)/, ".$1/$2").replace(/(\d{4})(\d)/, "$1-$2");
}

function opcao(nome, valor, rotulo, classe = "") {
  return Radar.el("label", { class: `opcao ${classe}` },
    Radar.el("input", { type: "checkbox", name: nome, value: valor }),
    Radar.el("span", {}, rotulo));
}

function marcados(nome) {
  return [...document.querySelectorAll(`input[name="${nome}"]:checked`)].map(i => i.value);
}

document.addEventListener("DOMContentLoaded", async () => {
  const form = document.getElementById("form");
  const erro = document.getElementById("erro");
  const cnpj = document.getElementById("cnpj");
  const cnpjMsg = document.getElementById("cnpj-msg");
  const caixaUfs = document.getElementById("ufs");

  UFS.forEach(uf => caixaUfs.append(opcao("uf", uf, uf, "opcao--uf")));
  document.getElementById("todas-ufs").addEventListener("click", () =>
    caixaUfs.querySelectorAll("input").forEach(i => { i.checked = true; }));
  document.getElementById("nenhuma-uf").addEventListener("click", () =>
    caixaUfs.querySelectorAll("input").forEach(i => { i.checked = false; }));

  try {
    const ramos = await Radar.api("/ramos");
    const caixa = document.getElementById("ramos");
    ramos.forEach(r => caixa.append(opcao("ramo", r.id, r.nome)));
  } catch (e) {
    Radar.mostrarErro(erro, e);
  }

  cnpj.addEventListener("input", () => {
    cnpj.value = mascaraCnpj(cnpj.value);
    const completo = cnpj.value.replace(/\D/g, "").length === 14;
    const ok = completo && cnpjValido(cnpj.value);
    cnpj.closest(".campo").classList.toggle("campo--erro", completo && !ok);
    cnpjMsg.textContent = completo ? (ok ? "CNPJ válido." : "CNPJ inválido: confira os números.") : "Usado só para identificar a empresa.";
    cnpjMsg.className = completo && !ok ? "campo__erro" : "dica";
  });

  form.addEventListener("submit", async evento => {
    evento.preventDefault();
    erro.classList.add("oculto");
    const ramos = marcados("ramo");
    const ufs = marcados("uf");
    const problemas = [];
    if (!cnpjValido(cnpj.value)) problemas.push("Confira o CNPJ.");
    if (!ramos.length) problemas.push("Escolha pelo menos um ramo.");
    if (!ufs.length) problemas.push("Escolha pelo menos um estado.");
    if (!document.getElementById("aceite").checked) problemas.push("É preciso aceitar os termos.");
    if (problemas.length) {
      Radar.mostrarErro(erro, { message: problemas.join(" ") });
      return;
    }
    const botao = document.getElementById("enviar");
    botao.disabled = true;
    botao.textContent = "Criando sua conta…";
    try {
      await Radar.api("/conta", {
        metodo: "POST",
        corpo: {
          email: document.getElementById("email").value,
          senha: document.getElementById("senha").value,
          cnpj: cnpj.value,
          ramos, ufs,
          palavras_chave: document.getElementById("palavras").value.split(",").map(p => p.trim()).filter(Boolean),
          aceite_termos: true,
        },
      });
      Radar.irPara("/painel");
    } catch (e) {
      Radar.mostrarErro(erro, e);
      botao.disabled = false;
      botao.textContent = "Ver meus editais";
    }
  });
});
