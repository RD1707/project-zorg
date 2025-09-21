"""
Factory para criação eficiente de objetos do jogo.
Substitui o uso excessivo de deepcopy por criação otimizada.
"""
from typing import Dict, Any, Type, Optional
import logging

from core.models import Item, Equipamento, Personagem


class ObjectFactory:
    """Factory para criação eficiente de objetos do jogo."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._item_cache: Dict[str, Dict[str, Any]] = {}
        self._equipment_cache: Dict[str, Dict[str, Any]] = {}
        self._enemy_cache: Dict[str, Dict[str, Any]] = {}

    def create_item(self, item_template: Item) -> Item:
        """Cria uma nova instância de item de forma eficiente."""
        return Item(
            nome=item_template.nome,
            descricao=item_template.descricao,
            cura_hp=item_template.cura_hp,
            cura_mp=item_template.cura_mp,
            cura_veneno=item_template.cura_veneno,
            preco_venda=item_template.preco_venda,
            quantidade=1,  # Sempre criar com quantidade 1
            stack_max=getattr(item_template, 'stack_max', 99),
            categoria=getattr(item_template, 'categoria', 'consumível')
        )

    def create_equipment(self, equipment_template: Equipamento) -> Equipamento:
        """Cria uma nova instância de equipamento de forma eficiente."""
        return Equipamento(
            nome=equipment_template.nome,
            tipo=equipment_template.tipo,
            descricao=equipment_template.descricao,
            preco=equipment_template.preco,
            efeito=equipment_template.efeito,
            ataque_bonus=getattr(equipment_template, 'ataque_bonus', 0),
            defesa_bonus=getattr(equipment_template, 'defesa_bonus', 0),
            hp_bonus=getattr(equipment_template, 'hp_bonus', 0),
            mp_bonus=getattr(equipment_template, 'mp_bonus', 0),
            raridade=getattr(equipment_template, 'raridade', 'comum'),
            durabilidade=getattr(equipment_template, 'durabilidade', 100),
            durabilidade_max=getattr(equipment_template, 'durabilidade_max', 100)
        )

    def create_enemy(self, enemy_template: Personagem) -> Personagem:
        """Cria uma nova instância de inimigo de forma eficiente."""
        enemy = Personagem(
            nome=enemy_template.nome,
            hp_max=enemy_template.hp_max,
            mp_max=enemy_template.mp_max,
            ataque_base=enemy_template.ataque_base,
            defesa_base=enemy_template.defesa_base
        )

        # Copiar atributos específicos de inimigo
        if hasattr(enemy_template, 'xp_reward'):
            enemy.xp_reward = enemy_template.xp_reward
        if hasattr(enemy_template, 'gold_reward'):
            enemy.gold_reward = enemy_template.gold_reward
        if hasattr(enemy_template, 'descricao'):
            enemy.descricao = enemy_template.descricao
        if hasattr(enemy_template, 'tipo'):
            enemy.tipo = enemy_template.tipo
        if hasattr(enemy_template, 'habilidades'):
            enemy.habilidades = list(enemy_template.habilidades)  # Shallow copy da lista
        if hasattr(enemy_template, 'resistencias'):
            enemy.resistencias = dict(enemy_template.resistencias)  # Shallow copy do dict
        if hasattr(enemy_template, 'fraquezas'):
            enemy.fraquezas = dict(enemy_template.fraquezas)

        # Inicializar HP e MP como máximo
        enemy.hp = enemy.hp_max
        enemy.mp = enemy.mp_max

        return enemy

    def create_item_from_data(self, item_data: Dict[str, Any]) -> Item:
        """Cria item a partir de dados serializados."""
        return Item(
            nome=item_data.get("nome", "Item Desconhecido"),
            descricao=item_data.get("descricao", ""),
            cura_hp=item_data.get("cura_hp", 0),
            cura_mp=item_data.get("cura_mp", 0),
            cura_veneno=item_data.get("cura_veneno", 0),
            preco_venda=item_data.get("preco_venda", 0),
            quantidade=item_data.get("quantidade", 1),
            stack_max=item_data.get("stack_max", 99),
            categoria=item_data.get("categoria", "consumível")
        )

    def create_equipment_from_data(self, eq_data: Dict[str, Any]) -> Equipamento:
        """Cria equipamento a partir de dados serializados."""
        return Equipamento(
            nome=eq_data.get("nome", "Equipamento Desconhecido"),
            tipo=eq_data.get("tipo", "arma"),
            descricao=eq_data.get("descricao", ""),
            preco=eq_data.get("preco", 0),
            efeito=eq_data.get("efeito", {}),
            ataque_bonus=eq_data.get("ataque_bonus", 0),
            defesa_bonus=eq_data.get("defesa_bonus", 0),
            hp_bonus=eq_data.get("hp_bonus", 0),
            mp_bonus=eq_data.get("mp_bonus", 0),
            raridade=eq_data.get("raridade", "comum"),
            durabilidade=eq_data.get("durabilidade", 100),
            durabilidade_max=eq_data.get("durabilidade_max", 100)
        )

    def clear_cache(self):
        """Limpa todos os caches para liberar memória."""
        self._item_cache.clear()
        self._equipment_cache.clear()
        self._enemy_cache.clear()
        self.logger.debug("Object factory cache cleared")


# Instância global do factory
_factory_instance: Optional[ObjectFactory] = None


def get_object_factory() -> ObjectFactory:
    """Retorna a instância singleton do object factory."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ObjectFactory()
    return _factory_instance


def clear_object_cache():
    """Limpa o cache de objetos."""
    factory = get_object_factory()
    factory.clear_cache()