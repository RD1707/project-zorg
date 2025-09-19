import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib

from core.managers.base_manager import BaseManager
from core.managers.event_manager import emit_event, EventType
from core.models import Personagem, TutorialFlags
from core.exceptions import SaveLoadError, DataValidationError
from utils.error_handler import handle_exceptions, validate_not_none
from utils.security import SaveFileValidator
from config.settings import get_config, get_save_path
from data.equipment import DB_EQUIPAMENTOS
from data.items import DB_ITENS
from data.abilities import DB_HABILIDADES


class SaveManager(BaseManager):

    def __init__(self):
        super().__init__("save_manager")
        self._config = get_config("save")
        self._save_dir = get_save_path().parent
        self._save_file = get_save_path()
        self._max_save_slots = 5  # Máximo de slots de save

    def _do_initialize(self) -> None:
        # Garantir que o diretório existe
        self._save_dir.mkdir(exist_ok=True)

    @handle_exceptions(reraise=True)
    def save_game(self, player: Personagem, metadata: Optional[Dict[str, Any]] = None) -> bool:
        validate_not_none(player, "jogador")

        try:
            if self._config.get("backup_enabled", True) and self._save_file.exists():
                self._create_backup()

            save_data = self._prepare_save_data(player, metadata)

            self._validate_save_data(save_data)

            temp_file = self._save_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            temp_file.replace(self._save_file)

            emit_event(EventType.SAVE_GAME, {
                "player_name": player.nome,
                "level": player.nivel,
                "phase": player.fase_atual,
                "timestamp": save_data["metadata"]["timestamp"]
            })

            self.logger.info(f"Jogo salvo com sucesso para {player.nome}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao salvar jogo: {e}")
            raise SaveLoadError(f"Falha ao salvar o jogo: {str(e)}")

    @handle_exceptions(reraise=True)
    def load_game(self) -> Optional[Personagem]:
        if not self._save_file.exists():
            self.logger.info("Arquivo de save não encontrado")
            return None

        try:
            with open(self._save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # Usar o SaveFileValidator para validação de segurança completa
            SaveFileValidator.validate_save_data(save_data)

            player = self._reconstruct_player(save_data)

            emit_event(EventType.LOAD_GAME, {
                "player_name": player.nome,
                "level": player.nivel,
                "phase": player.fase_atual
            })

            self.logger.info(f"Jogo carregado com sucesso para {player.nome}")
            return player

        except json.JSONDecodeError as e:
            self.logger.error(f"Arquivo de save corrompido: {e}")
            raise SaveLoadError("Arquivo de save está corrompido ou em formato inválido")
        except DataValidationError as e:
            self.logger.error(f"Dados de save inválidos: {e}")
            raise SaveLoadError(f"Arquivo de save contém dados inválidos: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar jogo: {e}")
            raise SaveLoadError(f"Falha ao carregar o jogo: {str(e)}")

    def _prepare_save_data(self, player: Personagem, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        save_data = {
            "version": "1.0.0",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "game_version": "1.0.0",
                **(metadata or {})
            },
            "player": {
                "nome": player.nome,
                "hp": player.hp,
                "hp_max": player.hp_max,
                "mp": player.mp,
                "mp_max": player.mp_max,
                "ataque_base": player.ataque_base,
                "defesa_base": player.defesa_base,

                "nivel": player.nivel,
                "xp": player.xp,
                "xp_proximo_nivel": player.xp_proximo_nivel,
                "ouro": player.ouro,
                "fase_atual": player.fase_atual,

                "turnos_veneno": player.turnos_veneno,
                "dano_por_turno_veneno": player.dano_por_turno_veneno,
                "turnos_buff_defesa": player.turnos_buff_defesa,
                "turnos_furia": player.turnos_furia,
                "turnos_regeneracao": player.turnos_regeneracao,

                "ajudou_marinheiro": player.ajudou_marinheiro,
                "tutoriais": player.tutoriais.to_dict(),

                "arma_equipada": player.arma_equipada.nome if player.arma_equipada else None,
                "armadura_equipada": player.armadura_equipada.nome if player.armadura_equipada else None,
                "escudo_equipada": player.escudo_equipada.nome if player.escudo_equipada else None,

                "inventario": [
                    {"nome": item.nome, "quantidade": item.quantidade}
                    for item in player.inventario
                ],

                "habilidades_conhecidas": [hab.nome for hab in player.habilidades_conhecidas],
            }
        }

        checksum_data = json.dumps(save_data["player"], sort_keys=True)
        save_data["checksum"] = hashlib.sha256(checksum_data.encode()).hexdigest()

        return save_data

    def _validate_save_data(self, save_data: Dict[str, Any]) -> None:
        required_fields = ["version", "metadata", "player", "checksum"]
        for field in required_fields:
            if field not in save_data:
                raise DataValidationError(f"Campo obrigatório '{field}' não encontrado")

        player_data = save_data["player"]
        expected_checksum = save_data["checksum"]
        checksum_data = json.dumps(player_data, sort_keys=True)
        actual_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()

        if expected_checksum != actual_checksum:
            raise DataValidationError("Checksum inválido - dados podem estar corrompidos")

        player_required = ["nome", "hp", "hp_max", "mp", "mp_max", "nivel"]
        for field in player_required:
            if field not in player_data:
                raise DataValidationError(f"Campo do jogador '{field}' não encontrado")

        if player_data["hp"] < 0 or player_data["hp"] > player_data["hp_max"]:
            raise DataValidationError("HP inválido")

        if player_data["mp"] < 0 or player_data["mp"] > player_data["mp_max"]:
            raise DataValidationError("MP inválido")

        if player_data["nivel"] < 1:
            raise DataValidationError("Nível inválido")

    def _reconstruct_player(self, save_data: Dict[str, Any]) -> Personagem:
        from copy import deepcopy

        player_data = save_data["player"]

        player = Personagem(
            nome=player_data["nome"],
            hp_max=player_data["hp_max"],
            mp_max=player_data["mp_max"],
            ataque_base=player_data["ataque_base"],
            defesa_base=player_data["defesa_base"]
        )

        player.hp = player_data["hp"]
        player.mp = player_data["mp"]
        player.nivel = player_data["nivel"]
        player.xp = player_data["xp"]
        player.xp_proximo_nivel = player_data["xp_proximo_nivel"]
        player.ouro = player_data["ouro"]
        player.fase_atual = player_data["fase_atual"]

        player.turnos_veneno = player_data.get("turnos_veneno", 0)
        player.dano_por_turno_veneno = player_data.get("dano_por_turno_veneno", 0)
        player.turnos_buff_defesa = player_data.get("turnos_buff_defesa", 0)
        player.turnos_furia = player_data.get("turnos_furia", 0)
        player.turnos_regeneracao = player_data.get("turnos_regeneracao", 0)

        player.ajudou_marinheiro = player_data.get("ajudou_marinheiro", False)
        if "tutoriais" in player_data:
            player.tutoriais = TutorialFlags.from_dict(player_data["tutoriais"])

        player.arma_equipada = DB_EQUIPAMENTOS.get(player_data.get("arma_equipada"))
        player.armadura_equipada = DB_EQUIPAMENTOS.get(player_data.get("armadura_equipada"))
        player.escudo_equipada = DB_EQUIPAMENTOS.get(player_data.get("escudo_equipada"))

        player.inventario = []
        for item_data in player_data.get("inventario", []):
            item_template = DB_ITENS.get(item_data["nome"])
            if item_template:
                item = deepcopy(item_template)
                item.quantidade = item_data["quantidade"]
                player.inventario.append(item)

        player.habilidades_conhecidas = []
        for skill_name in player_data.get("habilidades_conhecidas", []):
            skill = DB_HABILIDADES.get(skill_name)
            if skill:
                player.habilidades_conhecidas.append(skill)

        return player

    def _create_backup(self) -> None:
        if not self._save_file.exists():
            return

        backup_dir = self._save_dir / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"zorg_save_{timestamp}.json"

        shutil.copy2(self._save_file, backup_file)
        self.logger.debug(f"Backup criado: {backup_file}")

        self._cleanup_old_backups(backup_dir)

    def _cleanup_old_backups(self, backup_dir: Path) -> None:
        max_backups = self._config.get("max_backups", 5)
        backups = sorted(backup_dir.glob("zorg_save_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

        for backup in backups[max_backups:]:
            backup.unlink()
            self.logger.debug(f"Backup antigo removido: {backup}")

    def get_save_info(self) -> Optional[Dict[str, Any]]:
        if not self._save_file.exists():
            return None

        try:
            with open(self._save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            player_data = save_data["player"]
            metadata = save_data.get("metadata", {})

            return {
                "exists": True,
                "player_name": player_data["nome"],
                "level": player_data["nivel"],
                "phase": player_data["fase_atual"],
                "timestamp": metadata.get("timestamp"),
                "game_version": metadata.get("game_version"),
                "file_size": self._save_file.stat().st_size,
            }

        except Exception as e:
            self.logger.error(f"Erro ao ler informações do save: {e}")
            return {
                "exists": True,
                "corrupted": True,
                "error": str(e)
            }

    # === MÉTODOS PARA MÚLTIPLOS SAVES ===

    def get_save_slot_path(self, slot: int) -> Path:
        """Retorna o caminho do arquivo para um slot específico."""
        if slot < 1 or slot > self._max_save_slots:
            raise ValueError(f"Slot deve ser entre 1 e {self._max_save_slots}")
        return self._save_dir / f"zorg_save_slot_{slot}.json"

    def save_to_slot(self, player: Personagem, slot: int, save_name: str = "") -> bool:
        """Salva o jogo em um slot específico."""
        if slot < 1 or slot > self._max_save_slots:
            raise ValueError(f"Slot deve ser entre 1 e {self._max_save_slots}")

        validate_not_none(player, "jogador")

        # Usar o save_name fornecido ou gerar um padrão
        if not save_name:
            save_name = f"Save {slot} - {player.nome} Nv.{player.nivel}"

        try:
            slot_file = self.get_save_slot_path(slot)

            # Criar backup se o slot já existir
            if self._config.get("backup_enabled", True) and slot_file.exists():
                self._create_slot_backup(slot)

            # Adicionar metadata específica do slot
            metadata = {
                "slot": slot,
                "save_name": save_name,
                "timestamp": datetime.now().isoformat(),
                "game_version": "1.0.0",
                "auto_save": False
            }

            save_data = self._prepare_save_data(player, metadata)
            self._validate_save_data(save_data)

            # Salvar no slot específico
            temp_file = slot_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            temp_file.replace(slot_file)

            emit_event(EventType.SAVE_GAME, {
                "slot": slot,
                "save_name": save_name,
                "player_name": player.nome,
                "level": player.nivel,
                "timestamp": metadata["timestamp"]
            })

            self.logger.info(f"Jogo salvo no slot {slot}: {save_name}")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao salvar no slot {slot}: {e}")
            raise SaveLoadError(f"Falha ao salvar no slot {slot}: {e}")

    def load_from_slot(self, slot: int) -> Optional[Personagem]:
        """Carrega o jogo de um slot específico."""
        if slot < 1 or slot > self._max_save_slots:
            raise ValueError(f"Slot deve ser entre 1 e {self._max_save_slots}")

        slot_file = self.get_save_slot_path(slot)
        if not slot_file.exists():
            return None

        try:
            with open(slot_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            self._validate_save_data(save_data)
            player = self._deserialize_player(save_data["player"])

            emit_event(EventType.LOAD_GAME, {
                "slot": slot,
                "player_name": player.nome,
                "level": player.nivel,
                "metadata": save_data.get("metadata", {})
            })

            self.logger.info(f"Jogo carregado do slot {slot}: {player.nome}")
            return player

        except Exception as e:
            self.logger.error(f"Erro ao carregar do slot {slot}: {e}")
            raise SaveLoadError(f"Falha ao carregar do slot {slot}: {e}")

    def get_save_slots_info(self) -> List[Dict[str, Any]]:
        """Retorna informações de todos os slots de save."""
        slots_info = []

        for slot in range(1, self._max_save_slots + 1):
            slot_info = self.get_slot_info(slot)
            slots_info.append(slot_info)

        return slots_info

    def get_slot_info(self, slot: int) -> Dict[str, Any]:
        """Retorna informações de um slot específico."""
        if slot < 1 or slot > self._max_save_slots:
            raise ValueError(f"Slot deve ser entre 1 e {self._max_save_slots}")

        slot_file = self.get_save_slot_path(slot)

        if not slot_file.exists():
            return {
                "slot": slot,
                "exists": False,
                "empty": True
            }

        try:
            with open(slot_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            player_data = save_data["player"]
            metadata = save_data.get("metadata", {})

            return {
                "slot": slot,
                "exists": True,
                "empty": False,
                "save_name": metadata.get("save_name", f"Save {slot}"),
                "player_name": player_data["nome"],
                "level": player_data["nivel"],
                "phase": player_data["fase_atual"],
                "playtime": player_data.get("tempo_jogado", 0),
                "timestamp": metadata.get("timestamp"),
                "auto_save": metadata.get("auto_save", False),
                "file_size": slot_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(slot_file.stat().st_mtime).isoformat()
            }

        except Exception as e:
            self.logger.error(f"Erro ao ler slot {slot}: {e}")
            return {
                "slot": slot,
                "exists": True,
                "empty": False,
                "corrupted": True,
                "error": str(e)
            }

    def delete_save_slot(self, slot: int) -> bool:
        """Deleta um slot de save específico."""
        if slot < 1 or slot > self._max_save_slots:
            raise ValueError(f"Slot deve ser entre 1 e {self._max_save_slots}")

        slot_file = self.get_save_slot_path(slot)

        if not slot_file.exists():
            return True  # Já está deletado

        try:
            # Criar backup antes de deletar
            if self._config.get("backup_enabled", True):
                self._create_slot_backup(slot)

            slot_file.unlink()
            self.logger.info(f"Slot {slot} deletado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"Erro ao deletar slot {slot}: {e}")
            return False

    def _create_slot_backup(self, slot: int) -> None:
        """Cria backup de um slot específico."""
        slot_file = self.get_save_slot_path(slot)
        if not slot_file.exists():
            return

        backup_dir = self._save_dir / "slot_backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"slot_{slot}_backup_{timestamp}.json"

        shutil.copy2(slot_file, backup_file)
        self.logger.debug(f"Backup do slot {slot} criado: {backup_file}")

        # Limpar backups antigos deste slot
        self._cleanup_slot_backups(backup_dir, slot)

    def _cleanup_slot_backups(self, backup_dir: Path, slot: int) -> None:
        """Limpa backups antigos de um slot específico."""
        max_backups = self._config.get("max_backups", 3)
        pattern = f"slot_{slot}_backup_*.json"
        backups = sorted(backup_dir.glob(pattern), key=lambda x: x.stat().st_mtime, reverse=True)

        for backup in backups[max_backups:]:
            backup.unlink()
            self.logger.debug(f"Backup antigo do slot {slot} removido: {backup}")

    def delete_save(self) -> bool:
        if not self._save_file.exists():
            return True

        try:
            self._save_file.unlink()
            self.logger.info("Arquivo de save removido")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao remover save: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        backup_dir = self._save_dir / "backups"
        if not backup_dir.exists():
            return []

        backups = []
        for backup_file in sorted(backup_dir.glob("zorg_save_*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size
                })
            except Exception as e:
                self.logger.warning(f"Erro ao ler backup {backup_file}: {e}")

        return backups


_save_manager = SaveManager()


def get_save_manager() -> SaveManager:
    if not _save_manager.is_initialized():
        _save_manager.initialize()
    return _save_manager