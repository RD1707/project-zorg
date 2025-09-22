"""
Sistema de recompensas balanceadas baseadas na progressão do jogo.
"""

import random
from typing import Any, Dict, List


class RewardTable:
    """Sistema de recompensas balanceadas por fase."""

    # Tabela de recompensas por raridade e fase
    EQUIPMENT_BY_PHASE = {
        1: {
            "comum": ["Adaga Enferrujada", "Roupas de Pano", "Escudo de Madeira"],
            "raro": [],
            "épico": [],
            "lendário": [],
        },
        2: {
            "comum": ["Espada Curta", "Armadura de Couro", "Escudo de Bronze"],
            "raro": [],
            "épico": [],
            "lendário": [],
        },
        3: {
            "comum": ["Espada de Ferro", "Armadura de Malha", "Escudo de Ferro"],
            "raro": ["Cimitarra Enfeiticada"],
            "épico": [],
            "lendário": [],
        },
        4: {
            "comum": ["Espada de Ferro", "Armadura de Malha", "Escudo de Ferro"],
            "raro": ["Machado de Guerra", "Armadura de Aco Reforcado", "Escudo de Aco"],
            "épico": [],
            "lendário": [],
        },
        5: {
            "comum": [],
            "raro": ["Lâmina Élfica", "Manto Élfico", "Escudo Rúnico"],
            "épico": ["Espada Runica"],
            "lendário": [],
        },
        6: {
            "comum": [],
            "raro": ["Armadura de Placas"],
            "épico": ["Espada Runica", "Escudo Rúnico"],
            "lendário": [],
        },
        7: {
            "comum": [],
            "raro": [],
            "épico": ["Espada Runica", "Escudo Rúnico"],
            "lendário": ["Excalibur"],
        },
        8: {
            "comum": [],
            "raro": [],
            "épico": [],
            "lendário": ["Excalibur", "Armadura Dragão"],
        },
        9: {
            "comum": [],
            "raro": [],
            "épico": [],
            "lendário": ["Excalibur", "Armadura Dragão", "Aegis Celestial"],
        },
        10: {
            "comum": [],
            "raro": [],
            "épico": [],
            "lendário": ["Excalibur", "Armadura Dragão", "Aegis Celestial"],
        },
    }

    ABILITIES_BY_PHASE = {
        1: ["Golpe Poderoso", "Toque Restaurador", "Postura Defensiva"],
        2: ["Lanca de Gelo", "Lâmina Sombria"],
        3: ["Bola de Fogo", "Escudo Mágico", "Raio Congelante"],
        4: ["Drenar Vida", "Golpe Flamejante", "Combo Devastador"],
        5: ["Tempestade de Gelo", "Cura Suprema", "Rajada Arcana"],
        6: ["Meteoro", "Barreira Divina", "Benção da Natureza"],
        7: ["Meteoro", "Barreira Divina", "Cura Suprema"],
        8: ["Furia Berserker", "Regeneracao Vital"],
        9: ["Escudo de Luz", "Rajada Arcana"],
        10: ["Benção da Natureza", "Barreira Divina", "Meteoro"],
    }

    # Chances de drop por raridade baseada na fase
    DROP_CHANCES = {
        1: {"comum": 0.8, "raro": 0.15, "épico": 0.05, "lendário": 0.0},
        2: {"comum": 0.7, "raro": 0.25, "épico": 0.05, "lendário": 0.0},
        3: {"comum": 0.6, "raro": 0.3, "épico": 0.1, "lendário": 0.0},
        4: {"comum": 0.5, "raro": 0.35, "épico": 0.15, "lendário": 0.0},
        5: {"comum": 0.3, "raro": 0.45, "épico": 0.2, "lendário": 0.05},
        6: {"comum": 0.2, "raro": 0.4, "épico": 0.3, "lendário": 0.1},
        7: {"comum": 0.1, "raro": 0.3, "épico": 0.4, "lendário": 0.2},
        8: {"comum": 0.05, "raro": 0.2, "épico": 0.45, "lendário": 0.3},
        9: {"comum": 0.0, "raro": 0.1, "épico": 0.4, "lendário": 0.5},
        10: {"comum": 0.0, "raro": 0.05, "épico": 0.25, "lendário": 0.7},
    }

    @staticmethod
    def get_equipment_reward(
        phase: int, player_equipment: Dict[str, Any] = None
    ) -> str:
        """
        Retorna um equipamento apropriado para a fase atual.
        Evita duplicatas se o jogador já tiver o item.
        """
        if player_equipment is None:
            player_equipment = {}

        phase = min(max(phase, 1), 10)  # Limitar entre 1 e 10
        chances = RewardTable.DROP_CHANCES[phase]
        available_equipment = RewardTable.EQUIPMENT_BY_PHASE[phase]

        # Determinar raridade baseada nas chances
        rarity = RewardTable._roll_rarity(chances)

        # Filtrar equipamentos disponíveis para a raridade
        equipment_pool = available_equipment.get(rarity, [])
        if not equipment_pool:
            # Se não há equipamentos da raridade escolhida, pegar de uma raridade menor
            for fallback_rarity in ["épico", "raro", "comum"]:
                if available_equipment.get(fallback_rarity):
                    equipment_pool = available_equipment[fallback_rarity]
                    break

        if not equipment_pool:
            return None

        # Filtrar equipamentos que o jogador já possui
        available_items = []
        for item_name in equipment_pool:
            if not RewardTable._player_has_equipment(player_equipment, item_name):
                available_items.append(item_name)

        # Se todos os itens já foram obtidos, permitir duplicatas
        if not available_items:
            available_items = equipment_pool

        return random.choice(available_items) if available_items else None

    @staticmethod
    def get_ability_reward(phase: int, player_abilities: List[str] = None) -> str:
        """
        Retorna uma habilidade apropriada para a fase atual.
        Evita duplicatas se o jogador já tiver a habilidade.
        """
        if player_abilities is None:
            player_abilities = []

        phase = min(max(phase, 1), 10)
        available_abilities = RewardTable.ABILITIES_BY_PHASE.get(phase, [])

        # Filtrar habilidades que o jogador já conhece
        new_abilities = [
            ability
            for ability in available_abilities
            if ability not in player_abilities
        ]

        # Se todas as habilidades da fase já foram aprendidas, não dar recompensa
        if not new_abilities:
            # Tentar fases anteriores como fallback
            for prev_phase in range(phase - 1, 0, -1):
                prev_abilities = RewardTable.ABILITIES_BY_PHASE.get(prev_phase, [])
                new_abilities = [
                    ability
                    for ability in prev_abilities
                    if ability not in player_abilities
                ]
                if new_abilities:
                    break

        return random.choice(new_abilities) if new_abilities else None

    @staticmethod
    def _roll_rarity(chances: Dict[str, float]) -> str:
        """Determina a raridade baseada nas chances."""
        roll = random.random()
        cumulative = 0.0

        for rarity in ["lendário", "épico", "raro", "comum"]:
            cumulative += chances.get(rarity, 0.0)
            if roll <= cumulative:
                return rarity

        return "comum"  # Fallback

    @staticmethod
    def _player_has_equipment(player_equipment: Dict[str, Any], item_name: str) -> bool:
        """Verifica se o jogador já possui um equipamento específico."""
        equipped_items = [
            player_equipment.get("arma_equipada"),
            player_equipment.get("armadura_equipada"),
            player_equipment.get("escudo_equipada"),
        ]

        for item in equipped_items:
            if item and hasattr(item, "nome") and item.nome == item_name:
                return True

        # Verificar inventário se fornecido
        inventory = player_equipment.get("inventario", [])
        for item in inventory:
            if hasattr(item, "nome") and item.nome == item_name:
                return True

        return False

    @staticmethod
    def get_balanced_xp_gold(phase: int, base_xp: int, base_gold: int) -> tuple:
        """
        Retorna XP e ouro balanceados baseados na fase.
        Valores aumentam progressivamente mas não exponencialmente.
        """
        phase = min(max(phase, 1), 10)

        # Multiplicadores balanceados por fase
        xp_multipliers = {
            1: 1.0,
            2: 1.2,
            3: 1.5,
            4: 1.8,
            5: 2.2,
            6: 2.7,
            7: 3.3,
            8: 4.0,
            9: 4.8,
            10: 5.7,
        }

        gold_multipliers = {
            1: 1.0,
            2: 1.1,
            3: 1.3,
            4: 1.6,
            5: 2.0,
            6: 2.5,
            7: 3.1,
            8: 3.8,
            9: 4.6,
            10: 5.5,
        }

        balanced_xp = int(base_xp * xp_multipliers[phase])
        balanced_gold = int(base_gold * gold_multipliers[phase])

        return balanced_xp, balanced_gold


# Função conveniente para usar no GameEngine
def get_phase_reward(
    phase: int, reward_type: str, player_data: Dict[str, Any] = None
) -> str:
    """
    Função conveniente para obter recompensas balanceadas.

    Args:
        phase: Fase atual do jogo
        reward_type: 'equipment' ou 'ability'
        player_data: Dados do jogador para evitar duplicatas

    Returns:
        Nome do item/habilidade ou None se não houver recompensa
    """
    if reward_type == "equipment":
        return RewardTable.get_equipment_reward(phase, player_data)
    elif reward_type == "ability":
        player_abilities = []
        if player_data and "habilidades_conhecidas" in player_data:
            player_abilities = [h.nome for h in player_data["habilidades_conhecidas"]]
        return RewardTable.get_ability_reward(phase, player_abilities)
    else:
        return None
