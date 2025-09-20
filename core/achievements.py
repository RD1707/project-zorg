"""
Sistema de conquistas/achievements para o jogo ZORG.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
from datetime import datetime
import json
from pathlib import Path

from core.managers.event_manager import subscribe_to_event, EventType
from config.settings import SAVE_DIR
from utils.logging_config import get_logger


class AchievementType(Enum):
    """Tipos de conquistas."""
    PROGRESS = "progress"      # Conquistas de progresso (matar X inimigos)
    MILESTONE = "milestone"    # Marcos importantes (chegar na fase X)
    COLLECTION = "collection"  # Coleção (ter X itens)
    SKILL = "skill"           # Habilidades (usar X vezes uma habilidade)
    SECRET = "secret"         # Conquistas secretas
    STORY = "story"           # Relacionadas à história


class AchievementRarity(Enum):
    """Raridade das conquistas."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class Achievement:
    """Representa uma conquista do jogo."""
    id: str
    name: str
    description: str
    type: AchievementType
    rarity: AchievementRarity
    points: int
    icon: str = "[*]"  # Asterisco para conquista
    hidden: bool = False
    progress_max: int = 1
    progress_current: int = 0
    unlocked: bool = False
    unlock_date: Optional[str] = None
    condition_check: Optional[Callable[[Dict[str, Any]], bool]] = field(default=None, compare=False)

    def __post_init__(self):
        """Inicialização após criação."""
        if self.progress_current >= self.progress_max:
            self.unlock()

    def update_progress(self, amount: int = 1) -> bool:
        """Atualiza o progresso da conquista."""
        if self.unlocked:
            return False

        self.progress_current = min(self.progress_current + amount, self.progress_max)

        if self.progress_current >= self.progress_max:
            self.unlock()
            return True

        return False

    def unlock(self) -> None:
        """Desbloqueia a conquista."""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_date = datetime.now().isoformat()
            self.progress_current = self.progress_max

    def get_progress_percentage(self) -> float:
        """Retorna o progresso em porcentagem."""
        if self.progress_max == 0:
            return 100.0
        return (self.progress_current / self.progress_max) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            "id": self.id,
            "progress_current": self.progress_current,
            "unlocked": self.unlocked,
            "unlock_date": self.unlock_date
        }

    @classmethod
    def from_dict(cls, achievement_template: 'Achievement', data: Dict[str, Any]) -> 'Achievement':
        """Cria uma conquista a partir de dados salvos."""
        achievement = Achievement(
            id=achievement_template.id,
            name=achievement_template.name,
            description=achievement_template.description,
            type=achievement_template.type,
            rarity=achievement_template.rarity,
            points=achievement_template.points,
            icon=achievement_template.icon,
            hidden=achievement_template.hidden,
            progress_max=achievement_template.progress_max,
            condition_check=achievement_template.condition_check
        )

        achievement.progress_current = data.get("progress_current", 0)
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlock_date = data.get("unlock_date")

        return achievement


