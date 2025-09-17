from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Static

from core.models import Personagem

class ItemScreen(Screen):
    """Uma tela modal para selecionar um item do inventário em combate."""

    BINDINGS = [
        Binding("escape", "dismiss", "Cancelar"),
    ]

    CSS = """
    ItemScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #item_list_container {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 1;
        border: thick cyan;
        background: #0d0d0d;
    }

    #item_list_title {
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
    """

    def __init__(self, jogador: Personagem):
        """Recebe o objeto do jogador para aceder ao seu inventário."""
        super().__init__()
        self.jogador = jogador

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with VerticalScroll(id="item_list_container"):
            yield Static("--- INVENTÁRIO ---", id="item_list_title")
            
            # Se o inventário estiver vazio, mostra uma mensagem
            if not self.jogador.inventario:
                yield Static("O seu inventário está vazio.", classes="message")
            else:
                # Cria um botão para cada item no inventário
                for item in self.jogador.inventario:
                    # O id do botão será o nome do item com espaços substituídos, para ser um ID válido
                    yield Button(
                        f"{item.nome} (x{item.quantidade})", 
                        id=item.nome.replace(" ", "_"), 
                        variant="default"
                    )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """
        Chamado quando um botão de item é pressionado.
        Fecha a tela e retorna o nome do item (o id do botão).
        """
        self.dismiss(event.button.id)