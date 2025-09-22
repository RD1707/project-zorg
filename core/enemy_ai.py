"""
Sistema de IA para inimigos com comportamentos definidos em JSON.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from utils.logging_config import get_logger

logger = get_logger("enemy_ai")


class AIPersonality(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    CUNNING = "cunning"
    BERSERKER = "berserker"
    TACTICAL = "tactical"
    COWARDLY = "cowardly"


class AICondition(Enum):
    HP_ABOVE_75 = "hp_above_75"
    HP_ABOVE_50 = "hp_above_50"
    HP_ABOVE_25 = "hp_above_25"
    HP_BELOW_75 = "hp_below_75"
    HP_BELOW_50 = "hp_below_50"
    HP_BELOW_25 = "hp_below_25"
    MP_ABOVE_50 = "mp_above_50"
    MP_BELOW_50 = "mp_below_50"
    FIRST_TURN = "first_turn"
    PLAYER_HP_LOW = "player_hp_low"
    PLAYER_HP_HIGH = "player_hp_high"


class AIAction(Enum):
    BASIC_ATTACK = "basic_attack"
    USE_ABILITY = "use_ability"
    DEFEND = "defend"
    HEAL = "heal"
    TAUNT = "taunt"
    INTIMIDATE = "intimidate"
    FLEE_ATTEMPT = "flee_attempt"
    CHARGE_ATTACK = "charge_attack"
    SPECIAL_MOVE = "special_move"


@dataclass
class AIPattern:
    condition: str
    actions: List[str]
    weight: float = 1.0


@dataclass
class AISpecialCondition:
    trigger: str
    action: str
    text: str
    used: bool = False


@dataclass
class AIBehavior:
    personality: AIPersonality
    attack_patterns: List[AIPattern]
    special_conditions: List[AISpecialCondition]
    resistances: List[str]
    weaknesses: List[str]
    preferred_range: str
    aggression_level: float = 0.5
    intelligence_level: float = 0.5


class EnemyAI:
    """Sistema de IA para inimigos baseado em comportamentos JSON."""

    def __init__(self, enemy_data: Dict[str, Any]):
        self.enemy_data = enemy_data
        self.ai_behavior = self._parse_ai_behavior(enemy_data.get("ai_behavior", {}))
        self.turn_count = 0
        self.last_action = None
        self.action_history = []

    def _parse_ai_behavior(self, ai_data: Dict[str, Any]) -> AIBehavior:
        """Converte dados JSON em objeto AIBehavior."""
        try:
            personality = AIPersonality(ai_data.get("personality", "aggressive"))

            # Converter padrões de ataque
            patterns = []
            for pattern_data in ai_data.get("attack_patterns", []):
                pattern = AIPattern(
                    condition=pattern_data["condition"],
                    actions=pattern_data["actions"],
                    weight=pattern_data.get("weight", 1.0),
                )
                patterns.append(pattern)

            # Converter condições especiais
            special_conditions = []
            for cond_data in ai_data.get("special_conditions", []):
                condition = AISpecialCondition(
                    trigger=cond_data["trigger"],
                    action=cond_data["action"],
                    text=cond_data["text"],
                )
                special_conditions.append(condition)

            return AIBehavior(
                personality=personality,
                attack_patterns=patterns,
                special_conditions=special_conditions,
                resistances=ai_data.get("resistances", []),
                weaknesses=ai_data.get("weaknesses", []),
                preferred_range=ai_data.get("preferred_range", "close"),
                aggression_level=ai_data.get("aggression_level", 0.5),
                intelligence_level=ai_data.get("intelligence_level", 0.5),
            )

        except Exception as e:
            logger.warning(f"Error parsing AI behavior: {e}, using default")
            return self._default_behavior()

    def _default_behavior(self) -> AIBehavior:
        """Comportamento padrão para inimigos sem IA definida."""
        return AIBehavior(
            personality=AIPersonality.AGGRESSIVE,
            attack_patterns=[
                AIPattern("hp_above_50", ["basic_attack"]),
                AIPattern("hp_below_50", ["basic_attack", "defend"]),
            ],
            special_conditions=[],
            resistances=[],
            weaknesses=[],
            preferred_range="close",
        )

    def get_next_action(self, enemy, player) -> Dict[str, Any]:
        """Determina a próxima ação do inimigo baseada na IA."""
        self.turn_count += 1

        # Verificar condições especiais
        special_action = self._check_special_conditions(enemy, player)
        if special_action:
            return special_action

        # Encontrar padrão aplicável
        applicable_patterns = self._get_applicable_patterns(enemy, player)

        if not applicable_patterns:
            # Fallback para ataque básico
            return {"type": "basic_attack", "target": "player"}

        # Escolher padrão baseado no peso
        pattern = self._choose_weighted_pattern(applicable_patterns)

        # Escolher ação do padrão
        action = self._choose_action_from_pattern(pattern, enemy, player)

        self.last_action = action
        self.action_history.append(action)

        return action

    def _check_special_conditions(self, enemy, player) -> Optional[Dict[str, Any]]:
        """Verifica e executa condições especiais."""
        for condition in self.ai_behavior.special_conditions:
            if condition.used:
                continue

            should_trigger = False

            if condition.trigger == "first_turn" and self.turn_count == 1:
                should_trigger = True
            elif (
                condition.trigger == "low_hp" and self._get_hp_percentage(enemy) < 0.25
            ):
                should_trigger = True
            elif (
                condition.trigger == "player_low_hp"
                and self._get_hp_percentage(player) < 0.3
            ):
                should_trigger = True

            if should_trigger:
                condition.used = True
                return {
                    "type": condition.action,
                    "target": "player",
                    "text": condition.text,
                }

        return None

    def _get_applicable_patterns(self, enemy, player) -> List[AIPattern]:
        """Encontra padrões de IA aplicáveis à situação atual."""
        applicable = []

        for pattern in self.ai_behavior.attack_patterns:
            if self._evaluate_condition(pattern.condition, enemy, player):
                applicable.append(pattern)

        return applicable

    def _evaluate_condition(self, condition: str, enemy, player) -> bool:
        """Avalia se uma condição está satisfeita."""
        enemy_hp_pct = self._get_hp_percentage(enemy)
        enemy_mp_pct = self._get_mp_percentage(enemy)
        player_hp_pct = self._get_hp_percentage(player)

        condition_map = {
            "hp_above_75": enemy_hp_pct > 0.75,
            "hp_above_50": enemy_hp_pct > 0.50,
            "hp_above_25": enemy_hp_pct > 0.25,
            "hp_below_75": enemy_hp_pct <= 0.75,
            "hp_below_50": enemy_hp_pct <= 0.50,
            "hp_below_25": enemy_hp_pct <= 0.25,
            "mp_above_50": enemy_mp_pct > 0.50,
            "mp_below_50": enemy_mp_pct <= 0.50,
            "first_turn": self.turn_count == 1,
            "player_hp_low": player_hp_pct < 0.3,
            "player_hp_high": player_hp_pct > 0.7,
            "always": True,
        }

        return condition_map.get(condition, False)

    def _get_hp_percentage(self, character) -> float:
        """Calcula percentual de HP atual."""
        if hasattr(character, "hp_atual") and hasattr(character, "hp_max"):
            if character.hp_max > 0:
                return character.hp_atual / character.hp_max
        return 1.0

    def _get_mp_percentage(self, character) -> float:
        """Calcula percentual de MP atual."""
        if hasattr(character, "mp_atual") and hasattr(character, "mp_max"):
            if character.mp_max > 0:
                return character.mp_atual / character.mp_max
        return 1.0

    def _choose_weighted_pattern(self, patterns: List[AIPattern]) -> AIPattern:
        """Escolhe um padrão baseado no peso."""
        if len(patterns) == 1:
            return patterns[0]

        total_weight = sum(p.weight for p in patterns)
        if total_weight <= 0:
            return random.choice(patterns)

        rand = random.uniform(0, total_weight)
        current_weight = 0

        for pattern in patterns:
            current_weight += pattern.weight
            if rand <= current_weight:
                return pattern

        return patterns[-1]

    def _choose_action_from_pattern(
        self, pattern: AIPattern, enemy, player
    ) -> Dict[str, Any]:
        """Escolhe uma ação específica do padrão."""
        if not pattern.actions:
            return {"type": "basic_attack", "target": "player"}

        # Aplicar personalidade para influenciar escolha
        action_name = self._apply_personality_to_choice(pattern.actions, enemy, player)

        return self._create_action_dict(action_name, enemy, player)

    def _apply_personality_to_choice(self, actions: List[str], enemy, player) -> str:
        """Aplica personalidade para modificar escolha de ação."""
        if not actions:
            return "basic_attack"

        personality = self.ai_behavior.personality

        # Personalidades influenciam probabilidades
        if personality == AIPersonality.AGGRESSIVE:
            # Prefere ataques
            attack_actions = [a for a in actions if "attack" in a]
            if attack_actions and random.random() < 0.7:
                return random.choice(attack_actions)

        elif personality == AIPersonality.DEFENSIVE:
            # Prefere defesa quando com pouco HP
            if self._get_hp_percentage(enemy) < 0.5:
                defensive_actions = [a for a in actions if a in ["defend", "heal"]]
                if defensive_actions and random.random() < 0.6:
                    return random.choice(defensive_actions)

        elif personality == AIPersonality.CUNNING:
            # Varia estratégias, evita repetir ações
            if self.action_history:
                recent_actions = self.action_history[-2:]
                available = [
                    a
                    for a in actions
                    if a not in [act.get("type") for act in recent_actions]
                ]
                if available:
                    return random.choice(available)

        elif personality == AIPersonality.BERSERKER:
            # Mais agressivo quando ferido
            if self._get_hp_percentage(enemy) < 0.5:
                aggressive_actions = [
                    a for a in actions if "attack" in a or "charge" in a
                ]
                if aggressive_actions:
                    return random.choice(aggressive_actions)

        # Escolha padrão
        return random.choice(actions)

    def _create_action_dict(self, action_name: str, enemy, player) -> Dict[str, Any]:
        """Cria dicionário de ação baseado no nome."""
        action_map = {
            "basic_attack": {"type": "attack", "target": "player"},
            "use_ability": {
                "type": "ability",
                "target": "player",
                "ability": self._choose_ability(enemy),
            },
            "defend": {"type": "defend", "target": "self"},
            "heal": {"type": "heal", "target": "self"},
            "taunt": {
                "type": "taunt",
                "target": "player",
                "text": "O inimigo provoca você!",
            },
            "intimidate": {
                "type": "intimidate",
                "target": "player",
                "text": "O inimigo tenta intimidá-lo!",
            },
            "flee_attempt": {
                "type": "flee",
                "target": "self",
                "text": "O inimigo tenta fugir!",
            },
            "charge_attack": {"type": "charge_attack", "target": "player"},
            "special_move": {"type": "special", "target": "player"},
        }

        return action_map.get(action_name, {"type": "attack", "target": "player"})

    def _choose_ability(self, enemy) -> Optional[str]:
        """Escolhe uma habilidade para usar."""
        if hasattr(enemy, "habilidades_conhecidas") and enemy.habilidades_conhecidas:
            # Filtrar habilidades que podem ser usadas
            available_abilities = []
            for ability in enemy.habilidades_conhecidas:
                if hasattr(ability, "custo_mp") and enemy.mp_atual >= ability.custo_mp:
                    available_abilities.append(ability.nome)

            if available_abilities:
                return random.choice(available_abilities)

        return None

    def get_damage_modifier(self, damage_type: str) -> float:
        """Retorna modificador de dano baseado em resistências/fraquezas."""
        if damage_type in self.ai_behavior.resistances:
            return 0.5  # Resistência reduz dano pela metade
        elif damage_type in self.ai_behavior.weaknesses:
            return 1.5  # Fraqueza aumenta dano em 50%
        return 1.0

    def get_personality_description(self) -> str:
        """Retorna descrição da personalidade do inimigo."""
        descriptions = {
            AIPersonality.AGGRESSIVE: "Este inimigo é extremamente agressivo e ataca sem hesitar.",
            AIPersonality.DEFENSIVE: "Este inimigo prefere se defender e aguardar oportunidades.",
            AIPersonality.CUNNING: "Este inimigo é esperto e adapta suas estratégias.",
            AIPersonality.BERSERKER: "Este inimigo luta com fúria descontrolada.",
            AIPersonality.TACTICAL: "Este inimigo planeja cuidadosamente seus movimentos.",
            AIPersonality.COWARDLY: "Este inimigo prefere evitar confrontos diretos.",
        }
        return descriptions.get(self.ai_behavior.personality, "Comportamento padrão.")


def create_enemy_ai(enemy_data: Dict[str, Any]) -> EnemyAI:
    """Factory function para criar IA de inimigo."""
    return EnemyAI(enemy_data)
