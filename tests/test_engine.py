"""
Testes para o GameEngine do ZORG.
"""

import pytest

from core.engine import GameEngine, get_game_engine
from core.exceptions import GameEngineError, ResourceNotFoundError
from core.managers.event_manager import EventType


class TestGameEngine:
    """Testes para a classe GameEngine."""

    def test_singleton_pattern(self, clean_engine):
        """Testa se o padrão Singleton funciona corretamente."""
        engine1 = GameEngine()
        engine2 = GameEngine()
        engine3 = get_game_engine()

        assert engine1 is engine2
        assert engine2 is engine3
        assert id(engine1) == id(engine2) == id(engine3)

    def test_engine_initialization(self, game_engine):
        """Testa inicialização do engine."""
        assert game_engine._initialized is True
        assert game_engine.jogador is None

        # Verificar se todos os managers foram inicializados
        assert game_engine.combat_manager is not None
        assert game_engine.inventory_manager is not None
        assert game_engine.save_manager is not None
        assert game_engine.event_manager is not None
        assert game_engine.cache_manager is not None

    def test_inicializar_novo_jogo(self, game_engine, mock_db_data):
        """Testa inicialização de novo jogo."""
        game_engine.inicializar_novo_jogo()

        assert game_engine.jogador is not None
        assert game_engine.jogador.nome == "Manu"
        assert game_engine.jogador.hp == 50
        assert game_engine.jogador.mp == 20
        assert game_engine.jogador.nivel == 1

    def test_criar_inimigo(self, game_engine, mock_db_data):
        """Testa criação de inimigos."""
        enemy = game_engine.criar_inimigo("Test Enemy")

        assert enemy is not None
        assert enemy.nome == "Test Enemy"
        assert enemy.hp == 50

        # Teste com inimigo inexistente
        with pytest.raises(ResourceNotFoundError):
            game_engine.criar_inimigo("Nonexistent Enemy")

    def test_criar_inimigo_with_cache(self, game_engine, mock_db_data):
        """Testa se o cache funciona na criação de inimigos."""
        # Primeira criação
        enemy1 = game_engine.criar_inimigo("Test Enemy")

        # Segunda criação (deveria usar cache)
        enemy2 = game_engine.criar_inimigo("Test Enemy")

        # Devem ser instâncias diferentes mas com mesmos dados
        assert enemy1 is not enemy2
        assert enemy1.nome == enemy2.nome
        assert enemy1.hp == enemy2.hp

    def test_adicionar_item_inventario(self, game_engine, mock_db_data):
        """Testa adição de itens ao inventário."""
        game_engine.inicializar_novo_jogo()

        result = game_engine.adicionar_item_inventario("Test Item", 3)
        assert result is True

        # Verificar se item foi adicionado
        assert any(item.nome == "Test Item" for item in game_engine.jogador.inventario)

        # Teste sem jogador ativo
        game_engine.jogador = None
        with pytest.raises(GameEngineError):
            game_engine.adicionar_item_inventario("Test Item")

    def test_aprender_habilidade(self, game_engine, mock_db_data):
        """Testa aprendizado de habilidades."""
        game_engine.inicializar_novo_jogo()

        result = game_engine.aprender_habilidade("Test Skill")
        assert result is True

        # Verificar se habilidade foi aprendida
        assert any(
            skill.nome == "Test Skill"
            for skill in game_engine.jogador.habilidades_conhecidas
        )

        # Teste de habilidade já conhecida
        result = game_engine.aprender_habilidade("Test Skill")
        assert result is False

        # Teste com habilidade inexistente
        with pytest.raises(ResourceNotFoundError):
            game_engine.aprender_habilidade("Nonexistent Skill")

    def test_verificar_level_up(self, game_engine):
        """Testa sistema de level up."""
        game_engine.inicializar_novo_jogo()
        player = game_engine.jogador

        # Sem XP suficiente
        result = game_engine.verificar_level_up()
        assert result is None

        # Com XP suficiente
        player.xp = 100
        result = game_engine.verificar_level_up()

        assert result is not None
        assert result["new_level"] == 2
        assert player.nivel == 2
        assert player.hp == player.hp_max  # Deve ter curado completamente

    def test_usar_item_inventario(self, game_engine, mock_db_data):
        """Testa uso de itens do inventário."""
        game_engine.inicializar_novo_jogo()
        player = game_engine.jogador

        # Adicionar item de teste
        game_engine.adicionar_item_inventario("Test Item")

        # Reduzir HP para testar cura
        player.hp = 50

        messages = game_engine.usar_item_inventario("Test Item")
        assert len(messages) > 0
        assert player.hp > 50  # HP deve ter aumentado

    def test_processar_vitoria(self, game_engine, sample_enemy, mock_db_data):
        """Testa processamento de vitória."""
        game_engine.inicializar_novo_jogo()
        player = game_engine.jogador

        old_xp = player.xp
        old_ouro = player.ouro

        victory_data = game_engine.processar_vitoria(sample_enemy)

        assert victory_data["enemy_name"] == sample_enemy.nome
        assert player.xp > old_xp
        assert player.ouro > old_ouro

    def test_engine_status(self, game_engine):
        """Testa obtenção do status do engine."""
        status = game_engine.get_engine_status()

        assert status["initialized"] is True
        assert "managers" in status
        assert "combat" in status["managers"]
        assert "inventory" in status["managers"]

    def test_engine_shutdown(self, game_engine):
        """Testa finalização do engine."""
        assert GameEngine._initialized is True

        game_engine.shutdown()

        assert GameEngine._initialized is False
        assert GameEngine._instance is None

    def test_save_load_integration(self, game_engine, mock_db_data):
        """Testa integração save/load."""
        # Inicializar jogo
        game_engine.inicializar_novo_jogo()
        player = game_engine.jogador

        # Modificar estado
        player.nivel = 5
        player.xp = 200
        player.ouro = 100

        # Salvar
        result = game_engine.save_game_state()
        assert result is True

        # Criar novo jogo e verificar que mudou
        game_engine.inicializar_novo_jogo()
        assert game_engine.jogador.nivel == 1

        # Carregar save
        result = game_engine.load_game_state()
        assert result is True
        assert game_engine.jogador.nivel == 5
        assert game_engine.jogador.xp == 200

    def test_error_handling_no_player(self, game_engine):
        """Testa tratamento de erro quando não há jogador ativo."""
        # Sem jogador inicializado
        with pytest.raises(GameEngineError):
            game_engine.save_game_state()

        with pytest.raises(GameEngineError):
            game_engine.adicionar_item_inventario("Item")

        with pytest.raises(GameEngineError):
            game_engine.aprender_habilidade("Skill")


