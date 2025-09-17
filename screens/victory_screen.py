from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Static

class VictoryScreen(Screen):
    """Tela para exibir as recompensas após uma vitória em combate."""

    BINDINGS = [
        Binding("enter", "dismiss", "Continuar"),
    ]

    CSS = """
    VictoryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7); /* Fundo semi-transparente */
    }

    #victory_box {
        width: 60;
        height: auto;
        padding: 2;
        border: double yellow;
        background: #1e1e1e;
        align: center middle;
    }
    
    #victory_title {
        text-style: bold;
        color: yellow;
    }

    .reward_line {
        margin-top: 1;
    }
    
    #level_up_box {
        margin-top: 1;
        padding: 1;
        border: round green;
    }
    """

    def __init__(self, victory_data: dict):
        """Recebe o dicionário com os dados da vitória."""
        super().__init__()
        self.victory_data = victory_data

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with Vertical(id="victory_box"):
            yield Static("✨ V I T Ó R I A ✨", id="victory_title")

            # Mostra as recompensas base
            yield Static(f"⭐ XP Ganho: [b yellow]{self.victory_data['xp_ganho']}[/b yellow]", classes="reward_line")
            yield Static(f"🪙 Ouro Ganho: [b yellow]{self.victory_data['ouro_ganho']}[/b yellow]", classes="reward_line")

            # Se houve um level up, mostra os detalhes
            level_up_info = self.victory_data.get("level_up")
            if level_up_info:
                with Vertical(id="level_up_box"):
                    yield Static(f"[b green]LEVEL UP! Você alcançou o Nível {level_up_info['nivel']}![/b green]")
                    yield Static(f"❤️ HP Máximo +{level_up_info['hp_bonus']}")
                    yield Static(f"💙 MP Máximo +{level_up_info['mp_bonus']}")
                    yield Static(f"⚔️ Ataque Base +{level_up_info['atk_bonus']}")
                    yield Static(f"🛡️ Defesa Base +{level_up_info['def_bonus']}")