"""
Gerenciador de inventário com operações otimizadas e validadas.
"""
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from core.managers.base_manager import BaseManager
from core.managers.event_manager import emit_event, EventType
from core.models import Personagem, Item, Equipamento, TipoEquipamento
from core.exceptions import InvalidActionError, ResourceNotFoundError
from utils.error_handler import handle_exceptions, validate_not_none, validate_positive
from data.items import DB_ITENS
from data.equipment import DB_EQUIPAMENTOS


class InventoryAction(Enum):
    """Tipos de ação no inventário."""
    ADD_ITEM = "add_item"
    REMOVE_ITEM = "remove_item"
    USE_ITEM = "use_item"
    EQUIP_ITEM = "equip_item"
    UNEQUIP_ITEM = "unequip_item"
    SORT_INVENTORY = "sort_inventory"


class InventoryManager(BaseManager):
    """Gerenciador de inventário."""

    def __init__(self):
        super().__init__("inventory_manager")
        self._max_inventory_size = 50  # Limite do inventário

    def _do_initialize(self) -> None:
        """Inicialização do gerenciador de inventário."""
        pass

    @handle_exceptions(reraise=True)
    def add_item(self, player: Personagem, item_name: str, quantity: int = 1) -> bool:
        """Adiciona item ao inventário do jogador."""
        validate_not_none(player, "jogador")
        validate_positive(quantity, "quantidade")

        # Verificar se o item existe no banco de dados
        item_template = DB_ITENS.get(item_name)
        if not item_template:
            raise ResourceNotFoundError("item", item_name)

        # Verificar limite do inventário
        current_slots = len(player.inventario)
        if current_slots >= self._max_inventory_size:
            # Tentar empilhar com item existente
            if not self._try_stack_item(player, item_template, quantity):
                raise InvalidActionError("Inventário cheio e não é possível empilhar o item")

        # Tentar empilhar primeiro
        if self._try_stack_item(player, item_template, quantity):
            emit_event(EventType.ITEM_USED, {
                "action": "add_stacked",
                "item": item_name,
                "quantity": quantity,
                "player": player.nome
            })
            self.logger.debug(f"Item {item_name} x{quantity} empilhado no inventário de {player.nome}")
            return True

        # Adicionar como novo item
        from copy import deepcopy
        new_item = deepcopy(item_template)
        new_item.quantidade = quantity
        player.inventario.append(new_item)

        emit_event(EventType.ITEM_USED, {
            "action": "add_new",
            "item": item_name,
            "quantity": quantity,
            "player": player.nome
        })

        self.logger.debug(f"Novo item {item_name} x{quantity} adicionado ao inventário de {player.nome}")
        return True

    @handle_exceptions(reraise=True)
    def remove_item(self, player: Personagem, item_name: str, quantity: int = 1) -> bool:
        """Remove item do inventário do jogador."""
        validate_not_none(player, "jogador")
        validate_positive(quantity, "quantidade")

        for item in player.inventario:
            if item.nome == item_name:
                if item.quantidade >= quantity:
                    item.quantidade -= quantity
                    if item.quantidade <= 0:
                        player.inventario.remove(item)

                    emit_event(EventType.ITEM_USED, {
                        "action": "remove",
                        "item": item_name,
                        "quantity": quantity,
                        "player": player.nome
                    })

                    self.logger.debug(f"Item {item_name} x{quantity} removido do inventário de {player.nome}")
                    return True
                else:
                    raise InvalidActionError(f"Quantidade insuficiente de {item_name}: tem {item.quantidade}, precisa {quantity}")

        raise ResourceNotFoundError("item no inventário", item_name)

    @handle_exceptions(reraise=True)
    def use_item(self, player: Personagem, item_name: str) -> List[str]:
        """Usa um item do inventário."""
        validate_not_none(player, "jogador")

        # Verificar se tem o item
        item = self._find_item(player, item_name)
        if not item:
            raise ResourceNotFoundError("item no inventário", item_name)

        messages = []
        effects_applied = False

        # Aplicar efeitos de cura de HP
        if item.cura_hp > 0:
            heal_amount = player.heal(item.cura_hp)
            if heal_amount > 0:
                messages.append(f"🧪 {player.nome} usa {item_name} e recupera [b green]{heal_amount} HP[/b green]!")
                effects_applied = True
            else:
                messages.append(f"{player.nome} usa {item_name}, mas sua vida já está cheia.")

        # Aplicar efeitos de cura de MP
        if item.cura_mp > 0:
            mp_amount = player.restore_mp(item.cura_mp)
            if mp_amount > 0:
                messages.append(f"🧪 {player.nome} usa {item_name} e recupera [b blue]{mp_amount} MP[/b blue]!")
                effects_applied = True
            else:
                messages.append(f"{player.nome} usa {item_name}, mas seu MP já está cheio.")

        # Aplicar cura de veneno
        if item.cura_veneno > 0 and player.is_poisoned:
            player.turnos_veneno = 0
            player.dano_por_turno_veneno = 0
            messages.append(f"🧪 {player.nome} usa {item_name} e se cura do [b magenta]veneno[/b magenta]!")
            effects_applied = True

        # Se nenhum efeito foi aplicado
        if not effects_applied:
            messages.append(f"{player.nome} usa {item_name}, mas nada acontece.")

        # Remover item do inventário
        self.remove_item(player, item_name, 1)

        emit_event(EventType.ITEM_USED, {
            "action": "use",
            "item": item_name,
            "player": player.nome,
            "effects_applied": effects_applied
        })

        self.logger.debug(f"Item {item_name} usado por {player.nome}")
        return messages

    @handle_exceptions(reraise=True)
    def equip_item(self, player: Personagem, equipment_name: str) -> Tuple[bool, List[str]]:
        """Equipa um equipamento."""
        validate_not_none(player, "jogador")

        # Verificar se o equipamento existe
        equipment = DB_EQUIPAMENTOS.get(equipment_name)
        if not equipment:
            raise ResourceNotFoundError("equipamento", equipment_name)

        messages = []
        old_equipment = None

        # Determinar slot e equipar
        if equipment.is_weapon:
            old_equipment = player.arma_equipada
            player.arma_equipada = equipment
            messages.append(f"⚔️ {equipment_name} equipado como arma!")

        elif equipment.is_armor:
            old_equipment = player.armadura_equipada
            player.armadura_equipada = equipment
            messages.append(f"🛡️ {equipment_name} equipado como armadura!")

        elif equipment.is_shield:
            old_equipment = player.escudo_equipada
            player.escudo_equipada = equipment
            messages.append(f"🛡️ {equipment_name} equipado como escudo!")

        else:
            raise InvalidActionError(f"Tipo de equipamento desconhecido: {equipment.tipo}")

        # Adicionar equipamento anterior ao inventário se existir
        if old_equipment:
            self.add_item(player, old_equipment.nome, 1)
            messages.append(f"{old_equipment.nome} foi colocado no inventário.")

        emit_event(EventType.EQUIPMENT_CHANGED, {
            "action": "equip",
            "item": equipment_name,
            "old_item": old_equipment.nome if old_equipment else None,
            "player": player.nome,
            "slot": equipment.tipo.value
        })

        self.logger.debug(f"Equipamento {equipment_name} equipado por {player.nome}")
        return True, messages

    @handle_exceptions(reraise=True)
    def unequip_item(self, player: Personagem, slot: str) -> Tuple[bool, List[str]]:
        """Remove equipamento de um slot."""
        validate_not_none(player, "jogador")

        messages = []
        equipment_to_unequip = None

        # Determinar equipamento a remover
        if slot.lower() in ["arma", "weapon"]:
            equipment_to_unequip = player.arma_equipada
            player.arma_equipada = None
        elif slot.lower() in ["armadura", "armor"]:
            equipment_to_unequip = player.armadura_equipada
            player.armadura_equipada = None
        elif slot.lower() in ["escudo", "shield"]:
            equipment_to_unequip = player.escudo_equipada
            player.escudo_equipada = None
        else:
            raise InvalidActionError(f"Slot de equipamento inválido: {slot}")

        if not equipment_to_unequip:
            raise InvalidActionError(f"Nenhum equipamento no slot {slot}")

        # Adicionar ao inventário
        self.add_item(player, equipment_to_unequip.nome, 1)
        messages.append(f"{equipment_to_unequip.nome} foi removido e colocado no inventário.")

        emit_event(EventType.EQUIPMENT_CHANGED, {
            "action": "unequip",
            "item": equipment_to_unequip.nome,
            "player": player.nome,
            "slot": slot
        })

        self.logger.debug(f"Equipamento {equipment_to_unequip.nome} desequipado por {player.nome}")
        return True, messages

    def sort_inventory(self, player: Personagem, sort_by: str = "name") -> bool:
        """Organiza o inventário do jogador."""
        validate_not_none(player, "jogador")

        if sort_by == "name":
            player.inventario.sort(key=lambda item: item.nome)
        elif sort_by == "quantity":
            player.inventario.sort(key=lambda item: item.quantidade, reverse=True)
        elif sort_by == "value":
            player.inventario.sort(key=lambda item: item.preco_venda, reverse=True)
        elif sort_by == "category":
            player.inventario.sort(key=lambda item: item.categoria)
        else:
            raise InvalidActionError(f"Critério de ordenação inválido: {sort_by}")

        self.logger.debug(f"Inventário de {player.nome} organizado por {sort_by}")
        return True

    def get_inventory_info(self, player: Personagem) -> Dict[str, Any]:
        """Retorna informações detalhadas do inventário."""
        validate_not_none(player, "jogador")

        total_items = sum(item.quantidade for item in player.inventario)
        total_value = sum(item.preco_venda * item.quantidade for item in player.inventario)

        categories = {}
        for item in player.inventario:
            category = item.categoria
            if category not in categories:
                categories[category] = {"count": 0, "value": 0}
            categories[category]["count"] += item.quantidade
            categories[category]["value"] += item.preco_venda * item.quantidade

        return {
            "slots_used": len(player.inventario),
            "max_slots": self._max_inventory_size,
            "total_items": total_items,
            "total_value": total_value,
            "categories": categories,
            "equipment": {
                "weapon": player.arma_equipada.nome if player.arma_equipada else None,
                "armor": player.armadura_equipada.nome if player.armadura_equipada else None,
                "shield": player.escudo_equipada.nome if player.escudo_equipada else None,
            }
        }

    def _try_stack_item(self, player: Personagem, item_template: Item, quantity: int) -> bool:
        """Tenta empilhar item com item existente."""
        for existing_item in player.inventario:
            if (existing_item.nome == item_template.nome and
                existing_item.quantidade + quantity <= existing_item.stack_max):
                existing_item.quantidade += quantity
                return True
        return False

    def _find_item(self, player: Personagem, item_name: str) -> Optional[Item]:
        """Encontra item no inventário."""
        return next((item for item in player.inventario if item.nome == item_name), None)

    def can_add_item(self, player: Personagem, item_name: str, quantity: int = 1) -> bool:
        """Verifica se pode adicionar item ao inventário."""
        item_template = DB_ITENS.get(item_name)
        if not item_template:
            return False

        # Verificar se pode empilhar
        if self._try_stack_item(player, item_template, quantity):
            return True

        # Verificar se há espaço para novo slot
        return len(player.inventario) < self._max_inventory_size

    def get_items_by_category(self, player: Personagem, category: str) -> List[Item]:
        """Retorna itens de uma categoria específica."""
        return [item for item in player.inventario if item.categoria == category]


# Instância global do gerenciador de inventário
_inventory_manager = InventoryManager()


def get_inventory_manager() -> InventoryManager:
    """Retorna a instância global do gerenciador de inventário."""
    if not _inventory_manager.is_initialized():
        _inventory_manager.initialize()
    return _inventory_manager