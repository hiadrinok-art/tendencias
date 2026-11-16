"""API do Radar de Editais: contas, sessões e dados do usuário, com a camada de segurança.

Rodar localmente:
    RADAR_SEGREDO=... RADAR_HTTPS=0 RADAR_ORIGENS=http://localhost:3000 \
        uvicorn radar.app:app --no-server-header --no-proxy-headers
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Literal

from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response as RespostaBruta
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

import hashlib
import hmac
import os
import secrets

from . import banco, classificador, detalhes, notificacoes
from .config import Config
from .seguranca import auditoria, dispositivos, rede, senhas, sessoes, validacao
from .seguranca.limite import JanelaDeslizante
from .seguranca.protecao_http import LimiteDeCorpo, ProtecaoHTTP

Ramo = Literal["ti", "obra", "eng", "limp", "alim", "saude", "mob"]
UF = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

ERRO_LOGIN = "E-mail ou senha incorretos."
# Datas do PNCP vêm no horário de Brasília, sem fuso.
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")
PASTA_SITE = Path(__file__).parent / "site"
# Páginas do site: só scripts e estilos do próprio domínio (nada inline) e as
# fontes do Google. Dados do PNCP entram na página só como texto.
CSP_PAGINAS = (
    "default-src 'self'; script-src 'self'; style-src 'self' https://fonts.googleapis.com; "
    "font-src https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; "
    "form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
)
QUINZE_MINUTOS = 15 * 60


class NovaConta(BaseModel):
    email: str = Field(max_length=254)
    senha: str = Field(max_length=validacao.TAMANHO_MAX_SENHA)
    cnpj: str = Field(max_length=20)
    ramos: list[Ramo] = Field(min_length=1, max_length=7)
    ufs: list[UF] = Field(min_length=1, max_length=27)
    palavras_chave: list[str] = Field(default_factory=list, max_length=20)
    aceite_termos: bool

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        if not validacao.email_valido(v):
            raise ValueError("E-mail inválido.")
        return validacao.normalizar_email(v)

    @field_validator("cnpj")
    @classmethod
    def _cnpj(cls, v: str) -> str:
        if not validacao.cnpj_valido(v):
            raise ValueError("CNPJ inválido.")
        return validacao.so_digitos(v)

    @field_validator("palavras_chave")
    @classmethod
    def _palavras(cls, v: list[str]) -> list[str]:
        return validacao.limpar_palavras_chave(v)


class Login(BaseModel):
    email: str = Field(max_length=254)
    senha: str = Field(max_length=validacao.TAMANHO_MAX_SENHA)


class TrocaSenha(BaseModel):
    senha_atual: str = Field(max_length=validacao.TAMANHO_MAX_SENHA)
    senha_nova: str = Field(max_length=validacao.TAMANHO_MAX_SENHA)


class Confirmacao(BaseModel):
    senha: str = Field(max_length=validacao.TAMANHO_MAX_SENHA)


class Avaliacao(BaseModel):
    id: str = Field(max_length=60)
    serve: bool


STATUS_FUNIL = {
    "interesse": "Tenho interesse",
    "preparando": "Preparando proposta",
    "enviada": "Proposta enviada",
    "ganhou": "Ganhou",
    "perdeu": "Não ganhou",
}


class PreferenciasAlerta(BaseModel):
    novos_editais: bool
    processos: bool
    atas_ramo: bool
    atas_processos: bool


class NovoTelefone(BaseModel):
    telefone: str = Field(max_length=30)
    consentimento: bool


class CodigoTelefone(BaseModel):
    codigo: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


PALAVRAS_SAIR = {"sair", "parar", "pare", "stop", "cancelar", "descadastrar"}


class Acompanhamento(BaseModel):
    id: str = Field(max_length=60)
    status: Literal["interesse", "preparando", "enviada", "ganhou", "perdeu"]
    nota: str = Field(default="", max_length=1000)

    @field_validator("nota")
    @classmethod
    def _nota(cls, v: str) -> str:
        return validacao.limpar_texto_multilinha(v, 1000)


def _ics_texto(texto: str) -> str:
    """Escapa texto para o formato iCalendar (RFC 5545), sem quebras de linha soltas."""
    texto = texto.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")
    return texto.replace("\r", "").replace("\n", "\\n")


def criar_app(config: Config, notificador: notificacoes.Notificador | None = None) -> FastAPI:
    app = FastAPI(title="Radar de Editais", docs_url=None, redoc_url=None, openapi_url=None)
    banco.preparar(config.banco)
    proxies = set(config.proxies_confiaveis)

    # Limites. Todos contam por janela de tempo e se esvaziam sozinhos.
    limite_ip_login = JanelaDeslizante(limite=20, janela=60)
    limite_ip_cadastro = JanelaDeslizante(limite=10, janela=60 * 60)
    # Erros de senha: por e-mail+IP (trava só quem está errando) e por e-mail
    # no total (ataque distribuído; não vale para dispositivo já usado pelo dono).
    falhas_email_ip = JanelaDeslizante(limite=5, janela=QUINZE_MINUTOS)
    falhas_email = JanelaDeslizante(limite=20, janela=QUINZE_MINUTOS)
    # Senha pedida de novo para trocar senha ou excluir conta.
    falhas_confirmacao = JanelaDeslizante(limite=5, janela=QUINZE_MINUTOS)
    # Consultas de itens/documentos vão ao PNCP: limite por usuário.
    limite_detalhes = JanelaDeslizante(limite=60, janela=60)
    # Códigos de verificação do WhatsApp: no máximo 3 envios por hora por usuário.
    limite_codigos = JanelaDeslizante(limite=3, janela=60 * 60)
    notificador = notificador or notificacoes.do_ambiente()
    app.state.limites = {
        "ip_login": limite_ip_login, "ip_cadastro": limite_ip_cadastro,
        "email_ip": falhas_email_ip, "email": falhas_email, "confirmacao": falhas_confirmacao,
    }

    app.add_middleware(ProtecaoHTTP, origens_permitidas=config.origens, https=config.https,
                       nome_cookie=config.nome_cookie)
    if config.origens:
        app.add_middleware(
            CORSMiddleware, allow_origins=config.origens, allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"],
        )
    app.add_middleware(LimiteDeCorpo)  # o último adicionado é o primeiro a rodar

    # Erros sempre no formato {"erro": ...}, sem o padrão que revela o framework.
    @app.exception_handler(StarletteHTTPException)
    async def erro_http(request: Request, erro: StarletteHTTPException):
        return JSONResponse({"erro": erro.detail}, status_code=erro.status_code,
                            headers=getattr(erro, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def erro_de_validacao(request: Request, erro: RequestValidationError):
        # Nunca repete o valor enviado (seria devolver a senha no corpo do erro).
        campos = [
            {"campo": ".".join(str(p) for p in e["loc"][1:]), "mensagem": e["msg"]}
            for e in erro.errors()
        ]
        return JSONResponse({"erro": "Dados inválidos.", "campos": campos}, status_code=422)

    def db():
        conexao = banco.conectar(config.banco)
        try:
            yield conexao
        finally:
            conexao.close()

    def ip_de(request: Request) -> str:
        conexao_ip = request.client.host if request.client else ""
        return rede.ip_real(conexao_ip, request.headers.get("x-forwarded-for"), proxies)

    def auditar(conexao, evento: str, request: Request, **extra) -> None:
        auditoria.registrar(conexao, evento, segredo=config.segredo, ip=ip_de(request), **extra)

    def token_de(request: Request) -> str | None:
        cabecalho = request.headers.get("authorization", "")
        if cabecalho.lower().startswith("bearer "):
            return cabecalho[7:].strip()
        return request.cookies.get(config.nome_cookie)

    def usuario_atual(request: Request, conexao=Depends(db)):
        usuario_id = sessoes.validar(conexao, token_de(request))
        if usuario_id is None:
            raise HTTPException(401, "Faça login para continuar.")
        usuario = conexao.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(401, "Faça login para continuar.")
        return usuario

    def abrir_sessao(conexao, resposta: Response, usuario_id: int, email: str) -> None:
        token = sessoes.criar(conexao, usuario_id)
        resposta.set_cookie(
            config.nome_cookie, token, httponly=True, secure=config.https, samesite="strict",
            max_age=int(sessoes.DURACAO_MAXIMA.total_seconds()), path="/",
        )
        resposta.set_cookie(
            dispositivos.NOME_COOKIE, dispositivos.emitir(config.segredo, email), httponly=True,
            secure=config.https, samesite="strict", max_age=dispositivos.DURACAO_SEGUNDOS, path="/",
        )

    def bloqueio(janela: JanelaDeslizante, chave: str, mensagem: str) -> HTTPException:
        return HTTPException(429, mensagem,
                             headers={"Retry-After": str(janela.segundos_para_liberar(chave))})

    def conferir_senha(conexao, request: Request, usuario, senha: str) -> None:
        """Confirma a senha do usuário logado, com limite de tentativas."""
        chave = str(usuario["id"])
        if falhas_confirmacao.bloqueado(chave):
            raise bloqueio(falhas_confirmacao, chave, "Muitas tentativas erradas. Aguarde alguns minutos.")
        if not senhas.verificar(senha, usuario["senha_hash"]):
            falhas_confirmacao.registrar(chave)
            auditar(conexao, "confirmacao_falhou", request, usuario_id=usuario["id"])
            raise HTTPException(401, "Senha incorreta.")
        falhas_confirmacao.zerar(chave)

    @app.get("/saude")
    def saude():
        return {"ok": True}

    @app.post("/conta", status_code=201)
    def criar_conta(dados: NovaConta, request: Request, resposta: Response, conexao=Depends(db)):
        if not limite_ip_cadastro.permitir(rede.chave_de_limite(ip_de(request))):
            raise HTTPException(429, "Muitos cadastros a partir desta rede. Tente mais tarde.")
        if not dados.aceite_termos:
            raise HTTPException(422, "É preciso aceitar os termos de uso e a política de privacidade.")
        problemas = validacao.problemas_da_senha(dados.senha, dados.email)
        if problemas:
            raise HTTPException(422, " ".join(problemas))

        agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
        senha_hash = senhas.gerar_hash(dados.senha)  # fora da transação: não segura o banco
        try:
            with banco.transacao(conexao):
                cursor = conexao.execute(
                    "INSERT INTO usuarios (email, senha_hash, cnpj, ramos, ufs, palavras_chave,"
                    " termos_versao, termos_aceitos_em, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (dados.email, senha_hash, dados.cnpj,
                     json.dumps(sorted(set(dados.ramos))), json.dumps(sorted(set(dados.ufs))),
                     json.dumps(dados.palavras_chave), config.versao_termos, agora, agora),
                )
                auditar(conexao, "conta_criada", request, usuario_id=cursor.lastrowid, email=dados.email)
                abrir_sessao(conexao, resposta, cursor.lastrowid, dados.email)
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Não foi possível criar a conta com esse e-mail.") from None
        return {"ok": True}

    @app.post("/sessao")
    def entrar(dados: Login, request: Request, resposta: Response, conexao=Depends(db)):
        email = validacao.normalizar_email(dados.email)
        chave_ip = rede.chave_de_limite(ip_de(request))
        chave_par = f"{email}|{chave_ip}"

        if not limite_ip_login.permitir(chave_ip):
            raise HTTPException(429, "Muitas tentativas. Aguarde um minuto.")
        if falhas_email_ip.bloqueado(chave_par):
            auditar(conexao, "login_bloqueado", request, email=email, detalhe="email+ip")
            raise bloqueio(falhas_email_ip, chave_par, "Muitas tentativas erradas. Aguarde alguns minutos.")
        dispositivo_ok = dispositivos.confiavel(
            config.segredo, email, request.cookies.get(dispositivos.NOME_COOKIE))
        if falhas_email.bloqueado(email) and not dispositivo_ok:
            auditar(conexao, "login_bloqueado", request, email=email, detalhe="email")
            raise bloqueio(falhas_email, email,
                           "Esta conta recebeu muitas tentativas erradas. Entre por um "
                           "dispositivo que você já usou ou aguarde alguns minutos.")

        usuario = conexao.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        hash_salvo = usuario["senha_hash"] if usuario else senhas.HASH_FICTICIO
        senha_ok = senhas.verificar(dados.senha, hash_salvo)
        if usuario is None or not senha_ok:
            falhas_email_ip.registrar(chave_par)
            falhas_email.registrar(email)
            auditar(conexao, "login_falhou", request, email=email)
            raise HTTPException(401, ERRO_LOGIN)

        falhas_email_ip.zerar(chave_par)
        if senhas.precisa_rehash(usuario["senha_hash"]):
            conexao.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                            (senhas.gerar_hash(dados.senha), usuario["id"]))
        abrir_sessao(conexao, resposta, usuario["id"], email)
        auditar(conexao, "login_ok", request, usuario_id=usuario["id"], email=email)
        return {"ok": True}

    @app.delete("/sessao")
    def sair(request: Request, resposta: Response, conexao=Depends(db)):
        token = token_de(request)
        if token:
            sessoes.encerrar(conexao, token)
        resposta.delete_cookie(config.nome_cookie, path="/")
        return {"ok": True}

    @app.get("/eu")
    def perfil(usuario=Depends(usuario_atual)):
        return {
            "email": usuario["email"],
            "cnpj": usuario["cnpj"],
            "ramos": json.loads(usuario["ramos"]),
            "ufs": json.loads(usuario["ufs"]),
            "palavras_chave": json.loads(usuario["palavras_chave"]),
        }

    @app.put("/eu/senha")
    def trocar_senha(dados: TrocaSenha, request: Request, resposta: Response,
                     usuario=Depends(usuario_atual), conexao=Depends(db)):
        conferir_senha(conexao, request, usuario, dados.senha_atual)
        problemas = validacao.problemas_da_senha(dados.senha_nova, usuario["email"])
        if problemas:
            raise HTTPException(422, " ".join(problemas))
        novo_hash = senhas.gerar_hash(dados.senha_nova)
        with banco.transacao(conexao):
            conexao.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (novo_hash, usuario["id"]))
            sessoes.encerrar_todas(conexao, usuario["id"])
            auditar(conexao, "senha_trocada", request, usuario_id=usuario["id"])
            abrir_sessao(conexao, resposta, usuario["id"], usuario["email"])
        return {"ok": True}

    @app.get("/eu/dados")
    def exportar_dados(request: Request, usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Direito de acesso (LGPD, art. 18): tudo o que guardamos sobre a conta."""
        auditar(conexao, "dados_exportados", request, usuario_id=usuario["id"])
        dados = {k: usuario[k] for k in usuario.keys() if k != "senha_hash"}
        for campo in ("ramos", "ufs", "palavras_chave"):
            dados[campo] = json.loads(dados[campo])
        alerta = conexao.execute("SELECT * FROM alertas_config WHERE usuario_id = ?", (usuario["id"],)).fetchone()
        dados["alertas"] = ({k: alerta[k] for k in alerta.keys() if k not in ("codigo_hash", "codigo_expira")}
                            if alerta else None)
        return dados

    @app.delete("/eu")
    def excluir_conta(dados: Confirmacao, request: Request, resposta: Response,
                      usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Direito de eliminação (LGPD, art. 18): apaga a conta e todas as sessões."""
        conferir_senha(conexao, request, usuario, dados.senha)
        with banco.transacao(conexao):
            conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario["id"],))
            auditar(conexao, "conta_excluida", request, usuario_id=usuario["id"])
        resposta.delete_cookie(config.nome_cookie, path="/")
        resposta.delete_cookie(dispositivos.NOME_COOKIE, path="/")
        return {"ok": True}

    # ---------------------------------------------------------------- editais

    def _edital_publico(linha, agora: datetime) -> dict:
        encerramento = linha["encerramento"]
        dias = None
        if encerramento:
            fim = datetime.fromisoformat(encerramento).replace(tzinfo=FUSO_BRASILIA)
            dias = max(0, (fim.date() - agora.astimezone(FUSO_BRASILIA).date()).days)
        return {
            "id": linha["id"], "orgao": linha["orgao"], "unidade": linha["unidade"],
            "municipio": linha["municipio"], "uf": linha["uf"], "modalidade": linha["modalidade"],
            "objeto": linha["objeto"], "valor_estimado": linha["valor_estimado"],
            "abertura": linha["abertura"], "encerramento": encerramento, "dias_restantes": dias,
            "publicado": linha["publicado"], "link_origem": linha["link_origem"],
            "link_pncp": linha["link_pncp"],
            "ramos": [classificador.RAMOS[r] for r in json.loads(linha["ramos"]) if r in classificador.RAMOS],
        }

    @app.get("/ramos")
    def listar_ramos():
        return [{"id": k, "nome": v} for k, v in classificador.RAMOS.items()]

    @app.get("/editais")
    def meus_editais(filtro: Literal["todos", "prazo", "grandes"] = "todos",
                     q: str = Query(default="", max_length=100),
                     usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Editais com propostas abertas no ramo, nas UFs e nas palavras-chave do usuário.

        Com ``q``, vira busca livre: todos os editais abertos nas UFs do usuário
        cujo objeto ou órgão contenha todas as palavras buscadas, de qualquer ramo."""
        ramos = set(json.loads(usuario["ramos"]))
        ufs = json.loads(usuario["ufs"])
        palavras = json.loads(usuario["palavras_chave"])
        agora = datetime.now(timezone.utc)
        agora_local = agora.astimezone(FUSO_BRASILIA).replace(tzinfo=None).isoformat(timespec="seconds")
        marcadores = ",".join("?" * len(ufs))
        linhas = conexao.execute(
            f"SELECT * FROM editais WHERE encerramento > ? AND uf IN ({marcadores}) "
            "ORDER BY encerramento LIMIT 5000", (agora_local, *ufs),
        ).fetchall()
        termos = classificador.normalizar(validacao.limpar_texto(q, 100)).split()
        if termos:
            escolhidos = [
                l for l in linhas
                if all(t in classificador.normalizar(f"{l['objeto']} {l['orgao']} {l['municipio']}") for t in termos)
            ]
        else:
            escolhidos = [
                l for l in linhas
                if ramos & set(json.loads(l["ramos"])) or (palavras and classificador.casa_palavras(l["objeto"], palavras))
            ]
        acompanhados = {
            a["edital_id"]: a["status"] for a in conexao.execute(
                "SELECT edital_id, status FROM acompanhamentos WHERE usuario_id = ?", (usuario["id"],))
        }
        todos = [_edital_publico(l, agora) for l in escolhidos]
        for e in todos:
            e["acompanhamento"] = acompanhados.get(e["id"])
        if filtro == "prazo":
            visiveis = [e for e in todos if e["dias_restantes"] is not None and e["dias_restantes"] <= 10]
        elif filtro == "grandes":
            visiveis = [e for e in todos if (e["valor_estimado"] or 0) >= 100_000]
        else:
            visiveis = todos
        return {
            "resumo": {
                "total": len(todos),
                "valor_somado": round(sum(e["valor_estimado"] or 0 for e in todos), 2),
                "proximo_prazo": todos[0]["encerramento"] if todos else None,
                "proximo_em_dias": todos[0]["dias_restantes"] if todos else None,
                "prazo_10_dias": sum(1 for e in todos if (e["dias_restantes"] or 99) <= 10),
                "acima_100_mil": sum(1 for e in todos if (e["valor_estimado"] or 0) >= 100_000),
            },
            "editais": visiveis[:200],
        }

    @app.get("/edital")
    def ver_edital(id: str = Query(max_length=60), usuario=Depends(usuario_atual), conexao=Depends(db)):
        linha = conexao.execute("SELECT * FROM editais WHERE id = ?", (id,)).fetchone()
        if linha is None:
            raise HTTPException(404, "Edital não encontrado.")
        avaliacao = conexao.execute(
            "SELECT serve FROM avaliacoes WHERE usuario_id = ? AND edital_id = ?", (usuario["id"], id)
        ).fetchone()
        acompanhamento = conexao.execute(
            "SELECT status, nota FROM acompanhamentos WHERE usuario_id = ? AND edital_id = ?", (usuario["id"], id)
        ).fetchone()
        dados = _edital_publico(linha, datetime.now(timezone.utc))
        dados["avaliacao"] = None if avaliacao is None else bool(avaliacao["serve"])
        dados["acompanhamento"] = dict(acompanhamento) if acompanhamento else None
        return dados

    @app.get("/edital/detalhes")
    def detalhes_edital(id: str = Query(max_length=60), tipo: Literal["itens", "arquivos"] = "itens",
                        usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Itens ou documentos do edital, direto do PNCP (com cache de 6 h)."""
        linha = conexao.execute("SELECT * FROM editais WHERE id = ?", (id,)).fetchone()
        if linha is None:
            raise HTTPException(404, "Edital não encontrado.")
        if not limite_detalhes.permitir(str(usuario["id"])):
            raise HTTPException(429, "Muitas consultas seguidas. Aguarde um minuto.")
        try:
            return {"tipo": tipo, "lista": detalhes.obter(conexao, linha, tipo)}
        except detalhes.PncpIndisponivel:
            raise HTTPException(503, "O PNCP não respondeu agora. Tente de novo em instantes.") from None

    @app.get("/edital/agenda.ics")
    def agenda(id: str = Query(max_length=60), usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Evento de calendário com o fim do prazo de propostas (alarme 1 dia antes)."""
        linha = conexao.execute("SELECT * FROM editais WHERE id = ?", (id,)).fetchone()
        if linha is None or not linha["encerramento"]:
            raise HTTPException(404, "Edital sem data de encerramento.")
        fim = datetime.fromisoformat(linha["encerramento"]).replace(tzinfo=FUSO_BRASILIA).astimezone(timezone.utc)
        carimbo = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        objeto = linha["objeto"][:120]
        uid = "".join(c for c in linha["id"] if c.isalnum()) + "@radar-de-editais"
        linhas = [
            "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Radar de Editais//PT-BR", "CALSCALE:GREGORIAN",
            "BEGIN:VEVENT", f"UID:{uid}", f"DTSTAMP:{carimbo}",
            f"DTSTART:{fim.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{(fim + timedelta(minutes=30)).strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:{_ics_texto('Fim das propostas: ' + objeto)}",
            f"DESCRIPTION:{_ics_texto(linha['orgao'] + ' - ' + linha['objeto'][:500] + ' - Nº PNCP ' + linha['id'])}",
            f"URL:{linha['link_pncp']}",
            "BEGIN:VALARM", "ACTION:DISPLAY", "TRIGGER:-P1D", "DESCRIPTION:Prazo do edital amanhã", "END:VALARM",
            "END:VEVENT", "END:VCALENDAR",
        ]
        return RespostaBruta(
            "\r\n".join(linhas) + "\r\n", media_type="text/calendar; charset=utf-8",
            headers={"Content-Disposition": 'attachment; filename="prazo-edital.ics"'})

    @app.get("/funil")
    def meu_funil(usuario=Depends(usuario_atual), conexao=Depends(db)):
        linhas = conexao.execute(
            "SELECT e.*, a.status, a.nota, a.atualizado FROM acompanhamentos a "
            "JOIN editais e ON e.id = a.edital_id WHERE a.usuario_id = ? ORDER BY e.encerramento",
            (usuario["id"],)).fetchall()
        agora = datetime.now(timezone.utc)
        etapas = []
        for status, nome in STATUS_FUNIL.items():
            itens = []
            for l in linhas:
                if l["status"] == status:
                    e = _edital_publico(l, agora)
                    e.update(status=l["status"], nota=l["nota"], atualizado=l["atualizado"])
                    itens.append(e)
            etapas.append({"status": status, "nome": nome, "editais": itens})
        return {"etapas": etapas}

    @app.put("/funil")
    def acompanhar(dados: Acompanhamento, usuario=Depends(usuario_atual), conexao=Depends(db)):
        if conexao.execute("SELECT 1 FROM editais WHERE id = ?", (dados.id,)).fetchone() is None:
            raise HTTPException(404, "Edital não encontrado.")
        total = conexao.execute("SELECT COUNT(*) FROM acompanhamentos WHERE usuario_id = ?",
                                (usuario["id"],)).fetchone()[0]
        if total >= 1000:
            raise HTTPException(422, "Limite de 1.000 editais acompanhados.")
        conexao.execute(
            "INSERT INTO acompanhamentos (usuario_id, edital_id, status, nota, atualizado) VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(usuario_id, edital_id) DO UPDATE SET status = excluded.status, nota = excluded.nota, "
            "atualizado = excluded.atualizado",
            (usuario["id"], dados.id, dados.status, dados.nota, datetime.now(timezone.utc).isoformat(timespec="seconds")))
        return {"ok": True}

    @app.delete("/funil")
    def deixar_de_acompanhar(id: str = Query(max_length=60), usuario=Depends(usuario_atual), conexao=Depends(db)):
        conexao.execute("DELETE FROM acompanhamentos WHERE usuario_id = ? AND edital_id = ?", (usuario["id"], id))
        return {"ok": True}

    @app.post("/edital/avaliacao")
    def avaliar(dados: Avaliacao, usuario=Depends(usuario_atual), conexao=Depends(db)):
        if conexao.execute("SELECT 1 FROM editais WHERE id = ?", (dados.id,)).fetchone() is None:
            raise HTTPException(404, "Edital não encontrado.")
        conexao.execute(
            "INSERT INTO avaliacoes (usuario_id, edital_id, serve, quando) VALUES (?, ?, ?, ?) "
            "ON CONFLICT(usuario_id, edital_id) DO UPDATE SET serve = excluded.serve, quando = excluded.quando",
            (usuario["id"], dados.id, int(dados.serve), datetime.now(timezone.utc).isoformat(timespec="seconds")),
        )
        return {"ok": True}

    # ---------------------------------------------------------------- alertas

    def _hash_codigo(usuario_id: int, codigo: str) -> str:
        return hmac.new(config.segredo.encode(), f"codigo|{usuario_id}|{codigo}".encode(), hashlib.sha256).hexdigest()

    def _config_alerta(conexao, usuario_id: int):
        conexao.execute("INSERT OR IGNORE INTO alertas_config (usuario_id) VALUES (?)", (usuario_id,))
        return conexao.execute("SELECT * FROM alertas_config WHERE usuario_id = ?", (usuario_id,)).fetchone()

    @app.get("/alertas/config")
    def ver_alertas(usuario=Depends(usuario_atual), conexao=Depends(db)):
        c = _config_alerta(conexao, usuario["id"])
        nao_lidos = conexao.execute("SELECT COUNT(*) FROM eventos WHERE usuario_id = ? AND lido = 0",
                                    (usuario["id"],)).fetchone()[0]
        return {
            "canal": notificador.nome,
            "telefone": notificacoes.mascarar_telefone(c["telefone"]),
            "verificado": bool(c["telefone_verificado"]),
            "aguardando_codigo": bool(c["codigo_hash"]) and not c["telefone_verificado"],
            "preferencias": {k: bool(c[k]) for k in ("novos_editais", "processos", "atas_ramo", "atas_processos")},
            "nao_lidos": nao_lidos,
        }

    @app.put("/alertas/preferencias")
    def salvar_preferencias(dados: PreferenciasAlerta, usuario=Depends(usuario_atual), conexao=Depends(db)):
        _config_alerta(conexao, usuario["id"])
        conexao.execute(
            "UPDATE alertas_config SET novos_editais = ?, processos = ?, atas_ramo = ?, atas_processos = ? "
            "WHERE usuario_id = ?",
            (int(dados.novos_editais), int(dados.processos), int(dados.atas_ramo), int(dados.atas_processos),
             usuario["id"]))
        return {"ok": True}

    @app.post("/alertas/telefone")
    def cadastrar_telefone(dados: NovoTelefone, request: Request, usuario=Depends(usuario_atual), conexao=Depends(db)):
        if not dados.consentimento:
            raise HTTPException(422, "É preciso autorizar o envio de alertas pelo WhatsApp.")
        telefone = notificacoes.normalizar_telefone(dados.telefone)
        if telefone is None:
            raise HTTPException(422, "Informe um celular com DDD, ex.: (11) 98765-4321.")
        if not limite_codigos.permitir(str(usuario["id"])):
            raise HTTPException(429, "Muitos códigos pedidos. Tente de novo em uma hora.")
        codigo = f"{secrets.randbelow(10**6):06d}"
        expira = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(timespec="seconds")
        _config_alerta(conexao, usuario["id"])
        conexao.execute(
            "UPDATE alertas_config SET telefone = ?, telefone_verificado = 0, codigo_hash = ?, codigo_expira = ?, "
            "codigo_tentativas = 0 WHERE usuario_id = ?",
            (telefone, _hash_codigo(usuario["id"], codigo), expira, usuario["id"]))
        try:
            situacao = notificador.enviar_codigo(conexao, usuario["id"], telefone, codigo)
        except notificacoes.FalhaEnvio:
            raise HTTPException(502, "Não conseguimos enviar o código pelo WhatsApp agora. Tente mais tarde.") from None
        auditar(conexao, "whatsapp_codigo_enviado", request, usuario_id=usuario["id"])
        resposta = {"ok": True, "telefone": notificacoes.mascarar_telefone(telefone)}
        if situacao == "simulado":
            # Modo de teste (sem conta na Meta): nada é enviado, então mostramos o código.
            resposta["codigo_teste"] = codigo
        return resposta

    @app.post("/alertas/telefone/confirmar")
    def confirmar_telefone(dados: CodigoTelefone, request: Request, usuario=Depends(usuario_atual), conexao=Depends(db)):
        c = _config_alerta(conexao, usuario["id"])
        if not c["codigo_hash"] or not c["codigo_expira"]:
            raise HTTPException(422, "Peça um código primeiro.")
        if datetime.now(timezone.utc) > datetime.fromisoformat(c["codigo_expira"]):
            raise HTTPException(422, "O código expirou. Peça outro.")
        if c["codigo_tentativas"] >= 5:
            raise HTTPException(429, "Muitas tentativas. Peça um novo código.")
        if not hmac.compare_digest(c["codigo_hash"], _hash_codigo(usuario["id"], dados.codigo)):
            conexao.execute("UPDATE alertas_config SET codigo_tentativas = codigo_tentativas + 1 WHERE usuario_id = ?",
                            (usuario["id"],))
            raise HTTPException(422, "Código incorreto.")
        try:
            conexao.execute(
                "UPDATE alertas_config SET telefone_verificado = 1, consentimento_em = ?, codigo_hash = NULL, "
                "codigo_expira = NULL, codigo_tentativas = 0 WHERE usuario_id = ?",
                (datetime.now(timezone.utc).isoformat(timespec="seconds"), usuario["id"]))
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Este número já está em uso em outra conta.") from None
        auditar(conexao, "whatsapp_confirmado", request, usuario_id=usuario["id"])
        return {"ok": True}

    @app.delete("/alertas/telefone")
    def remover_telefone(request: Request, usuario=Depends(usuario_atual), conexao=Depends(db)):
        conexao.execute(
            "UPDATE alertas_config SET telefone = NULL, telefone_verificado = 0, consentimento_em = NULL, "
            "codigo_hash = NULL, codigo_expira = NULL WHERE usuario_id = ?", (usuario["id"],))
        conexao.execute("DELETE FROM mensagens_simuladas WHERE usuario_id = ?", (usuario["id"],))
        auditar(conexao, "whatsapp_removido", request, usuario_id=usuario["id"])
        return {"ok": True}

    @app.get("/alertas/eventos")
    def meus_eventos(usuario=Depends(usuario_atual), conexao=Depends(db)):
        linhas = conexao.execute(
            "SELECT id, tipo, edital_id, titulo, texto, link, criado, lido, whatsapp FROM eventos "
            "WHERE usuario_id = ? ORDER BY id DESC LIMIT 100", (usuario["id"],)).fetchall()
        return {"eventos": [dict(l) for l in linhas]}

    @app.post("/alertas/eventos/lidos")
    def marcar_lidos(usuario=Depends(usuario_atual), conexao=Depends(db)):
        conexao.execute("UPDATE eventos SET lido = 1 WHERE usuario_id = ?", (usuario["id"],))
        return {"ok": True}

    @app.get("/alertas/simuladas")
    def mensagens_de_teste(usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Modo de teste: mostra as mensagens que teriam ido para o WhatsApp do usuário."""
        if notificador.nome != "simulado":
            return {"mensagens": []}
        linhas = conexao.execute(
            "SELECT conteudo, criado FROM mensagens_simuladas WHERE usuario_id = ? ORDER BY id DESC LIMIT 30",
            (usuario["id"],)).fetchall()
        return {"mensagens": [dict(l) for l in linhas]}

    # Webhook da Meta: confirmação do endereço e mensagens recebidas ("SAIR").
    @app.get("/webhook/whatsapp")
    def webhook_verificar(request: Request):
        token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
        params = request.query_params
        if (token and params.get("hub.mode") == "subscribe"
                and hmac.compare_digest(params.get("hub.verify_token", ""), token)):
            return RespostaBruta(params.get("hub.challenge", "")[:100], media_type="text/plain")
        raise HTTPException(403, "Token inválido.")

    @app.post("/webhook/whatsapp")
    async def webhook_mensagem(request: Request):
        corpo = await request.body()
        if not notificacoes.assinatura_valida(os.environ.get("WHATSAPP_APP_SECRET", ""), corpo,
                                              request.headers.get("x-hub-signature-256")):
            raise HTTPException(403, "Assinatura inválida.")
        try:
            dados = json.loads(corpo)
        except ValueError:
            raise HTTPException(400, "JSON inválido.") from None
        saidas = []
        for entrada in dados.get("entry", []) if isinstance(dados, dict) else []:
            for mudanca in entrada.get("changes", []):
                for msg in (mudanca.get("value") or {}).get("messages", []) or []:
                    texto = ((msg.get("text") or {}).get("body") or "").strip().lower()
                    if texto in PALAVRAS_SAIR:
                        saidas.append(notificacoes.normalizar_telefone(str(msg.get("from", ""))))
        if saidas:
            conexao = banco.conectar(config.banco)
            try:
                for telefone in filter(None, saidas):
                    conexao.execute(
                        "UPDATE alertas_config SET telefone_verificado = 0, consentimento_em = NULL "
                        "WHERE telefone = ?", (telefone,))
                    auditar(conexao, "whatsapp_sair", request, detalhe="pediu para sair pelo WhatsApp")
            finally:
                conexao.close()
        return {"ok": True}

    # ------------------------------------------------------------------ site

    def pagina(nome: str):
        def servir():
            resposta = FileResponse(PASTA_SITE / f"{nome}.html", media_type="text/html; charset=utf-8")
            resposta.headers["Content-Security-Policy"] = CSP_PAGINAS
            resposta.headers["Cache-Control"] = "no-cache"
            return resposta
        return servir

    for caminho, nome in (("/", "index"), ("/cadastro", "cadastro"), ("/entrar", "entrar"),
                          ("/painel", "painel"), ("/ver", "edital"), ("/acompanhar", "funil"),
                          ("/alertas", "alertas")):
        app.add_api_route(caminho, pagina(nome), methods=["GET"], include_in_schema=False)
    app.mount("/static", StaticFiles(directory=PASTA_SITE / "static"), name="static")

    return app


def _app_padrao() -> FastAPI:
    return criar_app(Config.do_ambiente())


def __getattr__(nome: str):
    # `uvicorn radar.app:app` cria o app só quando pedido, para que importar o
    # módulo (nos testes, por exemplo) não exija RADAR_SEGREDO.
    if nome == "app":
        return _app_padrao()
    raise AttributeError(nome)
