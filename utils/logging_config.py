"""
Configuração do sistema de logging para o jogo ZORG.
"""

import logging
import logging.handlers
import sys
from typing import Optional

from config.settings import LOG_CONFIG, get_log_path


class ZorgLogger:
    """Classe singleton para gerenciar o sistema de logging do ZORG."""

    _instance: Optional["ZorgLogger"] = None
    _initialized = False

    def __new__(cls) -> "ZorgLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            ZorgLogger._initialized = True

    def _setup_logging(self) -> None:
        """Configura o sistema de logging."""
        # Configuração do logger raiz
        self.logger = logging.getLogger("zorg")
        self.logger.setLevel(getattr(logging, LOG_CONFIG["level"].upper()))

        # Limpar handlers existentes
        self.logger.handlers.clear()

        # Formatter
        formatter = logging.Formatter(LOG_CONFIG["format"])

        # Console handler - Desabilitado para manter interface limpa
        # Durante o jogo, logs ficam apenas nos arquivos
        if LOG_CONFIG["console_enabled"] and LOG_CONFIG.get("debug_mode", False):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.WARNING)  # Apenas warnings e erros críticos
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File handler
        if LOG_CONFIG["file_enabled"]:
            log_file = get_log_path() / "zorg.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=LOG_CONFIG["max_file_size"],
                backupCount=LOG_CONFIG["max_log_files"],
                encoding="utf-8",
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # Error file handler
        error_file = get_log_path() / "zorg_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_file,
            maxBytes=LOG_CONFIG["max_file_size"],
            backupCount=LOG_CONFIG["max_log_files"],
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)

    def get_logger(self, name: str = None) -> logging.Logger:
        """Retorna um logger com o nome especificado."""
        if name:
            return logging.getLogger(f"zorg.{name}")
        return self.logger


# Instância global do logger
_zorg_logger = ZorgLogger()


def get_logger(name: str = None) -> logging.Logger:
    """Função conveniente para obter um logger."""
    return _zorg_logger.get_logger(name)


def log_exception(logger: logging.Logger, exception: Exception, context: str = None):
    """Loga uma exceção com contexto adicional."""
    if context:
        logger.error(
            f"Exceção em {context}: {type(exception).__name__}: {exception}",
            exc_info=True,
        )
    else:
        logger.error(f"Exceção: {type(exception).__name__}: {exception}", exc_info=True)


def log_performance(logger: logging.Logger, operation: str, duration: float):
    """Loga informações de performance."""
    logger.debug(f"Performance - {operation}: {duration:.4f}s")


def log_user_action(logger: logging.Logger, action: str, details: dict = None):
    """Loga ações do usuário."""
    if details:
        logger.info(f"Ação do usuário: {action} | Detalhes: {details}")
    else:
        logger.info(f"Ação do usuário: {action}")


def log_game_event(logger: logging.Logger, event: str, details: dict = None):
    """Loga eventos do jogo."""
    if details:
        logger.info(f"Evento do jogo: {event} | Detalhes: {details}")
    else:
        logger.info(f"Evento do jogo: {event}")


class ContextLogger:
    """Logger com contexto automático."""

    def __init__(self, logger: logging.Logger, context: str):
        self.logger = logger
        self.context = context

    def debug(self, message: str, **kwargs):
        self.logger.debug(f"[{self.context}] {message}", **kwargs)

    def info(self, message: str, **kwargs):
        self.logger.info(f"[{self.context}] {message}", **kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(f"[{self.context}] {message}", **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(f"[{self.context}] {message}", **kwargs)

    def exception(self, message: str, **kwargs):
        self.logger.exception(f"[{self.context}] {message}", **kwargs)


def get_context_logger(name: str, context: str) -> ContextLogger:
    """Retorna um logger com contexto automático."""
    return ContextLogger(get_logger(name), context)
