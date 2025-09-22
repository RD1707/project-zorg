import asyncio

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Static


class StoryScreen(Screen):
    """
    Uma tela reutilizável para exibir texto de história de forma progressiva.
    """

    BINDINGS = [
        Binding("enter", "advance_story", "Avançar"),
    ]

    CSS = """
    StoryScreen {
        align: center middle;
    }

    #story_container {
        width: 80%;
        max-width: 90;
        height: auto;
        padding: 2;
        border: round #666;
        background: #1e1e1e;
    }

    #story_text {
        height: auto;
        margin-bottom: 1;
    }

    #prompt {
        text-align: right;
        text-style: italic;
    }
    """

    def __init__(self, story_segments: list[str]):
        """
        Ao criar a tela, passamos uma lista de textos que compõem a história.
        """
        super().__init__()
        self.story_segments = story_segments
        self.current_segment_index = 0
        self.is_typing = False
        self.current_typing_task = None

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with Center():
            with Vertical(id="story_container"):
                yield Static(id="story_text")
                yield Static("[Pressione ENTER para continuar...]", id="prompt")

    async def on_mount(self) -> None:
        """
        Chamado quando a tela é mostrada pela primeira vez.
        Exibe o primeiro segmento da história.
        """
        if self.story_segments:
            self.current_typing_task = asyncio.create_task(
                self.type_text(self.story_segments[self.current_segment_index])
            )
            await self.current_typing_task
        else:
            # Se não houver história, simplesmente permite fechar
            self.query_one("#story_text", Static).update("...")

    async def type_text(self, text: str):
        """Anima o texto letra por letra com suporte a velocidade configurável."""
        self.is_typing = True
        story_text_widget = self.query_one("#story_text", Static)
        prompt = self.query_one("#prompt")
        prompt.visible = False
        story_text_widget.update("")  # Limpa o texto anterior

        try:
            # Obter velocidade das configurações se disponível
            delay = 0.025  # Padrão
            if hasattr(self.app, 'engine') and hasattr(self.app.engine, 'settings'):
                if hasattr(self.app.engine.settings, 'get_text_speed_delay'):
                    delay = self.app.engine.settings.get_text_speed_delay()

            current_text = ""
            for char in text:
                current_text += char
                story_text_widget.update(current_text)
                if delay > 0:  # Se delay for 0, mostra instantaneamente
                    await asyncio.sleep(delay)
        except asyncio.CancelledError:
            # Se foi cancelado, mostra o texto completo imediatamente
            story_text_widget.update(text)

        prompt.visible = True
        self.is_typing = False
        self.current_typing_task = None

    async def action_advance_story(self) -> None:
        """
        Ação executada quando a tecla ENTER é pressionada.
        Avança para o próximo segmento da história.
        """
        # Se o texto ainda está a ser escrito, completa-o imediatamente
        if self.is_typing and self.current_typing_task:
            self.current_typing_task.cancel()
            # Aguarda um pouco para que o texto seja completado
            await asyncio.sleep(0.1)
            return

        self.current_segment_index += 1

        if self.current_segment_index < len(self.story_segments):
            self.current_typing_task = asyncio.create_task(
                self.type_text(self.story_segments[self.current_segment_index])
            )
            await self.current_typing_task
        else:
            self.dismiss()
