from textual.widgets import Static

from core.models import Personagem


class StatusBar(Static):
    """Um widget para exibir o status do jogador."""

    def update_status(self, jogador: Personagem) -> None:
        """Atualiza o conteúdo da barra de status."""
        self.update(
            f"HP: {jogador.hp}/{jogador.hp_max} | "
            f"MP: {jogador.mp}/{jogador.mp_max} | "
            f"Ouro: {jogador.ouro}"
        )
