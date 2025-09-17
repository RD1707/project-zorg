import asyncio
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, Container
from textual.screen import Screen
from textual.widgets import Button, RichLog, Static

from core.models import Personagem
from core.engine import GameEngine

# Importa as telas modais que o combate pode chamar
from .item_screen import ItemScreen
from .skill_screen import SkillScreen

class CombatScreen(Screen):
    """A tela principal onde o combate do jogo acontece."""

    BINDINGS = [
        Binding("a", "attack", "Atacar", priority=True),
        Binding("h", "skill", "Habilidade", priority=True),
        Binding("i", "item", "Item", priority=True),
    ]

    CSS = """
    #combat_layout {
        layout: horizontal;
        height: 100%;
    }

    #character_panels {
        width: 30%;
        height: 100%;
        padding: 1;
    }

    #action_panel {
        width: 70%;
        height: 100%;
        align: center middle;
    }

    .character_box {
        height: 50%;
        border: round white;
        padding: 1;
        margin-bottom: 2;
        /* Adiciona transição para suavizar a animação */
    }

    #player_box {
        border-title-color: cyan;
        border-title-align: center;
    }
    
    #enemy_box {
        border-title-color: red;
        border-title-align: center;
    }

    #combat_log {
        width: 90%;
        height: 70%;
        border: round #555;
        margin-bottom: 1;
    }
    
    #turn_indicator {
        width: 90%;
        text-align: center;
        text-style: bold;
        color: yellow;
        margin-bottom: 1;
    }

    #action_buttons {
        width: 90%;
        height: auto;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
    }
    
    Button {
        width: 100%;
    }
    
    Button.-disabled {
        background: #333;
        color: #555;
        border: tall #444;
    }
    """

    def __init__(self, engine: GameEngine, inimigo: Personagem):
        super().__init__()
        self.engine = engine
        self.jogador = engine.jogador
        self.inimigo = inimigo

    def _create_bar(self, current: int, maximum: int, color: str) -> str:
        """Cria uma barra de texto para representar HP, MP, etc."""
        percent = current / maximum if maximum > 0 else 0
        width = 15  # Largura da barra em caracteres
        filled_width = int(percent * width)
        bar = f"[{color}]" + "█" * filled_width + "[/]" + "░" * (width - filled_width)
        return f"{bar} {current}/{maximum}"

    def compose(self) -> ComposeResult:
        with Horizontal(id="combat_layout"):
            with Vertical(id="character_panels"):
                yield Container(id="player_box")
                yield Container(id="enemy_box")

            with Vertical(id="action_panel"):
                yield Static("Sua Vez!", id="turn_indicator")
                yield RichLog(id="combat_log", highlight=True, markup=True)
                with Horizontal(id="action_buttons"):
                    yield Button("Atacar (A)", id="attack", variant="primary")
                    yield Button("Habilidade (H)", id="skill", variant="warning")
                    yield Button("Item (I)", id="item", variant="success")
    
    def on_mount(self) -> None:
        self.update_character_panels()
        self.log_message(f"Um [b red]{self.inimigo.nome}[/b red] selvagem aparece!")

    def update_character_panels(self):
        # --- Painel do Jogador ---
        hp_bar = self._create_bar(self.jogador.hp, self.jogador.hp_max, "green")
        mp_bar = self._create_bar(self.jogador.mp, self.jogador.mp_max, "blue")
        
        player_status = ""
        if self.jogador.turnos_veneno > 0:
            player_status += f"[magenta]Envenenado ({self.jogador.turnos_veneno}t) [/magenta]"
        if self.jogador.turnos_buff_defesa > 0:
            player_status += f"[cyan]Defesa+ ({self.jogador.turnos_buff_defesa}t)[/cyan]"
        if player_status:
            player_status = f"\nStatus: {player_status}"

        player_content = f"""
[b cyan]Manu (Nível {self.jogador.nivel})[/b cyan]
HP: {hp_bar}
MP: {mp_bar}
Ataque: {self.jogador.ataque_total}   Defesa: {self.jogador.defesa_total}{player_status}
        """
        player_box = self.query_one("#player_box")
        player_box.border_title = self.jogador.nome
        player_box.remove_children()
        player_box.mount(Static(player_content))

        # --- Painel do Inimigo ---
        enemy_hp_bar = self._create_bar(self.inimigo.hp, self.inimigo.hp_max, "red")
        
        enemy_status = ""
        if self.inimigo.turnos_veneno > 0:
            enemy_status += f"[magenta]Envenenado ({self.inimigo.turnos_veneno}t)[/magenta]"
        if enemy_status:
            enemy_status = f"\nStatus: {enemy_status}"

        enemy_content = f"""
[b red]{self.inimigo.nome}[/b red]
HP: {enemy_hp_bar}
Ataque: {self.inimigo.ataque_total}   Defesa: {self.inimigo.defesa_total}{enemy_status}
        """
        enemy_box = self.query_one("#enemy_box")
        enemy_box.border_title = self.inimigo.nome
        enemy_box.remove_children()
        enemy_box.mount(Static(enemy_content))
    
    def log_message(self, message: str):
        self.query_one(RichLog).write(message)

    async def processar_turno_completo(self, acao: str, **kwargs):
        """Função centralizada para processar um turno completo (jogador e inimigo)."""
        turn_indicator = self.query_one("#turn_indicator")
        
        # --- Turno do Jogador ---
        turn_indicator.update("Sua Vez!")
        for btn in self.query(Button):
            btn.disabled = True

        if acao == "attack" or acao == "skill":
            player_box = self.query_one("#player_box")
            player_box.styles.offset = (2, 0)
            await asyncio.sleep(0.08)
            player_box.styles.offset = (0, 0)
            await asyncio.sleep(0.1)

        player_messages = self.engine.processar_turno_jogador(acao, self.inimigo, **kwargs)
        for msg in player_messages:
            self.log_message(msg)
            await asyncio.sleep(0.5)
        
        self.update_character_panels()

        if self.inimigo.hp <= 0:
            self.log_message(f"[b green]{self.inimigo.nome} foi derrotado![/b green]")
            await asyncio.sleep(1)
            self.dismiss(True)
            return

        # --- Turno do Inimigo ---
        turn_indicator.update(f"Vez de [b red]{self.inimigo.nome}[/b red]...")
        await asyncio.sleep(1)

        enemy_box = self.query_one("#enemy_box")
        enemy_box.styles.offset = (-2, 0)
        await asyncio.sleep(0.08)
        enemy_box.styles.offset = (0, 0)
        await asyncio.sleep(0.1)
        
        enemy_messages = self.engine.processar_turno_inimigo(self.inimigo)
        for msg in enemy_messages:
            self.log_message(msg)
            await asyncio.sleep(0.5)
        
        self.update_character_panels()

        if self.jogador.hp <= 0:
            self.log_message("[b red]Você foi derrotado...[/b red]")
            await asyncio.sleep(1)
            self.dismiss(False)
            return

        # --- Fim do Turno ---
        turn_indicator.update("Sua Vez!")
        for btn in self.query(Button):
            btn.disabled = False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com cliques nos botões de ação."""
        if event.button.id == "attack":
            await self.processar_turno_completo("attack")
        elif event.button.id == "item":
            self.app.push_screen(ItemScreen(self.jogador), self.on_item_selected)
        elif event.button.id == "skill":
            self.app.push_screen(SkillScreen(self.jogador), self.on_skill_selected)

    async def on_item_selected(self, item_selecionado: str):
        """Callback: chamado quando a ItemScreen é fechada."""
        if item_selecionado:
            item_nome_real = item_selecionado.replace("_", " ")
            await self.processar_turno_completo("item", nome_item=item_nome_real)
        else:
            self.log_message("Você decidiu não usar um item.")
    
    async def on_skill_selected(self, habilidade_selecionada: str):
        """Callback: chamado quando a SkillScreen é fechada."""
        if habilidade_selecionada:
            habilidade_nome_real = habilidade_selecionada.replace("_", " ")
            await self.processar_turno_completo("skill", nome_habilidade=habilidade_nome_real)
        else:
            self.log_message("Você decidiu não usar uma habilidade.")
            
    def action_attack(self):
        if not self.query_one("#attack", Button).disabled:
            self.query_one("#attack", Button).press()
    
    def action_item(self):
        if not self.query_one("#item", Button).disabled:
            self.query_one("#item", Button).press()

    def action_skill(self):
        if not self.query_one("#skill", Button).disabled:
            self.query_one("#skill", Button).press()