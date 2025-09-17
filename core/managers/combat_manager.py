"""
Gerenciador de combate com lógica encapsulada e eventos.
"""
import random
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from core.managers.base_manager import BaseManager
from core.managers.event_manager import emit_event, EventType
from core.models import Personagem, Habilidade, TipoHabilidade
from core.exceptions import CombatError, InsufficientResourcesError, InvalidActionError
from utils.error_handler import handle_exceptions, validate_not_none
from config.settings import get_config


class CombatAction(Enum):
    """Tipos de ação em combate."""
    ATTACK = "attack"
    SKILL = "skill"
    ITEM = "item"
    ESCAPE = "escape"


class CombatResult(Enum):
    """Resultados possíveis de combate."""
    ONGOING = "ongoing"
    PLAYER_WIN = "player_win"
    PLAYER_DEAD = "player_dead"
    ESCAPED = "escaped"


class CombatManager(BaseManager):
    """Gerenciador de combate."""

    def __init__(self):
        super().__init__("combat_manager")
        self._config = get_config("combat")
        self._current_combat: Optional[Dict[str, Any]] = None

    def _do_initialize(self) -> None:
        """Inicialização do gerenciador de combate."""
        self._current_combat = None

    @handle_exceptions(reraise=True)
    def start_combat(self, player: Personagem, enemy: Personagem) -> Dict[str, Any]:
        """Inicia um combate."""
        validate_not_none(player, "jogador")
        validate_not_none(enemy, "inimigo")

        if not player.is_alive:
            raise CombatError("Jogador não pode iniciar combate morto")

        if not enemy.is_alive:
            raise CombatError("Inimigo não pode iniciar combate morto")

        self._current_combat = {
            "player": player,
            "enemy": enemy,
            "turn_count": 0,
            "log": [],
            "result": CombatResult.ONGOING
        }

        emit_event(EventType.COMBAT_START, {
            "player_name": player.nome,
            "enemy_name": enemy.nome,
            "player_level": player.nivel,
            "enemy_hp": enemy.hp_max
        })

        self.logger.info(f"Combate iniciado: {player.nome} vs {enemy.nome}")
        return self.get_combat_state()

    @handle_exceptions(reraise=True)
    def process_player_turn(self, action: CombatAction, **kwargs) -> Dict[str, Any]:
        """Processa o turno do jogador."""
        if not self._current_combat:
            raise CombatError("Nenhum combate ativo")

        if self._current_combat["result"] != CombatResult.ONGOING:
            raise CombatError("Combate já finalizado")

        player = self._current_combat["player"]
        enemy = self._current_combat["enemy"]
        log_messages = []

        if action == CombatAction.ATTACK:
            log_messages.extend(self._process_attack(player, enemy))
        elif action == CombatAction.SKILL:
            skill_name = kwargs.get("skill_name")
            if not skill_name:
                raise InvalidActionError("Nome da habilidade não fornecido")
            log_messages.extend(self._process_skill_use(player, enemy, skill_name))
        elif action == CombatAction.ITEM:
            item_name = kwargs.get("item_name")
            if not item_name:
                raise InvalidActionError("Nome do item não fornecido")
            log_messages.extend(self._process_item_use(player, item_name))
        elif action == CombatAction.ESCAPE:
            log_messages.extend(self._process_escape(player, enemy))
        else:
            raise InvalidActionError(f"Ação de combate inválida: {action}")

        self._current_combat["log"].extend(log_messages)
        self._current_combat["turn_count"] += 1

        # Verificar fim de combate
        self._check_combat_end()

        return self.get_combat_state()

    @handle_exceptions(reraise=True)
    def process_enemy_turn(self) -> Dict[str, Any]:
        """Processa o turno do inimigo."""
        if not self._current_combat:
            raise CombatError("Nenhum combate ativo")

        if self._current_combat["result"] != CombatResult.ONGOING:
            return self.get_combat_state()

        player = self._current_combat["player"]
        enemy = self._current_combat["enemy"]

        log_messages = self._process_enemy_ai(enemy, player)
        
        # Processar efeitos de status
        log_messages.extend(player.process_status_effects())
        log_messages.extend(enemy.process_status_effects())

        self._current_combat["log"].extend(log_messages)

        # Verificar fim de combate
        self._check_combat_end()

        return self.get_combat_state()

    def _process_attack(self, attacker: Personagem, defender: Personagem) -> List[str]:
        """Processa um ataque básico."""
        messages = []

        # Calcular chance de crítico
        crit_chance = self._config["base_crit_chance"] + (attacker.nivel * 2)
        is_critical = random.randint(1, 100) <= crit_chance

        # Calcular dano
        base_damage = attacker.ataque_total + random.randint(0, 6)

        if is_critical:
            total_damage = int((base_damage * self._config["crit_multiplier"]) - (defender.defesa_total * 0.5))
            messages.append("[b yellow]GOLPE CRÍTICO![/b yellow]")
        else:
            total_damage = base_damage - defender.defesa_total

        total_damage = max(1, total_damage)
        actual_damage = defender.take_damage(total_damage)

        messages.append(f"⚔️ {attacker.nome} ataca {defender.nome} e causa [b red]{actual_damage}[/b red] de dano!")

        self.logger.debug(f"Ataque: {attacker.nome} -> {defender.nome}, dano: {actual_damage}, crítico: {is_critical}")
        return messages

    def _process_skill_use(self, user: Personagem, target: Personagem, skill_name: str) -> List[str]:
        """Processa o uso de uma habilidade."""
        messages = []

        # Encontrar habilidade
        skill = next((h for h in user.habilidades_conhecidas if h.nome == skill_name), None)
        if not skill:
            raise ResourceNotFoundError("habilidade", skill_name)

        # Verificar se pode usar
        if not user.can_use_skill(skill):
            if user.mp < skill.custo_mp:
                raise InsufficientResourcesError("MP", skill.custo_mp, user.mp)
            raise InvalidActionError(f"Não é possível usar a habilidade '{skill_name}'")

        # Gastar MP
        user.spend_mp(skill.custo_mp)
        messages.append(f"✨ {user.nome} usa [b yellow]{skill.nome}[/b yellow]!")

        # Aplicar efeito
        if skill.tipo == TipoHabilidade.ATAQUE:
            damage = (skill.valor_efeito + user.ataque_base) - target.defesa_total
            damage = max(1, damage)
            actual_damage = target.take_damage(damage)
            messages.append(f"{target.nome} sofre [b red]{actual_damage}[/b red] de dano mágico!")

        elif skill.tipo == TipoHabilidade.CURA:
            heal_amount = user.heal(skill.valor_efeito)
            if heal_amount > 0:
                messages.append(f"💚 {user.nome} se cura em [b green]{heal_amount} HP[/b green].")
            else:
                messages.append(f"{user.nome} já está com a vida cheia.")

        elif skill.tipo == TipoHabilidade.BUFF_DEFESA:
            user.turnos_buff_defesa = 3
            messages.append(f"🛡️ A defesa de {user.nome} aumenta por [b cyan]3 turnos[/b cyan]!")
        
        # NOVAS HABILIDADES AQUI
        elif skill.tipo == TipoHabilidade.FURIA:
            user.turnos_furia = 4
            messages.append(f"😠 {user.nome} entra em fúria! Seu ataque aumenta, mas sua defesa diminui por [b red]4 turnos[/b red]!")

        elif skill.tipo == TipoHabilidade.REGENERACAO:
            user.turnos_regeneracao = 5
            messages.append(f"♻️ {user.nome} ativa a regeneração vital! HP será recuperado a cada turno por [b green]5 turnos[/b green]!")
        
        else:
            raise InvalidActionError(f"Tipo de habilidade desconhecido: {skill.tipo.value}")


        emit_event(EventType.SKILL_USED, {
            "user": user.nome,
            "skill": skill.nome,
            "target": target.nome,
            "mp_cost": skill.custo_mp
        })

        self.logger.debug(f"Habilidade usada: {user.nome} -> {skill.nome} -> {target.nome}")
        return messages

    def _process_item_use(self, user: Personagem, item_name: str) -> List[str]:
        """Processa o uso de um item."""
        messages = []

        # Verificar se tem o item
        item = next((i for i in user.inventario if i.nome == item_name), None)
        if not item:
            raise ResourceNotFoundError("item no inventário", item_name)

        # Aplicar efeitos
        effects_applied = False

        if item.cura_hp > 0:
            heal_amount = user.heal(item.cura_hp)
            if heal_amount > 0:
                messages.append(f"🧪 {user.nome} usa [b cyan]{item_name}[/b cyan] e recupera [b green]{heal_amount} HP[/b green]!")
                effects_applied = True

        if item.cura_mp > 0:
            mp_amount = user.restore_mp(item.cura_mp)
            if mp_amount > 0:
                messages.append(f"🧪 {user.nome} usa [b cyan]{item_name}[/b cyan] e recupera [b blue]{mp_amount} MP[/b blue]!")
                effects_applied = True

        if item.cura_veneno > 0 and user.is_poisoned:
            user.turnos_veneno = 0
            user.dano_por_turno_veneno = 0
            messages.append(f"🧪 {user.nome} usa [b cyan]{item_name}[/b cyan] e se cura do [b magenta]veneno[/b magenta]!")
            effects_applied = True

        if not effects_applied:
            messages.append(f"{user.nome} usa [b cyan]{item_name}[/b cyan], mas nada acontece.")

        # Remover item do inventário
        user.remove_item_from_inventory(item_name, 1)

        emit_event(EventType.ITEM_USED, {
            "user": user.nome,
            "item": item_name,
            "effects_applied": effects_applied
        })

        self.logger.debug(f"Item usado: {user.nome} -> {item_name}")
        return messages

    def _process_escape(self, player: Personagem, enemy: Personagem) -> List[str]:
        """Processa tentativa de fuga."""
        escape_chance = self._config["escape_base_chance"]

        # Ajustar chance baseado na diferença de nível/velocidade
        level_diff = player.nivel - (enemy.nivel if hasattr(enemy, 'nivel') else 1)
        escape_chance += level_diff * 5
        escape_chance = max(10, min(90, escape_chance))  # Entre 10% e 90%

        if random.randint(1, 100) <= escape_chance:
            self._current_combat["result"] = CombatResult.ESCAPED
            return ["🏃 Você conseguiu escapar do combate!"]
        else:
            return ["🚫 Você tentou fugir, mas não conseguiu escapar!"]

    def _process_enemy_ai(self, enemy: Personagem, player: Personagem) -> List[str]:
        """Processa a IA do inimigo."""
        messages = []

        # Lógica de IA melhorada
        action = "attack"
        skill_to_use = None
        
        if enemy.habilidades_conhecidas and enemy.mp > 0:
            # Encontrar habilidades por tipo
            healing_skills = [h for h in enemy.habilidades_conhecidas
                              if h.tipo == TipoHabilidade.CURA and enemy.mp >= h.custo_mp]
            buff_skills = [h for h in enemy.habilidades_conhecidas
                           if h.tipo == TipoHabilidade.BUFF_DEFESA and enemy.mp >= h.custo_mp]
            regeneracao_skills = [h for h in enemy.habilidades_conhecidas
                                  if h.tipo == TipoHabilidade.REGENERACAO and enemy.mp >= h.custo_mp]
            furia_skills = [h for h in enemy.habilidades_conhecidas
                            if h.tipo == TipoHabilidade.FURIA and enemy.mp >= h.custo_mp]
            attack_skills = [h for h in enemy.habilidades_conhecidas
                             if h.tipo == TipoHabilidade.ATAQUE and enemy.mp >= h.custo_mp]
                             
            # 1. Usar cura se o HP estiver baixo
            if enemy.hp_percentage < 40 and healing_skills:
                action = "skill"
                skill_to_use = random.choice(healing_skills)
            
            # 2. Usar regeneração se o HP estiver baixo e a habilidade não estiver ativa
            elif enemy.hp_percentage < 60 and regeneracao_skills and not enemy.turnos_regeneracao > 0:
                action = "skill"
                skill_to_use = random.choice(regeneracao_skills)
            
            # 3. Usar buff de defesa se não estiver ativo e o HP não estiver baixo
            elif enemy.hp_percentage > 50 and buff_skills and not enemy.turnos_buff_defesa > 0:
                action = "skill"
                skill_to_use = random.choice(buff_skills)

            # 4. Usar fúria se o HP estiver alto e a habilidade não estiver ativa
            elif enemy.hp_percentage > 70 and furia_skills and not enemy.turnos_furia > 0:
                action = "skill"
                skill_to_use = random.choice(furia_skills)
            
            # 5. Usar ataque com habilidade se tiver MP e chance
            elif attack_skills and random.randint(1, 100) <= 60:
                action = "skill"
                skill_to_use = random.choice(attack_skills)

        if action == "skill" and skill_to_use:
            try:
                messages.extend(self._process_skill_use(enemy, player, skill_to_use.nome))
            except (InsufficientResourcesError, InvalidActionError):
                # Se não puder usar a habilidade, volta a atacar
                messages.extend(self._process_attack(enemy, player))
        else:
            messages.extend(self._process_attack(enemy, player))

        # Aplicar veneno se o inimigo tiver
        if enemy.dano_por_turno_veneno > 0 and not player.is_poisoned:
            if random.randint(1, 100) <= 50:
                player.turnos_veneno = 3
                player.dano_por_turno_veneno = enemy.dano_por_turno_veneno
                messages.append("☠️ Você foi [b magenta]envenenado![/b magenta]")

        return messages

    def _check_combat_end(self) -> None:
        """Verifica se o combate terminou."""
        if not self._current_combat:
            return

        player = self._current_combat["player"]
        enemy = self._current_combat["enemy"]

        if player.is_dead:
            self._current_combat["result"] = CombatResult.PLAYER_DEAD
            emit_event(EventType.PLAYER_DEATH, {
                "player_name": player.nome,
                "enemy_name": enemy.nome,
                "turn_count": self._current_combat["turn_count"]
            })
        elif enemy.is_dead:
            self._current_combat["result"] = CombatResult.PLAYER_WIN
            emit_event(EventType.COMBAT_END, {
                "winner": player.nome,
                "loser": enemy.nome,
                "turn_count": self._current_combat["turn_count"]
            })

    def get_combat_state(self) -> Dict[str, Any]:
        """Retorna o estado atual do combate."""
        if not self._current_combat:
            return {"active": False}

        return {
            "active": True,
            "player": self._current_combat["player"],
            "enemy": self._current_combat["enemy"],
            "turn_count": self._current_combat["turn_count"],
            "log": self._current_combat["log"].copy(),
            "result": self._current_combat["result"]
        }

    def end_combat(self) -> Dict[str, Any]:
        """Finaliza o combate e retorna o estado final."""
        if not self._current_combat:
            return {"active": False}

        final_state = self.get_combat_state()
        self._current_combat = None
        return final_state

    def is_combat_active(self) -> bool:
        """Verifica se há um combate ativo."""
        return self._current_combat is not None and self._current_combat["result"] == CombatResult.ONGOING