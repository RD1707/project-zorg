from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from core.managers.base_manager import BaseManager
from utils.logging_config import get_logger


class EventType(Enum):
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
    SHOW_SHOP_SCREEN = "show_shop_screen"
    SETTINGS_CHANGED = "settings_changed"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"


@dataclass
class GameEvent:
    type: EventType
    data: Dict[str, Any]
    timestamp: datetime
    source: str = "unknown"

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.now()


EventHandler = Callable[[GameEvent], None]


class EventManager(BaseManager):

    def __init__(self):
        super().__init__("event_manager")
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._event_history: List[GameEvent] = []
        self._max_history = 1000

    def _do_initialize(self) -> None:
        self._handlers.clear()
        self._event_history.clear()

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        if handler not in self._handlers[event_type]:
            self._handlers[event_type].append(handler)
            self.logger.debug(f"Handler inscrito para evento {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type in self._handlers:
            try:
                self._handlers[event_type].remove(handler)
                self.logger.debug(f"Handler removido do evento {event_type.value}")
            except ValueError:
                self.logger.warning(f"Handler não encontrado para evento {event_type.value}")

    def emit(self, event_type: EventType, data: Dict[str, Any] = None, source: str = "game") -> None:
        if data is None:
            data = {}

        event = GameEvent(
            type=event_type,
            data=data,
            timestamp=datetime.now(),
            source=source
        )

        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Erro ao executar handler para evento {event_type.value}: {e}")

        self.logger.debug(f"Evento {event_type.value} emitido com {len(self._handlers.get(event_type, []))} handlers")

    def get_event_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[GameEvent]:
        if event_type is None:
            return self._event_history[-limit:]

        filtered_events = [e for e in self._event_history if e.type == event_type]
        return filtered_events[-limit:]

    def clear_history(self) -> None:
        self._event_history.clear()
        self.logger.info("Histórico de eventos limpo")

    def get_handler_count(self, event_type: EventType) -> int:
        return len(self._handlers.get(event_type, []))

    def get_status(self) -> Dict[str, Any]:
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

_event_manager = EventManager()


def get_event_manager() -> EventManager:
    if not _event_manager.is_initialized():
        _event_manager.initialize()
    return _event_manager


def emit_event(event_type: EventType, data: Dict[str, Any] = None, source: str = "game") -> None:
    get_event_manager().emit(event_type, data, source)


def subscribe_to_event(event_type: EventType, handler: EventHandler) -> None:
    get_event_manager().subscribe(event_type, handler)