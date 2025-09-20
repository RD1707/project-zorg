from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer

from core.engine import GameEngine
from core.managers.event_manager import emit_event, EventType
from data.npcs import DB_NPCS
from .npc_screen import NPCLocationScreen

class CityScreen(Screen):
    """A tela principal para a cidade de Nullhaven (hub)."""

    BINDINGS = [
        ("p", "progress_story", "Partir"),
    ]

    CSS = """
    CityScreen {
        layout: vertical;
        align: center top;
    }

    #city_header {
        width: 100%;
        text-align: center;
        padding: 1 0;
        text-style: bold;
        color: cyan;
    }

    #player_status_bar {
        layout: horizontal;
        height: auto;
        width: 100%;
        align: center middle;
        padding: 0 2;
        margin-bottom: 1;
    }
    
    .status_item {
        width: 1fr;
        height: auto;
        content-align: center middle;
    }

    #city_options {
        width: 80%;
        max-width: 60;
        height: auto;
        margin-top: 2;
        align: center middle;
    }

    #city_options Button {
        width: 100%;
        margin-bottom: 1;
    }
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela da cidade."""
        yield Header(name="Zorg - A Torre do Ponteiro Nulo")
        yield Static("Bem-vinda a Nullhaven", id="city_header")
        yield self.create_status_bar()

        with Vertical(id="city_options"):
            yield Button("Visitar 'O Ponteiro Enferrujado' (Loja)", id="shop", variant="primary")
            yield Button("Descansar na estalagem 'O Pescador Cansado'", id="rest", variant="success")
            yield Button("Explorar as docas", id="docks", variant="default")
            yield Button("Visitar a Praca Central", id="plaza", variant="default")
            yield Button("Ir a Biblioteca Antiga", id="library", variant="default")
            yield Button("Ir ao Portao da Cidade", id="gate", variant="default")
            yield Button("Salvar Jogo", id="save", variant="warning")
            yield Button("Partir Rumo ao Mar (Continuar Aventura)", id="progress", variant="error")
        
        yield Footer()

    def on_resume(self) -> None:
        """Chamado sempre que esta tela volta a ser o foco (ex: ao sair da loja)."""
        # Garante que os status (especialmente o ouro) estão atualizados
        self.query_one("#player_status_bar").remove()
        self.mount(self.create_status_bar(), before="#city_options")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com as escolhas do jogador na cidade."""
        if event.button.id == "shop":
            # Emitir evento para mostrar a loja em vez de instanciar diretamente
            emit_event(EventType.SHOW_SHOP_SCREEN, {"engine": self.engine})
        
        elif event.button.id == "rest":
            self.engine.jogador.hp = self.engine.jogador.hp_max
            self.engine.jogador.mp = self.engine.jogador.mp_max
            self.engine.jogador.turnos_veneno = 0
            self.app.notify("Voce descansa e sente as suas forcas renovadas. HP e MP recuperados!")
            self.on_resume() # Reutiliza a logica para atualizar o ecra

        elif event.button.id == "docks":
            npcs_na_doca = [npc for npc in DB_NPCS.values() if npc.location == "docas"]
            self.app.push_screen(NPCLocationScreen(self.engine, "docas", npcs_na_doca))

        elif event.button.id == "plaza":
            npcs_na_praca = [npc for npc in DB_NPCS.values() if npc.location == "praca_central"]
            self.app.push_screen(NPCLocationScreen(self.engine, "praca_central", npcs_na_praca))

        elif event.button.id == "library":
            npcs_na_biblioteca = [npc for npc in DB_NPCS.values() if npc.location == "biblioteca"]
            self.app.push_screen(NPCLocationScreen(self.engine, "biblioteca", npcs_na_biblioteca))

        elif event.button.id == "gate":
            npcs_no_portao = [npc for npc in DB_NPCS.values() if npc.location == "entrada_cidade"]
            self.app.push_screen(NPCLocationScreen(self.engine, "entrada_cidade", npcs_no_portao))

        elif event.button.id == "save":
            sucesso = self.engine.save_game_state()
            if sucesso:
                self.app.notify("Jogo salvo com sucesso!")
            else:
                self.app.notify("[b]Erro:[/b] Nao foi possivel salvar o jogo.", timeout=5)

        elif event.button.id == "progress":
            self.dismiss(True)

    def action_progress_story(self) -> None:
        """Acao para o atalho de teclado 'p'."""
        self.dismiss(True)

    def create_status_bar(self) -> Horizontal:
        """Funcao auxiliar para recriar a barra de status."""
        return Horizontal(
            Static(f"HP: {self.engine.jogador.hp}/{self.engine.jogador.hp_max}", classes="status_item"),
            Static(f"Ouro: {self.engine.jogador.ouro}", classes="status_item"),
            Static(f"Nivel: {self.engine.jogador.nivel}", classes="status_item"),
            id="player_status_bar"
        )