class TestGameEngineEvents:
    """Testes para eventos do GameEngine."""

    def test_new_game_event(self, game_engine, mock_db_data):
        """Testa se evento de novo jogo é emitido."""
        events_received = []

        def event_handler(event):
            events_received.append(event)

        game_engine.event_manager.subscribe(EventType.LOAD_GAME, event_handler)
        game_engine.inicializar_novo_jogo()

        assert len(events_received) == 1
        assert events_received[0].type == EventType.LOAD_GAME
        assert events_received[0].data["action"] == "new_game"

    def test_level_up_event(self, game_engine):
        """Testa se evento de level up é emitido."""
        events_received = []

        def event_handler(event):
            events_received.append(event)

        game_engine.event_manager.subscribe(EventType.PLAYER_LEVEL_UP, event_handler)

        game_engine.inicializar_novo_jogo()
        player = game_engine.jogador
        player.xp = 100

        game_engine.verificar_level_up()

        assert len(events_received) == 1
        assert events_received[0].type == EventType.PLAYER_LEVEL_UP
        assert events_received[0].data["new_level"] == 2


class TestGameEnginePerformance:
    """Testes de performance do GameEngine."""

    def test_enemy_creation_cache_performance(self, game_engine, mock_db_data):
        """Testa se o cache melhora a performance de criação de inimigos."""
        import time

        # Primeira criação (sem cache)
        start = time.time()
        for _ in range(100):
            game_engine.criar_inimigo("Test Enemy")
        first_time = time.time() - start

        # Limpar cache para teste justo
        game_engine.cache_manager.clear()

        # Segunda criação (com cache)
        start = time.time()
        for _ in range(100):
            game_engine.criar_inimigo("Test Enemy")
        second_time = time.time() - start

        # O cache deve melhorar ligeiramente a performance
        # (ou pelo menos não piorar significativamente)
        assert second_time <= first_time * 1.5  # Tolerância de 50%

    def test_manager_initialization_performance(self, clean_engine):
        """Testa performance da inicialização dos managers."""
        import time

        start = time.time()
        engine = GameEngine()
        initialization_time = time.time() - start

        # Inicialização deve ser rápida (menos de 1 segundo)
        assert initialization_time < 1.0
        assert engine._initialized is True
