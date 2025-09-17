"""
Sistema de eventos baseado no padrão Observer.
"""
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.managers.base_manager import BaseManager
from utils.logging_config import get_logger


class EventType(Enum):
    """Tipos de eventos do jogo."""
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    PLAYER_LEVEL_UP = "player_level_up"
    PLAYER_DEATH = "player_death"
    ITEM_USED = "item_used"
    SKILL_USED = "skill_used"
    EQUIPMENT_CHANGED = "equipment_changed"
    PHASE_COMPLETED = "phase_completed"
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class GameEvent:
    """Representa um evento do jogo."""
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str = "unknown"

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()


EventHandler = Callable[[GameEvent], None]


class EventManager(BaseManager):
    """Gerenciador de eventos usando padrão Observer."""

    def __init__(self):
        super().__init__("event_manager")
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._event_history: List[GameEvent] = []
        self._max_history = 1000

    def _do_initialize(self) -> None:
        """Inicialização do gerenciador de eventos."""
        self._handlers.clear()
        self._event_history.clear()

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Inscreve um handler para um tipo de evento."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            self.logger.debug(f"Handler inscrito para evento {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Desinscreve um handler de um tipo de evento."""
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                self.logger.debug(f"Handler removido do evento {event_type.value}")
            except ValueError:
                self.logger.warning(f"Handler não encontrado para evento {event_type.value}")

    def emit(self, event_type: EventType, data: Dict[str, Any] = None, source: str = "game") -> None:
        """Emite um evento para todos os handlers inscritos."""
        if data is None:
            data = {}

        event = GameEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )

        # Adicionar ao histórico
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notificar handlers
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Erro ao executar handler para evento {event_type.value}: {e}")

        self.logger.debug(f"Evento {event_type.value} emitido com {len(self._handlers.get(event_type, []))} handlers")

    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[GameEvent]:
        """Retorna o histórico de eventos."""
        if event_type is None:
            return self._event_history[-limit:]

        filtered_events = [e for e in self._event_history if e.type == event_type]
        return filtered_events[-limit:]

    def clear_history(self) -> None:
        """Limpa o histórico de eventos."""
        self._event_history.clear()
        self.logger.info("Histórico de eventos limpo")

    def get_handler_count(self, event_type: EventType) -> int:
        """Retorna o número de handlers para um tipo de evento."""
        return len(self._handlers.get(event_type, []))

    def get_status(self) -> Dict[str, Any]:
        """Retorna o status do gerenciador de eventos."""
        status = super().get_status()
        status.update({
            "total_handlers": sum(len(handlers) for handlers in self._handlers.values()),
            "event_types": len(self._handlers),
            "history_size": len(self._event_history),
            "handlers_by_type": {
                event_type.value: len(handlers)
                for event_type, handlers in self._handlers.items()
            }
        })
        return status


# Instância global do gerenciador de eventos
_event_manager = EventManager()


def get_event_manager() -> EventManager:
    """Retorna a instância global do gerenciador de eventos."""
    if not _event_manager.is_initialized():
        _event_manager.initialize()
    return _event_manager


def emit_event(event_type: EventType, data: Dict[str, Any] = None, source: str = "game") -> None:
    """Função conveniente para emitir eventos."""
    get_event_manager().emit(event_type, data, source)


def subscribe_to_event(event_type: EventType, handler: EventHandler) -> None:
    """Função conveniente para se inscrever em eventos."""
    get_event_manager().subscribe(event_type, handler)