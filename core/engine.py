import random
from copy import deepcopy
from typing import Optional, List, Dict, Any
import threading

# Importa os modelos e os bancos de dados que criamos
from .models import Personagem, Item, Habilidade, TipoHabilidade
from .managers import CombatManager, InventoryManager, SaveManager, EventManager, CacheManager
from .managers.event_manager import emit_event, EventType
from .exceptions import GameEngineError, ResourceNotFoundError
from data.equipment import DB_EQUIPAMENTOS
from data.items import DB_ITENS
from data.abilities import DB_HABILIDADES
from data.enemies import DB_INIMIGOS
from utils.error_handler import handle_exceptions, validate_not_none
from utils.logging_config import get_logger
from config.settings import is_debug_mode


class GameEngine:
    """
    Controla todo o estado e a lógica principal do jogo ZORG.
    Implementa padrão Singleton para garantir única instância.
    """
    _instance: Optional['GameEngine'] = None
    _lock = threading.Lock()
    _initialized = False

    def __new__(cls) -> 'GameEngine':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if GameEngine._initialized:
            return

        self.logger = get_logger("engine")
        self.jogador: Optional[Personagem] = None

        # Inicializar managers
        self._combat_manager = CombatManager()
        self._inventory_manager = InventoryManager()
        self._save_manager = SaveManager()
        self._event_manager = EventManager()
        self._cache_manager = CacheManager()

        # Inicializar todos os managers
        self._initialize_managers()

        GameEngine._initialized = True
        self.logger.info("GameEngine inicializado")

    def _initialize_managers(self) -> None:
        """Inicializa todos os managers."""
        managers = [
            self._combat_manager,
            self._inventory_manager,
            self._save_manager,
            self._event_manager,
            self._cache_manager
        ]

        for manager in managers:
            if not manager.initialize():
                self.logger.error(f"Falha ao inicializar {manager.name}")
                raise GameEngineError(f"Falha ao inicializar {manager.name}")

    @property
    def combat_manager(self) -> CombatManager:
        """Retorna o gerenciador de combate."""
        return self._combat_manager

    @property
    def inventory_manager(self) -> InventoryManager:
        """Retorna o gerenciador de inventário."""
        return self._inventory_manager

    @property
    def save_manager(self) -> SaveManager:
        """Retorna o gerenciador de save."""
        return self._save_manager

    @property
    def event_manager(self) -> EventManager:
        """Retorna o gerenciador de eventos."""
        return self._event_manager

    @property
    def cache_manager(self) -> CacheManager:
        """Retorna o gerenciador de cache."""
        return self._cache_manager

    # --- FUNÇÕES DE SAVE/LOAD ATUALIZADAS ---
    @handle_exceptions(reraise=True)
    def save_game_state(self) -> bool:
        """Salva o estado atual do jogador usando o SaveManager."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador para salvar")
        return self._save_manager.save_game(self.jogador)

    @handle_exceptions(reraise=True)
    def load_game_state(self) -> bool:
        """Carrega o estado do jogador usando o SaveManager."""
        jogador_carregado = self._save_manager.load_game()
        if jogador_carregado:
            self.jogador = jogador_carregado
            return True
        return False

    @handle_exceptions(reraise=True)
    def inicializar_novo_jogo(self) -> None:
        """Cria uma nova instância do jogador para um novo jogo."""
        self.jogador = Personagem(
            nome="Manu",
            hp_max=50,
            mp_max=20,
            ataque_base=7,
            defesa_base=2
        )
        self.jogador.xp_proximo_nivel = 100
        self.jogador.ouro = 0
        self.jogador.fase_atual = 1

        # Equipar itens iniciais usando o InventoryManager
        initial_equipment = [
            "Adaga Enferrujada",
            "Roupas de Pano",
            "Escudo de Madeira"
        ]

        for equipment_name in initial_equipment:
            equipment = DB_EQUIPAMENTOS.get(equipment_name)
            if equipment:
                if equipment.is_weapon:
                    self.jogador.arma_equipada = equipment
                elif equipment.is_armor:
                    self.jogador.armadura_equipada = equipment
                elif equipment.is_shield:
                    self.jogador.escudo_equipada = equipment

        # Adicionar itens iniciais usando o InventoryManager
        initial_items = [
            ("Pocao de Cura", 2),
            ("Antidoto", 1)
        ]

        for item_name, quantity in initial_items:
            self._inventory_manager.add_item(self.jogador, item_name, quantity)

        # Adicionar habilidades iniciais
        initial_skills = [
            "Golpe Poderoso",
            "Toque Restaurador",
            "Postura Defensiva"
        ]

        for skill_name in initial_skills:
            self.aprender_habilidade(skill_name)

        self.logger.info(f"Novo jogo inicializado para {self.jogador.nome}")
        emit_event(EventType.LOAD_GAME, {
            "action": "new_game",
            "player_name": self.jogador.nome
        })

    @handle_exceptions(reraise=True)
    def criar_inimigo(self, nome_inimigo: str) -> Optional[Personagem]:
        """
        Cria uma cópia de um inimigo a partir do banco de dados.
        Usa cache para otimizar a criação de inimigos.
        """
        validate_not_none(nome_inimigo, "nome do inimigo")

        # Tentar obter do cache primeiro
        cache_key = f"enemy_template_{nome_inimigo}"
        enemy_template = self._cache_manager.get(cache_key, "resources")

        if enemy_template is None:
            enemy_template = DB_INIMIGOS.get(nome_inimigo)
            if enemy_template is None:
                raise ResourceNotFoundError("inimigo", nome_inimigo)

            # Cachear o template do inimigo
            self._cache_manager.set(cache_key, enemy_template, "resources")

        # Retornar cópia do template
        enemy_copy = deepcopy(enemy_template)
        self.logger.debug(f"Inimigo criado: {nome_inimigo}")
        return enemy_copy

    @handle_exceptions(reraise=True)
    def adicionar_item_inventario(self, nome_item: str, quantidade: int = 1) -> bool:
        """Adiciona um item ao inventário do jogador usando o InventoryManager."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        return self._inventory_manager.add_item(self.jogador, nome_item, quantidade)

    @handle_exceptions(reraise=True)
    def aprender_habilidade(self, nome_habilidade: str) -> bool:
        """Adiciona uma habilidade à lista de habilidades conhecidas do jogador."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        habilidade = DB_HABILIDADES.get(nome_habilidade)
        if not habilidade:
            raise ResourceNotFoundError("habilidade", nome_habilidade)

        if habilidade not in self.jogador.habilidades_conhecidas:
            self.jogador.habilidades_conhecidas.append(habilidade)
            self.logger.debug(f"Habilidade {nome_habilidade} aprendida por {self.jogador.nome}")
            return True
        return False

    @handle_exceptions(reraise=True)
    def verificar_level_up(self) -> Optional[Dict[str, Any]]:
        """
        Verifica se o jogador tem XP suficiente para subir de nível.
        Se sim, atualiza os status e retorna um dicionário com os bônus.
        """
        if not self.jogador or self.jogador.xp < self.jogador.xp_proximo_nivel:
            return None

        old_level = self.jogador.nivel
        self.jogador.nivel += 1
        self.jogador.xp -= self.jogador.xp_proximo_nivel
        self.jogador.xp_proximo_nivel = int(self.jogador.xp_proximo_nivel * 1.5)

        # Bônus escaláveis baseados no nível
        hp_bonus = 15 + (self.jogador.nivel * 2)
        mp_bonus = 10 + self.jogador.nivel
        atk_bonus = 2 + (self.jogador.nivel // 5)
        def_bonus = 1 + (self.jogador.nivel // 10)

        self.jogador.hp_max += hp_bonus
        self.jogador.mp_max += mp_bonus
        self.jogador.ataque_base += atk_bonus
        self.jogador.defesa_base += def_bonus

        # Curar completamente no level up
        self.jogador.hp = self.jogador.hp_max
        self.jogador.mp = self.jogador.mp_max

        level_up_data = {
            "old_level": old_level,
            "new_level": self.jogador.nivel,
            "hp_bonus": hp_bonus,
            "mp_bonus": mp_bonus,
            "atk_bonus": atk_bonus,
            "def_bonus": def_bonus,
        }

        emit_event(EventType.PLAYER_LEVEL_UP, {
            "player_name": self.jogador.nome,
            **level_up_data
        })

        self.logger.info(f"{self.jogador.nome} subiu para o nível {self.jogador.nivel}")
        return level_up_data

    @handle_exceptions(reraise=True)
    def processar_turno_jogador(self, acao: str, inimigo: Personagem, **kwargs) -> List[str]:
        """Processa a ação do jogador delegando para o CombatManager."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        validate_not_none(inimigo, "inimigo")

        # Usar o CombatManager para processar ações
        if not self._combat_manager.is_combat_active():
            self._combat_manager.start_combat(self.jogador, inimigo)

        from core.managers.combat_manager import CombatAction

        action_map = {
            "attack": CombatAction.ATTACK,
            "skill": CombatAction.SKILL,
            "item": CombatAction.ITEM,
            "escape": CombatAction.ESCAPE
        }

        combat_action = action_map.get(acao)
        if not combat_action:
            raise GameEngineError(f"Ação inválida: {acao}")

        combat_state = self._combat_manager.process_player_turn(combat_action, **kwargs)
        return combat_state.get("log", [])

    @handle_exceptions(reraise=True)
    def processar_turno_inimigo(self, inimigo: Personagem) -> List[str]:
        """
        Processa o turno do inimigo delegando para o CombatManager.
        """
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        validate_not_none(inimigo, "inimigo")

        # Usar o CombatManager para processar turno do inimigo
        if self._combat_manager.is_combat_active():
            combat_state = self._combat_manager.process_enemy_turn()
            return combat_state.get("log", [])

        return []

    @handle_exceptions(reraise=True)
    def processar_vitoria(self, inimigo: Personagem) -> Dict[str, Any]:
        """Processa as recompensas após derrotar um inimigo."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        validate_not_none(inimigo, "inimigo")

        xp_ganho = inimigo.xp_dado
        ouro_ganho = inimigo.ouro_dado

        # Bônus baseado no nível do jogador
        xp_bonus = int(xp_ganho * (1 + (self.jogador.nivel * 0.05)))
        ouro_bonus = int(ouro_ganho * (1 + (self.jogador.nivel * 0.03)))

        self.jogador.xp += xp_bonus
        self.jogador.ouro += ouro_bonus

        info_level_up = self.verificar_level_up()

        victory_data = {
            "enemy_name": inimigo.nome,
            "xp_ganho": xp_bonus,
            "ouro_ganho": ouro_bonus,
            "level_up": info_level_up
        }

        # Finalizar combate no CombatManager
        if self._combat_manager.is_combat_active():
            self._combat_manager.end_combat()

        self.logger.info(f"{self.jogador.nome} derrotou {inimigo.nome} - XP: +{xp_bonus}, Ouro: +{ouro_bonus}")
        return victory_data

    @handle_exceptions(reraise=True)
    def usar_item_inventario(self, nome_item: str) -> List[str]:
        """Usa um item do inventário delegando para o InventoryManager."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        return self._inventory_manager.use_item(self.jogador, nome_item)

    @handle_exceptions(reraise=True)
    def usar_habilidade(self, nome_habilidade: str, inimigo: Personagem) -> List[str]:
        """Usa uma habilidade delegando para o CombatManager se em combate."""
        if not self.jogador:
            raise GameEngineError("Nenhum jogador ativo")

        validate_not_none(inimigo, "inimigo")

        # Se em combate, usar o CombatManager
        if self._combat_manager.is_combat_active():
            from core.managers.combat_manager import CombatAction
            combat_state = self._combat_manager.process_player_turn(
                CombatAction.SKILL,
                skill_name=nome_habilidade
            )
            return combat_state.get("log", [])

        # Lógica para uso fora de combate (cura, etc.)
        hab_escolhida = next(
            (hab for hab in self.jogador.habilidades_conhecidas if hab.nome == nome_habilidade),
            None
        )

        if not hab_escolhida:
            raise ResourceNotFoundError("habilidade", nome_habilidade)

        if not self.jogador.can_use_skill(hab_escolhida):
            from core.exceptions import InsufficientResourcesError
            raise InsufficientResourcesError("MP", hab_escolhida.custo_mp, self.jogador.mp)

        self.jogador.spend_mp(hab_escolhida.custo_mp)
        log_mensagens = [f"✨ Você usa [b yellow]{hab_escolhida.nome}[/b yellow]!"]

        if hab_escolhida.tipo == TipoHabilidade.CURA:
            heal_amount = self.jogador.heal(hab_escolhida.valor_efeito)
            if heal_amount > 0:
                log_mensagens.append(f"💚 Você se cura em [b green]{heal_amount} HP[/b green].")
            else:
                log_mensagens.append("Sua vida já está no máximo.")

        elif hab_escolhida.tipo == TipoHabilidade.BUFF_DEFESA:
            self.jogador.turnos_buff_defesa = 3
            log_mensagens.append(f"🛡️ Sua defesa aumenta por [b cyan]3 turnos[/b cyan]!")

        return log_mensagens

    def get_engine_status(self) -> Dict[str, Any]:
        """Retorna o status completo do engine."""
        return {
            "initialized": GameEngine._initialized,
            "player_active": self.jogador is not None,
            "player_name": self.jogador.nome if self.jogador else None,
            "debug_mode": is_debug_mode(),
            "managers": {
                "combat": self._combat_manager.get_status(),
                "inventory": self._inventory_manager.get_status(),
                "save": self._save_manager.get_status(),
                "event": self._event_manager.get_status(),
                "cache": self._cache_manager.get_status(),
            }
        }

    def shutdown(self) -> None:
        """Finaliza o engine e todos os managers."""
        managers = [
            self._combat_manager,
            self._inventory_manager,
            self._save_manager,
            self._event_manager,
            self._cache_manager
        ]

        for manager in managers:
            manager.shutdown()

        self.logger.info("GameEngine finalizado")
        GameEngine._initialized = False
        GameEngine._instance = None


# Função conveniente para obter a instância global
def get_game_engine() -> GameEngine:
    """Retorna a instância global do GameEngine."""
    return GameEngine()