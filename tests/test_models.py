"""
Testes para os modelos do jogo ZORG.
"""
import pytest
from core.models import (
    Personagem, Item, Equipamento, Habilidade, TutorialFlags,
    TipoEquipamento, TipoHabilidade
)
from core.exceptions import CharacterStateError


class TestPersonagem:
    """Testes para a classe Personagem."""

    def test_personagem_creation(self):
        """Testa a criação de um personagem."""
        player = Personagem(
            nome="TestPlayer",
            hp_max=100,
            mp_max=50,
            ataque_base=10,
            defesa_base=5
        )

        assert player.nome == "TestPlayer"
        assert player.hp == 100  # HP inicializado com máximo
        assert player.mp == 50   # MP inicializado com máximo
        assert player.ataque_base == 10
        assert player.defesa_base == 5
        assert player.nivel == 1
        assert player.is_alive

    def test_personagem_invalid_values(self):
        """Testa criação com valores inválidos."""
        with pytest.raises(ValueError):
            Personagem(
                nome="",
                hp_max=100,
                mp_max=50,
                ataque_base=10,
                defesa_base=5
            )

        with pytest.raises(ValueError):
            Personagem(
                nome="Test",
                hp_max=-10,  # Inválido
                mp_max=50,
                ataque_base=10,
                defesa_base=5
            )

    def test_ataque_total_calculation(self, sample_player, sample_equipment):
        """Testa cálculo de ataque total."""
        assert sample_player.ataque_total == 10  # Sem equipamento

        sample_player.arma_equipada = sample_equipment
        assert sample_player.ataque_total == 15  # Com equipamento (+5)

    def test_defesa_total_calculation(self, sample_player):
        """Testa cálculo de defesa total."""
        assert sample_player.defesa_total == 5  # Sem equipamento

        # Com buff de defesa
        sample_player.turnos_buff_defesa = 3
        assert sample_player.defesa_total == 10  # +5 por buff

    def test_heal_method(self, sample_player):
        """Testa método de cura."""
        sample_player.hp = 50  # HP parcial

        healed = sample_player.heal(30)
        assert healed == 30
        assert sample_player.hp == 80

        # Teste de cura excessiva
        healed = sample_player.heal(50)
        assert healed == 20  # Só curou até o máximo
        assert sample_player.hp == 100

    def test_heal_dead_character(self, sample_player):
        """Testa cura em personagem morto."""
        sample_player.hp = 0
        with pytest.raises(CharacterStateError):
            sample_player.heal(50)

    def test_take_damage(self, sample_player):
        """Testa aplicação de dano."""
        damage_dealt = sample_player.take_damage(30)
        assert damage_dealt == 30
        assert sample_player.hp == 70

        # Teste de dano letal
        damage_dealt = sample_player.take_damage(100)
        assert damage_dealt == 70  # Só tinha 70 HP
        assert sample_player.hp == 0
        assert sample_player.is_dead

    def test_spend_mp(self, sample_player):
        """Testa gasto de MP."""
        assert sample_player.spend_mp(20) == True
        assert sample_player.mp == 30

        # Teste de MP insuficiente
        assert sample_player.spend_mp(40) == False
        assert sample_player.mp == 30  # Não mudou

    def test_inventory_operations(self, sample_player, sample_item):
        """Testa operações de inventário."""
        # Adicionar item
        assert sample_player.add_item_to_inventory(sample_item) == True
        assert len(sample_player.inventario) == 1

        # Verificar se tem item
        assert sample_player.has_item("Test Potion") == True
        assert sample_player.has_item("Nonexistent Item") == False

        # Remover item
        assert sample_player.remove_item_from_inventory("Test Potion") == True
        assert len(sample_player.inventario) == 0

    def test_skill_operations(self, sample_player, sample_skill):
        """Testa operações com habilidades."""
        sample_player.habilidades_conhecidas.append(sample_skill)

        assert sample_player.knows_skill("Test Heal") == True
        assert sample_player.can_use_skill(sample_skill) == True

        # Teste com MP insuficiente
        sample_player.mp = 5
        assert sample_player.can_use_skill(sample_skill) == False

    def test_status_effects_processing(self, sample_player):
        """Testa processamento de efeitos de status."""
        # Aplicar veneno
        sample_player.turnos_veneno = 2
        sample_player.dano_por_turno_veneno = 5

        messages = sample_player.process_status_effects()
        assert len(messages) > 0
        assert sample_player.hp == 95  # Perdeu 5 HP
        assert sample_player.turnos_veneno == 1

        # Segundo turno
        messages = sample_player.process_status_effects()
        assert sample_player.hp == 90
        assert sample_player.turnos_veneno == 0

    def test_get_stats_summary(self, sample_player):
        """Testa resumo de estatísticas."""
        stats = sample_player.get_stats_summary()

        assert stats["nome"] == "TestPlayer"
        assert stats["nivel"] == 1
        assert stats["hp"] == "100/100"
        assert stats["mp"] == "50/50"
        assert "status_effects" in stats


