"""
Configurações e fixtures compartilhadas para os testes do ZORG.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest

from core.engine import GameEngine
from core.managers.event_manager import get_event_manager
from core.models import (
    Equipamento,
    Habilidade,
    Item,
    Personagem,
    TipoEquipamento,
    TipoHabilidade,
)


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Cria um diretório temporário para os testes."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def mock_save_dir(temp_dir: Path):
    """Mock do diretório de save."""
    with patch("config.settings.get_save_path") as mock_path:
        save_file = temp_dir / "test_save.json"
        mock_path.return_value = save_file
        yield save_file


@pytest.fixture(scope="function")
def clean_engine():
    """Fixture que reseta o GameEngine entre os testes."""
    # Reset do singleton
    if hasattr(GameEngine, "_instance"):
        engine = GameEngine._instance
        if engine:
            engine.shutdown()
        GameEngine._instance = None
        GameEngine._initialized = False

    yield

    # Cleanup após o teste
    if hasattr(GameEngine, "_instance") and GameEngine._instance:
        GameEngine._instance.shutdown()
        GameEngine._instance = None
        GameEngine._initialized = False


@pytest.fixture
def sample_player() -> Personagem:
    """Cria um jogador de exemplo para testes."""
    player = Personagem(
        nome="TestPlayer", hp_max=100, mp_max=50, ataque_base=10, defesa_base=5
    )
    return player


@pytest.fixture
def sample_enemy() -> Personagem:
    """Cria um inimigo de exemplo para testes."""
    enemy = Personagem(
        nome="TestEnemy",
        hp_max=80,
        mp_max=30,
        ataque_base=8,
        defesa_base=3,
        xp_dado=50,
        ouro_dado=25,
    )
    return enemy


@pytest.fixture
def sample_item() -> Item:
    """Cria um item de exemplo para testes."""
    return Item(
        nome="Test Potion",
        descricao="Um item de teste",
        cura_hp=25,
        cura_mp=0,
        cura_veneno=0,
        preco_venda=10,
    )


@pytest.fixture
def sample_equipment() -> Equipamento:
    """Cria um equipamento de exemplo para testes."""
    return Equipamento(
        nome="Test Sword",
        tipo=TipoEquipamento.ARMA,
        bonus_ataque=5,
        bonus_defesa=0,
        descricao="Uma espada de teste",
    )


@pytest.fixture
def sample_skill() -> Habilidade:
    """Cria uma habilidade de exemplo para testes."""
    return Habilidade(
        nome="Test Heal",
        descricao="Uma habilidade de cura de teste",
        custo_mp=10,
        tipo=TipoHabilidade.CURA,
        valor_efeito=30,
    )


@pytest.fixture(scope="function")
def game_engine(clean_engine, mock_save_dir):
    """Cria uma instância limpa do GameEngine para testes."""
    engine = GameEngine()
    return engine


@pytest.fixture(autouse=True)
def reset_event_manager():
    """Reseta o gerenciador de eventos entre os testes."""
    event_manager = get_event_manager()
    event_manager.clear_history()
    # Limpar todos os handlers
    event_manager._handlers.clear()
    yield
    event_manager.clear_history()
    event_manager._handlers.clear()


@pytest.fixture
def mock_db_data():
    """Mock dos bancos de dados do jogo."""
    mock_items = {
        "Test Item": Item(
            nome="Test Item",
            descricao="Item para teste",
            cura_hp=20,
            cura_mp=0,
            cura_veneno=0,
            preco_venda=5,
        )
    }

    mock_equipment = {
        "Test Weapon": Equipamento(
            nome="Test Weapon",
            tipo=TipoEquipamento.ARMA,
            bonus_ataque=3,
            bonus_defesa=0,
        )
    }

    mock_skills = {
        "Test Skill": Habilidade(
            nome="Test Skill",
            descricao="Habilidade de teste",
            custo_mp=5,
            tipo=TipoHabilidade.ATAQUE,
            valor_efeito=15,
        )
    }

    mock_enemies = {
        "Test Enemy": Personagem(
            nome="Test Enemy",
            hp_max=50,
            mp_max=20,
            ataque_base=6,
            defesa_base=2,
            xp_dado=30,
            ouro_dado=15,
        )
    }

    with patch("data.items.DB_ITENS", mock_items), patch(
        "data.equipment.DB_EQUIPAMENTOS", mock_equipment
    ), patch("data.abilities.DB_HABILIDADES", mock_skills), patch(
        "data.enemies.DB_INIMIGOS", mock_enemies
    ):
        yield {
            "items": mock_items,
            "equipment": mock_equipment,
            "skills": mock_skills,
            "enemies": mock_enemies,
        }
