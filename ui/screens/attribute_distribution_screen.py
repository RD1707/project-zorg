"""
Tela de distribuição de atributos para quando o jogador sobe de nível.
Permite alocar pontos em diferentes estatísticas.
"""
from typing import Dict, List, Any, Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Static, ProgressBar, Label, Input
from textual.screen import Screen, ModalScreen
from textual.validation import Number

from core.models import Personagem
from utils.logging_config import get_logger

logger = get_logger("attribute_distribution_screen")


class AttributeAllocationWidget(Static):
    """Widget para alocar pontos em um atributo específico."""

    def __init__(self, attribute_name: str, current_value: int, **kwargs):
        super().__init__(**kwargs)
        self.attribute_name = attribute_name
        self.current_value = current_value
        self.allocated_points = 0
        self.max_points_per_attribute = 5

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f"{self.attribute_name}:", classes="attribute_label")
            yield Static(f"{self.current_value}", id=f"current_{self.attribute_name.lower()}", classes="current_value")
            yield Button("-", id=f"minus_{self.attribute_name.lower()}", classes="point_button")
            yield Static("0", id=f"allocated_{self.attribute_name.lower()}", classes="allocated_points")
            yield Button("+", id=f"plus_{self.attribute_name.lower()}", classes="point_button")
            yield Static(f"→ {self.current_value}", id=f"new_{self.attribute_name.lower()}", classes="new_value")

    def allocate_point(self) -> bool:
        """Tenta alocar um ponto. Retorna True se bem-sucedido."""
        if self.allocated_points < self.max_points_per_attribute:
            self.allocated_points += 1
            self._update_display()
            return True
        return False

    def deallocate_point(self) -> bool:
        """Tenta desalocar um ponto. Retorna True se bem-sucedido."""
        if self.allocated_points > 0:
            self.allocated_points -= 1
            self._update_display()
            return True
        return False

    def _update_display(self):
        """Atualiza a exibição dos valores."""
        try:
            allocated_display = self.query_one(f"#allocated_{self.attribute_name.lower()}", Static)
            new_value_display = self.query_one(f"#new_{self.attribute_name.lower()}", Static)

            allocated_display.update(str(self.allocated_points))
            new_value = self.current_value + self.allocated_points
            new_value_display.update(f"→ {new_value}")

            # Destacar se houve mudança
            if self.allocated_points > 0:
                new_value_display.add_class("highlighted")
            else:
                new_value_display.remove_class("highlighted")

        except Exception as e:
            logger.error(f"Erro ao atualizar display do atributo {self.attribute_name}: {e}")

    def reset_allocation(self):
        """Reseta a alocação de pontos."""
        self.allocated_points = 0
        self._update_display()

    def get_allocation(self) -> int:
        """Retorna pontos alocados."""
        return self.allocated_points


