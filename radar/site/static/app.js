// Funções comuns do site. Dados de fora (API/PNCP) só entram na página como
// texto (textContent), nunca como HTML: assim um edital com código malicioso
// no objeto não vira ataque XSS.
"use strict";

const Radar = {
  async api(caminho, { metodo = "GET", corpo } = {}) {
    const opcoes = { method: metodo, credentials: "same-origin", headers: {} };
    if (corpo !== undefined) {
      opcoes.headers["Content-Type"] = "application/json";
      opcoes.body = JSON.stringify(corpo);
    }
    let resposta;
    try {
      resposta = await fetch(caminho, opcoes);
    } catch (e) {
      throw new ErroApi(0, "Sem conexão com o servidor. Tente de novo.");
    }
    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      throw new ErroApi(resposta.status, dados.erro || "Algo deu errado.", dados.campos || []);
    }
    return dados;
  },

  // Cria um elemento: el("a", { href: "/x", class: "y" }, "texto", outroEl)
  el(tag, atributos = {}, ...filhos) {
    const no = document.createElement(tag);
    for (const [nome, valor] of Object.entries(atributos)) {
      if (valor === null || valor === undefined || valor === false) continue;
      if (nome === "class") no.className = valor;
      else if (nome.startsWith("on")) no.addEventListener(nome.slice(2), valor);
      else no.setAttribute(nome, valor === true ? "" : valor);
    }
    for (const filho of filhos.flat()) {
      if (filho === null || filho === undefined || filho === false) continue;
      no.append(filho instanceof Node ? filho : document.createTextNode(String(filho)));
    }
    return no;
  },

  dinheiro(valor) {
    if (valor === null || valor === undefined) return "Não informado";
    return valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
  },

  dinheiroCurto(valor) {
    if (!valor) return "R$ 0";
    if (valor >= 1e9) return "R$ " + (valor / 1e9).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " bi";
    if (valor >= 1e6) return "R$ " + (valor / 1e6).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mi";
    if (valor >= 1e3) return "R$ " + (valor / 1e3).toLocaleString("pt-BR", { maximumFractionDigits: 0 }) + " mil";
    return Radar.dinheiro(valor);
  },

  // Datas do PNCP já vêm no horário de Brasília.
  dataHora(iso) {
    if (!iso) return "Não informado";
    const [d, h] = iso.split("T");
    const [ano, mes, dia] = d.split("-");
    const [hh, mm] = (h || "00:00").split(":");
    return `${dia}/${mes}/${ano}, ${hh}h${mm === "00" ? "" : mm}`;
  },

  dataCurta(iso) {
    if (!iso) return "—";
    const [ano, mes, dia] = iso.slice(0, 10).split("-");
    const [hh, mm] = (iso.split("T")[1] || "00:00").split(":");
    return `${dia}/${mes}, ${hh}h${mm === "00" ? "" : mm}`;
  },

  // Textos do PNCP muitas vezes vêm TODO EM MAIÚSCULAS: exibe só a primeira
  // letra maiúscula (e mantém siglas curtas, como UFABC ou TIC).
  legivel(texto) {
    if (!texto) return "";
    const letras = texto.replace(/[^A-Za-zÀ-ÿ]/g, "");
    const maiusculas = letras.replace(/[^A-ZÀ-Þ]/g, "").length;
    if (letras.length < 8 || maiusculas / letras.length < 0.7) return texto;
    const minusculo = texto.toLocaleLowerCase("pt-BR").replace(/\b([a-zà-ÿ]{2,5})\b/g, (p, _, i) => {
      const original = texto.substr(i, p.length);
      return SIGLAS.has(original) ? original : p;
    });
    return minusculo.charAt(0).toLocaleUpperCase("pt-BR") + minusculo.slice(1);
  },

  emDias(n) {
    if (n === null || n === undefined) return "";
    if (n === 0) return "termina hoje";
    if (n === 1) return "termina amanhã";
    return `em ${n} dias`;
  },

  irPara(caminho) { window.location.assign(caminho); },

  async sair() {
    try { await Radar.api("/sessao", { metodo: "DELETE" }); } finally { Radar.irPara("/"); }
  },

  mostrarErro(caixa, erro) {
    caixa.textContent = "";
    caixa.append(erro.message);
    if (erro.campos && erro.campos.length) {
      const nomes = { email: "E-mail", senha: "Senha", cnpj: "CNPJ", ramos: "Ramos", ufs: "Estados" };
      const lista = Radar.el("ul", { class: "lista-erros" },
        erro.campos.map(c => Radar.el("li", {}, `${nomes[c.campo.split(".")[0]] || c.campo}: ${c.mensagem.replace(/^Value error, /, "")}`)));
      caixa.append(lista);
    }
    caixa.classList.remove("oculto");
    caixa.focus();
  },

  ligarSair() {
    const botao = document.getElementById("sair");
    if (botao) botao.addEventListener("click", Radar.sair);
  },
};

const SIGLAS = new Set(["TI", "TIC", "UF", "SUS", "UFABC", "UBS", "CNPJ", "CPF", "EPI", "GLP", "UPS",
  "SP", "RJ", "MG", "DF", "PR", "SC", "RS", "BA", "PE", "CE", "GO", "ES", "MT", "MS", "PA", "AM",
  "PB", "PI", "RN", "AL", "SE", "MA", "TO", "RO", "RR", "AP", "AC", "IFSP", "SRP", "ME", "EPP"]);

class ErroApi extends Error {
  constructor(status, mensagem, campos = []) {
    super(mensagem);
    this.status = status;
    this.campos = campos;
  }
}
