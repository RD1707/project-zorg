# -*- coding: utf-8 -*-
"""
Utils package do jogo ZORG.
Contem utilitarios e funcoes auxiliares.
"""

from .error_handler import handle_exceptions, validate_not_none
from .logging_config import get_logger

# Importacoes opcionais
try:
    from .security import SecurityManager
except ImportError:
    SecurityManager = None

__all__ = [
    'handle_exceptions',
    'validate_not_none',
    'get_logger',
    'SecurityManager'
]