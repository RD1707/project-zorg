"""
Sistema de tutorial completo para o jogo ZORG.
Gerencia dicas contextuais e tutoriais baseados em TutorialFlags.
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from core.managers.base_manager import BaseManager
from core.models import TutorialFlags
from utils.logging_config import get_logger

logger = get_logger("tutorial_manager")


class TutorialTrigger(Enum):
    FIRST_COMBAT = "first_combat"
    FIRST_ABILITY_USE = "first_ability_use"
    FIRST_ITEM_USE = "first_item_use"
    FIRST_LEVEL_UP = "first_level_up"
    FIRST_EQUIPMENT = "first_equipment"
    SAVE_GAME = "save_game"
    CITY_ENTRY = "city_entry"
    SHOP_ENTRY = "shop_entry"
    INVENTORY_FULL = "inventory_full"
    LOW_HP = "low_hp"
    BOSS_FIGHT = "boss_fight"
    STATUS_EFFECTS = "status_effects"
    QUEST_RECEIVED = "quest_received"


@dataclass
class TutorialStep:
    title: str
    content: List[str]
    visual_hint: Optional[str] = None
    action_required: Optional[str] = None


@dataclass
class Tutorial:
    id: str
    trigger: TutorialTrigger
    flag_name: str
    steps: List[TutorialStep]
    priority: int = 0
    context_sensitive: bool = True


class TutorialManager(BaseManager):
    """Gerenciador de tutoriais contextuais."""

    def __init__(self):
        super().__init__("tutorial_manager")
        self.tutorials = self._initialize_tutorials()
        self.pending_tutorials = []
        self.active_tutorial = None

    def _initialize_tutorials(self) -> Dict[str, Tutorial]:
        """Inicializa todos os tutoriais do jogo."""
        tutorials = {}

        # Tutorial de combate básico
        tutorials["combat_basic"] = Tutorial(
            id="combat_basic",
            trigger=TutorialTrigger.FIRST_COMBAT,
            flag_name="combate_basico_mostrado",
            steps=[
                TutorialStep(
                    title="💀 Seu Primeiro Combate!",
                    content=[
                        "Bem-vinda ao sistema de combate do ZORG!",
                        "Durante o combate, você pode:",
                        "• [A]tacar - Usa seu ataque básico",
                        "• [H]abilidades - Usa habilidades especiais (requer MP)",
                        "• [I]tens - Usa itens do inventário",
                        "• [F]ugir - Tenta escapar do combate"
                    ],
                    visual_hint="⚔️ Escolha sua ação sabiamente!"
                )
            ],
            priority=10
        )

        # Tutorial de habilidades
        tutorials["abilities"] = Tutorial(
            id="abilities",
            trigger=TutorialTrigger.FIRST_ABILITY_USE,
            flag_name="habilidades_mostrado",
            steps=[
                TutorialStep(
                    title="✨ Habilidades Especiais",
                    content=[
                        "Habilidades são ataques poderosos que custam MP (Mana Points).",
                        "Diferentes tipos de habilidades:",
                        "• Ataque - Causam dano extra",
                        "• Cura - Restauram HP",
                        "• Buff - Melhoram suas estatísticas",
                        "• Debuff - Enfraquecem inimigos"
                    ],
                    visual_hint="💫 Use MP sabiamente - ele não se regenera automaticamente!"
                )
            ],
            priority=8
        )

        # Tutorial de itens
        tutorials["items"] = Tutorial(
            id="items",
            trigger=TutorialTrigger.FIRST_ITEM_USE,
            flag_name="itens_mostrado",
            steps=[
                TutorialStep(
                    title="🧪 Usando Itens",
                    content=[
                        "Itens podem salvar sua vida em situações difíceis!",
                        "Tipos principais:",
                        "• Poções de Cura - Restauram HP",
                        "• Poções de Mana - Restauram MP",
                        "• Antídotos - Curam envenenamento",
                        "• Itens de Buff - Melhoram temporariamente suas stats"
                    ],
                    visual_hint="💡 Dica: Use itens estrategicamente - alguns são raros!"
                )
            ],
            priority=7
        )

        # Tutorial de level up
        tutorials["level_up"] = Tutorial(
            id="level_up",
            trigger=TutorialTrigger.FIRST_LEVEL_UP,
            flag_name="level_up_mostrado",
            steps=[
                TutorialStep(
                    title="🌟 Você Subiu de Nível!",
                    content=[
                        "Parabéns! Subir de nível traz muitos benefícios:",
                        "• HP e MP máximos aumentam",
                        "• Ataque e defesa melhoram",
                        "• Novas habilidades podem ser desbloqueadas",
                        "• Acesso a equipamentos melhores"
                    ],
                    visual_hint="⭐ Continue derrotando inimigos para ganhar mais XP!"
                )
            ],
            priority=9
        )

        # Tutorial de equipamentos
        tutorials["equipment"] = Tutorial(
            id="equipment",
            trigger=TutorialTrigger.FIRST_EQUIPMENT,
            flag_name="equipamentos_mostrado",
            steps=[
                TutorialStep(
                    title="⚔️ Equipamentos",
                    content=[
                        "Equipamentos melhoram suas capacidades de combate:",
                        "• Armas - Aumentam seu ataque",
                        "• Armaduras - Aumentam sua defesa",
                        "• Escudos - Proteção extra",
                        "• Acessórios - Bônus especiais"
                    ],
                    visual_hint="🔧 Visite a loja para comprar equipamentos melhores!"
                )
            ],
            priority=6
        )

        # Tutorial de save/load
        tutorials["save_load"] = Tutorial(
            id="save_load",
            trigger=TutorialTrigger.SAVE_GAME,
            flag_name="save_load_mostrado",
            steps=[
                TutorialStep(
                    title="💾 Sistema de Save",
                    content=[
                        "Importante: Salve seu progresso frequentemente!",
                        "• Use o menu da cidade para salvar",
                        "• Seus saves ficam protegidos contra corrupção",
                        "• Você pode carregar um save a qualquer momento",
                        "• O jogo salva automaticamente em momentos críticos"
                    ],
                    visual_hint="⚠️ Não deixe para salvar só no final - acidentes acontecem!"
                )
            ],
            priority=5
        )

        # Tutorial de cidade
        tutorials["city"] = Tutorial(
            id="city",
            trigger=TutorialTrigger.CITY_ENTRY,
            flag_name="cidade_mostrada",
            steps=[
                TutorialStep(
                    title="🏘️ Bem-vinda a Nullhaven!",
                    content=[
                        "A cidade é seu refúgio entre as aventuras:",
                        "• Loja - Compre itens e equipamentos",
                        "• NPCs - Conversem e aceitem missões",
                        "• Save/Load - Gerencie seus saves",
                        "• Status - Veja estatísticas detalhadas"
                    ],
                    visual_hint="🗺️ Explore e converse com todos os NPCs!"
                )
            ],
            priority=4
        )

        # Tutorial de status effects
        tutorials["status_effects"] = Tutorial(
            id="status_effects",
            trigger=TutorialTrigger.STATUS_EFFECTS,
            flag_name="status_effects_mostrado",
            steps=[
                TutorialStep(
                    title="🌪️ Efeitos de Status",
                    content=[
                        "Efeitos temporários podem afetar o combate:",
                        "• 🟢 Buffs - Melhoram suas capacidades",
                        "• 🔴 Debuffs - Prejudicam você ou inimigos",
                        "• ☠️ Veneno - Causa dano contínuo",
                        "• 💚 Regeneração - Cura HP gradualmente"
                    ],
                    visual_hint="⏰ Todos os efeitos têm duração limitada!"
                )
            ],
            priority=3
        )

        # Tutorial de quests
        tutorials["quests"] = Tutorial(
            id="quests",
            trigger=TutorialTrigger.QUEST_RECEIVED,
            flag_name="quests_mostrado",
            steps=[
                TutorialStep(
                    title="📜 Sistema de Missões",
                    content=[
                        "NPCs podem dar missões valiosas:",
                        "• Converse com NPCs para descobrir missões",
                        "• Complete objetivos para ganhar recompensas",
                        "• XP, ouro e itens especiais te aguardam",
                        "• Algumas missões desbloqueiam novas áreas"
                    ],
                    visual_hint="🎯 Verifique seus objetivos no menu de status!"
                )
            ],
            priority=2
        )

        return tutorials

    def check_trigger(self, trigger: TutorialTrigger, player_tutorials: TutorialFlags, **context) -> Optional[Tutorial]:
        """Verifica se algum tutorial deve ser ativado."""
        for tutorial in self.tutorials.values():
            if tutorial.trigger == trigger:
                # Verificar se já foi mostrado
                flag_value = getattr(player_tutorials, tutorial.flag_name, True)
                if not flag_value:  # False significa que ainda não foi mostrado
                    return tutorial
        return None

    def queue_tutorial(self, tutorial: Tutorial):
        """Adiciona tutorial à fila de execução."""
        if tutorial not in self.pending_tutorials:
            self.pending_tutorials.append(tutorial)
            self.pending_tutorials.sort(key=lambda t: t.priority, reverse=True)
            logger.info(f"Tutorial '{tutorial.id}' adicionado à fila")

    def get_next_tutorial(self) -> Optional[Tutorial]:
        """Retorna o próximo tutorial da fila."""
        if self.pending_tutorials:
            return self.pending_tutorials.pop(0)
        return None

    def start_tutorial(self, tutorial: Tutorial):
        """Inicia um tutorial."""
        self.active_tutorial = tutorial
        logger.info(f"Iniciando tutorial: {tutorial.id}")

    def complete_tutorial(self, player_tutorials: TutorialFlags):
        """Marca tutorial atual como completo."""
        if self.active_tutorial:
            setattr(player_tutorials, self.active_tutorial.flag_name, True)
            logger.info(f"Tutorial '{self.active_tutorial.id}' completado")
            self.active_tutorial = None

    def get_tutorial_display(self, tutorial: Tutorial) -> Dict[str, Any]:
        """Retorna dados formatados para exibição do tutorial."""
        if not tutorial.steps:
            return {}

        step = tutorial.steps[0]  # Por simplicidade, usar apenas o primeiro step

        return {
            "title": step.title,
            "content": step.content,
            "visual_hint": step.visual_hint,
            "action_required": step.action_required,
            "can_skip": True
        }

    def should_show_tutorial(self, trigger: TutorialTrigger, player_tutorials: TutorialFlags) -> bool:
        """Verifica se deve mostrar tutorial para um trigger específico."""
        tutorial = self.check_trigger(trigger, player_tutorials)
        return tutorial is not None

    def get_contextual_hint(self, context: str, player_tutorials: TutorialFlags) -> Optional[str]:
        """Retorna dica contextual baseada na situação atual."""
        hints = {
            "low_hp": "💡 Dica: Use uma Poção de Cura quando seu HP estiver baixo!",
            "no_mp": "💡 Dica: Use Poções de Mana para restaurar MP e usar habilidades!",
            "inventory_full": "💡 Dica: Seu inventário está cheio! Venda itens desnecessários na loja.",
            "boss_approaching": "⚠️ Cuidado: Um chefe poderoso se aproxima! Prepare-se bem.",
            "new_area": "🗺️ Você entrou em uma nova área. Explore com cuidado!",
            "status_poisoned": "☠️ Você está envenenado! Use um Antídoto rapidamente.",
            "equipment_damaged": "🔧 Seus equipamentos estão danificados. Visite um ferreiro."
        }

        # Verificar se já mostrou tutoriais relacionados
        if context == "low_hp" and not player_tutorials.itens_mostrado:
            return hints.get("low_hp")
        elif context == "no_mp" and not player_tutorials.habilidades_mostrado:
            return hints.get("no_mp")

        return hints.get(context)

    def get_tutorial_progress(self, player_tutorials: TutorialFlags) -> Dict[str, bool]:
        """Retorna progresso dos tutoriais."""
        return {
            "Combate Básico": player_tutorials.combate_basico_mostrado,
            "Habilidades": player_tutorials.habilidades_mostrado,
            "Itens": player_tutorials.itens_mostrado,
            "Level Up": player_tutorials.level_up_mostrado,
            "Equipamentos": player_tutorials.equipamentos_mostrado,
            "Save/Load": player_tutorials.save_load_mostrado
        }

    def reset_all_tutorials(self, player_tutorials: TutorialFlags):
        """Reseta todos os tutoriais (útil para testes)."""
        player_tutorials.combate_basico_mostrado = False
        player_tutorials.habilidades_mostrado = False
        player_tutorials.itens_mostrado = False
        player_tutorials.level_up_mostrado = False
        player_tutorials.equipamentos_mostrado = False
        player_tutorials.save_load_mostrado = False
        logger.info("Todos os tutoriais foram resetados")


# Funções utilitárias para fácil integração
def create_tutorial_manager() -> TutorialManager:
    """Factory function para criar manager de tutorial."""
    return TutorialManager()


def check_tutorial_trigger(trigger: TutorialTrigger, player_tutorials: TutorialFlags, manager: TutorialManager) -> Optional[Dict[str, Any]]:
    """Função helper para verificar e obter tutorial."""
    tutorial = manager.check_trigger(trigger, player_tutorials)
    if tutorial:
        return manager.get_tutorial_display(tutorial)
    return None