class AttributeDistributionScreen(Screen):
    """Tela para distribuição de pontos de atributo."""

    BINDINGS = [
        ("escape", "cancel", "Cancelar"),
        ("enter", "confirm", "Confirmar"),
        ("r", "reset", "Resetar")
    ]

    def __init__(self, player: Personagem, available_points: int, **kwargs):
        super().__init__(**kwargs)
        self.player = player
        self.available_points = available_points
        self.remaining_points = available_points
        self.attribute_widgets = {}

    def compose(self) -> ComposeResult:
        """Compõe a interface da tela."""
        with Container(id="main_container"):
            yield Static("🌟 Distribuição de Atributos", id="title", classes="title")

            yield Static(
                f"Você subiu de nível! Você tem {self.available_points} pontos para distribuir.",
                id="instruction",
                classes="instruction"
            )

            # Informações do jogador
            with Container(id="player_info"):
                yield Static(f"👤 {self.player.nome} - Nível {self.player.nivel}", classes="player_name")
                yield Static(f"🔢 Pontos disponíveis: {self.remaining_points}", id="remaining_points", classes="points_display")

            # Seção de atributos
            with ScrollableContainer(id="attributes_section"):
                yield Static("📊 Atributos Básicos", classes="section_header")

                # Criar widgets para cada atributo
                self.attribute_widgets["Força"] = AttributeAllocationWidget("Força", self._get_attribute_value("forca"))
                self.attribute_widgets["Defesa"] = AttributeAllocationWidget("Defesa", self._get_attribute_value("defesa"))
                self.attribute_widgets["HP Máximo"] = AttributeAllocationWidget("HP Máximo", self.player.hp_max)
                self.attribute_widgets["MP Máximo"] = AttributeAllocationWidget("MP Máximo", self.player.mp_max)

                for widget in self.attribute_widgets.values():
                    yield widget

                # Seção de preview dos benefícios
                yield Static("📈 Benefícios da Melhoria", classes="section_header")
                with Container(id="benefits_preview"):
                    yield Static("Selecione atributos para ver os benefícios.", id="benefits_text")

            # Botões de ação
            with Horizontal(id="action_buttons"):
                yield Button("🔄 Resetar Tudo", id="reset_all", variant="warning")
                yield Button("❌ Cancelar", id="cancel_allocation", variant="error")
                yield Button("✅ Confirmar", id="confirm_allocation", variant="success")

    def _get_attribute_value(self, attribute: str) -> int:
        """Obtém valor atual de um atributo."""
        if attribute == "forca":
            return getattr(self.player, 'forca', self.player.ataque_base)
        elif attribute == "defesa":
            return self.player.defesa_base
        return 0

    @on(Button.Pressed)
    def handle_button_press(self, event: Button.Pressed):
        """Lida com cliques nos botões."""
        button_id = event.button.id

        if button_id == "reset_all":
            self.action_reset()
        elif button_id == "cancel_allocation":
            self.action_cancel()
        elif button_id == "confirm_allocation":
            self.action_confirm()
        elif button_id.startswith("plus_"):
            attribute_name = self._get_attribute_from_button_id(button_id)
            self._allocate_point(attribute_name)
        elif button_id.startswith("minus_"):
            attribute_name = self._get_attribute_from_button_id(button_id)
            self._deallocate_point(attribute_name)

    def _get_attribute_from_button_id(self, button_id: str) -> str:
        """Extrai nome do atributo do ID do botão."""
        # Remove prefixo plus_/minus_ e converte para nome do atributo
        clean_id = button_id.replace("plus_", "").replace("minus_", "")

        id_to_attribute = {
            "força": "Força",
            "defesa": "Defesa",
            "hp_máximo": "HP Máximo",
            "mp_máximo": "MP Máximo"
        }

        return id_to_attribute.get(clean_id, "")

    def _allocate_point(self, attribute_name: str):
        """Aloca um ponto no atributo especificado."""
        if attribute_name in self.attribute_widgets and self.remaining_points > 0:
            widget = self.attribute_widgets[attribute_name]
            if widget.allocate_point():
                self.remaining_points -= 1
                self._update_remaining_points()
                self._update_benefits_preview()

    def _deallocate_point(self, attribute_name: str):
        """Desaloca um ponto do atributo especificado."""
        if attribute_name in self.attribute_widgets:
            widget = self.attribute_widgets[attribute_name]
            if widget.deallocate_point():
                self.remaining_points += 1
                self._update_remaining_points()
                self._update_benefits_preview()

    def _update_remaining_points(self):
        """Atualiza exibição de pontos restantes."""
        try:
            points_display = self.query_one("#remaining_points", Static)
            points_display.update(f"🔢 Pontos disponíveis: {self.remaining_points}")

            # Destacar quando sem pontos
            if self.remaining_points == 0:
                points_display.add_class("no_points")
            else:
                points_display.remove_class("no_points")
        except Exception as e:
            logger.error(f"Erro ao atualizar pontos restantes: {e}")

    def _update_benefits_preview(self):
        """Atualiza preview dos benefícios."""
        benefits = []

        for attribute_name, widget in self.attribute_widgets.items():
            points = widget.get_allocation()
            if points > 0:
                benefit = self._calculate_benefit(attribute_name, points)
                benefits.append(f"• {attribute_name}: {benefit}")

        try:
            benefits_text = self.query_one("#benefits_text", Static)
            if benefits:
                benefits_text.update("Benefícios dos pontos alocados:\n" + "\n".join(benefits))
            else:
                benefits_text.update("Selecione atributos para ver os benefícios.")
        except Exception as e:
            logger.error(f"Erro ao atualizar preview de benefícios: {e}")

    def _calculate_benefit(self, attribute_name: str, points: int) -> str:
        """Calcula e descreve o benefício de alocar pontos em um atributo."""
        if attribute_name == "Força":
            attack_bonus = points * 2
            return f"+{attack_bonus} de ataque"
        elif attribute_name == "Defesa":
            defense_bonus = points * 2
            return f"+{defense_bonus} de defesa"
        elif attribute_name == "HP Máximo":
            hp_bonus = points * 10
            return f"+{hp_bonus} HP máximo"
        elif attribute_name == "MP Máximo":
            mp_bonus = points * 5
            return f"+{mp_bonus} MP máximo"
        return f"+{points} pontos"

    def action_reset(self):
        """Reseta todas as alocações."""
        total_allocated = sum(widget.get_allocation() for widget in self.attribute_widgets.values())
        self.remaining_points = self.available_points

        for widget in self.attribute_widgets.values():
            widget.reset_allocation()

        self._update_remaining_points()
        self._update_benefits_preview()

    def action_cancel(self):
        """Cancela a distribuição de atributos."""
        self.app.pop_screen()

    def action_confirm(self):
        """Confirma e aplica a distribuição de atributos."""
        # Verificar se todos os pontos foram utilizados
        total_allocated = sum(widget.get_allocation() for widget in self.attribute_widgets.values())

        if total_allocated == 0:
            self._show_message("Você deve alocar pelo menos 1 ponto!")
            return

        # Aplicar as mudanças no jogador
        self._apply_attribute_changes()

        # Fechar tela com sucesso
        self.app.pop_screen()

    def _apply_attribute_changes(self):
        """Aplica as mudanças de atributos no jogador."""
        for attribute_name, widget in self.attribute_widgets.items():
            points = widget.get_allocation()
            if points > 0:
                self._apply_attribute_bonus(attribute_name, points)

        logger.info(f"Aplicados pontos de atributo ao jogador {self.player.nome}")

    def _apply_attribute_bonus(self, attribute_name: str, points: int):
        """Aplica bônus de um atributo específico."""
        if attribute_name == "Força":
            # Aumentar ataque base
            self.player.ataque_base += points * 2
            if hasattr(self.player, 'forca'):
                self.player.forca += points
            else:
                self.player.forca = points

        elif attribute_name == "Defesa":
            self.player.defesa_base += points * 2

        elif attribute_name == "HP Máximo":
            bonus_hp = points * 10
            self.player.hp_max += bonus_hp
            self.player.hp += bonus_hp  # Também curar o HP atual

        elif attribute_name == "MP Máximo":
            bonus_mp = points * 5
            self.player.mp_max += bonus_mp
            self.player.mp += bonus_mp  # Também restaurar MP atual

    def _show_message(self, message: str):
        """Mostra uma mensagem temporária."""
        try:
            title = self.query_one("#title", Static)
            original_text = title.renderable
            title.update(f"⚠️ {message}")

            # Restaurar após 3 segundos
            self.set_timer(3.0, lambda: title.update(original_text))
        except Exception as e:
            logger.error(f"Erro ao mostrar mensagem: {e}")

    def on_mount(self):
        """Configura a tela ao ser montada."""
        self.title = "Distribuição de Atributos - ZORG"

    def get_css(self) -> str:
        """Retorna CSS para estilização."""
        return """
        #main_container {
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
            text-style: bold;
        }

        .instruction {
            background: $secondary;
            padding: 1;
            margin-bottom: 1;
            text-align: center;
        }

        #player_info {
            background: $accent;
            padding: 1;
            margin-bottom: 1;
            border: solid $secondary;
        }

        .points_display {
            text-style: bold;
            color: $success;
        }

        .no_points {
            color: $error;
        }

        .section_header {
            background: $secondary;
            color: $text;
            padding: 0 1;
            margin: 1 0;
            text-style: bold;
        }

        .attribute_label {
            width: 12;
            padding: 0 1;
        }

        .current_value {
            width: 3;
            text-align: center;
            background: $secondary;
            border: solid $accent;
        }

        .allocated_points {
            width: 3;
            text-align: center;
            background: $warning;
            color: $text;
            text-style: bold;
        }

        .new_value {
            width: 8;
            text-align: center;
            background: $surface;
        }

        .highlighted {
            background: $success;
            color: $text;
            text-style: bold;
        }

        .point_button {
            width: 3;
            height: 1;
            margin: 0;
        }

        #action_buttons {
            dock: bottom;
            height: 3;
            background: $surface;
            padding: 1;
        }

        Button {
            margin: 0 1;
            min-width: 12;
        }

        #benefits_preview {
            background: $surface;
            border: solid $secondary;
            padding: 1;
            margin: 1 0;
        }

        AttributeAllocationWidget {
            margin: 0 0 1 0;
            padding: 1;
            background: $surface;
            border: solid $accent;
        }
        """


def show_attribute_distribution(player: Personagem, available_points: int):
    """Função utilitária para mostrar tela de distribuição de atributos."""
    from textual.app import get_current_app

    app = get_current_app()
    screen = AttributeDistributionScreen(player, available_points)
    app.push_screen(screen)