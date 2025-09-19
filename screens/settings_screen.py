"""
Tela de configurações do jogo.
"""
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Static, Header, Footer, Switch, Select
from textual.containers import Vertical, Horizontal
from textual.binding import Binding
from typing import Dict, Any

from config.settings import GameSettings


class SettingsScreen(Screen):
    """Tela de configurações do jogo."""

    BINDINGS = [
        Binding("escape", "dismiss", "Voltar"),
        Binding("s", "save_settings", "Salvar"),
    ]

    CSS = """
    SettingsScreen {
        align: center middle;
    }

    #settings_container {
        width: 80%;
        max-width: 100;
        height: 85%;
        padding: 1;
        border: round #444;
        background: #1e1e1e;
    }

    #settings_header {
        text-align: center;
        text-style: bold;
        color: cyan;
        margin-bottom: 2;
    }

    .setting_row {
        height: 3;
        margin-bottom: 1;
        padding: 1;
        background: #2a2a2a;
        border: round #555;
    }

    .setting_label {
        width: 50%;
        color: #cccccc;
    }

    .setting_control {
        width: 50%;
    }

    .section_header {
        text-style: bold;
        color: yellow;
        margin-top: 1;
        margin-bottom: 1;
    }

    #save_button {
        margin-top: 2;
        width: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self.settings = GameSettings()
        self.modified_settings: Dict[str, Any] = {}

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela de configurações."""
        yield Header(name="Configurações do Jogo")

        with Vertical(id="settings_container"):
            yield Static("⚙️ Configurações", id="settings_header")

            yield Static("🎮 Gameplay", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Velocidade do texto:", classes="setting_label")
                yield Select([
                    ("Muito Lenta", "very_slow"),
                    ("Lenta", "slow"),
                    ("Normal", "normal"),
                    ("Rápida", "fast"),
                    ("Instantânea", "instant")
                ], value=self.settings.get("text_speed", "normal"),
                id="text_speed", classes="setting_control")

            with Horizontal(classes="setting_row"):
                yield Static("Auto-save:", classes="setting_label")
                yield Switch(value=self.settings.get("auto_save", True),
                           id="auto_save", classes="setting_control")

            with Horizontal(classes="setting_row"):
                yield Static("Confirmação de ações:", classes="setting_label")
                yield Switch(value=self.settings.get("confirm_actions", True),
                           id="confirm_actions", classes="setting_control")

            yield Static("🔊 Audio", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Música de fundo:", classes="setting_label")
                yield Switch(value=self.settings.get("background_music", True),
                           id="background_music", classes="setting_control")

            with Horizontal(classes="setting_row"):
                yield Static("Efeitos sonoros:", classes="setting_label")
                yield Switch(value=self.settings.get("sound_effects", True),
                           id="sound_effects", classes="setting_control")

            with Horizontal(classes="setting_row"):
                yield Static("Volume geral:", classes="setting_label")
                yield Select([
                    ("Silencioso", "0"),
                    ("Baixo", "25"),
                    ("Médio", "50"),
                    ("Alto", "75"),
                    ("Máximo", "100")
                ], value=str(self.settings.get("master_volume", "75")),
                id="master_volume", classes="setting_control")

            yield Static("🎨 Interface", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Tema:", classes="setting_label")
                yield Select([
                    ("Escuro", "dark"),
                    ("Claro", "light"),
                    ("Contraste Alto", "high_contrast")
                ], value=self.settings.get("theme", "dark"),
                id="theme", classes="setting_control")

            with Horizontal(classes="setting_row"):
                yield Static("Mostrar dicas:", classes="setting_label")
                yield Switch(value=self.settings.get("show_tooltips", True),
                           id="show_tooltips", classes="setting_control")

            yield Button("💾 Salvar Configurações", id="save_button", variant="success")

        yield Footer()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Callback para mudanças nos switches."""
        self.modified_settings[event.switch.id] = event.value

    def on_select_changed(self, event: Select.Changed) -> None:
        """Callback para mudanças nos selects."""
        if event.value is not None:
            self.modified_settings[event.select.id] = event.value

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Callback para botões pressionados."""
        if event.button.id == "save_button":
            self.action_save_settings()

    def action_save_settings(self) -> None:
        """Salva as configurações modificadas."""
        try:
            # Aplicar mudanças
            for key, value in self.modified_settings.items():
                self.settings.set(key, value)

            # Salvar no arquivo
            success = self.settings.save()

            if success:
                self.app.notify("✅ Configurações salvas com sucesso!")
                # Aplicar configurações imediatamente
                self._apply_settings()
            else:
                self.app.notify("❌ Erro ao salvar configurações!", timeout=5)

        except Exception as e:
            self.app.notify(f"❌ Erro: {e}", timeout=5)

    def _apply_settings(self) -> None:
        """Aplica as configurações ao jogo."""
        # Aqui você pode aplicar as configurações em tempo real
        # Por exemplo, ajustar velocidade do texto, volume, etc.

        # Notificar outros componentes sobre mudanças
        from core.managers.event_manager import emit_event, EventType
        emit_event(EventType.SETTINGS_CHANGED, {
            "settings": dict(self.settings._data)
        })

    def action_dismiss(self) -> None:
        """Sai da tela sem salvar."""
        if self.modified_settings:
            # Poderia mostrar um diálogo de confirmação aqui
            self.app.notify("Configurações não salvas foram descartadas.")

        self.dismiss()