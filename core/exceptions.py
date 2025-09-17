"""
Exceções customizadas para o jogo ZORG.
"""
from typing import Optional, Any


class ZorgException(Exception):
    """Exceção base para todos os erros específicos do ZORG."""

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class GameEngineError(ZorgException):
    """Exceção para erros do motor do jogo."""
    pass


class SaveLoadError(ZorgException):
    """Exceção para erros de save/load."""
    pass


class CombatError(ZorgException):
    """Exceção para erros durante o combate."""
    pass


class InvalidActionError(ZorgException):
    """Exceção para ações inválidas do jogador."""
    pass


class DataValidationError(ZorgException):
    """Exceção para erros de validação de dados."""
    pass


class ConfigurationError(ZorgException):
    """Exceção para erros de configuração."""
    pass


class ResourceNotFoundError(ZorgException):
    """Exceção para recursos não encontrados (inimigos, itens, etc.)."""

    def __init__(self, resource_type: str, resource_name: str):
        message = f"{resource_type} '{resource_name}' não foi encontrado"
        super().__init__(message, "RESOURCE_NOT_FOUND", {
            "resource_type": resource_type,
            "resource_name": resource_name
        })


class InsufficientResourcesError(ZorgException):
    """Exceção para falta de recursos (MP, HP, itens, etc.)."""

    def __init__(self, resource_type: str, required: int, available: int):
        message = f"{resource_type} insuficiente: necessário {required}, disponível {available}"
        super().__init__(message, "INSUFFICIENT_RESOURCES", {
            "resource_type": resource_type,
            "required": required,
            "available": available
        })


class CharacterStateError(ZorgException):
    """Exceção para estados inválidos do personagem."""
    pass


class PhaseError(ZorgException):
    """Exceção para erros relacionados às fases do jogo."""
    pass


class UIError(ZorgException):
    """Exceção para erros da interface do usuário."""
    pass