"""
Tela de criação de personagem.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.validation import Length
from textual.widgets import Button, Footer, Header, Input, Label, Static

from ui.styles.global_styles import get_global_css


class CharacterCreationScreen(Screen):
    """Tela para criação de personagem."""

    BINDINGS = [
        Binding("escape", "dismiss", "Voltar"),
        Binding("enter", "create_character", "Criar"),
    ]

    CSS = f"""
    CharacterCreationScreen {{
        align: center middle;
    }}

    #creation_container {{
        width: 60%;
        max-width: 80;
        height: auto;
        padding: 2;
        border: round white;
        background: #1e1e1e;
    }}

    #title {{
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
    }}

    .form_row {{
        height: auto;
        margin-bottom: 2;
    }}

    .form_label {{
        width: 30%;
        text-align: right;
        padding-right: 2;
    }}

    .form_input {{
        width: 70%;
    }}

    #character_preview {{
        margin-top: 2;
        padding: 1;
        border: round #555;
        background: #2a2a2a;
    }}

    .preview_stat {{
        margin-bottom: 1;
    }}

    #buttons_container {{
        margin-top: 2;
        height: auto;
    }}

    #create_button {{
        width: 40%;
        margin-right: 1;
    }}

    #cancel_button {{
        width: 40%;
    }}

    .error_message {{
        margin-top: 1;
        text-align: center;
        text-style: italic;
    }}

    {get_global_css()}
    """

    def __init__(self):
        super().__init__()
        self.character_name = ""
        self.character_data = {
            "nome": "",
            "hp_max": 50,
            "mp_max": 20,
            "ataque_base": 7,
            "defesa_base": 2,
            "nivel": 1,
            "xp": 0,
            "xp_proximo_nivel": 100,
        }

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela de criação."""
        yield Header(name="Criação de Personagem")

        with Vertical(id="creation_container"):
            yield Static("Criar Novo Personagem", id="title")

            # Nome do personagem
            with Horizontal(classes="form_row"):
                yield Label("Nome:", classes="form_label")
                yield Input(
                    placeholder="Digite o nome do seu personagem...",
                    validators=[Length(minimum=2, maximum=20)],
                    id="name_input",
                    classes="form_input",
                )

            # Preview do personagem
            with Vertical(id="character_preview"):
                yield Static("Preview do Personagem:", classes="preview_stat")
                yield Static(
                    f"Nome: {self.character_data['nome'] or 'Não definido'}",
                    id="preview_name",
                )
                yield Static(f"HP: {self.character_data['hp_max']}", id="preview_hp")
                yield Static(f"MP: {self.character_data['mp_max']}", id="preview_mp")
                yield Static(
                    f"Ataque: {self.character_data['ataque_base']}", id="preview_attack"
                )
                yield Static(
                    f"Defesa: {self.character_data['defesa_base']}",
                    id="preview_defense",
                )

            # Botões
            with Horizontal(id="buttons_container"):
                yield Button("Criar Personagem", id="create_button", variant="success")
                yield Button("Cancelar", id="cancel_button", variant="error")

            # Mensagem de erro
            yield Static("", id="error_message", classes="error_message")

        yield Footer()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Callback para mudanças no input do nome."""
        if event.input.id == "name_input":
            self.character_name = event.value.strip()
            self.character_data["nome"] = self.character_name
            self._update_preview()

    def _update_preview(self) -> None:
        """Atualiza o preview do personagem."""
        try:
            preview_name = self.query_one("#preview_name", Static)
            preview_name.update(
                f"Nome: {self.character_data['nome'] or 'Não definido'}"
            )
        except Exception:
            pass  # Widget pode não estar montado ainda

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Callback para botões pressionados."""
        if event.button.id == "create_button":
            self.action_create_character()
        elif event.button.id == "cancel_button":
            self.action_dismiss()

    def action_create_character(self) -> None:
        """Cria o personagem e inicia o jogo."""
        if not self._validate_character():
            return

        # Limpar mensagem de erro
        error_msg = self.query_one("#error_message", Static)
        error_msg.update("")

        # Retornar os dados do personagem para o menu principal
        self.dismiss(self.character_data)

    def _validate_character(self) -> bool:
        """Valida os dados do personagem."""
        error_msg = self.query_one("#error_message", Static)

        if not self.character_name or len(self.character_name.strip()) < 2:
            error_msg.update("Nome deve ter pelo menos 2 caracteres!")
            return False

        if len(self.character_name.strip()) > 20:
            error_msg.update("Nome deve ter no máximo 20 caracteres!")
            return False

        # Verificar caracteres válidos
        if (
            not self.character_name.replace(" ", "")
            .replace("-", "")
            .replace("_", "")
            .isalnum()
        ):
            error_msg.update(
                "Nome deve conter apenas letras, números, espaços, hífens e underscores!"
            )
            return False

        return True

    def action_dismiss(self) -> None:
        """Cancela a criação e volta ao menu."""
        self.dismiss(None)
