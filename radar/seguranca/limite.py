"""Limite de requisições e de tentativas erradas por chave (IP, e-mail, usuário).

Guarda os contadores em memória, o que basta para um único processo (MVP).
Com mais de uma instância, trocar o armazenamento por Redis mantendo a mesma
interface.

Chaves sem eventos dentro da janela são apagadas: sem isso, um atacante que
inventa milhares de e-mails fazia a memória crescer para sempre.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict, deque

VARREDURA_A_CADA = 1000  # operações entre limpezas completas


class JanelaDeslizante:
    """Permite até ``limite`` eventos por chave a cada ``janela`` segundos."""

    def __init__(self, limite: int, janela: float, relogio=time.monotonic,
                 max_chaves: int = 100_000):
        self.limite = limite
        self.janela = janela
        self.max_chaves = max_chaves
        self._relogio = relogio
        self._eventos: OrderedDict[str, deque[float]] = OrderedDict()
        self._trava = threading.Lock()
        self._operacoes = 0

    def __len__(self) -> int:
        return len(self._eventos)

    # Os métodos com "_" assumem que a trava já está tomada.
    def _fila(self, chave: str, agora: float) -> deque[float]:
        fila = self._eventos.get(chave)
        if fila is None:
            return deque()
        while fila and agora - fila[0] >= self.janela:
            fila.popleft()
        if not fila:
            del self._eventos[chave]
        return fila

    def _anotar(self, chave: str, agora: float) -> None:
        fila = self._fila(chave, agora)
        fila.append(agora)
        self._eventos[chave] = fila
        # Acima do teto: descarta a chave mais antiga (custo constante).
        while len(self._eventos) > self.max_chaves:
            self._eventos.popitem(last=False)
        # Limpeza completa só depois de tantas operações quanto chaves
        # existentes: o custo médio por operação fica constante. (Varrer tudo a
        # cada operação deixaria um atacante travar a CPU.)
        self._operacoes += 1
        if self._operacoes >= max(VARREDURA_A_CADA, len(self._eventos)):
            self._operacoes = 0
            for chave_antiga in list(self._eventos):
                self._fila(chave_antiga, agora)

    def permitir(self, chave: str) -> bool:
        """Registra um evento e diz se ele está dentro do limite."""
        with self._trava:
            agora = self._relogio()
            if len(self._fila(chave, agora)) >= self.limite:
                return False
            self._anotar(chave, agora)
            return True

    def bloqueado(self, chave: str) -> bool:
        """Diz se a chave já atingiu o limite, sem registrar evento."""
        with self._trava:
            return len(self._fila(chave, self._relogio())) >= self.limite

    def registrar(self, chave: str) -> None:
        with self._trava:
            self._anotar(chave, self._relogio())

    def segundos_para_liberar(self, chave: str) -> int:
        with self._trava:
            agora = self._relogio()
            fila = self._fila(chave, agora)
            if len(fila) < self.limite:
                return 0
            return max(1, int(self.janela - (agora - fila[0])) + 1)

    def zerar(self, chave: str) -> None:
        with self._trava:
            self._eventos.pop(chave, None)
