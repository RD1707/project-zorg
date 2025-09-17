from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from enum import Enum

from core.exceptions import DataValidationError, CharacterStateError
from utils.error_handler import validate_positive, validate_non_negative, validate_string_not_empty

class TipoEquipamento(Enum):
    """Tipos válidos de equipamento."""
    ARMA = "arma"
    ARMADURA = "armadura"
    ESCUDO = "escudo"


class TipoHabilidade(Enum):
    """Tipos válidos de habilidade."""
    ATAQUE = "ataque"
    CURA = "cura"
    BUFF_DEFESA = "buff_defesa"
    BUFF_ATAQUE = "buff_ataque"
    DEBUFF = "debuff"


@dataclass
class Equipamento:
    """Representa um item de equipamento que um personagem pode usar."""
    nome: str
    tipo: TipoEquipamento
    bonus_ataque: int
    bonus_defesa: int
    descricao: str = ""
    preco: int = 0
    raridade: str = "comum"  # comum, raro, épico, lendário

    def __post_init__(self):
        """Validação após inicialização."""
        validate_string_not_empty(self.nome, "nome do equipamento")
        validate_non_negative(self.bonus_ataque, "bonus de ataque")
        validate_non_negative(self.bonus_defesa, "bonus de defesa")
        validate_non_negative(self.preco, "preço")

    @property
    def is_weapon(self) -> bool:
        """Verifica se é uma arma."""
        return self.tipo == TipoEquipamento.ARMA

    @property
    def is_armor(self) -> bool:
        """Verifica se é armadura."""
        return self.tipo == TipoEquipamento.ARMADURA

    @property
    def is_shield(self) -> bool:
        """Verifica se é escudo."""
        return self.tipo == TipoEquipamento.ESCUDO

@dataclass
class Item:
    """Representa um item consumível no inventário."""
    nome: str
    descricao: str
    cura_hp: int
    cura_mp: int
    cura_veneno: int
    preco_venda: int
    quantidade: int = 1
    stack_max: int = 99
    categoria: str = "consumível"

    def __post_init__(self):
        """Validação após inicialização."""
        validate_string_not_empty(self.nome, "nome do item")
        validate_non_negative(self.cura_hp, "cura HP")
        validate_non_negative(self.cura_mp, "cura MP")
        validate_non_negative(self.cura_veneno, "cura veneno")
        validate_non_negative(self.preco_venda, "preço de venda")
        validate_positive(self.quantidade, "quantidade")
        validate_positive(self.stack_max, "stack máximo")

    def can_stack_with(self, other: 'Item') -> bool:
        """Verifica se pode ser empilhado com outro item."""
        return self.nome == other.nome and self.quantidade + other.quantidade <= self.stack_max

    def add_quantity(self, amount: int) -> bool:
        """Adiciona quantidade se possível."""
        if self.quantidade + amount <= self.stack_max:
            self.quantidade += amount
            return True
        return False

    @property
    def is_full_stack(self) -> bool:
        """Verifica se o stack está completo."""
        return self.quantidade >= self.stack_max

@dataclass
class Habilidade:
    """Representa uma habilidade ou magia que um personagem pode usar."""
    nome: str
    descricao: str
    custo_mp: int
    tipo: TipoHabilidade
    valor_efeito: int
    cooldown: int = 0
    nivel_requerido: int = 1
    elemento: str = "neutro"

    def __post_init__(self):
        """Validação após inicialização."""
        validate_string_not_empty(self.nome, "nome da habilidade")
        validate_non_negative(self.custo_mp, "custo MP")
        validate_positive(self.valor_efeito, "valor do efeito")
        validate_non_negative(self.cooldown, "cooldown")
        validate_positive(self.nivel_requerido, "nível requerido")

    @property
    def is_offensive(self) -> bool:
        """Verifica se é uma habilidade ofensiva."""
        return self.tipo in [TipoHabilidade.ATAQUE, TipoHabilidade.DEBUFF]

    @property
    def is_defensive(self) -> bool:
        """Verifica se é uma habilidade defensiva."""
        return self.tipo in [TipoHabilidade.CURA, TipoHabilidade.BUFF_DEFESA, TipoHabilidade.BUFF_ATAQUE]

