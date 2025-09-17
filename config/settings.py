from pathlib import Path
from typing import Dict, Any
import os

BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = Path.home() / ".zorg"

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
    "console_enabled": True,
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