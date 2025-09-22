from abc import ABC, abstractmethod
from typing import Any, Dict

from utils.logging_config import get_logger


class BaseManager(ABC):

    def __init__(self, name: str):
        self.name = name
        self.logger = get_logger(f"manager.{name}")
        self._initialized = False

    def initialize(self) -> bool:
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
        pass

    def is_initialized(self) -> bool:
        return self._initialized

    def shutdown(self) -> None:
        if not self._initialized:
            return

        try:
            self._do_shutdown()
            self._initialized = False
            self.logger.info(f"Manager {self.name} finalizado")
        except Exception as e:
            self.logger.error(f"Erro ao finalizar manager {self.name}: {e}")

    def _do_shutdown(self) -> None:
        pass

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initialized": self._initialized,
        }
