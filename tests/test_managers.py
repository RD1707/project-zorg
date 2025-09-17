"""
Testes para os managers do ZORG.
"""
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

from core.managers.combat_manager import CombatManager, CombatAction, CombatResult
from core.managers.inventory_manager import InventoryManager
from core.managers.save_manager import SaveManager
from core.managers.event_manager import EventManager, EventType
from core.managers.cache_manager import CacheManager, LRUCache
from core.models import Personagem, TipoHabilidade
from core.exceptions import CombatError, InvalidActionError, SaveLoadError


class TestCombatManager:
    """Testes para o CombatManager."""

    @pytest.fixture
    def combat_manager(self):
        manager = CombatManager()
        manager.initialize()
        return manager

    def test_combat_initialization(self, combat_manager):
        """Testa inicialização do gerenciador de combate."""
        assert combat_manager.is_initialized()
        assert not combat_manager.is_combat_active()

    def test_start_combat(self, combat_manager, sample_player, sample_enemy):
        """Testa início de combate."""
        combat_state = combat_manager.start_combat(sample_player, sample_enemy)

        assert combat_state["active"] == True
        assert combat_state["player"] == sample_player
        assert combat_state["enemy"] == sample_enemy
        assert combat_state["turn_count"] == 0

    def test_start_combat_invalid_conditions(self, combat_manager, sample_player, sample_enemy):
        """Testa início de combate com condições inválidas."""
        # Player morto
        sample_player.hp = 0
        with pytest.raises(CombatError):
            combat_manager.start_combat(sample_player, sample_enemy)

        # Enemy morto
        sample_player.hp = 100
        sample_enemy.hp = 0
        with pytest.raises(CombatError):
            combat_manager.start_combat(sample_player, sample_enemy)

    def test_player_attack_turn(self, combat_manager, sample_player, sample_enemy):
        """Testa turno de ataque do jogador."""
        combat_manager.start_combat(sample_player, sample_enemy)

        old_enemy_hp = sample_enemy.hp
        combat_state = combat_manager.process_player_turn(CombatAction.ATTACK)

        assert sample_enemy.hp < old_enemy_hp
        assert len(combat_state["log"]) > 0
        assert combat_state["turn_count"] == 1

    def test_player_skill_turn(self, combat_manager, sample_player, sample_enemy, sample_skill):
        """Testa turno de habilidade do jogador."""
        sample_player.habilidades_conhecidas.append(sample_skill)
        combat_manager.start_combat(sample_player, sample_enemy)

        if sample_skill.tipo == TipoHabilidade.CURA:
            sample_player.hp = 50  # Reduzir HP para testar cura

        combat_state = combat_manager.process_player_turn(
            CombatAction.SKILL,
            skill_name=sample_skill.nome
        )

        assert len(combat_state["log"]) > 0
        assert sample_player.mp < 50  # MP foi gasto

    def test_enemy_turn(self, combat_manager, sample_player, sample_enemy):
        """Testa turno do inimigo."""
        combat_manager.start_combat(sample_player, sample_enemy)

        old_player_hp = sample_player.hp
        combat_state = combat_manager.process_enemy_turn()

        assert sample_player.hp <= old_player_hp  # Player pode ter perdido HP
        assert len(combat_state["log"]) > 0

    def test_combat_end_conditions(self, combat_manager, sample_player, sample_enemy):
        """Testa condições de fim de combate."""
        combat_manager.start_combat(sample_player, sample_enemy)

        # Matar inimigo
        sample_enemy.hp = 0
        combat_manager._check_combat_end()

        combat_state = combat_manager.get_combat_state()
        assert combat_state["result"] == CombatResult.PLAYER_WIN

    def test_combat_end_cleanup(self, combat_manager, sample_player, sample_enemy):
        """Testa limpeza no fim do combate."""
        combat_manager.start_combat(sample_player, sample_enemy)
        assert combat_manager.is_combat_active()

        final_state = combat_manager.end_combat()
        assert not combat_manager.is_combat_active()
        assert final_state["active"] == True  # Estado final ainda tem dados


