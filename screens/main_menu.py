from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical
from textual.binding import Binding

from .story_screen import StoryScreen
from .game_screen import GameScreen
from .character_creation_screen import CharacterCreationScreen

# Arte ASCII para o título.
ZORG_TITLE = r"""
   .-') _             _  .-')               
  (  OO) )           ( \( -O )              
,(_)----. .-'),-----. ,------.   ,----.     
|       |( OO'  .-.  '|   /`. ' '  .-./-')  
'--.   / /   |  | |  ||  /  | | |  |_( O- ) 
(_/   /  \_) |  |\|  ||  |_.' | |  | .--, \ 
 /   /___  \ |  | |  ||  .  '.'(|  | '. (_/ 
|        |  `'  '-'  '|  |\  \  |  '--'  |  
`--------'    `-----' `--' '--'  `------'   
"""

# A história de introdução do jogo.
STORY_INTRODUCTION = [
    "Era uma vez, em um tempo onde o amor ainda era puro... No tranquilo vilarejo de Coden, dois coracoes batiam em perfeita sintonia: Manuella, artesa de maos habilidosas, e Ramon, programador de codigos brilhantes.",
    "Seu amor era como um algoritmo perfeito - sem bugs, sem falhas, sem fim. Mas nas sombras, o feiticeiro Zorg observava com inveja corrosiva. Seu coracao era um void - vazio, corrompido, incapaz de amar.",
    "'Se eu nao posso ter amor', ele sussurrou, 'ninguem pode ter.' Em uma noite sem lua, Zorg atacou. Com magia negra, ele aprisionou Ramon num loop infinito no topo da temível Torre do Ponteiro Nulo.",
    "Com o coracao despedaçado mas o espirito inabalavel, Manuella ergue-se. Nao mais apenas uma artesa. Ela é agora uma HEROINA. E nada vai impedi-la de reescrever este destino cruel.",
    "A jornada começa AGORA."
]


class MainMenuScreen(Screen):
    """A tela do menu principal do jogo, com um design aprimorado e minimalista."""
    
    # BINDINGS e Footer foram removidos para uma interface mais limpa.
    
    CSS = """
    MainMenuScreen {
        align: center middle;
        background: #0d0d0d;
    }

    #main_menu_container {
        width: auto;
        height: auto;
        align: center middle;
    }

    #title {
        width: auto;
        height: auto;
        padding: 1 3;
        margin-bottom: 1;
        text-style: bold;
        color: white;
    }

    #subtitle {
        width: 100%;
        text-align: center;
        color: white;
        margin-bottom: 2;
    }

    #menu {
        width: 45;
        height: auto;
        border: round #333333;
        padding: 1 2;
    }

    Button {
        width: 100%;
        margin-bottom: 1;
        background: black;
        color: white;
        border: tall #222222;
    }
    
    Button:hover {
        background: #222222;
        border: tall white;
        color: white;
    }
    
    #quit {
        display: none;
    }
    """

    def compose(self) -> ComposeResult:
        """Cria os widgets para a tela do menu sem o botão de sair e o rodapé."""
        with Vertical(id="main_menu_container"):
            yield Static(ZORG_TITLE, id="title")
            yield Static("Onde o código encontra a coragem.", id="subtitle")
            
            with Vertical(id="menu"):
                yield Button("Novo Jogo", id="new_game", variant="primary")
                yield Button("Carregar Jogo", id="load_game", variant="default")
                yield Button("Salvar Jogo", id="save_game", variant="success", disabled=True)
                yield Button("Configurações", id="settings", variant="default")

    def on_mount(self) -> None:
        """Chamado quando a tela é montada. Ativa o botão de salvar se houver um jogo em andamento."""
        save_button = self.query_one("#save_game", Button)
        save_button.disabled = self.app.engine.jogador is None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Chamado quando um botão é pressionado."""
        if event.button.id == "new_game":
            self.app.push_screen(CharacterCreationScreen(), self._handle_character_creation)
            
        elif event.button.id == "load_game":
            sucesso = self.app.engine.load_game_state()
            if sucesso:
                self.app.notify("Jogo carregado com sucesso!")
                self.start_game(None)
            else:
                self.app.notify("[b]Erro:[/b] Nenhum jogo salvo encontrado ou o ficheiro esta corrompido.", timeout=5)

        elif event.button.id == "save_game":
            sucesso = self.app.engine.save_game_state()
            if sucesso:
                self.app.notify("Jogo salvo com sucesso!")
            else:
                self.app.notify("[b]Erro:[/b] Nao foi possivel salvar o jogo.", timeout=5)

        elif event.button.id == "settings":
            from .settings_screen import SettingsScreen
            self.app.push_screen(SettingsScreen())

    def _handle_character_creation(self, character_data):
        """Callback para lidar com a criação de personagem."""
        if character_data is None:
            # Usuário cancelou a criação
            return

        # Inicializar novo jogo com os dados do personagem
        self.app.engine.inicializar_novo_jogo(character_data)
        self.app.push_screen(StoryScreen(STORY_INTRODUCTION), self.start_game)

    def start_game(self, _):
        """Callback que inicia a tela principal do jogo."""
        self.app.push_screen(GameScreen(self.app.engine))