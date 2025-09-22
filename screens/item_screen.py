from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Input, Static, TabbedContent, TabPane

from core.models import Personagem
from data.items import DB_ITENS


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

    #item_container {
        width: 90;
        height: auto;
        max-height: 85%;
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
        margin-bottom: 1;
    }

    #filter_section {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: #1a1a1a;
        border: round #444;
    }

    #filter_input {
        width: 100%;
        margin-bottom: 1;
    }

    .item_row {
        layout: horizontal;
        width: 100%;
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: #222;
        border: round #555;
    }

    .item_info {
        width: 70%;
        content-align: left middle;
    }

    .item_details {
        width: 30%;
        content-align: right middle;
    }

    .item_name {
        text-style: bold;
    }

    .item_description {
        color: #aaa;
        text-style: italic;
    }

    .item_type {
    }

    .filter_buttons {
        layout: horizontal;
        height: auto;
    }

    .filter_buttons Button {
        width: 1fr;
        margin-right: 1;
    }

    TabPane {
        padding: 1;
    }
    """

    def __init__(self, jogador: Personagem):
        """Recebe o objeto do jogador para aceder ao seu inventário."""
        super().__init__()
        self.jogador = jogador
        self.filter_text = ""
        self.current_filter = "all"

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with VerticalScroll(id="item_container"):
            yield Static("--- INVENTÁRIO APRIMORADO ---", id="item_list_title")

            # Seção de filtros
            with Vertical(id="filter_section"):
                yield Input(placeholder="Buscar item...", id="filter_input")
                with Horizontal(classes="filter_buttons"):
                    yield Button("Todos", id="filter_all", variant="primary")
                    yield Button(
                        "Consumíveis", id="filter_consumable", variant="default"
                    )
                    yield Button(
                        "Equipamentos", id="filter_equipment", variant="default"
                    )
                    yield Button("Cura", id="filter_healing", variant="default")

            with TabbedContent():
                with TabPane("Inventário", id="inventory_tab"):
                    yield Vertical(id="inventory_list")
                with TabPane("Equipados", id="equipped_tab"):
                    yield Vertical(id="equipped_list")

    def on_mount(self) -> None:
        """Preenche as listas quando a tela é montada."""
        self.update_inventory_list()
        self.update_equipped_list()

    def update_inventory_list(self):
        """Atualiza a lista de itens do inventário."""
        inventory_list = self.query_one("#inventory_list")
        inventory_list.remove_children()

        if not self.jogador.inventario:
            inventory_list.mount(
                Static("Seu inventário está vazio.", classes="message")
            )
        else:
            filtered_items = self.filter_items(self.jogador.inventario)

            if not filtered_items:
                inventory_list.mount(
                    Static(
                        "Nenhum item encontrado com os filtros atuais.",
                        classes="message",
                    )
                )
            else:
                for item in filtered_items:
                    item_template = DB_ITENS.get(item.nome)
                    if item_template:
                        self.create_item_row(inventory_list, item, item_template, True)

    def update_equipped_list(self):
        """Atualiza a lista de equipamentos equipados."""
        equipped_list = self.query_one("#equipped_list")
        equipped_list.remove_children()

        equipment_slots = [
            ("Arma", self.jogador.arma_equipada),
            ("Armadura", self.jogador.armadura_equipada),
            ("Escudo", self.jogador.escudo_equipada),
        ]

        has_equipment = False
        for slot_name, equipment in equipment_slots:
            if equipment:
                has_equipment = True
                self.create_equipment_row(equipped_list, slot_name, equipment)

        if not has_equipment:
            equipped_list.mount(
                Static("Nenhum equipamento equipado.", classes="message")
            )

    def create_item_row(self, container, item, item_template, is_inventory=True):
        """Cria uma linha de item com informações detalhadas."""
        with container:
            with Horizontal(classes="item_row"):
                with Vertical(classes="item_info"):
                    yield Static(
                        f"{item.nome} (x{item.quantidade})", classes="item_name"
                    )
                    yield Static(item_template.descricao, classes="item_description")
                    yield Static(f"Tipo: {item_template.tipo}", classes="item_type")

                with Vertical(classes="item_details"):
                    if (
                        hasattr(item_template, "valor_cura")
                        and item_template.valor_cura > 0
                    ):
                        yield Static(
                            f"Cura: {item_template.valor_cura} HP", classes="item_stat"
                        )
                    if (
                        hasattr(item_template, "valor_mp")
                        and item_template.valor_mp > 0
                    ):
                        yield Static(
                            f"MP: +{item_template.valor_mp}", classes="item_stat"
                        )
                    if is_inventory:
                        yield Button(
                            "Usar",
                            id=f"use_{item.nome.replace(' ', '_')}",
                            variant="success",
                        )

    def create_equipment_row(self, container, slot_name, equipment):
        """Cria uma linha de equipamento com estatísticas."""
        with container:
            with Horizontal(classes="item_row"):
                with Vertical(classes="item_info"):
                    yield Static(f"{slot_name}: {equipment.nome}", classes="item_name")
                    yield Static(equipment.descricao, classes="item_description")

                with Vertical(classes="item_details"):
                    if equipment.bonus_ataque > 0:
                        yield Static(
                            f"Ataque: +{equipment.bonus_ataque}", classes="item_stat"
                        )
                    if equipment.bonus_defesa > 0:
                        yield Static(
                            f"Defesa: +{equipment.bonus_defesa}", classes="item_stat"
                        )

    def filter_items(self, items):
        """Filtra itens baseado no filtro atual e texto de busca."""
        filtered = items

        # Filtrar por texto
        if self.filter_text:
            filtered = [
                item
                for item in filtered
                if self.filter_text.lower() in item.nome.lower()
            ]

        # Filtrar por categoria
        if self.current_filter != "all":
            filtered = []
            for item in items:
                item_template = DB_ITENS.get(item.nome)
                if item_template:
                    if (
                        self.current_filter == "consumable"
                        and item_template.tipo == "Consumível"
                    ):
                        filtered.append(item)
                    elif self.current_filter == "equipment" and item_template.tipo in [
                        "Arma",
                        "Armadura",
                        "Escudo",
                    ]:
                        filtered.append(item)
                    elif (
                        self.current_filter == "healing"
                        and hasattr(item_template, "valor_cura")
                        and item_template.valor_cura > 0
                    ):
                        filtered.append(item)

        return filtered

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Lida com cliques nos botões."""
        if event.button.id.startswith("filter_"):
            filter_type = event.button.id.split("_", 1)[1]
            self.current_filter = filter_type

            # Atualizar aparência dos botões de filtro
            for button in self.query(".filter_buttons Button"):
                if button.id == event.button.id:
                    button.variant = "primary"
                else:
                    button.variant = "default"

            self.update_inventory_list()

        elif event.button.id.startswith("use_"):
            item_name = event.button.id.replace("use_", "").replace("_", " ")
            self.dismiss(item_name)

    def on_input_changed(self, event: Input.Changed) -> None:
        """Atualiza a lista quando o filtro de texto muda."""
        if event.input.id == "filter_input":
            self.filter_text = event.value
            self.update_inventory_list()
