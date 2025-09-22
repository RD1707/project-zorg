from textual.screen import Screen

from core.engine import GameEngine

# 1. Importar TODOS os scripts de fase
from scenes.phase_scripts import (
    phase1,
    phase2,
    phase3,
    phase4,
    phase5,
    phase6,
    phase7,
    phase8,
    phase9,
    phase10,
)

from .city_screen import CityScreen
from .combat_screen import CombatScreen

# Importa as telas que este gestor irá controlar
from .story_screen import StoryScreen
from .victory_screen import VictoryScreen

# Mapeia o número da fase para a função geradora correspondente
PHASE_MAP = {
    1: phase1.run_phase_1,
    2: phase2.run_phase_2,
    3: phase3.run_phase_3,
    4: phase4.run_phase_4,
    5: phase5.run_phase_5,
    6: phase6.run_phase_6,
    7: phase7.run_phase_7,
    8: phase8.run_phase_8,
    9: phase9.run_phase_9,
    10: phase10.run_phase_10,
}


class GameScreen(Screen):
    """
    Tela principal de jogo que gere o fluxo de uma fase,
    alternando entre história e combate.
    """

    def __init__(self, engine: GameEngine):
        """
        Inicializa a tela de jogo com uma instância do motor do jogo.
        """
        super().__init__()
        self.engine = engine
        self.phase_generator = None
        self.current_enemy = None
        self.victory_text = ""
        # Lista para armazenar as recompensas pendentes
        self._pending_rewards = []

    def on_mount(self) -> None:
        """
        Chamado quando a tela é montada. Inicia a fase atual do jogador.
        """
        self.start_phase(self.engine.jogador.fase_atual)

    def start_phase(self, phase_number: int):
        """
        Carrega e inicia o gerador de eventos para a fase especificada.
        """
        generator_func = PHASE_MAP.get(phase_number)
        if generator_func:
            self.phase_generator = generator_func()
            self.process_next_event()
        else:
            # Se não houver mais fases, termina
            self.app.pop_screen()
            return

    def process_next_event(self, _=None):
        """
        Pega o próximo evento do gerador da fase e apresenta a tela correspondente.
        """
        try:
            event = next(self.phase_generator)

            if event["type"] == "show_text":
                story_segments = event.get("segments", [])
                self.app.push_screen(
                    StoryScreen(story_segments), self.process_next_event
                )

            elif event["type"] == "combat":
                enemy_name = event.get("enemy_name")
                self.current_enemy = self.engine.criar_inimigo(enemy_name)
                self.victory_text = event.get("victory_text")
                if self.current_enemy:
                    self.app.push_screen(
                        CombatScreen(self.engine, self.current_enemy),
                        self.on_combat_finished,
                    )

            elif event["type"] == "enter_hub":
                self.app.push_screen(CityScreen(self.engine), self.on_hub_closed)

            elif event["type"] == "grant_reward":
                # Agora apenas armazena o nome da recompensa, o processamento será no GameEngine
                if "equipment" in event:
                    self._pending_rewards.append(event["equipment"])
                elif "ability" in event:
                    self._pending_rewards.append(event["ability"])
                self.process_next_event()

            elif event["type"] == "phase_end":
                self.engine.jogador.fase_atual += 1
                self.start_phase(self.engine.jogador.fase_atual)

            # 3. Adicionar lógica para o fim do jogo
            elif event["type"] == "game_end":
                # Sai da tela de jogo e volta para o menu principal
                self.app.pop_screen()

        except StopIteration:
            self.app.pop_screen()

    def on_combat_finished(self, combat_result: bool):
        """Callback: chamado quando a CombatScreen é fechada."""
        if combat_result:
            # Processar vitória com recompensas pendentes centralizadamente no GameEngine
            victory_data = self.engine.processar_vitoria(
                self.current_enemy, self._pending_rewards
            )
            self._pending_rewards = []  # Limpar a lista
            self.app.push_screen(VictoryScreen(victory_data), self.on_victory_closed)
        else:
            self.app.pop_screen()

    def on_victory_closed(self, _):
        """Callback: chamado após a tela de vitória ser fechada."""
        if self.victory_text:
            self.app.push_screen(
                StoryScreen([self.victory_text]), self.process_next_event
            )
        else:
            self.process_next_event()

    def on_hub_closed(self, can_progress: bool):
        """Callback: chamado quando uma tela de hub é fechada."""
        if can_progress:
            self.engine.jogador.fase_atual += 1
            self.start_phase(self.engine.jogador.fase_atual)
        else:
            self.app.pop_screen()
