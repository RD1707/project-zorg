# -*- coding: utf-8 -*-
"""
Screens package do jogo ZORG.
Contem todas as telas da interface do usuario.
"""

from .main_menu import MainMenuScreen
from .game_screen import GameScreen
from .combat_screen import CombatScreen
from .story_screen import StoryScreen
from .shop_screen import ShopScreen
from .victory_screen import VictoryScreen

# Importacoes opcionais para screens que podem existir
try:
    from .settings_screen import SettingsScreen
except ImportError:
    SettingsScreen = None

try:
    from .item_screen import ItemScreen
except ImportError:
    ItemScreen = None

try:
    from .skill_screen import SkillScreen
except ImportError:
    SkillScreen = None

__all__ = [
    'MainMenuScreen',
    'GameScreen',
    'CombatScreen',
    'StoryScreen',
    'ShopScreen',
    'VictoryScreen',
    'SettingsScreen',
    'ItemScreen',
    'SkillScreen'
]