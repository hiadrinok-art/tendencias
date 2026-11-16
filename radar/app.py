"""API do Radar de Editais: contas, sessões e dados do usuário, com a camada de segurança.

Rodar localmente:
    RADAR_SEGREDO=... RADAR_HTTPS=0 RADAR_ORIGENS=http://localhost:3000 \
        uvicorn radar.app:app --no-server-header --no-proxy-headers
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Literal

from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import banco, classificador
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


def criar_app(config: Config) -> FastAPI:
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
                     usuario=Depends(usuario_atual), conexao=Depends(db)):
        """Editais com propostas abertas no ramo, nas UFs e nas palavras-chave do usuário."""
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
        escolhidos = [
            l for l in linhas
            if ramos & set(json.loads(l["ramos"])) or (palavras and classificador.casa_palavras(l["objeto"], palavras))
        ]
        todos = [_edital_publico(l, agora) for l in escolhidos]
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
        dados = _edital_publico(linha, datetime.now(timezone.utc))
        dados["avaliacao"] = None if avaliacao is None else bool(avaliacao["serve"])
        return dados

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

    # ------------------------------------------------------------------ site

    def pagina(nome: str):
        def servir():
            resposta = FileResponse(PASTA_SITE / f"{nome}.html", media_type="text/html; charset=utf-8")
            resposta.headers["Content-Security-Policy"] = CSP_PAGINAS
            resposta.headers["Cache-Control"] = "no-cache"
            return resposta
        return servir

    for caminho, nome in (("/", "index"), ("/cadastro", "cadastro"), ("/entrar", "entrar"),
                          ("/painel", "painel"), ("/ver", "edital")):
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
