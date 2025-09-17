"""
Sistema de carregamento de dados JSON para o jogo ZORG.
Mantém compatibilidade com o sistema Python existente.
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from copy import deepcopy

from core.models import Personagem, Item, Habilidade, TipoHabilidade, Equipamento, TipoEquipamento
from utils.logging_config import get_logger

logger = get_logger("data_loaders")


class DataLoader:
    """Carregador centralizado de dados JSON."""

    def __init__(self):
        self.data_dir = Path(__file__).parent / "json"
        self._cache = {}

    def _load_json_file(self, filename: str) -> Dict[str, Any]:
        """Carrega um arquivo JSON com cache."""
        if filename in self._cache:
            return self._cache[filename]

        file_path = self.data_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._cache[filename] = data
                logger.debug(f"Loaded JSON data from {filename}")
                return data
        except FileNotFoundError:
            logger.error(f"JSON file not found: {filename}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file {filename}: {e}")
            return {}

    def load_enemies(self) -> Dict[str, Personagem]:
        """Carrega inimigos do JSON e converte para objetos Personagem."""
        json_data = self._load_json_file("enemies.json")
        enemies = {}

        for enemy_id, enemy_data in json_data.get("enemies", {}).items():
            try:
                # Converter habilidades conhecidas
                habilidades = []
                for skill_name in enemy_data.get("habilidades_conhecidas", []):
                    # Importação tardia para evitar dependência circular
                    from data.abilities import DB_HABILIDADES
                    if skill_name in DB_HABILIDADES:
                        habilidades.append(DB_HABILIDADES[skill_name])

                enemy = Personagem(
                    nome=enemy_data["nome"],
                    hp_max=enemy_data["hp_max"],
                    mp_max=enemy_data["mp_max"],
                    ataque_base=enemy_data["ataque_base"],
                    defesa_base=enemy_data["defesa_base"],
                    xp_dado=enemy_data["xp_dado"],
                    ouro_dado=enemy_data["ouro_dado"],
                    dano_por_turno_veneno=enemy_data.get("dano_por_turno_veneno", 0),
                    habilidades_conhecidas=habilidades
                )

                enemies[enemy_id] = enemy

            except Exception as e:
                logger.error(f"Error creating enemy {enemy_id}: {e}")

        logger.info(f"Loaded {len(enemies)} enemies from JSON")
        return enemies

    def load_items(self) -> Dict[str, Item]:
        """Carrega itens do JSON e converte para objetos Item."""
        json_data = self._load_json_file("items.json")
        items = {}

        for item_id, item_data in json_data.get("items", {}).items():
            try:
                item = Item(
                    nome=item_data["nome"],
                    descricao=item_data["descricao"],
                    cura_hp=item_data["cura_hp"],
                    cura_mp=item_data["cura_mp"],
                    cura_veneno=item_data["cura_veneno"],
                    preco_venda=item_data["preco_venda"],
                    stack_max=item_data.get("stack_max", 99),
                    categoria=item_data.get("tipo", "consumível")
                )

                # Adicionar propriedades extras do JSON
                item.tipo = item_data.get("tipo", "Consumível")
                item.rarity = item_data.get("rarity", "common")
                item.effects = item_data.get("effects", [])
                item.valor_cura = item_data["cura_hp"]  # Alias para compatibilidade
                item.valor_mp = item_data["cura_mp"]    # Alias para compatibilidade

                items[item_id] = item

            except Exception as e:
                logger.error(f"Error creating item {item_id}: {e}")

        logger.info(f"Loaded {len(items)} items from JSON")
        return items

    def load_abilities(self) -> Dict[str, Habilidade]:
        """Carrega habilidades do JSON e converte para objetos Habilidade."""
        json_data = self._load_json_file("abilities.json")
        abilities = {}

        for ability_id, ability_data in json_data.get("abilities", {}).items():
            try:
                # Converter tipo de string para enum
                tipo_map = {
                    "ataque": TipoHabilidade.ATAQUE,
                    "cura": TipoHabilidade.CURA,
                    "buff_defesa": TipoHabilidade.BUFF_DEFESA,
                    "buff_ataque": TipoHabilidade.BUFF_ATAQUE,
                    "debuff": TipoHabilidade.DEBUFF,
                    "furia": TipoHabilidade.FURIA,
                    "regeneracao": TipoHabilidade.REGENERACAO,
                    "combo": TipoHabilidade.COMBO,
                }

                ability = Habilidade(
                    nome=ability_data["nome"],
                    descricao=ability_data["descricao"],
                    custo_mp=ability_data["custo_mp"],
                    tipo=tipo_map.get(ability_data["tipo"], TipoHabilidade.ATAQUE),
                    valor_efeito=ability_data["valor_efeito"],
                    cooldown=ability_data.get("cooldown", 0),
                    nivel_requerido=ability_data.get("nivel_requerido", 1),
                    elemento=ability_data.get("elemento", "neutro")
                )

                # Adicionar propriedades extras do JSON
                ability.rarity = ability_data.get("rarity", "common")
                ability.effects = ability_data.get("effects", [])
                ability.target_type = ability_data.get("target_type", "single_enemy")

                abilities[ability_id] = ability

            except Exception as e:
                logger.error(f"Error creating ability {ability_id}: {e}")

        logger.info(f"Loaded {len(abilities)} abilities from JSON")
        return abilities

    def load_equipment(self) -> Dict[str, Equipamento]:
        """Carrega equipamentos do JSON e converte para objetos Equipamento."""
        json_data = self._load_json_file("equipment.json")
        equipment = {}

        for equip_id, equip_data in json_data.get("equipment", {}).items():
            try:
                # Converter tipo de string para enum
                tipo_map = {
                    "arma": TipoEquipamento.ARMA,
                    "armadura": TipoEquipamento.ARMADURA,
                    "escudo": TipoEquipamento.ESCUDO,
                    "acessorio": TipoEquipamento.ACESSORIO
                }

                equip = Equipamento(
                    nome=equip_data["nome"],
                    tipo=tipo_map.get(equip_data["tipo"], TipoEquipamento.ARMA),
                    bonus_ataque=equip_data["bonus_ataque"],
                    bonus_defesa=equip_data["bonus_defesa"],
                    descricao=equip_data["descricao"],
                    preco=equip_data["preco"],
                    raridade=equip_data["raridade"]
                )

                # Adicionar propriedades extras do JSON
                equip.durabilidade = equip_data.get("durabilidade", 100)
                equip.special_effects = equip_data.get("special_effects", [])
                equip.requirements = equip_data.get("requirements", {})

                equipment[equip_id] = equip

            except Exception as e:
                logger.error(f"Error creating equipment {equip_id}: {e}")

        logger.info(f"Loaded {len(equipment)} equipment items from JSON")
        return equipment

    def load_phases(self) -> Dict[str, Dict[str, Any]]:
        """Carrega estrutura das fases do JSON."""
        json_data = self._load_json_file("phases.json")
        phases = json_data.get("phases", {})
        logger.info(f"Loaded {len(phases)} phases from JSON")
        return phases

    def load_npcs(self) -> Dict[str, Dict[str, Any]]:
        """Carrega NPCs do JSON."""
        json_data = self._load_json_file("npcs.json")
        npcs = json_data.get("npcs", {})
        logger.info(f"Loaded {len(npcs)} NPCs from JSON")
        return npcs

    def reload_data(self):
        """Recarrega todos os dados, útil para desenvolvimento."""
        self._cache.clear()
        logger.info("Data cache cleared, will reload on next access")


# Instância global do loader
_data_loader = DataLoader()


def get_data_loader() -> DataLoader:
    """Retorna a instância global do data loader."""
    return _data_loader


def create_hybrid_databases():
    """
    Cria versões híbridas dos bancos de dados que combinam JSON e Python.
    Permite migração gradual dos dados.
    """
    # Carregar dados JSON
    json_enemies = _data_loader.load_enemies()
    json_items = _data_loader.load_items()
    json_abilities = _data_loader.load_abilities()
    json_equipment = _data_loader.load_equipment()

    # Importar dados Python existentes
    try:
        from data.enemies import DB_INIMIGOS as python_enemies
        from data.items import DB_ITENS as python_items
        from data.abilities import DB_HABILIDADES as python_abilities
        from data.equipment import DB_EQUIPAMENTOS as python_equipment
    except ImportError:
        python_enemies = {}
        python_items = {}
        python_abilities = {}
        python_equipment = {}

    # Criar bancos híbridos (JSON tem prioridade)
    hybrid_enemies = {**python_enemies, **json_enemies}
    hybrid_items = {**python_items, **json_items}
    hybrid_abilities = {**python_abilities, **json_abilities}
    hybrid_equipment = {**python_equipment, **json_equipment}

    logger.info(f"Created hybrid databases: {len(hybrid_enemies)} enemies, "
                f"{len(hybrid_items)} items, {len(hybrid_abilities)} abilities, "
                f"{len(hybrid_equipment)} equipment")

    return hybrid_enemies, hybrid_items, hybrid_abilities, hybrid_equipment


def get_hybrid_enemy_db() -> Dict[str, Personagem]:
    """Retorna banco híbrido de inimigos."""
    hybrid_enemies, _, _, _ = create_hybrid_databases()
    return hybrid_enemies


def get_hybrid_item_db() -> Dict[str, Item]:
    """Retorna banco híbrido de itens."""
    _, hybrid_items, _, _ = create_hybrid_databases()
    return hybrid_items


def get_hybrid_ability_db() -> Dict[str, Habilidade]:
    """Retorna banco híbrido de habilidades."""
    _, _, hybrid_abilities, _ = create_hybrid_databases()
    return hybrid_abilities


def get_hybrid_equipment_db() -> Dict[str, Equipamento]:
    """Retorna banco híbrido de equipamentos."""
    _, _, _, hybrid_equipment = create_hybrid_databases()
    return hybrid_equipment


def get_phases_data() -> Dict[str, Dict[str, Any]]:
    """Retorna dados das fases do JSON."""
    return _data_loader.load_phases()


def get_npcs_data() -> Dict[str, Dict[str, Any]]:
    """Retorna dados dos NPCs do JSON."""
    return _data_loader.load_npcs()


# Validação de dados JSON
def validate_json_data():
    """Valida a integridade dos dados JSON."""
    loader = get_data_loader()
    errors = []

    # Validar inimigos
    try:
        enemies = loader.load_enemies()
        for enemy_name, enemy in enemies.items():
            if enemy.hp_max <= 0:
                errors.append(f"Enemy {enemy_name} has invalid HP: {enemy.hp_max}")
            if enemy.ataque_base < 0:
                errors.append(f"Enemy {enemy_name} has invalid attack: {enemy.ataque_base}")
    except Exception as e:
        errors.append(f"Error validating enemies: {e}")

    # Validar itens
    try:
        items = loader.load_items()
        for item_name, item in items.items():
            if item.cura_hp < 0:
                errors.append(f"Item {item_name} has invalid HP healing: {item.cura_hp}")
            if item.preco_venda < 0:
                errors.append(f"Item {item_name} has invalid sell price: {item.preco_venda}")
    except Exception as e:
        errors.append(f"Error validating items: {e}")

    # Validar habilidades
    try:
        abilities = loader.load_abilities()
        for ability_name, ability in abilities.items():
            if ability.custo_mp < 0:
                errors.append(f"Ability {ability_name} has invalid MP cost: {ability.custo_mp}")
            if ability.nivel_requerido <= 0:
                errors.append(f"Ability {ability_name} has invalid level requirement: {ability.nivel_requerido}")
    except Exception as e:
        errors.append(f"Error validating abilities: {e}")

    # Validar equipamentos
    try:
        equipment = loader.load_equipment()
        for equip_name, equip in equipment.items():
            if equip.bonus_ataque < 0:
                errors.append(f"Equipment {equip_name} has invalid attack bonus: {equip.bonus_ataque}")
            if equip.bonus_defesa < 0:
                errors.append(f"Equipment {equip_name} has invalid defense bonus: {equip.bonus_defesa}")
            if equip.preco < 0:
                errors.append(f"Equipment {equip_name} has invalid price: {equip.preco}")
    except Exception as e:
        errors.append(f"Error validating equipment: {e}")

    if errors:
        logger.error(f"JSON data validation failed with {len(errors)} errors:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    else:
        logger.info("JSON data validation passed successfully")
        return True


if __name__ == "__main__":
    # Executar validação quando o módulo for executado diretamente
    validate_json_data()