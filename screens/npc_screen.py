"""
Tela de interação com NPCs.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer
from textual.containers import ScrollableContainer, Vertical 
from typing import Optional

from core.engine import GameEngine
from data.npcs import NPC, DialogOption, QuestStatus


class NPCScreen(Screen):
    """Tela para interagir com NPCs."""

    BINDINGS = [
        ("escape", "dismiss", "Voltar"),
    ]

    CSS = """
    NPCScreen {
        align: center top;
    }

    #npc_container {
        width: 90%;
        max-width: 100;
        height: 85%;
        margin-top: 2;
    }

    #npc_info {
        height: auto;
        margin-bottom: 2;
        padding: 1;
        background: #1e1e1e;
        border: round #444;
    }

    #npc_name {
        text-style: bold;
        margin-bottom: 1;
    }

    #npc_description {
        color: #cccccc;
        margin-bottom: 1;
    }

    #npc_greeting {
        text-style: italic;
        margin-bottom: 1;
    }

    #dialog_options {
        height: auto;
    }

    #dialog_options Button {
        width: 100%;
        margin-bottom: 1;
    }

    #quests_section {
        margin-top: 2;
        padding: 1;
        background: #2a2a2a;
        border: round #555;
    }

    .quest_item {
        margin-bottom: 1;
        padding: 1;
        background: #333;
        border: round #666;
    }

    .quest_available {
        border: round green;
    }

    .quest_active {
        border: round yellow;
    }

    .quest_completed {
        border: round blue;
    }
    """

    def __init__(self, engine: GameEngine, npc: NPC):
        super().__init__()
        self.engine = engine
        self.npc = npc

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela de NPC."""
        yield Header(name=f"Conversando com {self.npc.name}")

        with ScrollableContainer(id="npc_container"):
            with Vertical(id="npc_info"):
                yield Static(self.npc.name, id="npc_name")
                yield Static(self.npc.description, id="npc_description")
                yield Static(f'"{self.npc.greeting}"', id="npc_greeting")

            with Vertical(id="dialog_options"):
                for i, option in enumerate(self.npc.dialog_options):
                    yield Button(option.text, id=f"dialog_{i}", variant="primary")

            # Seção de missões
            if self.npc.quests:
                with Vertical(id="quests_section"):
                    yield Static("Missões:", classes="quest_header")
                    for quest in self.npc.quests:
                        quest_class = f"quest_{quest.status.value}"
                        status_icon = self._get_quest_status_icon(quest.status)

                        quest_info = f"{status_icon} {quest.name}\n{quest.description}"
                        if quest.status == QuestStatus.ACTIVE:
                            quest_info += f"\nProgresso: {quest.progress}/{quest.max_progress}"
                        elif quest.status == QuestStatus.COMPLETED:
                            quest_info += "\nConcluída!"

                        yield Static(quest_info, classes=f"quest_item {quest_class}")

        yield Footer()

    def _get_quest_status_icon(self, status: QuestStatus) -> str:
        """Retorna o ícone apropriado para o status da missão."""
        icons = {
            QuestStatus.AVAILABLE: "!",
            QuestStatus.ACTIVE: "-",
            QuestStatus.COMPLETED: "✓",
            QuestStatus.FAILED: "X"
        }
        return icons.get(status, "?")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com as opções de diálogo."""
        if event.button.id.startswith("dialog_"):
            option_index = int(event.button.id.split("_")[1])
            option = self.npc.dialog_options[option_index]

            # Mostrar resposta do NPC
            self.app.notify(f'{self.npc.name}: "{option.response}"', timeout=8)

            # Processar ações especiais
            if option.action == "give_quest" and option.quest_id:
                self._handle_give_quest(option.quest_id)
            elif option.action == "complete_quest" and option.quest_id:
                self._handle_complete_quest(option.quest_id)

    def _handle_give_quest(self, quest_id: str) -> None:
        """Processa o evento de dar uma missão."""
        quest = next((q for q in self.npc.quests if q.id == quest_id), None)
        if quest and quest.status == QuestStatus.AVAILABLE:
            quest.status = QuestStatus.ACTIVE

            # Adicionar missão ao jogador (assumindo que o sistema de missões será implementado)
            self.app.notify(f"Nova missão aceita: {quest.name}!", timeout=5)

            # Atualizar a tela
            self.refresh()

    def _handle_complete_quest(self, quest_id: str) -> None:
        """Processa o evento de completar uma missão."""
        quest = next((q for q in self.npc.quests if q.id == quest_id), None)
        if quest and quest.is_complete():
            quest.complete_quest()

            # Dar recompensas
            self.engine.jogador.xp += quest.reward_xp
            self.engine.jogador.ouro += quest.reward_gold

            for item_name in quest.reward_items:
                self.engine.adicionar_item_inventario(item_name)

            # Verificar level up
            level_up_info = self.engine.verificar_level_up()

            reward_text = f"Missão completada!\n+{quest.reward_xp} XP, +{quest.reward_gold} Ouro"
            if quest.reward_items:
                reward_text += f"\nItens: {', '.join(quest.reward_items)}"

            if level_up_info:
                reward_text += f"\nNível aumentou para {level_up_info['new_level']}!"

            self.app.notify(reward_text, timeout=10)

            # Atualizar a tela
            self.refresh()


class NPCLocationScreen(Screen):
    """Tela para escolher NPCs em uma localização específica."""

    BINDINGS = [
        ("escape", "dismiss", "Voltar"),
    ]

    CSS = """
    NPCLocationScreen {
        align: center top;
    }

    #location_container {
        width: 80%;
        max-width: 80;
        height: 80%;
        margin-top: 2;
    }

    #location_header {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }

    #npcs_list {
        height: auto;
    }

    #npcs_list Button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    def __init__(self, engine: GameEngine, location: str, npcs: list):
        super().__init__()
        self.engine = engine
        self.location = location
        self.npcs = npcs

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela de localização."""
        location_names = {
            "docas": "Docas do Porto",
            "praca_central": "Praça Central",
            "taverna": "Taverna 'O Pescador Cansado'",
            "entrada_cidade": "Portão da Cidade",
            "biblioteca": "Biblioteca Antiga"
        }

        location_title = location_names.get(self.location, self.location.title())

        yield Header(name=f"Explorando: {location_title}")

        with Vertical(id="location_container"):
            yield Static(location_title, id="location_header")

            with Vertical(id="npcs_list"):
                if not self.npcs:
                    yield Static("Não há ninguém interessante por aqui no momento.", classes="empty_message")
                else:
                    for npc in self.npcs:
                        quest_indicator = ""
                        available_quests = npc.get_available_quests()
                        active_quests = npc.get_active_quests()

                        if available_quests:
                            quest_indicator = " !"
                        elif active_quests:
                            quest_indicator = " -"

                        button_text = f"{npc.name}{quest_indicator}"
                        yield Button(button_text, id=f"npc_{npc.id}", variant="primary")

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com a seleção de NPCs."""
        if event.button.id.startswith("npc_"):
            npc_id = event.button.id.split("_", 1)[1]
            npc = next((n for n in self.npcs if n.id == npc_id), None)
            if npc:
                self.app.push_screen(NPCScreen(self.engine, npc))