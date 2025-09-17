"""
Sistema de eventos aleatórios para o jogo ZORG.
Gera eventos inesperados durante as fases para aumentar a imersão.
"""
import random
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from core.managers.base_manager import BaseManager
from utils.logging_config import get_logger

logger = get_logger("random_event_manager")


class EventType(Enum):
    MERCHANT = "merchant"
    TRAP = "trap"
    TREASURE = "treasure"
    HEALING_SPRING = "healing_spring"
    MYSTERIOUS_SHRINE = "mysterious_shrine"
    ABANDONED_CAMP = "abandoned_camp"
    MONSTER_AMBUSH = "monster_ambush"
    HELPFUL_SPIRIT = "helpful_spirit"
    CURSED_ITEM = "cursed_item"
    WISE_HERMIT = "wise_hermit"


class EventRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


@dataclass
class EventChoice:
    text: str
    result_text: str
    effects: Dict[str, Any]  # Efeitos no jogador/jogo
    requirements: Dict[str, Any] = None  # Requisitos para escolha


@dataclass
class RandomEvent:
    id: str
    name: str
    description: str
    event_type: EventType
    rarity: EventRarity
    choices: List[EventChoice]
    base_probability: float
    phase_restrictions: List[int] = None
    one_time_only: bool = False
    flavor_text: List[str] = None


