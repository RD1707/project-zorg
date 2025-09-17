"""
Utilitários de segurança para o jogo ZORG.
"""
import re
import json
import hashlib
import secrets
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from utils.logging_config import get_logger
from core.exceptions import DataValidationError

logger = get_logger("security")


class DataValidator:
    """Validador de dados para prevenir ataques e corrupção."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo removendo caracteres perigosos."""
        # Remover caracteres perigosos
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Remover caracteres de controle
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
        # Limitar tamanho
        sanitized = sanitized[:100]
        # Garantir que não seja vazio
        if not sanitized.strip():
            sanitized = "default_filename"

        return sanitized.strip()

    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Valida estrutura básica de JSON."""
        if not isinstance(data, dict):
            raise DataValidationError("Dados devem ser um objeto JSON")

        for field in required_fields:
            if field not in data:
                raise DataValidationError(f"Campo obrigatório '{field}' não encontrado")

        return True

    @staticmethod
    def validate_numeric_range(value: Union[int, float], min_val: Union[int, float],
                             max_val: Union[int, float], field_name: str) -> bool:
        """Valida se um valor numérico está dentro do intervalo esperado."""
        if not isinstance(value, (int, float)):
            raise DataValidationError(f"{field_name} deve ser numérico")

        if not (min_val <= value <= max_val):
            raise DataValidationError(
                f"{field_name} deve estar entre {min_val} e {max_val}, valor: {value}"
            )

        return True

    @staticmethod
    def validate_string_length(value: str, min_len: int, max_len: int, field_name: str) -> bool:
        """Valida comprimento de string."""
        if not isinstance(value, str):
            raise DataValidationError(f"{field_name} deve ser uma string")

        if not (min_len <= len(value) <= max_len):
            raise DataValidationError(
                f"{field_name} deve ter entre {min_len} e {max_len} caracteres"
            )

        return True

    @staticmethod
    def validate_no_script_injection(value: str, field_name: str) -> bool:
        """Verifica se não há tentativas de injeção de script."""
        dangerous_patterns = [
            r'<script',
            r'javascript:',
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__',
            r'\.system\(',
            r'os\.',
            r'subprocess\.',
        ]

        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                raise DataValidationError(f"Conteúdo perigoso detectado em {field_name}")

        return True


class SaveFileValidator:
    """Validador específico para arquivos de save."""

    @staticmethod
    def validate_save_data(data: Dict[str, Any]) -> bool:
        """Valida dados de save completos."""
        # Validar estrutura básica
        required_fields = ["version", "metadata", "player", "checksum"]
        DataValidator.validate_json_structure(data, required_fields)

        # Validar jogador
        SaveFileValidator.validate_player_data(data["player"])

        # Validar checksum
        SaveFileValidator.validate_checksum(data)

        logger.debug("Dados de save validados com sucesso")
        return True

    @staticmethod
    def validate_player_data(player_data: Dict[str, Any]) -> bool:
        """Valida dados específicos do jogador."""
        required_fields = ["nome", "hp", "hp_max", "mp", "mp_max", "nivel", "xp"]
        DataValidator.validate_json_structure(player_data, required_fields)

        # Validar nome
        DataValidator.validate_string_length(player_data["nome"], 1, 50, "nome")
        DataValidator.validate_no_script_injection(player_data["nome"], "nome")

        # Validar stats
        DataValidator.validate_numeric_range(player_data["hp"], 0, 9999, "HP")
        DataValidator.validate_numeric_range(player_data["hp_max"], 1, 9999, "HP máximo")
        DataValidator.validate_numeric_range(player_data["mp"], 0, 9999, "MP")
        DataValidator.validate_numeric_range(player_data["mp_max"], 1, 9999, "MP máximo")
        DataValidator.validate_numeric_range(player_data["nivel"], 1, 100, "nível")
        DataValidator.validate_numeric_range(player_data["xp"], 0, 999999, "XP")

        # Validar relações lógicas
        if player_data["hp"] > player_data["hp_max"]:
            raise DataValidationError("HP não pode ser maior que HP máximo")

        if player_data["mp"] > player_data["mp_max"]:
            raise DataValidationError("MP não pode ser maior que MP máximo")

        # Validar inventário se presente
        if "inventario" in player_data:
            SaveFileValidator.validate_inventory_data(player_data["inventario"])

        return True

    @staticmethod
    def validate_inventory_data(inventory_data: List[Dict[str, Any]]) -> bool:
        """Valida dados do inventário."""
        if not isinstance(inventory_data, list):
            raise DataValidationError("Inventário deve ser uma lista")

        if len(inventory_data) > 100:  # Limite razoável
            raise DataValidationError("Inventário muito grande")

        for item in inventory_data:
            if not isinstance(item, dict):
                raise DataValidationError("Item do inventário deve ser um objeto")

            required_fields = ["nome", "quantidade"]
            DataValidator.validate_json_structure(item, required_fields)

            DataValidator.validate_string_length(item["nome"], 1, 100, "nome do item")
            DataValidator.validate_no_script_injection(item["nome"], "nome do item")
            DataValidator.validate_numeric_range(item["quantidade"], 1, 999, "quantidade")

        return True

    @staticmethod
    def validate_checksum(data: Dict[str, Any]) -> bool:
        """Valida checksum dos dados."""
        if "checksum" not in data:
            raise DataValidationError("Checksum não encontrado")

        # Recalcular checksum
        player_data = data["player"]
        checksum_data = json.dumps(player_data, sort_keys=True)
        expected_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()

        if data["checksum"] != expected_checksum:
            raise DataValidationError("Checksum inválido - dados podem estar corrompidos")

        return True


class FilePathValidator:
    """Validador para caminhos de arquivo."""

    @staticmethod
    def validate_save_path(file_path: Path) -> bool:
        """Valida caminho de arquivo de save."""
        # Verificar se é um caminho absoluto e está em local seguro
        if not file_path.is_absolute():
            raise DataValidationError("Caminho deve ser absoluto")

        # Verificar se não tenta sair do diretório permitido
        try:
            file_path.resolve()
        except (OSError, ValueError):
            raise DataValidationError("Caminho de arquivo inválido")

        # Verificar extensão
        if file_path.suffix.lower() != '.json':
            raise DataValidationError("Arquivo deve ter extensão .json")

        # Verificar tamanho do nome
        if len(file_path.name) > 255:
            raise DataValidationError("Nome do arquivo muito longo")

        return True

    @staticmethod
    def is_path_traversal_attempt(path_str: str) -> bool:
        """Detecta tentativas de path traversal."""
        dangerous_patterns = [
            '..',
            '~',
            '/etc/',
            '/root/',
            '/home/',
            'C:\\',
            'D:\\',
            '%',
            '$'
        ]

        path_lower = path_str.lower()
        return any(pattern in path_lower for pattern in dangerous_patterns)


class InputSanitizer:
    """Sanitizador para entradas do usuário."""

    @staticmethod
    def sanitize_player_name(name: str) -> str:
        """Sanitiza nome do jogador."""
        if not isinstance(name, str):
            raise DataValidationError("Nome deve ser uma string")

        # Remover espaços extras
        name = name.strip()

        # Validar comprimento
        if len(name) == 0:
            raise DataValidationError("Nome não pode estar vazio")

        if len(name) > 50:
            name = name[:50]

        # Remover caracteres perigosos
        name = re.sub(r'[<>"\'/\\]', '', name)

        # Verificar injeção
        DataValidator.validate_no_script_injection(name, "nome")

        return name

    @staticmethod
    def sanitize_numeric_input(value: Any, min_val: int = 0, max_val: int = 999999) -> int:
        """Sanitiza entrada numérica."""
        try:
            num_value = int(value)
        except (ValueError, TypeError):
            raise DataValidationError("Valor deve ser numérico")

        if not (min_val <= num_value <= max_val):
            raise DataValidationError(f"Valor deve estar entre {min_val} e {max_val}")

        return num_value


def generate_secure_token(length: int = 32) -> str:
    """Gera token seguro para uso em identificadores."""
    return secrets.token_hex(length)


def hash_data(data: str) -> str:
    """Cria hash seguro de dados."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def verify_file_integrity(file_path: Path, expected_hash: str) -> bool:
    """Verifica integridade de arquivo usando hash."""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash == expected_hash
    except (IOError, OSError):
        return False


def secure_delete_file(file_path: Path) -> bool:
    """Remove arquivo de forma segura."""
    try:
        if file_path.exists() and file_path.is_file():
            # Sobrescrever com dados aleatórios antes de deletar
            file_size = file_path.stat().st_size
            with open(file_path, 'wb') as f:
                f.write(secrets.token_bytes(file_size))

            file_path.unlink()
            return True
    except (IOError, OSError) as e:
        logger.error(f"Erro ao deletar arquivo seguramente: {e}")
        return False

    return False