"""
Sistema de crafting/melhoramento de equipamentos para o jogo ZORG.
Permite que jogadores aprimorem suas armas e armaduras usando materiais coletados.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random

from core.managers.base_manager import BaseManager
from core.models import Equipamento, Item
from core.elemental_system import Element
from utils.logging_config import get_logger

logger = get_logger("crafting_manager")


class MaterialType(Enum):
    COMMON_METAL = "common_metal"
    RARE_METAL = "rare_metal"
    PRECIOUS_METAL = "precious_metal"
    MAGIC_CRYSTAL = "magic_crystal"
    ELEMENTAL_ESSENCE = "elemental_essence"
    MONSTER_PART = "monster_part"
    ANCIENT_RUNE = "ancient_rune"


class CraftingCategory(Enum):
    WEAPON_UPGRADE = "weapon_upgrade"
    ARMOR_UPGRADE = "armor_upgrade"
    ENCHANTMENT = "enchantment"
    REPAIR = "repair"
    FUSION = "fusion"


@dataclass
class CraftingMaterial:
    """Material usado no crafting."""
    name: str
    material_type: MaterialType
    description: str
    rarity: str
    value: int = 0
    element: Optional[Element] = None
    special_properties: List[str] = None

    def __post_init__(self):
        if self.special_properties is None:
            self.special_properties = []


@dataclass
class CraftingRecipe:
    """Receita de crafting."""
    id: str
    name: str
    description: str
    category: CraftingCategory
    required_materials: Dict[str, int]  # material_name: quantity
    required_gold: int
    required_level: int
    success_chance: float
    output_item: Optional[str] = None
    upgrade_bonus: Dict[str, int] = None
    special_effects: List[str] = None

    def __post_init__(self):
        if self.upgrade_bonus is None:
            self.upgrade_bonus = {}
        if self.special_effects is None:
            self.special_effects = []


@dataclass
class CraftingResult:
    """Resultado de uma operação de crafting."""
    success: bool
    message: str
    item_created: Optional[Any] = None
    item_modified: Optional[Any] = None
    materials_consumed: Dict[str, int] = None
    gold_spent: int = 0
    experience_gained: int = 0

    def __post_init__(self):
        if self.materials_consumed is None:
            self.materials_consumed = {}


class CraftingManager(BaseManager):
    """Gerenciador do sistema de crafting."""

    def __init__(self):
        super().__init__("crafting_manager")
        self.materials = self._initialize_materials()
        self.recipes = self._initialize_recipes()
        self.player_materials = {}  # player_id: {material_name: quantity}

    def _initialize_materials(self) -> Dict[str, CraftingMaterial]:
        """Inicializa materiais de crafting."""
        materials = {}

        # Metais comuns
        materials["ferro_bruto"] = CraftingMaterial(
            name="Ferro Bruto",
            material_type=MaterialType.COMMON_METAL,
            description="Metal básico encontrado em minas. Útil para melhorias simples.",
            rarity="common",
            value=10
        )

        materials["aco_refinado"] = CraftingMaterial(
            name="Aço Refinado",
            material_type=MaterialType.RARE_METAL,
            description="Metal de alta qualidade, forjado com técnicas avançadas.",
            rarity="uncommon",
            value=50
        )

        materials["mithril"] = CraftingMaterial(
            name="Mithril",
            material_type=MaterialType.PRECIOUS_METAL,
            description="Metal élfico lendário, leve como uma pluma mas forte como diamante.",
            rarity="rare",
            value=200
        )

        # Cristais mágicos
        materials["cristal_menor"] = CraftingMaterial(
            name="Cristal Menor",
            material_type=MaterialType.MAGIC_CRYSTAL,
            description="Cristal que pulsa com energia mágica fraca.",
            rarity="common",
            value=25
        )

        materials["cristal_maior"] = CraftingMaterial(
            name="Cristal Maior",
            material_type=MaterialType.MAGIC_CRYSTAL,
            description="Cristal radiante com poder mágico considerável.",
            rarity="rare",
            value=150
        )

        # Essências elementais
        materials["essencia_fogo"] = CraftingMaterial(
            name="Essência de Fogo",
            material_type=MaterialType.ELEMENTAL_ESSENCE,
            description="Energia ígnea condensada, quente ao toque.",
            rarity="uncommon",
            value=75,
            element=Element.FOGO,
            special_properties=["fire_enchantment", "burn_chance"]
        )

        materials["essencia_gelo"] = CraftingMaterial(
            name="Essência de Gelo",
            material_type=MaterialType.ELEMENTAL_ESSENCE,
            description="Energia glacial cristalizada, fria como o vazio.",
            rarity="uncommon",
            value=75,
            element=Element.GELO,
            special_properties=["ice_enchantment", "slow_chance"]
        )

        materials["essencia_sombra"] = CraftingMaterial(
            name="Essência de Sombra",
            material_type=MaterialType.ELEMENTAL_ESSENCE,
            description="Fragmento das trevas, absorve a luz ao redor.",
            rarity="rare",
            value=100,
            element=Element.SOMBRA,
            special_properties=["shadow_enchantment", "critical_boost"]
        )

        # Partes de monstros
        materials["garra_lobo"] = CraftingMaterial(
            name="Garra de Lobo das Sombras",
            material_type=MaterialType.MONSTER_PART,
            description="Garra afiada de um predador sombrio.",
            rarity="common",
            value=30,
            special_properties=["sharpness", "agility_boost"]
        )

        materials["escama_dragao"] = CraftingMaterial(
            name="Escama de Dragão",
            material_type=MaterialType.MONSTER_PART,
            description="Escama quase indestrutível de um dragão antigo.",
            rarity="legendary",
            value=500,
            special_properties=["fire_resistance", "defense_boost", "intimidation"]
        )

        # Runas antigas
        materials["runa_poder"] = CraftingMaterial(
            name="Runa do Poder",
            material_type=MaterialType.ANCIENT_RUNE,
            description="Símbolo antigo que amplifica força física.",
            rarity="rare",
            value=180,
            special_properties=["attack_boost", "strength_enhancement"]
        )

        materials["runa_protecao"] = CraftingMaterial(
            name="Runa da Proteção",
            material_type=MaterialType.ANCIENT_RUNE,
            description="Símbolo antigo que oferece proteção divina.",
            rarity="rare",
            value=180,
            special_properties=["defense_boost", "magic_resistance"]
        )

        return materials

    def _initialize_recipes(self) -> Dict[str, CraftingRecipe]:
        """Inicializa receitas de crafting."""
        recipes = {}

        # Melhorias de arma - Nível 1
        recipes["weapon_upgrade_1"] = CraftingRecipe(
            id="weapon_upgrade_1",
            name="Melhoramento de Arma +1",
            description="Melhora básica que aumenta o poder de ataque da arma.",
            category=CraftingCategory.WEAPON_UPGRADE,
            required_materials={"ferro_bruto": 2, "cristal_menor": 1},
            required_gold=100,
            required_level=3,
            success_chance=0.9,
            upgrade_bonus={"bonus_ataque": 2}
        )

        # Melhorias de arma - Nível 2
        recipes["weapon_upgrade_2"] = CraftingRecipe(
            id="weapon_upgrade_2",
            name="Melhoramento de Arma +2",
            description="Melhoria avançada que aumenta significativamente o poder de ataque.",
            category=CraftingCategory.WEAPON_UPGRADE,
            required_materials={"aco_refinado": 1, "cristal_maior": 1, "garra_lobo": 2},
            required_gold=250,
            required_level=5,
            success_chance=0.75,
            upgrade_bonus={"bonus_ataque": 5}
        )

        # Melhorias de armadura - Nível 1
        recipes["armor_upgrade_1"] = CraftingRecipe(
            id="armor_upgrade_1",
            name="Melhoramento de Armadura +1",
            description="Melhoria básica que aumenta a proteção da armadura.",
            category=CraftingCategory.ARMOR_UPGRADE,
            required_materials={"ferro_bruto": 3, "cristal_menor": 1},
            required_gold=120,
            required_level=3,
            success_chance=0.85,
            upgrade_bonus={"bonus_defesa": 3}
        )

        # Encantamentos elementais
        recipes["fire_enchantment"] = CraftingRecipe(
            id="fire_enchantment",
            name="Encantamento de Fogo",
            description="Imbui a arma com poder ígneo, causando dano de fogo.",
            category=CraftingCategory.ENCHANTMENT,
            required_materials={"essencia_fogo": 2, "cristal_maior": 1},
            required_gold=300,
            required_level=4,
            success_chance=0.7,
            special_effects=["fire_damage", "burn_chance"]
        )

        recipes["ice_enchantment"] = CraftingRecipe(
            id="ice_enchantment",
            name="Encantamento de Gelo",
            description="Imbui a arma com poder glacial, podendo congelar inimigos.",
            category=CraftingCategory.ENCHANTMENT,
            required_materials={"essencia_gelo": 2, "cristal_maior": 1},
            required_gold=300,
            required_level=4,
            success_chance=0.7,
            special_effects=["ice_damage", "slow_chance"]
        )

        # Reparo de equipamentos
        recipes["basic_repair"] = CraftingRecipe(
            id="basic_repair",
            name="Reparo Básico",
            description="Restaura a durabilidade de um equipamento danificado.",
            category=CraftingCategory.REPAIR,
            required_materials={"ferro_bruto": 1},
            required_gold=50,
            required_level=1,
            success_chance=1.0,
            special_effects=["restore_durability"]
        )

        # Fusão de itens
        recipes["crystal_fusion"] = CraftingRecipe(
            id="crystal_fusion",
            name="Fusão de Cristais",
            description="Combina cristais menores em um cristal maior.",
            category=CraftingCategory.FUSION,
            required_materials={"cristal_menor": 3},
            required_gold=80,
            required_level=2,
            success_chance=0.8,
            output_item="cristal_maior"
        )

        # Receitas lendárias
        recipes["legendary_weapon"] = CraftingRecipe(
            id="legendary_weapon",
            name="Forja Lendária",
            description="Cria uma arma lendária usando materiais raríssimos.",
            category=CraftingCategory.WEAPON_UPGRADE,
            required_materials={"mithril": 2, "escama_dragao": 1, "runa_poder": 1, "cristal_maior": 3},
            required_gold=1000,
            required_level=8,
            success_chance=0.5,
            upgrade_bonus={"bonus_ataque": 15, "bonus_defesa": 5},
            special_effects=["legendary_power", "critical_boost", "intimidation"]
        )

        return recipes

    def get_available_recipes(self, player_level: int) -> List[CraftingRecipe]:
        """Retorna receitas disponíveis para o nível do jogador."""
        return [recipe for recipe in self.recipes.values()
                if recipe.required_level <= player_level]

    def check_recipe_requirements(
        self,
        recipe: CraftingRecipe,
        player_materials: Dict[str, int],
        player_gold: int
    ) -> Tuple[bool, List[str]]:
        """Verifica se o jogador atende aos requisitos da receita."""
        missing_requirements = []

        # Verificar materiais
        for material, required_qty in recipe.required_materials.items():
            current_qty = player_materials.get(material, 0)
            if current_qty < required_qty:
                missing_requirements.append(
                    f"{material}: {required_qty - current_qty} a mais"
                )

        # Verificar ouro
        if player_gold < recipe.required_gold:
            missing_requirements.append(
                f"Ouro: {recipe.required_gold - player_gold} a mais"
            )

        return len(missing_requirements) == 0, missing_requirements

    def craft_item(
        self,
        recipe_id: str,
        player_materials: Dict[str, int],
        player_gold: int,
        target_item: Optional[Any] = None
    ) -> CraftingResult:
        """Executa uma operação de crafting."""
        if recipe_id not in self.recipes:
            return CraftingResult(
                success=False,
                message="Receita não encontrada!"
            )

        recipe = self.recipes[recipe_id]

        # Verificar requisitos
        can_craft, missing = self.check_recipe_requirements(
            recipe, player_materials, player_gold
        )

        if not can_craft:
            return CraftingResult(
                success=False,
                message=f"Requisitos não atendidos: {', '.join(missing)}"
            )

        # Calcular chance de sucesso
        success_roll = random.random()
        crafting_success = success_roll <= recipe.success_chance

        if not crafting_success:
            # Falha - consome apenas metade dos materiais
            consumed_materials = {
                material: qty // 2
                for material, qty in recipe.required_materials.items()
            }
            gold_spent = recipe.required_gold // 2

            return CraftingResult(
                success=False,
                message=f"Crafting falhou! ({success_roll:.2f} > {recipe.success_chance:.2f})",
                materials_consumed=consumed_materials,
                gold_spent=gold_spent,
                experience_gained=10
            )

        # Sucesso - aplicar efeitos da receita
        result = self._apply_crafting_effects(recipe, target_item)
        result.materials_consumed = recipe.required_materials.copy()
        result.gold_spent = recipe.required_gold
        result.experience_gained = self._calculate_xp_reward(recipe)

        return result

    def _apply_crafting_effects(
        self,
        recipe: CraftingRecipe,
        target_item: Optional[Any]
    ) -> CraftingResult:
        """Aplica os efeitos de uma receita de crafting."""

        if recipe.category == CraftingCategory.WEAPON_UPGRADE:
            return self._upgrade_weapon(recipe, target_item)

        elif recipe.category == CraftingCategory.ARMOR_UPGRADE:
            return self._upgrade_armor(recipe, target_item)

        elif recipe.category == CraftingCategory.ENCHANTMENT:
            return self._apply_enchantment(recipe, target_item)

        elif recipe.category == CraftingCategory.REPAIR:
            return self._repair_item(recipe, target_item)

        elif recipe.category == CraftingCategory.FUSION:
            return self._fuse_materials(recipe)

        else:
            return CraftingResult(
                success=False,
                message="Categoria de crafting não implementada!"
            )

    def _upgrade_weapon(self, recipe: CraftingRecipe, weapon: Any) -> CraftingResult:
        """Melhora uma arma."""
        if not weapon:
            return CraftingResult(
                success=False,
                message="Nenhuma arma selecionada para melhoramento!"
            )

        # Aplicar bônus
        for stat, bonus in recipe.upgrade_bonus.items():
            current_value = getattr(weapon, stat, 0)
            setattr(weapon, stat, current_value + bonus)

        # Aplicar efeitos especiais
        if hasattr(weapon, 'special_effects'):
            weapon.special_effects.extend(recipe.special_effects)
        else:
            weapon.special_effects = recipe.special_effects.copy()

        # Aumentar nível de melhoramento
        if not hasattr(weapon, 'upgrade_level'):
            weapon.upgrade_level = 0
        weapon.upgrade_level += 1

        return CraftingResult(
            success=True,
            message=f"{weapon.nome} foi melhorada para nível +{weapon.upgrade_level}!",
            item_modified=weapon
        )

    def _upgrade_armor(self, recipe: CraftingRecipe, armor: Any) -> CraftingResult:
        """Melhora uma armadura."""
        if not armor:
            return CraftingResult(
                success=False,
                message="Nenhuma armadura selecionada para melhoramento!"
            )

        # Aplicar bônus
        for stat, bonus in recipe.upgrade_bonus.items():
            current_value = getattr(armor, stat, 0)
            setattr(armor, stat, current_value + bonus)

        # Aplicar efeitos especiais
        if hasattr(armor, 'special_effects'):
            armor.special_effects.extend(recipe.special_effects)
        else:
            armor.special_effects = recipe.special_effects.copy()

        # Aumentar nível de melhoramento
        if not hasattr(armor, 'upgrade_level'):
            armor.upgrade_level = 0
        armor.upgrade_level += 1

        return CraftingResult(
            success=True,
            message=f"{armor.nome} foi melhorada para nível +{armor.upgrade_level}!",
            item_modified=armor
        )

    def _apply_enchantment(self, recipe: CraftingRecipe, item: Any) -> CraftingResult:
        """Aplica encantamento a um item."""
        if not item:
            return CraftingResult(
                success=False,
                message="Nenhum item selecionado para encantamento!"
            )

        # Verificar se já tem encantamento
        if hasattr(item, 'enchantment') and item.enchantment:
            return CraftingResult(
                success=False,
                message=f"{item.nome} já possui um encantamento!"
            )

        # Aplicar encantamento
        item.enchantment = recipe.special_effects[0] if recipe.special_effects else "magical"

        if hasattr(item, 'special_effects'):
            item.special_effects.extend(recipe.special_effects)
        else:
            item.special_effects = recipe.special_effects.copy()

        # Adicionar descrição do encantamento
        enchantment_desc = self._get_enchantment_description(recipe.special_effects)
        item.nome += f" {enchantment_desc}"

        return CraftingResult(
            success=True,
            message=f"{item.nome} foi encantado com sucesso!",
            item_modified=item
        )

    def _repair_item(self, recipe: CraftingRecipe, item: Any) -> CraftingResult:
        """Repara um item danificado."""
        if not item:
            return CraftingResult(
                success=False,
                message="Nenhum item selecionado para reparo!"
            )

        # Restaurar durabilidade
        if hasattr(item, 'durabilidade'):
            item.durabilidade = 100
        else:
            item.durabilidade = 100

        return CraftingResult(
            success=True,
            message=f"{item.nome} foi reparado completamente!",
            item_modified=item
        )

    def _fuse_materials(self, recipe: CraftingRecipe) -> CraftingResult:
        """Funde materiais para criar um novo."""
        if not recipe.output_item:
            return CraftingResult(
                success=False,
                message="Receita de fusão sem item de saída definido!"
            )

        # Criar novo material
        output_material = self.materials.get(recipe.output_item)
        if not output_material:
            return CraftingResult(
                success=False,
                message="Material de saída não encontrado!"
            )

        return CraftingResult(
            success=True,
            message=f"Criou {output_material.name} através da fusão!",
            item_created=output_material
        )

    def _get_enchantment_description(self, effects: List[str]) -> str:
        """Retorna descrição do encantamento baseada nos efeitos."""
        descriptions = {
            "fire_damage": "Flamejante",
            "ice_damage": "Gélido",
            "shadow_damage": "Sombrio",
            "light_damage": "Radiante",
            "critical_boost": "Letal",
            "legendary_power": "Lendário"
        }

        for effect in effects:
            if effect in descriptions:
                return descriptions[effect]

        return "Encantado"

    def _calculate_xp_reward(self, recipe: CraftingRecipe) -> int:
        """Calcula recompensa de XP baseada na receita."""
        base_xp = 50
        level_multiplier = recipe.required_level * 10
        difficulty_multiplier = int((1.0 - recipe.success_chance) * 100)

        return base_xp + level_multiplier + difficulty_multiplier

    def add_material_to_player(self, player_id: str, material_name: str, quantity: int):
        """Adiciona material ao inventário do jogador."""
        if player_id not in self.player_materials:
            self.player_materials[player_id] = {}

        current_qty = self.player_materials[player_id].get(material_name, 0)
        self.player_materials[player_id][material_name] = current_qty + quantity

    def get_player_materials(self, player_id: str) -> Dict[str, int]:
        """Retorna materiais do jogador."""
        return self.player_materials.get(player_id, {})

    def get_material_info(self, material_name: str) -> Optional[CraftingMaterial]:
        """Retorna informações sobre um material."""
        return self.materials.get(material_name)

    def get_recipe_details(self, recipe_id: str) -> Optional[CraftingRecipe]:
        """Retorna detalhes de uma receita."""
        return self.recipes.get(recipe_id)


def create_crafting_manager() -> CraftingManager:
    """Factory function para criar manager de crafting."""
    return CraftingManager()