class RandomEventManager(BaseManager):
    """Gerenciador de eventos aleatórios."""

    def __init__(self):
        super().__init__("random_event_manager")
        self.events = self._initialize_events()
        self.triggered_events = set()  # Eventos únicos já ativados
        self.event_cooldown = {}  # Cooldown para eventos

    def _initialize_events(self) -> Dict[str, RandomEvent]:
        """Inicializa todos os eventos aleatórios."""
        events = {}

        # Evento: Vendedor Ambulante
        events["traveling_merchant"] = RandomEvent(
            id="traveling_merchant",
            name="Vendedor Ambulante",
            description="Você encontra um mercador misterioso com uma carroça cheia de itens raros.",
            event_type=EventType.MERCHANT,
            rarity=EventRarity.UNCOMMON,
            base_probability=0.15,
            phase_restrictions=[2, 3, 4, 5, 6, 7, 8],
            choices=[
                EventChoice(
                    text="Examinar suas mercadorias",
                    result_text="O mercador mostra itens raros e poções poderosas!",
                    effects={"action": "open_special_shop", "items": ["Pocao de Vigor Supremo", "Cristal de Mana", "Erva Rara"]}
                ),
                EventChoice(
                    text="Conversar sobre rumores",
                    result_text="'Ouvi dizer que há tesouros escondidos na próxima área...', sussurra o mercador.",
                    effects={"gain_info": "next_area_treasure", "xp": 25}
                ),
                EventChoice(
                    text="Seguir viagem",
                    result_text="Você acena educadamente e continua sua jornada.",
                    effects={}
                )
            ],
            flavor_text=[
                "Um homem encapuzado conduz uma carroça ornamentada.",
                "Cristais mágicos brilham em sua mercadoria.",
                "'Olá, aventureira! Tenho exatamente o que você precisa...'"
            ]
        )

        # Evento: Armadilha Antiga
        events["ancient_trap"] = RandomEvent(
            id="ancient_trap",
            name="Armadilha Antiga",
            description="O chão cede sob seus pés! Uma armadilha antiga foi ativada.",
            event_type=EventType.TRAP,
            rarity=EventRarity.COMMON,
            base_probability=0.2,
            choices=[
                EventChoice(
                    text="Tentar desviar rapidamente",
                    result_text="Você consegue se desviar parcialmente, mas ainda sofre alguns danos.",
                    effects={"hp_damage": 15, "message": "Você evitou o pior da armadilha!"}
                ),
                EventChoice(
                    text="Se proteger com os braços",
                    result_text="Você se protege, reduzindo o dano mas perdendo alguns itens.",
                    effects={"hp_damage": 10, "lose_random_item": True}
                ),
                EventChoice(
                    text="Tentar desarmar a armadilha",
                    result_text="Com cuidado, você consegue desarmar o mecanismo!",
                    effects={"xp": 50, "find_gold": 75},
                    requirements={"min_level": 3}
                )
            ],
            flavor_text=[
                "Clique! Você ouve um som mecânico ominoso.",
                "Dardos voam em sua direção!",
                "Pedras começam a cair do teto!"
            ]
        )

        # Evento: Tesouro Escondido
        events["hidden_treasure"] = RandomEvent(
            id="hidden_treasure",
            name="Tesouro Escondido",
            description="Entre as ruínas, algo brilha... Um baú antigo meio enterrado!",
            event_type=EventType.TREASURE,
            rarity=EventRarity.RARE,
            base_probability=0.08,
            choices=[
                EventChoice(
                    text="Abrir o baú imediatamente",
                    result_text="O baú se abre revelando tesouros valiosos!",
                    effects={"random_treasure": True, "gold": [100, 300], "items": ["random_rare"]}
                ),
                EventChoice(
                    text="Examinar por armadilhas primeiro",
                    result_text="Sua cautela é recompensada - você encontra e desarma uma armadilha!",
                    effects={"random_treasure": True, "gold": [150, 350], "xp": 75, "items": ["random_rare", "random_common"]}
                ),
                EventChoice(
                    text="Ignorar o baú",
                    result_text="Você decide que não vale o risco e continua sua jornada.",
                    effects={"xp": 25, "message": "Às vezes a prudência é a melhor escolha."}
                )
            ],
            flavor_text=[
                "O baú é feito de madeira escura com dobradiças de ouro.",
                "Runas antigas brilham fracamente na tampa.",
                "Você sente uma aura mágica emanando do baú."
            ]
        )

        # Evento: Fonte de Cura
        events["healing_spring"] = RandomEvent(
            id="healing_spring",
            name="Fonte da Cura",
            description="Você descobre uma fonte cristalina que emana energia curativa.",
            event_type=EventType.HEALING_SPRING,
            rarity=EventRarity.UNCOMMON,
            base_probability=0.12,
            choices=[
                EventChoice(
                    text="Beber da fonte",
                    result_text="A água mágica restaura sua vitalidade completamente!",
                    effects={"heal_full": True, "restore_mp": True, "remove_debuffs": True}
                ),
                EventChoice(
                    text="Encher suas poções vazias",
                    result_text="Você consegue criar várias poções com a água mágica!",
                    effects={"gain_items": ["Pocao de Cura", "Pocao de Cura", "Pocao de Mana"]}
                ),
                EventChoice(
                    text="Apenas descansar perto da fonte",
                    result_text="O descanso perto da fonte restaura parte de sua energia.",
                    effects={"heal_percentage": 50, "restore_mp_percentage": 30}
                )
            ],
            flavor_text=[
                "A água é de um azul cristalino impossível.",
                "Pequenas partículas de luz dançam na superfície.",
                "Você sente uma sensação de paz absoluta."
            ]
        )

        # Evento: Santuário Misterioso
        events["mysterious_shrine"] = RandomEvent(
            id="mysterious_shrine",
            name="Santuário Misterioso",
            description="Um pequeno santuário de origem desconhecida bloqueia seu caminho.",
            event_type=EventType.MYSTERIOUS_SHRINE,
            rarity=EventRarity.RARE,
            base_probability=0.06,
            choices=[
                EventChoice(
                    text="Oferecer ouro ao santuário",
                    result_text="O santuário aceita sua oferenda e você se sente abençoado!",
                    effects={"lose_gold": 100, "gain_blessing": {"type": "attack_boost", "duration": 5}},
                    requirements={"min_gold": 100}
                ),
                EventChoice(
                    text="Oferecer um item valioso",
                    result_text="O santuário brilha intensamente e retribui sua generosidade!",
                    effects={"lose_random_valuable_item": True, "gain_blessing": {"type": "defense_boost", "duration": 5}, "xp": 100}
                ),
                EventChoice(
                    text="Apenas fazer uma reverência",
                    result_text="Você mostra respeito e o santuário concede uma pequena bênção.",
                    effects={"gain_blessing": {"type": "luck_boost", "duration": 3}, "xp": 50}
                ),
                EventChoice(
                    text="Ignorar o santuário",
                    result_text="Você contorna o santuário, mas sente um peso em sua consciência.",
                    effects={"lose_luck": True}
                )
            ],
            flavor_text=[
                "O santuário é feito de pedra negra com veios dourados.",
                "Uma energia antiga pulsa no ar ao redor.",
                "Você sente que está sendo observado por olhos invisíveis."
            ]
        )

        # Evento: Acampamento Abandonado
        events["abandoned_camp"] = RandomEvent(
            id="abandoned_camp",
            name="Acampamento Abandonado",
            description="Você encontra os restos de um acampamento de outros aventureiros.",
            event_type=EventType.ABANDONED_CAMP,
            rarity=EventRarity.COMMON,
            base_probability=0.18,
            choices=[
                EventChoice(
                    text="Procurar por suprimentos",
                    result_text="Você encontra alguns itens úteis deixados para trás.",
                    effects={"random_items": 2, "gold": [20, 80]}
                ),
                EventChoice(
                    text="Ler o diário abandonado",
                    result_text="O diário contém informações valiosas sobre os perigos à frente.",
                    effects={"gain_info": "area_dangers", "xp": 75, "temporary_insight": True}
                ),
                EventChoice(
                    text="Usar o local para descansar",
                    result_text="Você descansa no abrigo abandonado, recuperando energia.",
                    effects={"heal_percentage": 30, "restore_mp_percentage": 25}
                )
            ],
            flavor_text=[
                "Cinzas frias indicam que o acampamento foi abandonado há dias.",
                "Equipamentos espalhados sugerem uma partida apressada.",
                "Um diário meio queimado está entre os pertences."
            ]
        )

        # Evento: Emboscada de Monstros
        events["monster_ambush"] = RandomEvent(
            id="monster_ambush",
            name="Emboscada!",
            description="Criaturas selvagens saltam das sombras para atacá-la!",
            event_type=EventType.MONSTER_AMBUSH,
            rarity=EventRarity.COMMON,
            base_probability=0.15,
            choices=[
                EventChoice(
                    text="Lutar contra todos",
                    result_text="Você luta bravamente contra múltiplos inimigos!",
                    effects={"start_combat": "ambush_multiple", "xp_bonus": 50}
                ),
                EventChoice(
                    text="Tentar fugir",
                    result_text="Você consegue escapar, mas não sem consequências.",
                    effects={"hp_damage": 20, "escape_success": True}
                ),
                EventChoice(
                    text="Usar intimidação",
                    result_text="Seu olhar feroz faz os monstros hesitarem!",
                    effects={"start_combat": "ambush_weakened", "enemy_debuff": True},
                    requirements={"min_level": 4}
                )
            ],
            flavor_text=[
                "Olhos vermelhos brilham na escuridão!",
                "Rosnados baixos ecoam ao seu redor.",
                "Você está cercada!"
            ]
        )

        return events

    def check_for_event(self, phase: int, player_level: int, **context) -> Optional[RandomEvent]:
        """Verifica se um evento aleatório deve ocorrer."""

        # Aplicar cooldown global para eventos
        if "last_event_phase" in context and context["last_event_phase"] == phase:
            return None

        available_events = self._get_available_events(phase, player_level, **context)

        if not available_events:
            return None

        # Calcular probabilidade total
        total_probability = sum(event.base_probability for event in available_events)

        # Ajustar probabilidade baseado no contexto
        probability_modifier = self._calculate_probability_modifier(**context)
        adjusted_probability = total_probability * probability_modifier

        # Verificar se evento deve ocorrer
        if random.random() < adjusted_probability:
            return self._select_weighted_event(available_events)

        return None

    def _get_available_events(self, phase: int, player_level: int, **context) -> List[RandomEvent]:
        """Filtra eventos disponíveis baseado nas condições atuais."""
        available = []

        for event in self.events.values():
            # Verificar se já foi usado (para eventos únicos)
            if event.one_time_only and event.id in self.triggered_events:
                continue

            # Verificar restrições de fase
            if event.phase_restrictions and phase not in event.phase_restrictions:
                continue

            # Verificar cooldown
            if event.id in self.event_cooldown and self.event_cooldown[event.id] > 0:
                continue

            # Verificar contexto específico
            if self._check_event_context(event, **context):
                available.append(event)

        return available

    def _check_event_context(self, event: RandomEvent, **context) -> bool:
        """Verifica se o contexto permite o evento."""

        # Eventos de cura são mais prováveis se o jogador estiver ferido
        if event.event_type == EventType.HEALING_SPRING:
            player_hp_ratio = context.get("player_hp_ratio", 1.0)
            if player_hp_ratio > 0.8:
                return random.random() < 0.3  # Reduz chance se HP alto

        # Armadilhas são menos prováveis em fases iniciais
        if event.event_type == EventType.TRAP:
            phase = context.get("phase", 1)
            if phase <= 2:
                return random.random() < 0.5

        # Tesouros são mais raros em fases iniciais
        if event.event_type == EventType.TREASURE:
            phase = context.get("phase", 1)
            if phase <= 3:
                return random.random() < 0.4

        return True

    def _calculate_probability_modifier(self, **context) -> float:
        """Calcula modificador de probabilidade baseado no contexto."""
        modifier = 1.0

        # Fase atual
        phase = context.get("phase", 1)
        if phase <= 2:
            modifier *= 0.7  # Menos eventos nas primeiras fases
        elif phase >= 8:
            modifier *= 1.3  # Mais eventos nas fases finais

        # HP do jogador
        player_hp_ratio = context.get("player_hp_ratio", 1.0)
        if player_hp_ratio < 0.3:
            modifier *= 1.2  # Mais eventos quando HP baixo

        # Nível do jogador
        player_level = context.get("player_level", 1)
        if player_level >= 5:
            modifier *= 1.1  # Ligeiramente mais eventos para níveis altos

        return min(modifier, 2.0)  # Limitar multiplicador

    def _select_weighted_event(self, events: List[RandomEvent]) -> RandomEvent:
        """Seleciona evento baseado na raridade (pesos)."""
        rarity_weights = {
            EventRarity.COMMON: 1.0,
            EventRarity.UNCOMMON: 0.6,
            EventRarity.RARE: 0.3,
            EventRarity.LEGENDARY: 0.1
        }

        weighted_events = []
        for event in events:
            weight = rarity_weights.get(event.rarity, 1.0)
            weighted_events.extend([event] * int(weight * 10))

        return random.choice(weighted_events)

    def trigger_event(self, event: RandomEvent):
        """Marca evento como ativado."""
        if event.one_time_only:
            self.triggered_events.add(event.id)

        # Aplicar cooldown
        self.event_cooldown[event.id] = 3  # 3 fases de cooldown

        logger.info(f"Evento '{event.name}' ativado")

    def process_event_choice(self, event: RandomEvent, choice_index: int, player) -> Dict[str, Any]:
        """Processa a escolha do jogador em um evento."""
        if choice_index >= len(event.choices):
            return {"error": "Escolha inválida"}

        choice = event.choices[choice_index]

        # Verificar requisitos
        if choice.requirements:
            if not self._check_requirements(choice.requirements, player):
                return {"error": "Requisitos não atendidos", "requirements": choice.requirements}

        # Aplicar efeitos
        results = self._apply_effects(choice.effects, player)
        results["choice_text"] = choice.text
        results["result_text"] = choice.result_text

        return results

    def _check_requirements(self, requirements: Dict[str, Any], player) -> bool:
        """Verifica se o jogador atende aos requisitos."""
        if "min_level" in requirements:
            if player.nivel < requirements["min_level"]:
                return False

        if "min_gold" in requirements:
            if player.ouro < requirements["min_gold"]:
                return False

        if "required_item" in requirements:
            # Verificar se tem o item necessário
            # Implementar quando sistema de inventário estiver pronto
            pass

        return True

    def _apply_effects(self, effects: Dict[str, Any], player) -> Dict[str, Any]:
        """Aplica os efeitos da escolha do evento."""
        results = {"effects_applied": []}

        for effect_type, effect_value in effects.items():
            if effect_type == "hp_damage":
                damage = min(effect_value, player.hp - 1)  # Não mata o jogador
                player.hp -= damage
                results["effects_applied"].append(f"Perdeu {damage} HP")

            elif effect_type == "heal_full":
                healed = player.hp_max - player.hp
                player.hp = player.hp_max
                results["effects_applied"].append(f"HP totalmente restaurado (+{healed})")

            elif effect_type == "heal_percentage":
                heal_amount = int(player.hp_max * effect_value / 100)
                player.hp = min(player.hp_max, player.hp + heal_amount)
                results["effects_applied"].append(f"Curou {heal_amount} HP")

            elif effect_type == "restore_mp":
                restored = player.mp_max - player.mp
                player.mp = player.mp_max
                results["effects_applied"].append(f"MP totalmente restaurado (+{restored})")

            elif effect_type == "restore_mp_percentage":
                restore_amount = int(player.mp_max * effect_value / 100)
                player.mp = min(player.mp_max, player.mp + restore_amount)
                results["effects_applied"].append(f"Restaurou {restore_amount} MP")

            elif effect_type == "xp":
                player.ganhar_xp(effect_value)
                results["effects_applied"].append(f"Ganhou {effect_value} XP")

            elif effect_type == "gold":
                if isinstance(effect_value, list):
                    amount = random.randint(effect_value[0], effect_value[1])
                else:
                    amount = effect_value
                player.ouro += amount
                results["effects_applied"].append(f"Ganhou {amount} ouro")

            elif effect_type == "lose_gold":
                amount = min(effect_value, player.ouro)
                player.ouro -= amount
                results["effects_applied"].append(f"Perdeu {amount} ouro")

            elif effect_type == "gain_blessing":
                # Implementar sistema de bênçãos temporárias
                blessing = effect_value
                results["effects_applied"].append(f"Recebeu bênção: {blessing['type']}")

            elif effect_type == "message":
                results["special_message"] = effect_value

            # Adicionar mais efeitos conforme necessário

        return results

    def update_cooldowns(self):
        """Atualiza cooldowns dos eventos."""
        for event_id in list(self.event_cooldown.keys()):
            self.event_cooldown[event_id] -= 1
            if self.event_cooldown[event_id] <= 0:
                del self.event_cooldown[event_id]

    def get_event_display_data(self, event: RandomEvent) -> Dict[str, Any]:
        """Retorna dados formatados para exibição do evento."""
        return {
            "name": event.name,
            "description": event.description,
            "flavor_text": random.choice(event.flavor_text) if event.flavor_text else "",
            "choices": [
                {
                    "text": choice.text,
                    "available": True  # Verificar requisitos se necessário
                }
                for choice in event.choices
            ],
            "rarity": event.rarity.value,
            "type": event.event_type.value
        }


def create_random_event_manager() -> RandomEventManager:
    """Factory function para criar manager de eventos."""
    return RandomEventManager()