class AchievementManager:
    """Gerenciador de conquistas."""

    def __init__(self):
        self.logger = get_logger("achievements")
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked_achievements: List[str] = []
        self.save_file = SAVE_DIR / "achievements.json"

        # Registrar eventos
        self._register_event_handlers()

        # Carregar conquistas
        self._initialize_achievements()
        self._load_progress()

    def _register_event_handlers(self) -> None:
        """Registra handlers para eventos do jogo."""
        subscribe_to_event(EventType.COMBAT_END, self._on_combat_end)
        subscribe_to_event(EventType.PLAYER_LEVEL_UP, self._on_level_up)
        subscribe_to_event(EventType.PHASE_COMPLETED, self._on_phase_completed)
        subscribe_to_event(EventType.SKILL_USED, self._on_skill_used)
        subscribe_to_event(EventType.ITEM_USED, self._on_item_used)
        subscribe_to_event(EventType.SAVE_GAME, self._on_save_game)

    def _initialize_achievements(self) -> None:
        """Inicializa todas as conquistas do jogo."""
        # Conquistas de progresso
        self.add_achievement(Achievement(
            id="first_blood",
            name="Primeiro Sangue",
            description="Derrote seu primeiro inimigo",
            type=AchievementType.MILESTONE,
            rarity=AchievementRarity.COMMON,
            points=10,
            icon="[X]"  # X para combate
        ))

        self.add_achievement(Achievement(
            id="monster_slayer",
            name="Caçador de Monstros",
            description="Derrote 10 inimigos",
            type=AchievementType.PROGRESS,
            rarity=AchievementRarity.COMMON,
            points=25,
            icon="[#]",  # Hash para matador
            progress_max=10
        ))

        self.add_achievement(Achievement(
            id="level_up_5",
            name="Crescimento",
            description="Alcance o nível 5",
            type=AchievementType.MILESTONE,
            rarity=AchievementRarity.COMMON,
            points=20,
            icon="[+]"  # Plus para progresso
        ))

        self.add_achievement(Achievement(
            id="phase_5_complete",
            name="Meio do Caminho",
            description="Complete a Fase 5",
            type=AchievementType.STORY,
            rarity=AchievementRarity.UNCOMMON,
            points=50,
            icon="[>]"  # Seta para exploracao
        ))

        self.add_achievement(Achievement(
            id="game_complete",
            name="Herói de Zorg",
            description="Complete o jogo e salve Ramon",
            type=AchievementType.STORY,
            rarity=AchievementRarity.LEGENDARY,
            points=200,
            icon="[@]"  # Arroba para realizacao final
        ))

        self.add_achievement(Achievement(
            id="spell_master",
            name="Mestre da Magia",
            description="Use habilidades 25 vezes",
            type=AchievementType.SKILL,
            rarity=AchievementRarity.RARE,
            points=75,
            icon="[~]",  # Til para magia
            progress_max=25
        ))

        self.add_achievement(Achievement(
            id="potion_addict",
            name="Viciado em Poções",
            description="Use 20 poções",
            type=AchievementType.COLLECTION,
            rarity=AchievementRarity.UNCOMMON,
            points=30,
            icon="[=]",  # Igual para pocoes
            progress_max=20
        ))

        # Conquista secreta
        self.add_achievement(Achievement(
            id="secret_explorer",
            name="Explorador Secreto",
            description="Descubra todos os segredos do jogo",
            type=AchievementType.SECRET,
            rarity=AchievementRarity.EPIC,
            points=100,
            icon="[?]",  # Interrogacao para colecionador
            hidden=True
        ))

    def add_achievement(self, achievement: Achievement) -> None:
        """Adiciona uma conquista ao sistema."""
        self.achievements[achievement.id] = achievement

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Desbloqueia uma conquista específica."""
        achievement = self.achievements.get(achievement_id)
        if not achievement or achievement.unlocked:
            return False

        achievement.unlock()
        self.unlocked_achievements.append(achievement_id)

        self.logger.info(f"Conquista desbloqueada: {achievement.name}")

        # Emitir evento de conquista desbloqueada
        from core.managers.event_manager import emit_event
        emit_event(EventType.ACHIEVEMENT_UNLOCKED, {
            "achievement_id": achievement_id,
            "achievement_name": achievement.name,
            "points": achievement.points,
            "rarity": achievement.rarity.value
        })

        return True

    def update_achievement_progress(self, achievement_id: str, amount: int = 1) -> bool:
        """Atualiza o progresso de uma conquista."""
        achievement = self.achievements.get(achievement_id)
        if not achievement:
            return False

        unlocked = achievement.update_progress(amount)
        if unlocked:
            self.unlocked_achievements.append(achievement_id)
            self.logger.info(f"Conquista desbloqueada por progresso: {achievement.name}")

        return unlocked

    def get_achievements_by_type(self, achievement_type: AchievementType) -> List[Achievement]:
        """Retorna conquistas de um tipo específico."""
        return [a for a in self.achievements.values() if a.type == achievement_type]

    def get_unlocked_achievements(self) -> List[Achievement]:
        """Retorna todas as conquistas desbloqueadas."""
        return [a for a in self.achievements.values() if a.unlocked]

    def get_locked_achievements(self, include_hidden: bool = False) -> List[Achievement]:
        """Retorna conquistas ainda bloqueadas."""
        achievements = [a for a in self.achievements.values() if not a.unlocked]
        if not include_hidden:
            achievements = [a for a in achievements if not a.hidden]
        return achievements

    def get_total_points(self) -> int:
        """Retorna o total de pontos conquistados."""
        return sum(a.points for a in self.achievements.values() if a.unlocked)

    def get_completion_percentage(self) -> float:
        """Retorna a porcentagem de conquistas completadas."""
        total = len(self.achievements)
        unlocked = len([a for a in self.achievements.values() if a.unlocked])
        return (unlocked / total) * 100 if total > 0 else 0

    def _save_progress(self) -> None:
        """Salva o progresso das conquistas."""
        try:
            data = {
                "achievements": {
                    aid: achievement.to_dict()
                    for aid, achievement in self.achievements.items()
                },
                "last_updated": datetime.now().isoformat()
            }

            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Erro ao salvar progresso das conquistas: {e}")

    def _load_progress(self) -> None:
        """Carrega o progresso das conquistas."""
        if not self.save_file.exists():
            return

        try:
            with open(self.save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            achievements_data = data.get("achievements", {})

            for achievement_id, achievement_data in achievements_data.items():
                if achievement_id in self.achievements:
                    template = self.achievements[achievement_id]
                    self.achievements[achievement_id] = Achievement.from_dict(template, achievement_data)

                    if self.achievements[achievement_id].unlocked:
                        self.unlocked_achievements.append(achievement_id)

            self.logger.info(f"Progresso das conquistas carregado: {len(self.unlocked_achievements)} desbloqueadas")

        except Exception as e:
            self.logger.error(f"Erro ao carregar progresso das conquistas: {e}")

    # Event handlers
    def _on_combat_end(self, event) -> None:
        """Handler para fim de combate."""
        if event.data.get("winner"):  # Jogador ganhou
            # Primeira vitória
            if not self.achievements["first_blood"].unlocked:
                self.unlock_achievement("first_blood")

            # Progresso de inimigos derrotados
            self.update_achievement_progress("monster_slayer")

    def _on_level_up(self, event) -> None:
        """Handler para level up."""
        new_level = event.data.get("new_level", 0)

        if new_level >= 5:
            self.unlock_achievement("level_up_5")

    def _on_phase_completed(self, event) -> None:
        """Handler para fase completada."""
        phase = event.data.get("phase", 0)

        if phase >= 5:
            self.unlock_achievement("phase_5_complete")

        if phase >= 10:  # Assumindo que fase 10 é a última
            self.unlock_achievement("game_complete")

    def _on_skill_used(self, event) -> None:
        """Handler para uso de habilidade."""
        self.update_achievement_progress("spell_master")

    def _on_item_used(self, event) -> None:
        """Handler para uso de item."""
        item_name = event.data.get("item", "").lower()
        if "poção" in item_name or "pocao" in item_name:
            self.update_achievement_progress("potion_addict")

    def _on_save_game(self, event) -> None:
        """Handler para salvamento do jogo."""
        self._save_progress()


# Instância global
_achievement_manager: Optional[AchievementManager] = None


def get_achievement_manager() -> AchievementManager:
    """Retorna a instância global do gerenciador de conquistas."""
    global _achievement_manager
    if _achievement_manager is None:
        _achievement_manager = AchievementManager()
    return _achievement_manager