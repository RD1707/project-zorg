# main.py
"""
ZORG - Aplicação principal do jogo.
Um RPG épico baseado em texto onde o código encontra a coragem.
"""

from textual.app import App
from textual.geometry import Size

from core.engine import GameEngine
from core.managers.event_manager import EventType, subscribe_to_event
from screens.main_menu import MainMenuScreen
from screens.shop_screen import ShopScreen
from ui.styles.global_styles import get_global_css


class ZorgApp(App):
    """
    A aplicação principal do jogo ZORG construída com Textual.

    Gerencia o ciclo de vida do jogo, eventos globais e navegação entre telas.
    """

    # Configurações de tamanho da aplicação
    MIN_SIZE = Size(80, 25)  # Tamanho mínimo para uma boa experiência

    CSS = get_global_css()

    BINDINGS = [
        ("q", "quit", "Sair do Jogo"),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = GameEngine()

    def on_mount(self) -> None:
        """
        Método chamado quando a aplicação está pronta para ser exibida.
        Configura eventos e exibe a tela inicial.
        """
        # Configurar event handlers
        subscribe_to_event(EventType.SHOW_SHOP_SCREEN, self._handle_show_shop)

        # Iniciar música de menu se disponível
        if hasattr(self.engine, "audio_manager"):
            self.engine.audio_manager.play_music("main_menu_theme")

        # Mostrar tela principal
        self.push_screen(MainMenuScreen())

    def _handle_show_shop(self, event) -> None:
        """Handler para evento de mostrar a loja."""
        engine = event.data.get("engine")
        if engine:
            self.push_screen(ShopScreen(engine))

    def action_quit(self) -> None:
        """Ação para sair do jogo, limpando recursos."""
        self._cleanup_resources()
        self.exit()

    def on_exit(self) -> None:
        """Chamado quando a aplicação está sendo finalizada."""
        self._cleanup_resources()

    def _cleanup_resources(self) -> None:
        """Limpa recursos do engine antes de encerrar."""
        if hasattr(self, "engine") and self.engine:
            self.engine.shutdown()


if __name__ == "__main__":
    app = ZorgApp()
    app.run()
