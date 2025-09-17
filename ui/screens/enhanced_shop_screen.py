"""
Interface de loja melhorada com compra múltipla e descrições detalhadas.
"""
from typing import Dict, List, Any, Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Button, Static, DataTable, Tabs, TabPane,
    Input, Select, Label, ProgressBar
)
from textual.screen import Screen, ModalScreen
from textual.validation import Number

from core.models import Personagem, Item, Equipamento
from data.loaders import get_hybrid_item_db, get_hybrid_equipment_db
from utils.logging_config import get_logger

logger = get_logger("enhanced_shop_screen")


class ItemDetailModal(ModalScreen):
    """Modal para mostrar detalhes de um item."""

    def __init__(self, item: Any, **kwargs):
        super().__init__(**kwargs)
        self.item = item

    def compose(self) -> ComposeResult:
        with Container(id="detail_modal"):
            yield Static(f"📦 {self.item.nome}", id="detail_title", classes="title")

            with ScrollableContainer():
                yield Static(f"📝 {self.item.descricao}", classes="description")

                if hasattr(self.item, 'cura_hp') and self.item.cura_hp > 0:
                    yield Static(f"❤️ Cura HP: +{self.item.cura_hp}")

                if hasattr(self.item, 'cura_mp') and self.item.cura_mp > 0:
                    yield Static(f"💙 Cura MP: +{self.item.cura_mp}")

                if hasattr(self.item, 'bonus_ataque') and self.item.bonus_ataque > 0:
                    yield Static(f"⚔️ Bônus de Ataque: +{self.item.bonus_ataque}")

                if hasattr(self.item, 'bonus_defesa') and self.item.bonus_defesa > 0:
                    yield Static(f"🛡️ Bônus de Defesa: +{self.item.bonus_defesa}")

                if hasattr(self.item, 'raridade'):
                    rarity_colors = {
                        "comum": "🟢",
                        "common": "🟢",
                        "incomum": "🔵",
                        "uncommon": "🔵",
                        "raro": "🟡",
                        "rare": "🟡",
                        "épico": "🟣",
                        "epic": "🟣",
                        "lendário": "🟠",
                        "legendary": "🟠"
                    }
                    rarity_icon = rarity_colors.get(self.item.raridade.lower(), "⚪")
                    yield Static(f"{rarity_icon} Raridade: {self.item.raridade.title()}")

                if hasattr(self.item, 'effects') and self.item.effects:
                    yield Static("✨ Efeitos Especiais:")
                    for effect in self.item.effects:
                        yield Static(f"  • {effect}")

            with Horizontal(id="detail_buttons"):
                yield Button("❌ Fechar", id="close_detail", variant="error")

    @on(Button.Pressed, "#close_detail")
    def close_modal(self):
        self.app.pop_screen()


