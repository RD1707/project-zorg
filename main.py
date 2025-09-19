# main.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.geometry import Size  # <--- 1. VERIFIQUE SE ESTA IMPORTAÇÃO ESTÁ AQUI

# Imports do seu projeto
from core.engine import GameEngine
from core.managers.event_manager import subscribe_to_event, EventType
from screens.main_menu import MainMenuScreen
from screens.shop_screen import ShopScreen
from ui.styles.global_styles import get_global_css

class ZorgApp(App):
    """A aplicação principal do jogo ZORG construída com Textual."""

    # --- 2. VERIFIQUE SE OS TAMANHOS ESTÃO DEFINIDOS AQUI ---
    # Devem estar DENTRO da classe, mas FORA de qualquer método.
    MIN_SIZE = Size(139, 42)
    MAX_SIZE = Size(139, 42)

    CSS = get_global_css()

    BINDINGS = [
        ("q", "quit", "Sair do Jogo"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = GameEngine()
        # --- 3. GARANTA QUE A LINHA ABAIXO FOI REMOVIDA OU COMENTADA ---
        # self.full_screen = True

    def on_mount(self) -> None:
        """
        Método chamado quando a aplicação está pronta para ser exibida.
        É o local ideal para mostrar a primeira tela.
        """
        subscribe_to_event(EventType.SHOW_SHOP_SCREEN, self._handle_show_shop)

        # Iniciar música de menu
        if hasattr(self.engine, 'audio_manager'):
            self.engine.audio_manager.play_music("main_menu_theme")

        self.push_screen(MainMenuScreen())

    def _handle_show_shop(self, event) -> None:
        """Handler para evento de mostrar a loja."""
        engine = event.data.get("engine")
        if engine:
            self.push_screen(ShopScreen(engine))

    def action_quit(self) -> None:
        # Limpar recursos do engine antes de sair
        if hasattr(self, 'engine') and self.engine:
            self.engine.shutdown()
        self.exit()

    def on_exit(self) -> None:
        """Chamado quando a aplicação está sendo finalizada."""
        # Garantir que o engine seja limpo na saída
        if hasattr(self, 'engine') and self.engine:
            self.engine.shutdown()

if __name__ == "__main__":
    app = ZorgApp()
    app.run()