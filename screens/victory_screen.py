from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Static


class VictoryScreen(Screen):
    """Tela para exibir as recompensas apos uma vitoria em combate."""

    BINDINGS = [
        Binding("enter", "dismiss", "Continuar"),
    ]

    CSS = """
    VictoryScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7); /* Fundo semi-transparente */
    }

    #victory_box {
        width: 60;
        height: auto;
        padding: 2;
        border: double white;
        background: #1e1e1e;
        align: center middle;
    }

    #victory_title {
        text-style: bold;
    }

    .reward_line {
        margin-top: 1;
    }

    #level_up_box {
        margin-top: 1;
        padding: 1;
        border: round white;
    }

    .new_reward_box {
        margin-top: 1;
        padding: 1;
        border: round white;
    }
    """

    def __init__(self, victory_data: dict):
        """Recebe o dicionario com os dados da vitoria e as recompensas."""
        super().__init__()
        self.victory_data = victory_data

    def compose(self) -> ComposeResult:
        """Cria os widgets da tela."""
        with Vertical(id="victory_box"):
            yield Static("V I T O R I A", id="victory_title")

            # Mostra as recompensas base
            yield Static(
                f"XP Ganho: [b]{self.victory_data['xp_ganho']}[/b]",
                classes="reward_line",
            )
            yield Static(
                f"Ouro Ganho: [b]{self.victory_data['ouro_ganho']}[/b]",
                classes="reward_line",
            )

            # Se houve um level up, mostra os detalhes
            level_up_info = self.victory_data.get("level_up")
            if level_up_info:
                with Vertical(id="level_up_box"):
                    yield Static(
                        f"[b]LEVEL UP! Voce alcancou o Nivel {level_up_info['new_level']}![/b]"
                    )
                    yield Static(f"HP Maximo +{level_up_info['hp_bonus']}")
                    yield Static(f"MP Maximo +{level_up_info['mp_bonus']}")
                    yield Static(f"Ataque Base +{level_up_info['atk_bonus']}")
                    yield Static(f"Defesa Base +{level_up_info['def_bonus']}")

            # Se houver recompensas adicionais, mostra-as
            rewards = self.victory_data.get("rewards", [])
            if rewards:
                for reward in rewards:
                    if reward:
                        with Vertical(classes="new_reward_box"):
                            if hasattr(reward, "tipo"):  # É um equipamento
                                yield Static(
                                    f"Voce recebeu o equipamento [b]{reward.nome}[/b]!"
                                )
                            else:  # É uma habilidade
                                yield Static(
                                    f"Voce aprendeu a habilidade [b]{reward.nome}[/b]!"
                                )
