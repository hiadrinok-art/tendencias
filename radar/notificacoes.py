"""Envio de mensagens no WhatsApp.

Dois modos, escolhidos pelas variáveis de ambiente:

- **WhatsApp Cloud API (Meta)**: com ``WHATSAPP_TOKEN`` e ``WHATSAPP_PHONE_ID``.
  Mensagens que a empresa inicia precisam de *modelos* (templates) aprovados
  pela Meta; os nomes vêm de ``WHATSAPP_MODELO_CODIGO`` e
  ``WHATSAPP_MODELO_ALERTA`` (texto sugerido em docs/WHATSAPP.md).
- **Simulação** (padrão, sem essas variáveis): nada sai do servidor; a
  mensagem é gravada na tabela ``mensagens_simuladas``. Serve para
  desenvolver e testar sem conta na Meta.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import re
from datetime import datetime, timezone

import httpx

log = logging.getLogger("radar.notificacoes")

MAX_PARAMETRO = 900   # a Meta limita o texto de cada variável do modelo


class FalhaEnvio(RuntimeError):
    pass


def normalizar_telefone(texto: str) -> str | None:
    """Celular brasileiro em formato E.164 sem '+' (ex.: 5511987654321), ou None."""
    d = re.sub(r"\D", "", texto or "")
    if d.startswith("55") and len(d) in (12, 13):
        d = d[2:]
    if len(d) == 11 and d[2] == "9" and d[0] != "0":  # DDD + 9 + 8 dígitos
        return "55" + d
    return None


def mascarar_telefone(telefone: str | None) -> str | None:
    if not telefone:
        return None
    return f"+{telefone[:2]} ({telefone[2:4]}) *****-{telefone[-4:]}"


def _parametro(texto: str) -> str:
    """A Meta recusa variáveis com quebra de linha, tabulação ou 4+ espaços seguidos."""
    texto = re.sub(r"[\r\n\t]+", " · ", texto or "")
    texto = re.sub(r" {4,}", "   ", texto).strip()
    return texto[:MAX_PARAMETRO]


class Notificador:
    nome = "base"

    def enviar_codigo(self, conexao, usuario_id: int, telefone: str, codigo: str) -> str:
        raise NotImplementedError

    def enviar_alerta(self, conexao, usuario_id: int, telefone: str, titulo: str, texto: str, link: str) -> str:
        raise NotImplementedError


class NotificadorSimulado(Notificador):
    """Não envia nada: grava a mensagem no banco (aparece na página de alertas)."""

    nome = "simulado"

    def _gravar(self, conexao, usuario_id, telefone, conteudo):
        conexao.execute(
            "INSERT INTO mensagens_simuladas (usuario_id, telefone, conteudo, criado) VALUES (?, ?, ?, ?)",
            (usuario_id, telefone, conteudo, datetime.now(timezone.utc).isoformat(timespec="seconds")))
        log.info("[WhatsApp simulado] para %s: %s", mascarar_telefone(telefone), conteudo[:80])
        return "simulado"

    def enviar_codigo(self, conexao, usuario_id, telefone, codigo):
        return self._gravar(conexao, usuario_id, telefone, f"{codigo} é o seu código de verificação do Radar de Editais.")

    def enviar_alerta(self, conexao, usuario_id, telefone, titulo, texto, link):
        return self._gravar(conexao, usuario_id, telefone, f"Radar de Editais: {_parametro(titulo)}\n\n{_parametro(texto)}\n\n{link}")


class NotificadorWhatsAppCloud(Notificador):
    """WhatsApp Cloud API da Meta (graph.facebook.com)."""

    nome = "whatsapp"

    def __init__(self, token: str, phone_id: str, modelo_codigo: str, modelo_alerta: str,
                 versao: str = "v21.0", idioma: str = "pt_BR", cliente: httpx.Client | None = None):
        self.url = f"https://graph.facebook.com/{versao}/{phone_id}/messages"
        self.token = token
        self.modelo_codigo = modelo_codigo
        self.modelo_alerta = modelo_alerta
        self.idioma = idioma
        self.cliente = cliente or httpx.Client(timeout=20)

    def _enviar(self, telefone: str, modelo: str, componentes: list) -> str:
        corpo = {
            "messaging_product": "whatsapp", "to": telefone, "type": "template",
            "template": {"name": modelo, "language": {"code": self.idioma}, "components": componentes},
        }
        try:
            r = self.cliente.post(self.url, json=corpo, headers={"Authorization": f"Bearer {self.token}"})
        except httpx.HTTPError as erro:
            raise FalhaEnvio(f"sem conexão com a Meta: {type(erro).__name__}") from erro
        if r.status_code >= 400:
            # A resposta de erro da Meta não traz dados do usuário; guardamos só o código.
            try:
                codigo = r.json().get("error", {}).get("code")
            except ValueError:
                codigo = None
            raise FalhaEnvio(f"Meta recusou (HTTP {r.status_code}, código {codigo})")
        return "enviado"

    def enviar_codigo(self, conexao, usuario_id, telefone, codigo):
        # Modelo da categoria AUTENTICAÇÃO: código no corpo e no botão "copiar código".
        return self._enviar(telefone, self.modelo_codigo, [
            {"type": "body", "parameters": [{"type": "text", "text": codigo}]},
            {"type": "button", "sub_type": "url", "index": "0", "parameters": [{"type": "text", "text": codigo}]},
        ])

    def enviar_alerta(self, conexao, usuario_id, telefone, titulo, texto, link):
        return self._enviar(telefone, self.modelo_alerta, [
            {"type": "body", "parameters": [
                {"type": "text", "text": _parametro(titulo)},
                {"type": "text", "text": _parametro(texto)},
                {"type": "text", "text": _parametro(link)},
            ]},
        ])


def do_ambiente() -> Notificador:
    token = os.environ.get("WHATSAPP_TOKEN", "")
    phone_id = os.environ.get("WHATSAPP_PHONE_ID", "")
    if token and phone_id:
        return NotificadorWhatsAppCloud(
            token, phone_id,
            modelo_codigo=os.environ.get("WHATSAPP_MODELO_CODIGO", "radar_codigo"),
            modelo_alerta=os.environ.get("WHATSAPP_MODELO_ALERTA", "radar_alerta"),
            versao=os.environ.get("WHATSAPP_API_VERSAO", "v21.0"),
        )
    return NotificadorSimulado()


def assinatura_valida(segredo_app: str, corpo: bytes, cabecalho: str | None) -> bool:
    """Confere o X-Hub-Signature-256 que a Meta manda nos webhooks."""
    if not segredo_app or not cabecalho or not cabecalho.startswith("sha256="):
        return False
    esperado = hmac.new(segredo_app.encode(), corpo, hashlib.sha256).hexdigest()
    return hmac.compare_digest(esperado, cabecalho[7:])