class PurchaseModal(ModalScreen):
    """Modal para compra múltipla de itens."""

    def __init__(self, item: Any, price: int, player_gold: int, **kwargs):
        super().__init__(**kwargs)
        self.item = item
        self.price = price
        self.player_gold = player_gold
        self.max_quantity = min(10, player_gold // price) if price > 0 else 0

    def compose(self) -> ComposeResult:
        with Container(id="purchase_modal"):
            yield Static(f"🛒 Comprar: {self.item.nome}", id="purchase_title", classes="title")

            yield Static(f"💰 Preço unitário: {self.price} ouro")
            yield Static(f"💳 Seu ouro: {self.player_gold}")
            yield Static(f"📦 Máximo disponível: {self.max_quantity}")

            with Horizontal():
                yield Label("Quantidade:", classes="input_label")
                yield Input(
                    value="1",
                    type="integer",
                    id="quantity_input",
                    validators=[Number(minimum=1, maximum=self.max_quantity)]
                )

            yield Static("", id="total_cost")

            with Horizontal(id="purchase_buttons"):
                yield Button("✅ Comprar", id="confirm_purchase", variant="success")
                yield Button("❌ Cancelar", id="cancel_purchase", variant="error")

    @on(Input.Changed, "#quantity_input")
    def update_total(self, event: Input.Changed):
        try:
            quantity = int(event.value) if event.value else 0
            total_cost = quantity * self.price
            cost_display = self.query_one("#total_cost", Static)

            if total_cost <= self.player_gold:
                cost_display.update(f"💰 Total: {total_cost} ouro")
                cost_display.remove_class("error")
            else:
                cost_display.update(f"❌ Total: {total_cost} ouro (Ouro insuficiente!)")
                cost_display.add_class("error")
        except ValueError:
            pass

    @on(Button.Pressed, "#confirm_purchase")
    def confirm_purchase(self):
        try:
            quantity_input = self.query_one("#quantity_input", Input)
            quantity = int(quantity_input.value) if quantity_input.value else 0

            if 1 <= quantity <= self.max_quantity:
                total_cost = quantity * self.price
                if total_cost <= self.player_gold:
                    self.dismiss({"action": "purchase", "item": self.item, "quantity": quantity, "cost": total_cost})
                    return

            # Caso de erro
            self.dismiss({"action": "error", "message": "Quantidade inválida ou ouro insuficiente"})

        except ValueError:
            self.dismiss({"action": "error", "message": "Quantidade deve ser um número"})

    @on(Button.Pressed, "#cancel_purchase")
    def cancel_purchase(self):
        self.dismiss({"action": "cancel"})


class EnhancedShopScreen(Screen):
    """Interface de loja melhorada."""

    BINDINGS = [
        ("escape", "quit", "Voltar"),
        ("q", "quit", "Quit"),
        ("r", "refresh", "Atualizar")
    ]

    def __init__(self, player: Personagem, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.items_db = get_hybrid_item_db()
        self.equipment_db = get_hybrid_equipment_db()

        # Inventário da loja (simulado)
        self.shop_inventory = self._initialize_shop_inventory()

    def _initialize_shop_inventory(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa inventário da loja com preços e estoque."""
        inventory = {}

        # Itens consumíveis
        consumable_items = {
            "Pocao de Cura": {"price": 30, "stock": 20},
            "Pocao de Mana": {"price": 35, "stock": 15},
            "Antidoto": {"price": 40, "stock": 10},
            "Pocao de Vigor": {"price": 80, "stock": 8},
            "Elixir de Regeneracao": {"price": 120, "stock": 5},
            "Pedra de Afiar": {"price": 60, "stock": 12},
            "Oleo Protetor": {"price": 55, "stock": 12}
        }

        for item_name, data in consumable_items.items():
            if item_name in self.items_db:
                inventory[item_name] = {
                    "item": self.items_db[item_name],
                    "price": data["price"],
                    "stock": data["stock"],
                    "category": "consumable"
                }

        # Equipamentos básicos
        equipment_items = {
            "Adaga Enferrujada": {"price": 15, "stock": 3},
            "Espada Curta": {"price": 75, "stock": 2},
            "Armadura de Couro": {"price": 50, "stock": 3},
            "Escudo de Madeira": {"price": 25, "stock": 4},
            "Escudo de Bronze": {"price": 60, "stock": 2}
        }

        for item_name, data in equipment_items.items():
            if item_name in self.equipment_db:
                inventory[item_name] = {
                    "item": self.equipment_db[item_name],
                    "price": data["price"],
                    "stock": data["stock"],
                    "category": "equipment"
                }

        return inventory

    def compose(self) -> ComposeResult:
        """Compõe a interface da loja."""
        with Container(id="shop_container"):
            yield Static("🏪 Loja de Nullhaven", id="shop_title", classes="title")

            # Informações do jogador
            with Container(id="player_info"):
                yield Static(f"💰 Seu ouro: {self.player.ouro}", id="player_gold")
                yield Static(f"👤 {self.player.nome} (Nível {self.player.nivel})", id="player_name")

            # Abas da loja
            with Tabs(id="shop_tabs"):
                with TabPane("Consumíveis", id="consumables_tab"):
                    yield self._create_items_table("consumable")

                with TabPane("Equipamentos", id="equipment_tab"):
                    yield self._create_items_table("equipment")

                with TabPane("Vender", id="sell_tab"):
                    yield self._create_sell_interface()

            # Botões principais
            with Horizontal(id="main_buttons"):
                yield Button("🔄 Atualizar Loja", id="refresh_shop", variant="success")
                yield Button("⬅️ Sair da Loja", id="exit_shop", variant="primary")

    def _create_items_table(self, category: str) -> DataTable:
        """Cria tabela de itens para uma categoria."""
        table = DataTable(id=f"{category}_table")
        table.add_columns("Item", "Preço", "Estoque", "Descrição", "Ações")

        for item_name, shop_data in self.shop_inventory.items():
            if shop_data["category"] == category:
                item = shop_data["item"]
                price = shop_data["price"]
                stock = shop_data["stock"]

                # Criar descrição resumida
                description = self._get_item_summary(item)

                # Botões de ação
                actions = "Comprar | Detalhes"

                table.add_row(
                    item_name,
                    f"{price}💰",
                    f"{stock}📦",
                    description,
                    actions,
                    key=item_name
                )

        return table

    def _get_item_summary(self, item: Any) -> str:
        """Cria resumo do item para a tabela."""
        summary_parts = []

        if hasattr(item, 'cura_hp') and item.cura_hp > 0:
            summary_parts.append(f"+{item.cura_hp}❤️")

        if hasattr(item, 'cura_mp') and item.cura_mp > 0:
            summary_parts.append(f"+{item.cura_mp}💙")

        if hasattr(item, 'bonus_ataque') and item.bonus_ataque > 0:
            summary_parts.append(f"+{item.bonus_ataque}⚔️")

        if hasattr(item, 'bonus_defesa') and item.bonus_defesa > 0:
            summary_parts.append(f"+{item.bonus_defesa}🛡️")

        return " ".join(summary_parts) if summary_parts else "Item especial"

    def _create_sell_interface(self) -> Container:
        """Cria interface para vender itens."""
        with ScrollableContainer():
            yield Static("💸 Vender Itens", classes="section_header")
            yield Static("Funcionalidade de venda será implementada em breve.", classes="info_text")

            # Aqui seria a lista de itens do jogador para vender
            return Container()

    @on(DataTable.CellSelected)
    def handle_cell_selection(self, event: DataTable.CellSelected):
        """Lida com seleção de células na tabela."""
        if event.coordinate.column == 4:  # Coluna de ações
            item_key = event.data_table.get_row_at(event.coordinate.row)[0]

            if item_key in self.shop_inventory:
                shop_data = self.shop_inventory[item_key]

                # Determinar ação baseada na posição do clique
                # Por simplicidade, vamos mostrar um menu de contexto
                self._show_item_actions(item_key, shop_data)

    def _show_item_actions(self, item_key: str, shop_data: Dict[str, Any]):
        """Mostra ações disponíveis para um item."""
        item = shop_data["item"]
        price = shop_data["price"]

        # Para este exemplo, vamos diretamente abrir a modal de compra
        def handle_purchase_result(result):
            if result and result.get("action") == "purchase":
                self._process_purchase(result)
            elif result and result.get("action") == "error":
                self._show_error(result["message"])

        modal = PurchaseModal(item, price, self.player.ouro)
        self.app.push_screen(modal, handle_purchase_result)

    def _process_purchase(self, purchase_data: Dict[str, Any]):
        """Processa uma compra."""
        item = purchase_data["item"]
        quantity = purchase_data["quantity"]
        total_cost = purchase_data["cost"]

        # Verificar se ainda tem ouro suficiente
        if self.player.ouro < total_cost:
            self._show_error("Ouro insuficiente!")
            return

        # Processar compra
        self.player.ouro -= total_cost

        # Adicionar itens ao inventário do jogador
        # Nota: Isso requer que o sistema de inventário esteja implementado
        for _ in range(quantity):
            self.player.adicionar_item_inventario(item)

        # Atualizar estoque da loja
        item_name = item.nome
        if item_name in self.shop_inventory:
            self.shop_inventory[item_name]["stock"] -= quantity

        # Atualizar interface
        self._refresh_display()

        # Mostrar confirmação
        self._show_success(f"Comprou {quantity}x {item.nome} por {total_cost} ouro!")

    def _show_error(self, message: str):
        """Mostra mensagem de erro."""
        # Por simplicidade, atualizar o título temporariamente
        title = self.query_one("#shop_title", Static)
        original_text = title.renderable
        title.update(f"❌ {message}")

        # Restaurar após 3 segundos (simplificado)
        self.set_timer(3.0, lambda: title.update(original_text))

    def _show_success(self, message: str):
        """Mostra mensagem de sucesso."""
        title = self.query_one("#shop_title", Static)
        original_text = title.renderable
        title.update(f"✅ {message}")

        # Restaurar após 3 segundos
        self.set_timer(3.0, lambda: title.update(original_text))

    def _refresh_display(self):
        """Atualiza a exibição da loja."""
        # Atualizar ouro do jogador
        gold_display = self.query_one("#player_gold", Static)
        gold_display.update(f"💰 Seu ouro: {self.player.ouro}")

        # Recriar tabelas
        for category in ["consumable", "equipment"]:
            try:
                old_table = self.query_one(f"#{category}_table", DataTable)
                new_table = self._create_items_table(category)
                old_table.remove()

                # Encontrar o TabPane correto e adicionar nova tabela
                if category == "consumable":
                    tab_pane = self.query_one("#consumables_tab", TabPane)
                else:
                    tab_pane = self.query_one("#equipment_tab", TabPane)

                tab_pane.mount(new_table)
            except Exception as e:
                logger.error(f"Erro ao atualizar tabela {category}: {e}")

    @on(Button.Pressed, "#refresh_shop")
    def refresh_shop(self):
        """Atualiza a loja."""
        # Recarregar inventário da loja
        self.shop_inventory = self._initialize_shop_inventory()
        self._refresh_display()

    @on(Button.Pressed, "#exit_shop")
    def action_quit(self):
        """Sai da loja."""
        self.app.pop_screen()

    def on_mount(self):
        """Configura a tela ao ser montada."""
        self.title = "Loja Enhanced - ZORG"

    def get_css(self) -> str:
        """Retorna CSS para estilização."""
        return """
        #shop_container {
            background: $surface;
            border: solid $primary;
            height: 100%;
            padding: 1;
        }

        .title {
            text-align: center;
            background: $primary;
            color: $text;
            padding: 1;
            margin-bottom: 1;
        }

        #player_info {
            background: $secondary;
            padding: 1;
            margin-bottom: 1;
            border: solid $accent;
        }

        .section_header {
            background: $accent;
            color: $text;
            padding: 0 1;
            margin: 1 0;
            text-style: bold;
        }

        #main_buttons {
            dock: bottom;
            height: 3;
            background: $surface;
            padding: 1;
        }

        DataTable {
            margin: 1 0;
            height: 1fr;
        }

        Button {
            margin: 0 1;
            min-width: 15;
        }

        #purchase_modal, #detail_modal {
            background: $surface;
            border: solid $primary;
            width: 60%;
            height: 70%;
        }

        .error {
            color: $error;
            text-style: bold;
        }

        .input_label {
            width: 12;
            padding: 1 0;
        }

        #purchase_buttons, #detail_buttons {
            dock: bottom;
            height: 3;
            padding: 1;
        }
        """