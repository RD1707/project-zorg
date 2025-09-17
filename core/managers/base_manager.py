"""
Classe base para todos os managers do jogo.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from utils.logging_config import get_logger


class BaseManager(ABC):
    """Classe base para todos os managers."""

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"manager.{name}")
        self._initialized = False

    def initialize(self) -> bool:
        """Inicializa o manager."""
        if self._initialized:
            self.logger.warning(f"Manager {self.name} já foi inicializado")
            return True

        try:
            self._do_initialize()
            self._initialized = True
            self.logger.info(f"Manager {self.name} inicializado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar manager {self.name}: {e}")
            return False

    @abstractmethod
    def _do_initialize(self) -> None:
        """Implementação específica da inicialização."""
        pass

    def is_initialized(self) -> bool:
        """Verifica se o manager foi inicializado."""
        return self._initialized

    def shutdown(self) -> None:
        """Finaliza o manager."""
        if not self._initialized:
            return

        try:
            self._do_shutdown()
            self._initialized = False
            self.logger.info(f"Manager {self.name} finalizado")
        except Exception as e:
            self.logger.error(f"Erro ao finalizar manager {self.name}: {e}")

    def _do_shutdown(self) -> None:
        """Implementação específica da finalização."""
        pass

    def get_status(self) -> Dict[str, Any]:
        """Retorna o status do manager."""
        return {
            "name": self.name,
            "initialized": self._initialized,
        }