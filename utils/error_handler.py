"""
Sistema de tratamento de erros robusto para o ZORG.
"""
import functools
import traceback
from typing import Any, Callable, TypeVar, Optional, Union
import logging

from core.exceptions import ZorgException
from utils.logging_config import get_logger, log_exception

logger = get_logger("error_handler")

F = TypeVar('F', bound=Callable[..., Any])


def handle_exceptions(
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    context: str = None
) -> Callable[[F], F]:
    """
    Decorator para tratamento automático de exceções.

    Args:
        default_return: Valor retornado em caso de erro
        log_errors: Se deve logar os erros
        reraise: Se deve re-lançar a exceção após o tratamento
        context: Contexto adicional para o log
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ZorgException as e:
                if log_errors:
                    log_exception(logger, e, context or func.__name__)
                if reraise:
                    raise
                return default_return
            except Exception as e:
                if log_errors:
                    log_exception(logger, e, context or func.__name__)
                if reraise:
                    raise ZorgException(f"Erro inesperado em {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    log_errors: bool = True,
    context: str = None,
    **kwargs
) -> Any:
    """
    Executa uma função de forma segura, tratando exceções.

    Args:
        func: Função para executar
        *args: Argumentos para a função
        default_return: Valor retornado em caso de erro
        log_errors: Se deve logar os erros
        context: Contexto adicional para o log
        **kwargs: Argumentos nomeados para a função
    """
    try:
        return func(*args, **kwargs)
    except ZorgException as e:
        if log_errors:
            log_exception(logger, e, context or func.__name__)
        return default_return
    except Exception as e:
        if log_errors:
            log_exception(logger, e, context or func.__name__)
        return default_return


class ErrorCollector:
    """Coletor de erros para operações em lote."""

    def __init__(self):
        self.errors: list[Exception] = []

    def add_error(self, error: Exception):
        """Adiciona um erro à coleção."""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Verifica se há erros coletados."""
        return len(self.errors) > 0

    def get_errors(self) -> list[Exception]:
        """Retorna a lista de erros."""
        return self.errors.copy()

    def clear(self):
        """Limpa a lista de erros."""
        self.errors.clear()

    def log_all_errors(self, logger: logging.Logger, context: str = "ErrorCollector"):
        """Loga todos os erros coletados."""
        for error in self.errors:
            log_exception(logger, error, context)


class RetryableOperation:
    """Wrapper para operações que podem ser tentadas novamente."""

    def __init__(self, max_attempts: int = 3, delay: float = 0.1):
        self.max_attempts = max_attempts
        self.delay = delay

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time

            last_exception = None
            for attempt in range(self.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Tentativa {attempt + 1} de {self.max_attempts} falhou para {func.__name__}: {e}"
                    )
                    if attempt < self.max_attempts - 1:
                        time.sleep(self.delay)

            # Se chegou aqui, todas as tentativas falharam
            log_exception(logger, last_exception, f"{func.__name__} (após {self.max_attempts} tentativas)")
            raise last_exception

        return wrapper


def validate_not_none(value: Any, name: str = "valor") -> Any:
    """Valida que um valor não é None."""
    if value is None:
        raise ValueError(f"{name} não pode ser None")
    return value


def validate_positive(value: Union[int, float], name: str = "valor") -> Union[int, float]:
    """Valida que um valor é positivo."""
    if value <= 0:
        raise ValueError(f"{name} deve ser positivo, recebido: {value}")
    return value


def validate_non_negative(value: Union[int, float], name: str = "valor") -> Union[int, float]:
    """Valida que um valor não é negativo."""
    if value < 0:
        raise ValueError(f"{name} não pode ser negativo, recebido: {value}")
    return value


def validate_in_range(value: Union[int, float], min_val: Union[int, float], max_val: Union[int, float], name: str = "valor") -> Union[int, float]:
    """Valida que um valor está dentro de um intervalo."""
    if not (min_val <= value <= max_val):
        raise ValueError(f"{name} deve estar entre {min_val} e {max_val}, recebido: {value}")
    return value


def validate_string_not_empty(value: str, name: str = "string") -> str:
    """Valida que uma string não está vazia."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} deve ser uma string não vazia")
    return value.strip()


# Decorator para validação automática de parâmetros
def validate_parameters(**validations):
    """
    Decorator para validação automática de parâmetros.

    Exemplo:
        @validate_parameters(nome=validate_string_not_empty, hp=validate_positive)
        def criar_personagem(nome: str, hp: int):
            pass
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Obter nomes dos parâmetros
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Aplicar validações
            for param_name, validator in validations.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        bound_args.arguments[param_name] = validator(value, param_name)
                    except Exception as e:
                        raise ValueError(f"Erro na validação do parâmetro '{param_name}' em {func.__name__}: {e}")

            return func(*bound_args.args, **bound_args.kwargs)
        return wrapper
    return decorator