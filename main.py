from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

# Imports que faltavam, agora adicionados:
from core.engine import GameEngine
from screens.main_menu import MainMenuScreen

class ZorgApp(App):
    """A aplicação principal do jogo ZORG construída com Textual."""

    CSS = """
    Screen {
        background: #0d0d0d;
        color: #cccccc;
    }

    Header {
        background: #2d2d2d;
        color: #cccccc;
        text-style: bold;
    }
    """

    BINDINGS = [
        ("q", "quit", "Sair do Jogo"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = GameEngine()
        # MODO DE ECRÃ INTEIRO ATIVADO AQUI
        self.full_screen = True

    def on_mount(self) -> None:
        """
        Método chamado quando a aplicação está pronta para ser exibida.
        É o local ideal para mostrar a primeira tela.
        """
        self.push_screen(MainMenuScreen())

    def action_quit(self) -> None:
        self.exit()

if __name__ == "__main__":
    app = ZorgApp()
    app.run()