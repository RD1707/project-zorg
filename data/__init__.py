# -*- coding: utf-8 -*-
"""
Data package do jogo ZORG.
Contem todos os bancos de dados de itens, equipamentos, inimigos, habilidades, etc.
"""

from .abilities import DB_HABILIDADES
from .enemies import DB_INIMIGOS
from .equipment import DB_EQUIPAMENTOS
from .items import DB_ITENS

# Importacoes opcionais para modulos que podem existir
try:
    from .npcs import DB_NPCS
except ImportError:
    DB_NPCS = {}

try:
    from .reward_tables import DB_REWARD_TABLES
except ImportError:
    DB_REWARD_TABLES = {}

__all__ = [
    "DB_EQUIPAMENTOS",
    "DB_ITENS",
    "DB_HABILIDADES",
    "DB_INIMIGOS",
    "DB_NPCS",
    "DB_REWARD_TABLES",
]
