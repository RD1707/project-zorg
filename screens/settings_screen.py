"""
Tela de configurações do jogo.
"""

from typing import Any, Dict

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Select, Static, Switch

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
        background: #000000;
    }

    #settings_container {
        width: 85%;
        max-width: 120;
        height: 90%;
        padding: 2;
        border: round #777;
        background: #1a1a1a;
    }

    #settings_header {
        text-align: center;
        text-style: bold;
        margin-bottom: 2;
        color: white;
    }

    .setting_row {
        height: auto;
        margin-bottom: 1;
        padding: 1;
        background: #333;
        border: round #777;
    }

    .setting_label {
        width: 60%;
        color: white;
        text-style: bold;
    }

    .setting_control {
        width: 40%;
    }

    .section_header {
        text-style: bold;
        color: #ddd;
        margin-top: 2;
        margin-bottom: 1;
        text-align: center;
    }

    #save_button {
        margin-top: 2;
        width: 100%;
        background: #555;
        color: white;
        border: tall #777;
    }

    #save_button:hover {
        background: #777;
        border: tall white;
    }

    /* Melhorar visibilidade dos controles */
    Select {
        background: #555 !important;
        color: white !important;
        border: tall #777 !important;
    }

    Select:focus {
        border: tall white !important;
    }

    Switch {
        background: #333 !important;
        color: white !important;
    }

    Switch.-on {
        background: #777 !important;
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
            yield Static("Configurações", id="settings_header")

            yield Static("Gameplay", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Velocidade do texto:", classes="setting_label")
                yield Select(
                    [
                        ("Muito Lenta", "very_slow"),
                        ("Lenta", "slow"),
                        ("Normal", "normal"),
                        ("Rápida", "fast"),
                        ("Instantânea", "instant"),
                    ],
                    value=self.settings.get("text_speed", "normal"),
                    id="text_speed",
                    classes="setting_control",
                )

            with Horizontal(classes="setting_row"):
                yield Static("Auto-save:", classes="setting_label")
                yield Switch(
                    value=self.settings.get("auto_save", True),
                    id="auto_save",
                    classes="setting_control",
                )

            with Horizontal(classes="setting_row"):
                yield Static("Confirmação de ações:", classes="setting_label")
                yield Switch(
                    value=self.settings.get("confirm_actions", True),
                    id="confirm_actions",
                    classes="setting_control",
                )

            yield Static("Audio", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Música de fundo:", classes="setting_label")
                yield Switch(
                    value=self.settings.get("background_music", True),
                    id="background_music",
                    classes="setting_control",
                )

            with Horizontal(classes="setting_row"):
                yield Static("Efeitos sonoros:", classes="setting_label")
                yield Switch(
                    value=self.settings.get("sound_effects", True),
                    id="sound_effects",
                    classes="setting_control",
                )

            with Horizontal(classes="setting_row"):
                yield Static("Volume geral:", classes="setting_label")
                yield Select(
                    [
                        ("Silencioso", "0"),
                        ("Baixo", "25"),
                        ("Médio", "50"),
                        ("Alto", "75"),
                        ("Máximo", "100"),
                    ],
                    value=str(self.settings.get("master_volume", "75")),
                    id="master_volume",
                    classes="setting_control",
                )

            yield Static("Interface", classes="section_header")

            with Horizontal(classes="setting_row"):
                yield Static("Tema:", classes="setting_label")
                yield Select(
                    [
                        ("Escuro", "dark"),
                        ("Claro", "light"),
                        ("Contraste Alto", "high_contrast"),
                    ],
                    value=self.settings.get("theme", "dark"),
                    id="theme",
                    classes="setting_control",
                )

            with Horizontal(classes="setting_row"):
                yield Static("Mostrar dicas:", classes="setting_label")
                yield Switch(
                    value=self.settings.get("show_tooltips", True),
                    id="show_tooltips",
                    classes="setting_control",
                )

            yield Button("Salvar Configurações", id="save_button")

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
                self.app.notify("Configurações salvas com sucesso!")
                # Aplicar configurações imediatamente
                self._apply_settings()
            else:
                self.app.notify("Erro ao salvar configurações!", timeout=5)

        except Exception as e:
            self.app.notify(f"Erro: {e}", timeout=5)

    def _apply_settings(self) -> None:
        """Aplica as configurações ao jogo em tempo real."""
        # Aplicar configurações de áudio se o engine tiver audio manager
        if hasattr(self.app, 'engine') and hasattr(self.app.engine, 'audio_manager'):
            audio_manager = self.app.engine.audio_manager

            # Volume geral
            if 'master_volume' in self.modified_settings:
                volume = int(self.modified_settings['master_volume']) / 100.0
                audio_manager.set_master_volume(volume)

            # Música de fundo
            if 'background_music' in self.modified_settings:
                if self.modified_settings['background_music']:
                    audio_manager.resume_music()
                else:
                    audio_manager.pause_music()

            # Efeitos sonoros
            if 'sound_effects' in self.modified_settings:
                audio_manager.sound_effects_enabled = self.modified_settings['sound_effects']

        # Aplicar configurações de interface
        if 'theme' in self.modified_settings:
            # Aplicar mudanças de tema se necessário
            pass

        # Notificar outros componentes sobre mudanças
        from core.managers.event_manager import EventType, emit_event
        emit_event(EventType.SETTINGS_CHANGED, {"settings": dict(self.settings._data)})

    def action_dismiss(self) -> None:
        """Sai da tela sem salvar."""
        if self.modified_settings:
            # Poderia mostrar um diálogo de confirmação aqui
            self.app.notify("Configurações não salvas foram descartadas.")

        self.dismiss()
