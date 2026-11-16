"""Proteções aplicadas a toda requisição HTTP.

- Cabeçalhos de segurança (CSP, HSTS, nosniff, anti-clickjacking).
- Limite de tamanho do corpo da requisição.
- Proteção contra CSRF: requisições que mudam dados e usam o cookie de
  sessão precisam vir de uma origem autorizada.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}

CABECALHOS = {
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cache-Control": "no-store",
}


class ProtecaoHTTP(BaseHTTPMiddleware):
    def __init__(self, app, *, origens_permitidas: list[str], https: bool,
                 nome_cookie: str, tamanho_max_corpo: int = 64 * 1024):
        super().__init__(app)
        self.origens = {o.rstrip("/") for o in origens_permitidas}
        self.https = https
        self.nome_cookie = nome_cookie
        self.tamanho_max = tamanho_max_corpo

    async def dispatch(self, request, call_next):
        tamanho = request.headers.get("content-length")
        if tamanho is not None and (not tamanho.isdigit() or int(tamanho) > self.tamanho_max):
            return self._com_cabecalhos(JSONResponse({"erro": "Requisição grande demais."}, 413))

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