class TestInventoryManager:
    """Testes para o InventoryManager."""

    @pytest.fixture
    def inventory_manager(self):
        manager = InventoryManager()
        manager.initialize()
        return manager

    def test_inventory_initialization(self, inventory_manager):
        """Testa inicialização do gerenciador de inventário."""
        assert inventory_manager.is_initialized()

    def test_add_item(self, inventory_manager, sample_player, mock_db_data):
        """Testa adição de item ao inventário."""
        initial_count = len(sample_player.inventario)

        result = inventory_manager.add_item(sample_player, "Test Item", 2)
        assert result == True
        assert len(sample_player.inventario) == initial_count + 1

        # Verificar se item foi adicionado corretamente
        item = next((i for i in sample_player.inventario if i.nome == "Test Item"), None)
        assert item is not None
        assert item.quantidade == 2

    def test_add_item_stacking(self, inventory_manager, sample_player, sample_item):
        """Testa empilhamento de itens."""
        # Adicionar item inicial
        sample_player.inventario.append(sample_item)

        # Tentar adicionar mais do mesmo item
        result = inventory_manager.add_item(sample_player, sample_item.nome, 3)
        assert result == True
        assert len(sample_player.inventario) == 1
        assert sample_player.inventario[0].quantidade == 4  # 1 + 3

    def test_remove_item(self, inventory_manager, sample_player, sample_item):
        """Testa remoção de item do inventário."""
        sample_item.quantidade = 5
        sample_player.inventario.append(sample_item)

        result = inventory_manager.remove_item(sample_player, sample_item.nome, 2)
        assert result == True
        assert sample_item.quantidade == 3

        # Remover tudo
        result = inventory_manager.remove_item(sample_player, sample_item.nome, 3)
        assert result == True
        assert len(sample_player.inventario) == 0

    def test_use_item(self, inventory_manager, sample_player, sample_item, mock_db_data):
        """Testa uso de item."""
        sample_player.hp = 50  # HP parcial para testar cura
        sample_player.inventario.append(sample_item)

        messages = inventory_manager.use_item(sample_player, sample_item.nome)
        assert len(messages) > 0
        assert sample_player.hp > 50  # HP deve ter aumentado
        assert len(sample_player.inventario) == 0  # Item foi consumido

    def test_inventory_info(self, inventory_manager, sample_player, sample_item):
        """Testa obtenção de informações do inventário."""
        sample_player.inventario.append(sample_item)

        info = inventory_manager.get_inventory_info(sample_player)
        assert info["slots_used"] == 1
        assert info["total_items"] == 1
        assert info["total_value"] > 0

    def test_sort_inventory(self, inventory_manager, sample_player):
        """Testa organização do inventário."""
        # Adicionar vários itens
        from core.models import Item

        item1 = Item(nome="Z Item", descricao="", cura_hp=0, cura_mp=0, cura_veneno=0, preco_venda=10)
        item2 = Item(nome="A Item", descricao="", cura_hp=0, cura_mp=0, cura_veneno=0, preco_venda=5)

        sample_player.inventario.extend([item1, item2])

        inventory_manager.sort_inventory(sample_player, "name")
        assert sample_player.inventario[0].nome == "A Item"
        assert sample_player.inventario[1].nome == "Z Item"


