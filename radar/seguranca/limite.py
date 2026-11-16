"""Limite de requisições e bloqueio temporário após tentativas de login erradas.

Guarda os contadores em memória, o que basta para um único processo (MVP).
Com mais de uma instância, trocar o armazenamento por Redis mantendo a mesma
interface.
"""

from __future__ import annotations

import threading
import time
from collections import defaultdict, deque


class JanelaDeslizante:
    """Permite até ``limite`` eventos por chave a cada ``janela`` segundos."""

    def __init__(self, limite: int, janela: float, relogio=time.monotonic):
        self.limite = limite
        self.janela = janela
        self._relogio = relogio
        self._eventos: dict[str, deque[float]] = defaultdict(deque)
        self._trava = threading.Lock()

    def _limpar(self, chave: str, agora: float) -> deque[float]:
        fila = self._eventos[chave]
        while fila and agora - fila[0] >= self.janela:
            fila.popleft()
        return fila

    def permitir(self, chave: str) -> bool:
        """Registra um evento e diz se ele está dentro do limite."""
        with self._trava:
            agora = self._relogio()
            fila = self._limpar(chave, agora)
            if len(fila) >= self.limite:
                return False
            fila.append(agora)
            return True

    def bloqueado(self, chave: str) -> bool:
        """Diz se a chave já atingiu o limite, sem registrar evento."""
        with self._trava:
            return len(self._limpar(chave, self._relogio())) >= self.limite

    def registrar(self, chave: str) -> None:
        with self._trava:
            agora = self._relogio()
            self._limpar(chave, agora).append(agora)

    def segundos_para_liberar(self, chave: str) -> int:
        with self._trava:
            agora = self._relogio()
            fila = self._limpar(chave, agora)
            if len(fila) < self.limite:
                return 0
            return max(1, int(self.janela - (agora - fila[0])) + 1)

    def zerar(self, chave: str) -> None:
        with self._trava:
            self._eventos.pop(chave, None)