class TestItem:
    """Testes para a classe Item."""

    def test_item_creation(self, sample_item):
        """Testa criação de item."""
        assert sample_item.nome == "Test Potion"
        assert sample_item.cura_hp == 25
        assert sample_item.quantidade == 1

    def test_item_stacking(self):
        """Testa empilhamento de itens."""
        item1 = Item(
            nome="Potion",
            descricao="Test",
            cura_hp=10,
            cura_mp=0,
            cura_veneno=0,
            preco_venda=5,
            quantidade=5
        )

        item2 = Item(
            nome="Potion",
            descricao="Test",
            cura_hp=10,
            cura_mp=0,
            cura_veneno=0,
            preco_venda=5,
            quantidade=3
        )

        assert item1.can_stack_with(item2) == True
        assert item1.add_quantity(3) == True
        assert item1.quantidade == 8

    def test_item_validation(self):
        """Testa validação de item."""
        with pytest.raises(ValueError):
            Item(
                nome="",  # Nome vazio
                descricao="Test",
                cura_hp=10,
                cura_mp=0,
                cura_veneno=0,
                preco_venda=5
            )


class TestEquipamento:
    """Testes para a classe Equipamento."""

    def test_equipamento_creation(self, sample_equipment):
        """Testa criação de equipamento."""
        assert sample_equipment.nome == "Test Sword"
        assert sample_equipment.tipo == TipoEquipamento.ARMA
        assert sample_equipment.is_weapon == True
        assert sample_equipment.is_armor == False

    def test_equipamento_types(self):
        """Testa diferentes tipos de equipamento."""
        armor = Equipamento(
            nome="Test Armor",
            tipo=TipoEquipamento.ARMADURA,
            bonus_ataque=0,
            bonus_defesa=5
        )

        assert armor.is_armor == True
        assert armor.is_weapon == False
        assert armor.is_shield == False

    def test_equipamento_validation(self):
        """Testa validação de equipamento."""
        with pytest.raises(ValueError):
            Equipamento(
                nome="Test",
                tipo=TipoEquipamento.ARMA,
                bonus_ataque=-5,  # Inválido
                bonus_defesa=0
            )


class TestHabilidade:
    """Testes para a classe Habilidade."""

    def test_habilidade_creation(self, sample_skill):
        """Testa criação de habilidade."""
        assert sample_skill.nome == "Test Heal"
        assert sample_skill.tipo == TipoHabilidade.CURA
        assert sample_skill.is_defensive == True
        assert sample_skill.is_offensive == False

    def test_habilidade_types(self):
        """Testa diferentes tipos de habilidade."""
        attack_skill = Habilidade(
            nome="Test Attack",
            descricao="Ataque de teste",
            custo_mp=15,
            tipo=TipoHabilidade.ATAQUE,
            valor_efeito=20
        )

        assert attack_skill.is_offensive == True
        assert attack_skill.is_defensive == False

    def test_habilidade_validation(self):
        """Testa validação de habilidade."""
        with pytest.raises(ValueError):
            Habilidade(
                nome="Test",
                descricao="Test",
                custo_mp=-5,  # Inválido
                tipo=TipoHabilidade.ATAQUE,
                valor_efeito=10
            )


class TestTutorialFlags:
    """Testes para a classe TutorialFlags."""

    def test_tutorial_flags_creation(self):
        """Testa criação de flags de tutorial."""
        flags = TutorialFlags()
        assert flags.combate_basico_mostrado == False
        assert flags.habilidades_mostrado == False

    def test_tutorial_flags_dict_conversion(self):
        """Testa conversão para/de dicionário."""
        flags = TutorialFlags(combate_basico_mostrado=True)
        data = flags.to_dict()

        assert data["combate_basico_mostrado"] == True
        assert data["habilidades_mostrado"] == False

        # Teste de recriação
        new_flags = TutorialFlags.from_dict(data)
        assert new_flags.combate_basico_mostrado == True
        assert new_flags.habilidades_mostrado == False