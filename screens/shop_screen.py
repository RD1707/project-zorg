from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, Container
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer, Tabs, Tab, TabbedContent, TabPane

from core.engine import GameEngine
from data.items import DB_ITENS

# Itens que estarao a venda na loja
ITENS_DA_LOJA = {
    "Pocao de Cura": 50,
    "Antidoto": 75,
    "Pocao de Mana": 60,
}

class ShopScreen(Screen):
    """A tela da loja para comprar e vender itens."""

    BINDINGS = [
        Binding("escape", "dismiss", "Sair da Loja"),
    ]

    CSS = """
    ShopScreen {
        align: center top;
    }

    #shop_container {
        width: 80%;
        max-width: 80;
        height: 80%;
        margin-top: 2;
    }

    TabPane {
        padding-top: 1;
    }

    #player_gold {
        width: 100%;
        text-align: right;
        padding: 1;
        background: #222;
        border: round #555;
    }

    .item_row {
        layout: horizontal;
        width: 100%;
        height: auto;
        margin-bottom: 1;
    }

    .item_name {
        width: 70%;
        content-align: left middle;
    }

    .item_action {
        width: 30%;
        content-align: right middle;
    }
    """

    def __init__(self, engine: GameEngine):
        super().__init__()
        self.engine = engine

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela da loja."""
        yield Header(name="Loja 'O Ponteiro Enferrujado'")
        yield Static(f"Seu Ouro: [b]{self.engine.jogador.ouro}[/b]", id="player_gold")
        
        with TabbedContent(id="shop_container"):
            # Separador de Compra
            with TabPane("Comprar", id="buy_tab"):
                yield Vertical(id="buy_list")
            # Separador de Venda
            with TabPane("Vender", id="sell_tab"):
                yield Vertical(id="sell_list")
        
        yield Footer()

    def on_mount(self) -> None:
        """Preenche as listas de compra e venda quando a tela é montada."""
        self.update_buy_list()
        self.update_sell_list()

    def update_buy_list(self):
        """Atualiza a lista de itens para comprar."""
        buy_list = self.query_one("#buy_list")
        buy_list.remove_children()

        for nome, preco in ITENS_DA_LOJA.items():
            item = DB_ITENS.get(nome)
            if item:
                can_afford = self.engine.jogador.ouro >= preco
                container = Container(classes="item_row")

                # Informações detalhadas do item
                item_info = f"[b]{item.nome}[/b]\n[i]{item.descricao}[/i]"
                if hasattr(item, 'valor_cura') and item.valor_cura > 0:
                    item_info += f"\nCura: {item.valor_cura} HP"
                if hasattr(item, 'valor_mp') and item.valor_mp > 0:
                    item_info += f"\nMP: +{item.valor_mp}"

                container.mount(Static(item_info, classes="item_name"))

                button_text = f"Comprar ({preco} Ouro)"
                if not can_afford:
                    button_text += " - Sem ouro suficiente"

                container.mount(Button(button_text, id=f"buy_{nome}", disabled=not can_afford, classes="item_action"))
                buy_list.mount(container)

    def update_sell_list(self):
        """Atualiza a lista de itens para vender do inventario do jogador."""
        sell_list = self.query_one("#sell_list")
        sell_list.remove_children()

        if not self.engine.jogador.inventario:
            sell_list.mount(Static("Seu inventario esta vazio."))
        else:
            for item in self.engine.jogador.inventario:
                preco_venda = item.preco_venda
                container = Container(classes="item_row")

                # Informações detalhadas do item
                item_template = DB_ITENS.get(item.nome)
                item_info = f"[b]{item.nome}[/b] (x{item.quantidade})"
                if item_template:
                    item_info += f"\n[i]{item_template.descricao}[/i]"
                    if hasattr(item_template, 'valor_cura') and item_template.valor_cura > 0:
                        item_info += f"\nCura: {item_template.valor_cura} HP"

                container.mount(Static(item_info, classes="item_name"))
                container.mount(Button(f"Vender ({preco_venda} Ouro)", id=f"sell_{item.nome}", classes="item_action"))
                sell_list.mount(container)

    def update_gold_display(self):
        """Atualiza a exibicao de ouro do jogador."""
        self.query_one("#player_gold").update(f"Seu Ouro: [b]{self.engine.jogador.ouro}[/b]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com os cliques nos botões de comprar e vender."""
        action, item_name = event.button.id.split("_", 1)

        if action == "buy":
            preco = ITENS_DA_LOJA.get(item_name)
            if preco and self.engine.jogador.ouro >= preco:
                self.engine.jogador.ouro -= preco
                self.engine.adicionar_item_inventario(item_name)
                self.app.notify(f"Voce comprou [b]{item_name}[/b]!")
        
        elif action == "sell":
            item_para_vender = next((item for item in self.engine.jogador.inventario if item.nome == item_name), None)
            if item_para_vender:
                self.engine.jogador.ouro += item_para_vender.preco_venda
                item_para_vender.quantidade -= 1
                if item_para_vender.quantidade <= 0:
                    self.engine.jogador.inventario.remove(item_para_vender)
                self.app.notify(f"Voce vendeu [b]{item_name}[/b]!")
        
        # Atualiza tudo
        self.update_gold_display()
        self.update_buy_list()
        self.update_sell_list()