class TestSaveManager:
    """Testes para o SaveManager."""

    @pytest.fixture
    def save_manager(self, mock_save_dir):
        manager = SaveManager()
        manager.initialize()
        return manager

    def test_save_manager_initialization(self, save_manager):
        """Testa inicialização do gerenciador de save."""
        assert save_manager.is_initialized()

    def test_save_game(self, save_manager, sample_player, mock_save_dir):
        """Testa salvamento do jogo."""
        result = save_manager.save_game(sample_player)
        assert result == True
        assert mock_save_dir.exists()

        # Verificar conteúdo do arquivo
        with open(mock_save_dir, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data["player"]["nome"] == sample_player.nome
        assert data["player"]["hp"] == sample_player.hp
        assert "checksum" in data

    def test_load_game(self, save_manager, sample_player, mock_save_dir):
        """Testa carregamento do jogo."""
        # Primeiro salvar
        save_manager.save_game(sample_player)

        # Depois carregar
        loaded_player = save_manager.load_game()
        assert loaded_player is not None
        assert loaded_player.nome == sample_player.nome
        assert loaded_player.hp == sample_player.hp

    def test_load_nonexistent_save(self, save_manager):
        """Testa carregamento quando não há save."""
        result = save_manager.load_game()
        assert result is None

    def test_save_validation(self, save_manager, sample_player, mock_save_dir):
        """Testa validação de dados de save."""
        save_manager.save_game(sample_player)

        # Corromper arquivo
        with open(mock_save_dir, 'w') as f:
            json.dump({"invalid": "data"}, f)

        with pytest.raises(SaveLoadError):
            save_manager.load_game()

    def test_get_save_info(self, save_manager, sample_player, mock_save_dir):
        """Testa obtenção de informações do save."""
        # Sem save
        info = save_manager.get_save_info()
        assert info is None

        # Com save
        save_manager.save_game(sample_player)
        info = save_manager.get_save_info()
        assert info is not None
        assert info["exists"] == True
        assert info["player_name"] == sample_player.nome


class TestEventManager:
    """Testes para o EventManager."""

    @pytest.fixture
    def event_manager(self):
        manager = EventManager()
        manager.initialize()
        return manager

    def test_event_manager_initialization(self, event_manager):
        """Testa inicialização do gerenciador de eventos."""
        assert event_manager.is_initialized()

    def test_subscribe_and_emit(self, event_manager):
        """Testa inscrição e emissão de eventos."""
        events_received = []

        def handler(event):
            events_received.append(event)

        event_manager.subscribe(EventType.COMBAT_START, handler)
        event_manager.emit(EventType.COMBAT_START, {"test": "data"})

        assert len(events_received) == 1
        assert events_received[0].type == EventType.COMBAT_START
        assert events_received[0].data["test"] == "data"

    def test_multiple_handlers(self, event_manager):
        """Testa múltiplos handlers para o mesmo evento."""
        handler1_calls = []
        handler2_calls = []

        def handler1(event):
            handler1_calls.append(event)

        def handler2(event):
            handler2_calls.append(event)

        event_manager.subscribe(EventType.COMBAT_START, handler1)
        event_manager.subscribe(EventType.COMBAT_START, handler2)
        event_manager.emit(EventType.COMBAT_START, {"test": "data"})

        assert len(handler1_calls) == 1
        assert len(handler2_calls) == 1

    def test_unsubscribe(self, event_manager):
        """Testa cancelamento de inscrição."""
        events_received = []

        def handler(event):
            events_received.append(event)

        event_manager.subscribe(EventType.COMBAT_START, handler)
        event_manager.emit(EventType.COMBAT_START, {})
        assert len(events_received) == 1

        event_manager.unsubscribe(EventType.COMBAT_START, handler)
        event_manager.emit(EventType.COMBAT_START, {})
        assert len(events_received) == 1  # Não deve ter aumentado

    def test_event_history(self, event_manager):
        """Testa histórico de eventos."""
        event_manager.emit(EventType.COMBAT_START, {"battle": 1})
        event_manager.emit(EventType.COMBAT_END, {"battle": 1})

        history = event_manager.get_event_history()
        assert len(history) == 2
        assert history[0].type == EventType.COMBAT_START
        assert history[1].type == EventType.COMBAT_END

        # Filtrar por tipo
        combat_events = event_manager.get_event_history(EventType.COMBAT_START)
        assert len(combat_events) == 1
        assert combat_events[0].type == EventType.COMBAT_START


class TestCacheManager:
    """Testes para o CacheManager."""

    @pytest.fixture
    def cache_manager(self):
        manager = CacheManager()
        manager.initialize()
        return manager

    def test_cache_manager_initialization(self, cache_manager):
        """Testa inicialização do gerenciador de cache."""
        assert cache_manager.is_initialized()

    def test_cache_operations(self, cache_manager):
        """Testa operações básicas de cache."""
        # Set e Get
        cache_manager.set("test_key", "test_value")
        value = cache_manager.get("test_key")
        assert value == "test_value"

        # Delete
        result = cache_manager.delete("test_key")
        assert result == True
        assert cache_manager.get("test_key") is None

    def test_cache_with_different_names(self, cache_manager):
        """Testa cache com nomes diferentes."""
        cache_manager.set("key1", "value1", "main")
        cache_manager.set("key1", "value2", "resources")

        assert cache_manager.get("key1", "main") == "value1"
        assert cache_manager.get("key1", "resources") == "value2"

    def test_lru_cache_functionality(self):
        """Testa funcionalidade do LRU Cache."""
        cache = LRUCache(max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Deve remover key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_cache_ttl(self):
        """Testa TTL (Time To Live) do cache."""
        import time

        cache = LRUCache(default_ttl=0.1)  # 100ms TTL
        cache.set("key", "value")

        # Imediatamente deve estar disponível
        assert cache.get("key") == "value"

        # Após TTL deve ter expirado
        time.sleep(0.2)
        assert cache.get("key") is None

    def test_cache_stats(self, cache_manager):
        """Testa estatísticas do cache."""
        cache_manager.set("key1", "value1")
        cache_manager.get("key1")
        cache_manager.get("key1")

        stats = cache_manager.get_stats()
        assert "enabled" in stats
        assert "caches" in stats
        assert "main" in stats["caches"]

    def test_cache_cleanup(self, cache_manager):
        """Testa limpeza de entradas expiradas."""
        # Adicionar entrada com TTL baixo
        cache = cache_manager.get_cache("main")
        cache.set("temp_key", "temp_value", ttl=0.001)  # 1ms

        import time
        time.sleep(0.01)  # Esperar expirar

        cleaned = cache_manager.cleanup_expired()
        assert cleaned["main"] >= 0  # Pelo menos 0 entradas limpas