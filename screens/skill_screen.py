from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from core.models import Personagem

class SkillScreen(Screen):
    """Uma tela modal para selecionar uma habilidade em combate."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancelar"),
    ]

    CSS = """
    SkillScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #skill_list_container {
        width: 70;
        height: auto;
        max-height: 80%;
        padding: 1;
        border: thick yellow;
        background: #0d0d0d;
    }

    #skill_list_title {
        width: 100%;
        text-align: center;
        text-style: bold;
        padding-bottom: 1;
        border-bottom: solid #333;
    }

    Button {
        width: 100%;
        margin-top: 1;
    }
    
    Button.-disabled {
        background: #333;
        color: #555;
        border: tall #444;
    }
    """

    def __init__(self, jogador: Personagem):
        """Recebe o objeto do jogador para aceder às suas habilidades e MP."""
        super().__init__()
        self.jogador = jogador

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with VerticalScroll(id="skill_list_container"):
            yield Static("--- HABILIDADES ---", id="skill_list_title")
            
            if not self.jogador.habilidades_conhecidas:
                yield Static("Você não conhece nenhuma habilidade.")
            else:
                for habilidade in self.jogador.habilidades_conhecidas:
                    # Verifica se o jogador tem MP suficiente para usar a habilidade
                    tem_mp_suficiente = self.jogador.mp >= habilidade.custo_mp
                    
                    yield Button(
                        f"{habilidade.nome} (Custo: {habilidade.custo_mp} MP)", 
                        id=habilidade.nome.replace(" ", "_"), 
                        variant="warning",
                        disabled=not tem_mp_suficiente # Desativa o botão se não houver MP
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Chamado quando um botão de habilidade é pressionado.
        Fecha a tela e retorna o nome da habilidade (o id do botão).
        """
        self.dismiss(event.button.id)