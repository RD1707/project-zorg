from typing import Optional, Any


class ZorgException(Exception):

    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class GameEngineError(ZorgException):
    pass


class SaveLoadError(ZorgException):
    pass


class CombatError(ZorgException):
    pass


class InvalidActionError(ZorgException):
    pass


class DataValidationError(ZorgException):
    pass


class ConfigurationError(ZorgException):
    pass


class ResourceNotFoundError(ZorgException):

    def __init__(self, resource_type: str, resource_name: str):
        message = f"{resource_type} '{resource_name}' não foi encontrado"
        super().__init__(message, "RESOURCE_NOT_FOUND", {
            "resource_type": resource_type,
            "resource_name": resource_name
        })


class InsufficientResourcesError(ZorgException):

    def __init__(self, resource_type: str, required: int, available: int):
        message = f"{resource_type} insuficiente: necessário {required}, disponível {available}"
        super().__init__(message, "INSUFFICIENT_RESOURCES", {
            "resource_type": resource_type,
            "required": required,
            "available": available
        })


class CharacterStateError(ZorgException):
    pass


class PhaseError(ZorgException):
    pass


class UIError(ZorgException):
    pass