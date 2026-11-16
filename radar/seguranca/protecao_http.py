"""Proteções aplicadas a toda requisição HTTP.

- ``LimiteDeCorpo``: recusa corpos acima do limite contando os bytes que
  realmente chegam. Conferir só o cabeçalho Content-Length não bastava: um
  envio "em pedaços" (Transfer-Encoding: chunked) não traz esse cabeçalho.
- ``ProtecaoHTTP``: cabeçalhos de segurança e proteção contra CSRF
  (requisições que mudam dados com o cookie de sessão só vindas de origens
  autorizadas).
"""

from __future__ import annotations

import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}
MENSAGEM_CORPO_GRANDE = "Requisição grande demais."

CABECALHOS = {
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cache-Control": "no-store",
}


class LimiteDeCorpo:
    """Middleware ASGI puro: interrompe a leitura assim que o corpo passa do limite."""

    def __init__(self, app, tamanho_max: int = 64 * 1024):
        self.app = app
        self.tamanho_max = tamanho_max

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        declarado = dict(scope.get("headers") or []).get(b"content-length")
        if declarado is not None and (not declarado.isdigit() or int(declarado) > self.tamanho_max):
            await self._recusar(send)
            return

        recebido = 0
        recusado = False
        resposta_iniciada = False

        async def receber():
            nonlocal recebido, recusado
            if recusado:
                return {"type": "http.disconnect"}
            mensagem = await receive()
            if mensagem["type"] == "http.request":
                recebido += len(mensagem.get("body", b""))
                if recebido > self.tamanho_max:
                    # Para de ler na hora: responde 413 e, para a aplicação, o
                    # cliente "desconectou" (o que ela tentar responder é descartado).
                    recusado = True
                    if not resposta_iniciada:
                        await self._recusar(send)
                    return {"type": "http.disconnect"}
            return mensagem

        async def enviar(mensagem):
            nonlocal resposta_iniciada
            if recusado:
                return
            if mensagem["type"] == "http.response.start":
                resposta_iniciada = True
            await send(mensagem)

        await self.app(scope, receber, enviar)

    async def _recusar(self, send):
        corpo = json.dumps({"erro": MENSAGEM_CORPO_GRANDE}).encode()
        cabecalhos = [(b"content-type", b"application/json"),
                      (b"content-length", str(len(corpo)).encode())]
        cabecalhos += [(k.lower().encode(), v.encode()) for k, v in CABECALHOS.items()]
        await send({"type": "http.response.start", "status": 413, "headers": cabecalhos})
        await send({"type": "http.response.body", "body": corpo})


class ProtecaoHTTP(BaseHTTPMiddleware):
    def __init__(self, app, *, origens_permitidas: list[str], https: bool, nome_cookie: str):
        super().__init__(app)
        self.origens = {o.rstrip("/") for o in origens_permitidas}
        self.https = https
        self.nome_cookie = nome_cookie

    async def dispatch(self, request, call_next):
        if request.method not in METODOS_SEGUROS and self.nome_cookie in request.cookies:
            origem = request.headers.get("origin") or ""
            if origem.rstrip("/") not in self.origens:
                return self._com_cabecalhos(JSONResponse({"erro": "Origem não autorizada."}, 403))
        resposta = await call_next(request)
        return self._com_cabecalhos(resposta)

    def _com_cabecalhos(self, resposta):
        for nome, valor in CABECALHOS.items():
            resposta.headers.setdefault(nome, valor)
        if self.https:
            resposta.headers.setdefault("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        return resposta