@dataclass
class TutorialFlags:
    """Controla quais tutoriais já foram mostrados ao jogador."""
    combate_basico_mostrado: bool = False
    habilidades_mostrado: bool = False
    itens_mostrado: bool = False
    level_up_mostrado: bool = False
    equipamentos_mostrado: bool = False
    save_load_mostrado: bool = False

    def to_dict(self) -> Dict[str, bool]:
        """Converte para dicionário."""
        return {
            "combate_basico_mostrado": self.combate_basico_mostrado,
            "habilidades_mostrado": self.habilidades_mostrado,
            "itens_mostrado": self.itens_mostrado,
            "level_up_mostrado": self.level_up_mostrado,
            "equipamentos_mostrado": self.equipamentos_mostrado,
            "save_load_mostrado": self.save_load_mostrado,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, bool]) -> 'TutorialFlags':
        """Cria instância a partir de dicionário."""
        return cls(
            combate_basico_mostrado=data.get("combate_basico_mostrado", False),
            habilidades_mostrado=data.get("habilidades_mostrado", False),
            itens_mostrado=data.get("itens_mostrado", False),
            level_up_mostrado=data.get("level_up_mostrado", False),
            equipamentos_mostrado=data.get("equipamentos_mostrado", False),
            save_load_mostrado=data.get("save_load_mostrado", False),
        )

