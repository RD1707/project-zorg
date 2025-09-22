"""
Configurações globais do jogo ZORG.
Define paths, configurações de sistema e preferências do usuário.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict

# Paths do sistema
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = Path.home() / ".zorg"

# Garantir que o diretório de save existe
SAVE_DIR.mkdir(exist_ok=True)

GAME_CONFIG: Dict[str, Any] = {
    "name": "ZORG",
    "version": "1.0.0",
    "author": "Ramon Mendonça",
    "description": "Um RPG épico baseado em texto",
}

SAVE_CONFIG: Dict[str, Any] = {
    "save_file_name": "zorg_save.json",
    "backup_enabled": True,
    "max_backups": 5,
    "auto_save_interval": 300,
}

COMBAT_CONFIG: Dict[str, Any] = {
    "base_crit_chance": 15,
    "crit_multiplier": 1.75,
    "poison_max_turns": 5,
    "buff_max_turns": 10,
    "escape_base_chance": 60,
}

UI_CONFIG: Dict[str, Any] = {
    "animation_speed": 0.1,
    "text_scroll_delay": 0.05,
    "notification_timeout": 3.0,
    "theme": "dark",
}

LOG_CONFIG: Dict[str, Any] = {
    "level": os.getenv("ZORG_LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_enabled": True,
    "console_enabled": False,  # Desabilitado para interface limpa
    "debug_mode": os.getenv("ZORG_DEBUG", "false").lower() == "true",
    "max_log_files": 10,
    "max_file_size": 10 * 1024 * 1024,
}

DEV_CONFIG: Dict[str, Any] = {
    "debug_mode": os.getenv("ZORG_DEBUG", "false").lower() == "true",
    "profiling_enabled": False,
    "test_mode": False,
    "skip_intro": os.getenv("ZORG_SKIP_INTRO", "false").lower() == "true",
}

PERFORMANCE_CONFIG: Dict[str, Any] = {
    "cache_enabled": True,
    "cache_size": 1000,
    "lazy_loading": True,
    "preload_phases": True,
}


def get_save_path(filename: str = None) -> Path:
    if filename is None:
        filename = SAVE_CONFIG["save_file_name"]
    return SAVE_DIR / filename


def get_log_path() -> Path:
    log_dir = SAVE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)
    return log_dir


def is_debug_mode() -> bool:
    return DEV_CONFIG["debug_mode"]


def get_config(section: str) -> Dict[str, Any]:
    config_map = {
        "game": GAME_CONFIG,
        "save": SAVE_CONFIG,
        "combat": COMBAT_CONFIG,
        "ui": UI_CONFIG,
        "log": LOG_CONFIG,
        "dev": DEV_CONFIG,
        "performance": PERFORMANCE_CONFIG,
    }
    return config_map.get(section, {})


class GameSettings:
    """Gerenciador de configurações do usuário."""

    def __init__(self):
        self.settings_file = SAVE_DIR / "user_settings.json"
        self._data = self._load_default_settings()
        self._load()

    def _load_default_settings(self) -> Dict[str, Any]:
        """Carrega as configurações padrão."""
        return {
            # Gameplay
            "text_speed": "normal",
            "auto_save": True,
            "confirm_actions": True,
            # Audio
            "background_music": True,
            "sound_effects": True,
            "master_volume": "75",
            # Interface
            "theme": "dark",
            "show_tooltips": True,
            # Controles
            "key_bindings": {
                "quit": "q",
                "menu": "escape",
                "confirm": "enter",
                "cancel": "escape",
            },
        }

    def _load(self) -> None:
        """Carrega configurações do arquivo."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    saved_settings = json.load(f)
                    # Mesclar com configurações padrão
                    self._data.update(saved_settings)
            except Exception:
                # Em caso de erro, manter configurações padrão
                pass

    def get(self, key: str, default=None):
        """Obtém uma configuração."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Define uma configuração."""
        self._data[key] = value

    def save(self) -> bool:
        """Salva as configurações no arquivo."""
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            # Falha silenciosa - retorna False para indicar erro
            return False

    def reset_to_defaults(self) -> None:
        """Restaura configurações padrão."""
        self._data = self._load_default_settings()

    def get_text_speed_delay(self) -> float:
        """
        Converte configuração de velocidade para delay em segundos.

        Returns:
            float: Delay em segundos entre caracteres (0.0 = instantâneo)
        """
        SPEED_DELAYS = {
            "very_slow": 0.1,
            "slow": 0.05,
            "normal": 0.025,
            "fast": 0.01,
            "instant": 0.0,
        }
        current_speed = self.get("text_speed", "normal")
        return SPEED_DELAYS.get(current_speed, 0.025)
