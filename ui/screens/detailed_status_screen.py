"""
Tela de status detalhada do personagem.
Mostra todos os atributos, equipamentos e efeitos ativos.
"""
from typing import List, Dict, Any, Optional
from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Button, Static, DataTable, Tabs, TabPane, ProgressBar
from textual.screen import Screen

from core.models import Personagem
from utils.logging_config import get_logger

logger = get_logger("detailed_status_screen")


class AttributeDisplay(Static):
    """Widget para exibir um atributo com valor e barra."""

    def __init__(self, name: str, current: int, maximum: int = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.current = current
        self.maximum = maximum

    def render(self) -> str:
        if self.maximum is not None:
            percentage = (self.current / self.maximum) * 100 if self.maximum > 0 else 0
            bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
            return f"{self.name}: {self.current}/{self.maximum} [{bar}] {percentage:.1f}%"
        else:
            return f"{self.name}: {self.current}"


class StatusEffectDisplay(Static):
    """Widget para exibir efeitos de status ativos."""

    def __init__(self, effects: Dict[str, int], **kwargs):
        super().__init__(**kwargs)
        self.effects = effects

    def render(self) -> str:
        if not self.effects:
            return "✨ Nenhum efeito ativo"

        lines = ["🌪️ Efeitos Ativos:"]
        for effect, duration in self.effects.items():
            if duration > 0:
                icon = self._get_effect_icon(effect)
                lines.append(f"  {icon} {effect.title()}: {duration} turnos")

        return "\n".join(lines) if len(lines) > 1 else "✨ Nenhum efeito ativo"

    def _get_effect_icon(self, effect: str) -> str:
        icons = {
            "veneno": "☠️",
            "buff_defesa": "🛡️",
            "furia": "😠",
            "regeneracao": "💚",
            "buff_ataque": "⚔️",
            "slow": "🐌",
            "freeze": "🧊",
            "burn": "🔥"
        }
        return icons.get(effect, "🌟")


class EquipmentDisplay(Static):
    """Widget para exibir equipamentos."""

    def __init__(self, equipment: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.equipment = equipment

    def render(self) -> str:
        lines = ["⚔️ Equipamentos:"]

        slots = ["arma", "armadura", "escudo", "acessorio"]
        slot_names = {
            "arma": "🗡️ Arma",
            "armadura": "🛡️ Armadura",
            "escudo": "🛡️ Escudo",
            "acessorio": "💍 Acessório"
        }

        for slot in slots:
            item = self.equipment.get(slot)
            if item:
                bonus_text = ""
                if hasattr(item, 'bonus_ataque') and item.bonus_ataque > 0:
                    bonus_text += f" (+{item.bonus_ataque} ATK)"
                if hasattr(item, 'bonus_defesa') and item.bonus_defesa > 0:
                    bonus_text += f" (+{item.bonus_defesa} DEF)"

                lines.append(f"  {slot_names[slot]}: {item.nome}{bonus_text}")
            else:
                lines.append(f"  {slot_names[slot]}: [Vazio]")

        return "\n".join(lines)


class DetailedStatusScreen(Screen):
    """Tela de status detalhada do personagem."""

    BINDINGS = [
        ("escape", "quit", "Voltar"),
        ("q", "quit", "Quit"),
        ("r", "refresh", "Atualizar")
    ]

    def __init__(self, player: Personagem, **kwargs):
        super().__init__(**kwargs)
        self.player = player

    def compose(self) -> ComposeResult:
        """Compõe a interface da tela."""
        with Container(id="main_container"):
            yield Static(f"📊 Status Detalhado - {self.player.nome}", id="title", classes="title")

            with Tabs(id="status_tabs"):
                with TabPane("Atributos", id="tab_attributes"):
                    yield self._create_attributes_tab()

                with TabPane("Equipamentos", id="tab_equipment"):
                    yield self._create_equipment_tab()

                with TabPane("Efeitos", id="tab_effects"):
                    yield self._create_effects_tab()

                with TabPane("Progresso", id="tab_progress"):
                    yield self._create_progress_tab()

                with TabPane("Estatísticas", id="tab_stats"):
                    yield self._create_stats_tab()

            with Horizontal(id="button_container"):
                yield Button("🔄 Atualizar", id="refresh_btn", variant="success")
                yield Button("⬅️ Voltar", id="back_btn", variant="primary")

    def _create_attributes_tab(self) -> Container:
        """Cria aba de atributos básicos."""
        with ScrollableContainer():
            # Atributos vitais
            yield Static("💖 Atributos Vitais", classes="section_header")
            yield AttributeDisplay("HP", self.player.hp, self.player.hp_max)
            yield AttributeDisplay("MP", self.player.mp, self.player.mp_max)

            # Atributos de combate
            yield Static("⚔️ Atributos de Combate", classes="section_header")
            yield AttributeDisplay("Ataque Base", self.player.ataque_base)
            yield AttributeDisplay("Defesa Base", self.player.defesa_base)
            yield AttributeDisplay("Ataque Total", self.player.ataque_total)
            yield AttributeDisplay("Defesa Total", self.player.defesa_total)

            # Progressão
            yield Static("🌟 Progressão", classes="section_header")
            yield AttributeDisplay("Nível", self.player.nivel)
            yield AttributeDisplay("XP", self.player.xp, self.player.xp_proximo_nivel)
            yield AttributeDisplay("Ouro", self.player.ouro)
            yield AttributeDisplay("Fase Atual", self.player.fase_atual)

    def _create_equipment_tab(self) -> Container:
        """Cria aba de equipamentos."""
        with ScrollableContainer():
            # Equipamentos atuais
            equipment_data = {
                "arma": getattr(self.player, 'arma_equipada', None),
                "armadura": getattr(self.player, 'armadura_equipada', None),
                "escudo": getattr(self.player, 'escudo_equipado', None),
                "acessorio": getattr(self.player, 'acessorio_equipado', None)
            }

            yield EquipmentDisplay(equipment_data)

            # Bônus totais
            yield Static("📈 Bônus Totais dos Equipamentos", classes="section_header")
            total_atk_bonus = sum(
                getattr(item, 'bonus_ataque', 0)
                for item in equipment_data.values()
                if item is not None
            )
            total_def_bonus = sum(
                getattr(item, 'bonus_defesa', 0)
                for item in equipment_data.values()
                if item is not None
            )

            yield Static(f"⚔️ Bônus Total de Ataque: +{total_atk_bonus}")
            yield Static(f"🛡️ Bônus Total de Defesa: +{total_def_bonus}")

    def _create_effects_tab(self) -> Container:
        """Cria aba de efeitos de status."""
        with ScrollableContainer():
            # Efeitos ativos
            effects = {}
            if hasattr(self.player, 'turnos_veneno') and self.player.turnos_veneno > 0:
                effects["veneno"] = self.player.turnos_veneno
            if hasattr(self.player, 'turnos_buff_defesa') and self.player.turnos_buff_defesa > 0:
                effects["buff_defesa"] = self.player.turnos_buff_defesa
            if hasattr(self.player, 'turnos_furia') and self.player.turnos_furia > 0:
                effects["furia"] = self.player.turnos_furia
            if hasattr(self.player, 'turnos_regeneracao') and self.player.turnos_regeneracao > 0:
                effects["regeneracao"] = self.player.turnos_regeneracao

            yield StatusEffectDisplay(effects)

            # Resistências (se implementadas)
            yield Static("🛡️ Resistências e Imunidades", classes="section_header")
            yield Static("• Implementação futura: Sistema de elementos")

    def _create_progress_tab(self) -> Container:
        """Cria aba de progresso e conquistas."""
        with ScrollableContainer():
            yield Static("🏆 Progresso na Aventura", classes="section_header")

            # Progresso das fases
            phases_completed = self.player.fase_atual - 1
            total_phases = 10

            yield Static(f"📍 Fases Completadas: {phases_completed}/{total_phases}")
            yield ProgressBar(
                total=total_phases,
                progress=phases_completed,
                show_eta=False,
                show_percentage=True
            )

            # Estatísticas de combate (se disponíveis)
            yield Static("⚔️ Estatísticas de Combate", classes="section_header")
            yield Static("• Inimigos derrotados: Em desenvolvimento")
            yield Static("• Bosses derrotados: Em desenvolvimento")
            yield Static("• Itens coletados: Em desenvolvimento")

    def _create_stats_tab(self) -> Container:
        """Cria aba com tabela de estatísticas detalhadas."""
        with ScrollableContainer():
            yield Static("📋 Resumo Completo", classes="section_header")

            # Criar tabela de stats
            table = DataTable()
            table.add_columns("Atributo", "Valor", "Observações")

            # Adicionar dados à tabela
            stats_data = [
                ("Nome", self.player.nome, ""),
                ("Nível", str(self.player.nivel), f"XP: {self.player.xp}/{self.player.xp_proximo_nivel}"),
                ("HP", f"{self.player.hp}/{self.player.hp_max}", "Pontos de Vida"),
                ("MP", f"{self.player.mp}/{self.player.mp_max}", "Pontos de Mana"),
                ("Ataque", str(self.player.ataque_total), f"Base: {self.player.ataque_base}"),
                ("Defesa", str(self.player.defesa_total), f"Base: {self.player.defesa_base}"),
                ("Ouro", str(self.player.ouro), "Moeda do jogo"),
                ("Fase", str(self.player.fase_atual), "Progresso na história"),
            ]

            for stat in stats_data:
                table.add_row(*stat)

            yield table

    @on(Button.Pressed, "#refresh_btn")
    def refresh_display(self):
        """Atualiza a exibição."""
        logger.info("Atualizando tela de status")
        self.refresh()

    @on(Button.Pressed, "#back_btn")
    def action_quit(self):
        """Volta para a tela anterior."""
        self.app.pop_screen()

    def action_refresh(self):
        """Ação de atualizar."""
        self.refresh_display()

    def on_mount(self):
        """Configura a tela ao ser montada."""
        self.title = "Status Detalhado - ZORG"

    def get_css(self) -> str:
        """Retorna CSS para estilização."""
        return """
        #main_container {
            background: $surface;
            border: solid $primary;
            height: 100%;
        }

        .title {
            text-align: center;
            background: $primary;
            color: $text;
            padding: 1;
            margin-bottom: 1;
        }

        .section_header {
            background: $secondary;
            color: $text;
            padding: 0 1;
            margin: 1 0;
            text-style: bold;
        }

        #button_container {
            dock: bottom;
            height: 3;
            background: $surface;
            padding: 1;
        }

        #status_tabs {
            margin: 1;
        }

        Button {
            margin: 0 1;
            min-width: 12;
        }

        DataTable {
            margin: 1 0;
        }

        ProgressBar {
            margin: 1 0;
        }
        """