"""Classifica editais por ramo a partir do texto do objeto (palavras-chave).

É a etapa simples do roadmap; a classificação por IA/CNAE vem na fase 2.
"""

from __future__ import annotations

import re
import unicodedata

RAMOS = {
    "ti": "TI e software",
    "obra": "Construção civil",
    "eng": "Engenharia",
    "limp": "Limpeza e conservação",
    "alim": "Alimentação",
    "saude": "Saúde",
    "mob": "Móveis e escritório",
}

_PADROES = {
    "ti": r"software|informatica|tecnologia da informacao|\btic\b|\bti\b|licenc\w* de uso|"
          r"\bcomputador(es)?\b|notebook|servidor(es)? (rack|de dados)|rede de dados|data ?center|nuvem|"
          r"\bsaas\b|backup|sistema (de gestao|informatizado|integrado)|desenvolvimento de sistema|"
          r"impressora|ativos de rede|switch(es)?\b|firewall",
    "obra": r"(?<!mao de )\bobras?\b|construcao|reforma|pavimenta|edificac|alvenaria|drenagem|recapeamento|"
            r"terraplenagem|ampliacao (da|do|de)",
    "eng": r"engenharia|projeto(s)? (arquitet|executivo|basico)|manutencao predial|topograf|"
           r"laudo tecnico|fiscalizacao de obra",
    "limp": r"limpeza|conservacao|higieniza|asseio|desinfec|material de limpeza|"
            r"coleta de residuos|jardinagem",
    "alim": r"generos alimenticios|alimentacao|aliment(os|icios)|merenda|refeic|hortifruti|"
            r"lanches?\b|carnes?\b|panificacao|cafe\b",
    "saude": r"medicament|hospitalar|\bsaude\b|odontolog|laborator|insumos medicos|"
             r"material medico|ortese|protese|exames",
    "mob": r"mobiliario|\bmoveis\b|cadeiras?\b|mesas?\b|armarios?\b|material de escritorio|"
           r"expediente|estantes?\b",
}
_COMPILADOS = {ramo: re.compile(p) for ramo, p in _PADROES.items()}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return re.sub(r"[\s\-_/]+", " ", sem_acento.lower())


def classificar(objeto: str) -> list[str]:
    texto = normalizar(objeto)
    return [ramo for ramo, padrao in _COMPILADOS.items() if padrao.search(texto)]


def casa_palavras(objeto: str, palavras: list[str]) -> bool:
    texto = normalizar(objeto)
    return any(normalizar(p) in texto for p in palavras)