@dataclass
class Personagem:
    """
    A classe principal que representa qualquer personagem no jogo,
    seja o jogador ou um inimigo.
    """
    nome: str
    hp_max: int
    mp_max: int
    ataque_base: int
    defesa_base: int
    
    # Atributos específicos de inimigos
    xp_dado: int = 0
    ouro_dado: int = 0  # Renomeado de 'ouro' para evitar confusão com o ouro do jogador

    # Atributos que mudam durante o jogo
    hp: int = field(init=False)
    mp: int = field(init=False)
    
    # Atributos de progressão do jogador
    nivel: int = 1
    xp: int = 0
    xp_proximo_nivel: int = 100
    ouro: int = 0
    fase_atual: int = 1

    # Status e Efeitos
    turnos_veneno: int = 0
    dano_por_turno_veneno: int = 0
    turnos_buff_defesa: int = 0
    turnos_furia: int = 0
    turnos_regeneracao: int = 0
    
    # Equipamento do Jogador
    arma_equipada: Optional[Equipamento] = None
    armadura_equipada: Optional[Equipamento] = None
    escudo_equipada: Optional[Equipamento] = None

    # Inventário e Habilidades do Jogador
    inventario: List[Item] = field(default_factory=list)
    habilidades_conhecidas: List[Habilidade] = field(default_factory=list)

    # Flags de controle
    tutoriais: TutorialFlags = field(default_factory=TutorialFlags)
    ajudou_marinheiro: bool = False
    
    def __post_init__(self):
        """
        Método especial de dataclasses que é chamado após a criação do objeto.
        Usamo-lo para inicializar HP e MP com os seus valores máximos.
        """
        # Validações
        validate_string_not_empty(self.nome, "nome do personagem")
        validate_positive(self.hp_max, "HP máximo")
        validate_positive(self.mp_max, "MP máximo")
        validate_non_negative(self.ataque_base, "ataque base")
        validate_non_negative(self.defesa_base, "defesa base")
        validate_non_negative(self.xp_dado, "XP dado")
        validate_non_negative(self.ouro_dado, "ouro dado")

        # Inicialização
        self.hp = self.hp_max
        self.mp = self.mp_max

    @property
    def ataque_total(self) -> int:
        """Calcula o ataque total, incluindo o bónus da arma."""
        bonus_arma = self.arma_equipada.bonus_ataque if self.arma_equipada else 0
        return self.ataque_base + bonus_arma

    @property
    def defesa_total(self) -> int:
        """Calcula a defesa total, incluindo bónus de armadura e escudo."""
        bonus_armadura = self.armadura_equipada.bonus_defesa if self.armadura_equipada else 0
        bonus_escudo = self.escudo_equipada.bonus_defesa if self.escudo_equipada else 0
        bonus_buff = 5 if self.turnos_buff_defesa > 0 else 0
        return self.defesa_base + bonus_armadura + bonus_escudo + bonus_buff

    @property
    def is_alive(self) -> bool:
        """Verifica se o personagem está vivo."""
        return self.hp > 0

    @property
    def is_dead(self) -> bool:
        """Verifica se o personagem está morto."""
        return self.hp <= 0

    @property
    def hp_percentage(self) -> float:
        """Percentual de HP atual."""
        return (self.hp / self.hp_max) * 100 if self.hp_max > 0 else 0

    @property
    def mp_percentage(self) -> float:
        """Percentual de MP atual."""
        return (self.mp / self.mp_max) * 100 if self.mp_max > 0 else 0

    @property
    def is_poisoned(self) -> bool:
        """Verifica se está envenenado."""
        return self.turnos_veneno > 0

    @property
    def has_defense_buff(self) -> bool:
        """Verifica se tem buff de defesa."""
        return self.turnos_buff_defesa > 0

    def heal(self, amount: int) -> int:
        """Cura o personagem e retorna a quantidade curada."""
        if self.is_dead:
            raise CharacterStateError("Não é possível curar um personagem morto")

        old_hp = self.hp
        self.hp = min(self.hp_max, self.hp + amount)
        return self.hp - old_hp

    def restore_mp(self, amount: int) -> int:
        """Restaura MP e retorna a quantidade restaurada."""
        old_mp = self.mp
        self.mp = min(self.mp_max, self.mp + amount)
        return self.mp - old_mp

    def take_damage(self, damage: int) -> int:
        """Aplica dano e retorna o dano real causado."""
        if damage < 0:
            raise ValueError("Dano não pode ser negativo")

        actual_damage = min(damage, self.hp)
        self.hp = max(0, self.hp - damage)
        return actual_damage

    def spend_mp(self, cost: int) -> bool:
        """Gasta MP se possível."""
        if cost < 0:
            raise ValueError("Custo de MP não pode ser negativo")

        if self.mp >= cost:
            self.mp -= cost
            return True
        return False

    def add_item_to_inventory(self, item: Item) -> bool:
        """Adiciona item ao inventário."""
        # Tenta empilhar com item existente
        for existing_item in self.inventario:
            if existing_item.can_stack_with(item):
                return existing_item.add_quantity(item.quantidade)

        # Se não conseguiu empilhar, adiciona novo
        self.inventario.append(item)
        return True

    def remove_item_from_inventory(self, item_name: str, quantity: int = 1) -> bool:
        """Remove item do inventário."""
        for item in self.inventario:
            if item.nome == item_name and item.quantidade >= quantity:
                item.quantidade -= quantity
                if item.quantidade <= 0:
                    self.inventario.remove(item)
                return True
        return False

    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Verifica se tem um item no inventário."""
        for item in self.inventario:
            if item.nome == item_name and item.quantidade >= quantity:
                return True
        return False

    def knows_skill(self, skill_name: str) -> bool:
        """Verifica se conhece uma habilidade."""
        return any(hab.nome == skill_name for hab in self.habilidades_conhecidas)

    def can_use_skill(self, skill: Habilidade) -> bool:
        """Verifica se pode usar uma habilidade."""
        return (
            self.mp >= skill.custo_mp and
            self.nivel >= skill.nivel_requerido and
            skill in self.habilidades_conhecidas
        )

    def process_status_effects(self) -> List[str]:
        """Processa efeitos de status e retorna mensagens."""
        messages = []

        # Veneno
        if self.turnos_veneno > 0:
            damage = min(self.dano_por_turno_veneno, self.hp)
            self.hp = max(0, self.hp - self.dano_por_turno_veneno)
            messages.append(f"☠️ {self.nome} sofre {damage} de dano por veneno!")
            self.turnos_veneno -= 1
            if self.turnos_veneno <= 0:
                self.dano_por_turno_veneno = 0
                messages.append(f"✨ {self.nome} se recupera do veneno.")

        # Buff de defesa
        if self.turnos_buff_defesa > 0:
            self.turnos_buff_defesa -= 1
            if self.turnos_buff_defesa <= 0:
                messages.append(f"🛡️ O buff de defesa de {self.nome} termina.")

        # Fúria
        if self.turnos_furia > 0:
            self.turnos_furia -= 1
            if self.turnos_furia <= 0:
                messages.append(f"😠 A fúria de {self.nome} termina.")

        # Regeneração
        if self.turnos_regeneracao > 0:
            heal_amount = min(5, self.hp_max - self.hp)
            if heal_amount > 0:
                self.hp += heal_amount
                messages.append(f"💚 {self.nome} regenera {heal_amount} HP.")
            self.turnos_regeneracao -= 1
            if self.turnos_regeneracao <= 0:
                messages.append(f"✨ A regeneração de {self.nome} termina.")

        return messages

    def get_stats_summary(self) -> Dict[str, Any]:
        """Retorna um resumo das estatísticas."""
        return {
            "nome": self.nome,
            "nivel": self.nivel,
            "hp": f"{self.hp}/{self.hp_max}",
            "mp": f"{self.mp}/{self.mp_max}",
            "ataque_total": self.ataque_total,
            "defesa_total": self.defesa_total,
            "xp": f"{self.xp}/{self.xp_proximo_nivel}",
            "ouro": self.ouro,
            "fase_atual": self.fase_atual,
            "status_effects": {
                "veneno": self.turnos_veneno,
                "buff_defesa": self.turnos_buff_defesa,
                "furia": self.turnos_furia,
                "regeneracao": self.turnos_regeneracao,
            }
        }