"""API do Radar de Editais: contas, sessões e dados do usuário, com a camada de segurança.

Rodar localmente:
    RADAR_SEGREDO=... RADAR_HTTPS=0 RADAR_ORIGENS=http://localhost:3000 \
        uvicorn radar.app:app --reload
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import banco
from .config import Config
from .seguranca import auditoria, senhas, sessoes, validacao
from .seguranca.limite import JanelaDeslizante
from .seguranca.protecao_http import ProtecaoHTTP

Ramo = Literal["ti", "obra", "eng", "limp", "alim", "saude", "mob"]
UF = Literal[
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA",
    "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
]

ERRO_LOGIN = "E-mail ou senha incorretos."


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


def criar_app(config: Config) -> FastAPI:
    app = FastAPI(title="Radar de Editais", docs_url=None, redoc_url=None, openapi_url=None)
    conexao = banco.conectar(config.banco)

    limite_ip_login = JanelaDeslizante(limite=20, janela=60)
    falhas_por_email = JanelaDeslizante(limite=5, janela=15 * 60)
    limite_ip_cadastro = JanelaDeslizante(limite=10, janela=60 * 60)

    app.add_middleware(
        ProtecaoHTTP, origens_permitidas=config.origens, https=config.https,
        nome_cookie=config.nome_cookie,
    )
    if config.origens:
        app.add_middleware(
            CORSMiddleware, allow_origins=config.origens, allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE"], allow_headers=["Content-Type"],
        )

    @app.exception_handler(RequestValidationError)
    async def erro_de_validacao(request: Request, erro: RequestValidationError):
        # A resposta padrão do FastAPI repete o valor enviado, o que devolveria
        # a senha no corpo do erro. Aqui só vão o campo e a mensagem.
        campos = [
            {"campo": ".".join(str(p) for p in e["loc"][1:]), "mensagem": e["msg"]}
            for e in erro.errors()
        ]
        return JSONResponse({"erro": "Dados inválidos.", "campos": campos}, status_code=422)

    def ip_de(request: Request) -> str:
        return request.client.host if request.client else ""

    def auditar(evento: str, request: Request, **extra) -> None:
        auditoria.registrar(conexao, evento, segredo=config.segredo, ip=ip_de(request), **extra)

    def token_de(request: Request) -> str | None:
        cabecalho = request.headers.get("authorization", "")
        if cabecalho.lower().startswith("bearer "):
            return cabecalho[7:].strip()
        return request.cookies.get(config.nome_cookie)

    def usuario_atual(request: Request):
        usuario_id = sessoes.validar(conexao, token_de(request))
        if usuario_id is None:
            raise HTTPException(401, "Faça login para continuar.")
        usuario = conexao.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
        if usuario is None:
            raise HTTPException(401, "Faça login para continuar.")
        return usuario

    def abrir_sessao(resposta: Response, usuario_id: int) -> None:
        token = sessoes.criar(conexao, usuario_id)
        resposta.set_cookie(
            config.nome_cookie, token, httponly=True, secure=config.https, samesite="strict",
            max_age=int(sessoes.DURACAO_MAXIMA.total_seconds()), path="/",
        )

    def conferir_senha_ou_401(usuario, senha: str) -> None:
        if not senhas.verificar(senha, usuario["senha_hash"]):
            raise HTTPException(401, "Senha incorreta.")

    @app.get("/saude")
    def saude():
        return {"ok": True}

    @app.post("/conta", status_code=201)
    def criar_conta(dados: NovaConta, request: Request, resposta: Response):
        if not limite_ip_cadastro.permitir(ip_de(request)):
            raise HTTPException(429, "Muitos cadastros a partir desta rede. Tente mais tarde.")
        if not dados.aceite_termos:
            raise HTTPException(422, "É preciso aceitar os termos de uso e a política de privacidade.")
        problemas = validacao.problemas_da_senha(dados.senha, dados.email)
        if problemas:
            raise HTTPException(422, " ".join(problemas))

        agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with banco.transacao(conexao):
            if conexao.execute("SELECT 1 FROM usuarios WHERE email = ?", (dados.email,)).fetchone():
                raise HTTPException(409, "Não foi possível criar a conta com esse e-mail.")
            cursor = conexao.execute(
                "INSERT INTO usuarios (email, senha_hash, cnpj, ramos, ufs, palavras_chave,"
                " termos_versao, termos_aceitos_em, criado_em) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (dados.email, senhas.gerar_hash(dados.senha), dados.cnpj,
                 json.dumps(sorted(set(dados.ramos))), json.dumps(sorted(set(dados.ufs))),
                 json.dumps(dados.palavras_chave), config.versao_termos, agora, agora),
            )
            auditar("conta_criada", request, usuario_id=cursor.lastrowid, email=dados.email)
            abrir_sessao(resposta, cursor.lastrowid)
        return {"ok": True}

    @app.post("/sessao")
    def entrar(dados: Login, request: Request, resposta: Response):
        ip = ip_de(request)
        email = validacao.normalizar_email(dados.email)
        if not limite_ip_login.permitir(ip):
            raise HTTPException(429, "Muitas tentativas. Aguarde um minuto.")
        if falhas_por_email.bloqueado(email):
            espera = falhas_por_email.segundos_para_liberar(email)
            auditar("login_bloqueado", request, email=email)
            raise HTTPException(
                429, "Conta bloqueada temporariamente por tentativas erradas.",
                headers={"Retry-After": str(espera)},
            )

        usuario = conexao.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        hash_salvo = usuario["senha_hash"] if usuario else senhas.HASH_FICTICIO
        senha_ok = senhas.verificar(dados.senha, hash_salvo)
        if usuario is None or not senha_ok:
            falhas_por_email.registrar(email)
            auditar("login_falhou", request, email=email)
            raise HTTPException(401, ERRO_LOGIN)

        falhas_por_email.zerar(email)
        if senhas.precisa_rehash(usuario["senha_hash"]):
            conexao.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                            (senhas.gerar_hash(dados.senha), usuario["id"]))
        abrir_sessao(resposta, usuario["id"])
        auditar("login_ok", request, usuario_id=usuario["id"], email=email)
        return {"ok": True}

    @app.delete("/sessao")
    def sair(request: Request, resposta: Response):
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
                     usuario=Depends(usuario_atual)):
        conferir_senha_ou_401(usuario, dados.senha_atual)
        problemas = validacao.problemas_da_senha(dados.senha_nova, usuario["email"])
        if problemas:
            raise HTTPException(422, " ".join(problemas))
        with banco.transacao(conexao):
            conexao.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?",
                            (senhas.gerar_hash(dados.senha_nova), usuario["id"]))
            sessoes.encerrar_todas(conexao, usuario["id"])
            auditar("senha_trocada", request, usuario_id=usuario["id"])
            abrir_sessao(resposta, usuario["id"])
        return {"ok": True}

    @app.get("/eu/dados")
    def exportar_dados(request: Request, usuario=Depends(usuario_atual)):
        """Direito de acesso (LGPD, art. 18): tudo o que guardamos sobre a conta."""
        auditar("dados_exportados", request, usuario_id=usuario["id"])
        dados = {k: usuario[k] for k in usuario.keys() if k != "senha_hash"}
        for campo in ("ramos", "ufs", "palavras_chave"):
            dados[campo] = json.loads(dados[campo])
        return dados

    @app.delete("/eu")
    def excluir_conta(dados: Confirmacao, request: Request, resposta: Response,
                      usuario=Depends(usuario_atual)):
        """Direito de eliminação (LGPD, art. 18): apaga a conta e todas as sessões."""
        conferir_senha_ou_401(usuario, dados.senha)
        with banco.transacao(conexao):
            conexao.execute("DELETE FROM usuarios WHERE id = ?", (usuario["id"],))
            auditar("conta_excluida", request, usuario_id=usuario["id"])
        resposta.delete_cookie(config.nome_cookie, path="/")
        return {"ok": True}

    app.state.conexao = conexao
    return app


def _app_padrao() -> FastAPI:
    return criar_app(Config.do_ambiente())


def __getattr__(nome: str):
    # `uvicorn radar.app:app` cria o app só quando pedido, para que importar o
    # módulo (nos testes, por exemplo) não exija RADAR_SEGREDO.
    if nome == "app":
        return _app_padrao()
    raise AttributeError(nome)
