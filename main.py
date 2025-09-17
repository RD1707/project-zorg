from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

# Imports que faltavam, agora adicionados:
from core.engine import GameEngine
from core.managers.event_manager import subscribe_to_event, EventType
from screens.main_menu import MainMenuScreen
from screens.shop_screen import ShopScreen

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
        # Configurar event handlers
        subscribe_to_event(EventType.SHOW_SHOP_SCREEN, self._handle_show_shop)

        self.push_screen(MainMenuScreen())

    def _handle_show_shop(self, event) -> None:
        """Handler para evento de mostrar a loja."""
        engine = event.data.get("engine")
        if engine:
            self.push_screen(ShopScreen(engine))

    def action_quit(self) -> None:
        self.exit()

if __name__ == "__main__":
    app = ZorgApp()
    app.run()