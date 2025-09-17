import asyncio
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static
from textual.containers import Center, Vertical
from textual.binding import Binding

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
        color: #ddd;
    }

    #prompt {
        text-align: right;
        color: #888;
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
            await self.type_text(self.story_segments[self.current_segment_index])
        else:
            # Se não houver história, simplesmente permite fechar
            self.query_one("#story_text", Static).update("...")


    async def type_text(self, text: str):
        """Anima o texto letra por letra."""
        self.is_typing = True
        story_text_widget = self.query_one("#story_text", Static)
        prompt = self.query_one("#prompt")
        prompt.visible = False
        story_text_widget.update("") # Limpa o texto anterior
        
        for char in text:
            story_text_widget.update(story_text_widget.render() + char)
            await asyncio.sleep(0.025) # Ajuste este valor para mudar a velocidade
        
        prompt.visible = True
        self.is_typing = False

    async def action_advance_story(self) -> None:
        """
        Ação executada quando a tecla ENTER é pressionada.
        Avança para o próximo segmento da história.
        """
        # Se o texto ainda está a ser escrito, completa-o imediatamente
        if self.is_typing:
            # Esta é uma simplificação. A implementação completa exigiria
            # cancelar a tarefa de digitação e mostrar o texto completo.
            # Por agora, vamos manter simples e não fazer nada.
            return

        self.current_segment_index += 1
        
        if self.current_segment_index < len(self.story_segments):
            await self.type_text(self.story_segments[self.current_segment_index])
        else:
            self.dismiss()