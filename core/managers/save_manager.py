"""
Gerenciador de save/load melhorado com backup e validação.
"""
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
from config.settings import get_config, get_save_path
from data.equipment import DB_EQUIPAMENTOS
from data.items import DB_ITENS
from data.abilities import DB_HABILIDADES


class SaveManager(BaseManager):
    """Gerenciador de save/load melhorado."""

    def __init__(self):
        super().__init__("save_manager")
        self._config = get_config("save")
        self._save_dir = get_save_path().parent
        self._save_file = get_save_path()

    def _do_initialize(self) -> None:
        """Inicialização do gerenciador de save."""
        # Garantir que o diretório existe
        self._save_dir.mkdir(exist_ok=True)

    @handle_exceptions(reraise=True)
    def save_game(self, player: Personagem, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Salva o estado do jogo com backup e validação."""
        validate_not_none(player, "jogador")

        try:
            # Criar backup se habilitado
            if self._config.get("backup_enabled", True) and self._save_file.exists():
                self._create_backup()

            # Preparar dados para salvar
            save_data = self._prepare_save_data(player, metadata)

            # Validar dados
            self._validate_save_data(save_data)

            # Salvar arquivo temporário primeiro
            temp_file = self._save_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            # Mover arquivo temporário para o definitivo (operação atômica)
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
        """Carrega o estado do jogo com validação."""
        if not self._save_file.exists():
            self.logger.info("Arquivo de save não encontrado")
            return None

        try:
            # Carregar dados
            with open(self._save_file, "r", encoding="utf-8") as f:
                save_data = json.load(f)

            # Validar dados
            self._validate_save_data(save_data)

            # Reconstruir personagem
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
        except Exception as e:
            self.logger.error(f"Erro ao carregar jogo: {e}")
            raise SaveLoadError(f"Falha ao carregar o jogo: {str(e)}")

    def _prepare_save_data(self, player: Personagem, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara os dados para salvamento."""
        save_data = {
            "version": "1.0.0",
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "game_version": "1.0.0",
                **(metadata or {})
            },
            "player": {
                # Atributos básicos
                "nome": player.nome,
                "hp": player.hp,
                "hp_max": player.hp_max,
                "mp": player.mp,
                "mp_max": player.mp_max,
                "ataque_base": player.ataque_base,
                "defesa_base": player.defesa_base,

                # Progressão
                "nivel": player.nivel,
                "xp": player.xp,
                "xp_proximo_nivel": player.xp_proximo_nivel,
                "ouro": player.ouro,
                "fase_atual": player.fase_atual,

                # Status effects
                "turnos_veneno": player.turnos_veneno,
                "dano_por_turno_veneno": player.dano_por_turno_veneno,
                "turnos_buff_defesa": player.turnos_buff_defesa,
                "turnos_furia": player.turnos_furia,
                "turnos_regeneracao": player.turnos_regeneracao,

                # Flags
                "ajudou_marinheiro": player.ajudou_marinheiro,
                "tutoriais": player.tutoriais.to_dict(),

                # Equipamentos (salvar apenas nomes)
                "arma_equipada": player.arma_equipada.nome if player.arma_equipada else None,
                "armadura_equipada": player.armadura_equipada.nome if player.armadura_equipada else None,
                "escudo_equipada": player.escudo_equipada.nome if player.escudo_equipada else None,

                # Inventário
                "inventario": [
                    {"nome": item.nome, "quantidade": item.quantidade}
                    for item in player.inventario
                ],

                # Habilidades
                "habilidades_conhecidas": [hab.nome for hab in player.habilidades_conhecidas],
            }
        }

        # Adicionar checksum para validação
        checksum_data = json.dumps(save_data["player"], sort_keys=True)
        save_data["checksum"] = hashlib.sha256(checksum_data.encode()).hexdigest()

        return save_data

    def _validate_save_data(self, save_data: Dict[str, Any]) -> None:
        """Valida os dados de save."""
        required_fields = ["version", "metadata", "player", "checksum"]
        for field in required_fields:
            if field not in save_data:
                raise DataValidationError(f"Campo obrigatório '{field}' não encontrado")

        # Validar checksum
        player_data = save_data["player"]
        expected_checksum = save_data["checksum"]
        checksum_data = json.dumps(player_data, sort_keys=True)
        actual_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()

        if expected_checksum != actual_checksum:
            raise DataValidationError("Checksum inválido - dados podem estar corrompidos")

        # Validar campos do jogador
        player_required = ["nome", "hp", "hp_max", "mp", "mp_max", "nivel"]
        for field in player_required:
            if field not in player_data:
                raise DataValidationError(f"Campo do jogador '{field}' não encontrado")

        # Validar valores
        if player_data["hp"] < 0 or player_data["hp"] > player_data["hp_max"]:
            raise DataValidationError("HP inválido")

        if player_data["mp"] < 0 or player_data["mp"] > player_data["mp_max"]:
            raise DataValidationError("MP inválido")

        if player_data["nivel"] < 1:
            raise DataValidationError("Nível inválido")

    def _reconstruct_player(self, save_data: Dict[str, Any]) -> Personagem:
        """Reconstrói o objeto Personagem a partir dos dados salvos."""
        from copy import deepcopy

        player_data = save_data["player"]

        # Criar personagem base
        player = Personagem(
            nome=player_data["nome"],
            hp_max=player_data["hp_max"],
            mp_max=player_data["mp_max"],
            ataque_base=player_data["ataque_base"],
            defesa_base=player_data["defesa_base"]
        )

        # Restaurar atributos variáveis
        player.hp = player_data["hp"]
        player.mp = player_data["mp"]
        player.nivel = player_data["nivel"]
        player.xp = player_data["xp"]
        player.xp_proximo_nivel = player_data["xp_proximo_nivel"]
        player.ouro = player_data["ouro"]
        player.fase_atual = player_data["fase_atual"]

        # Status effects
        player.turnos_veneno = player_data.get("turnos_veneno", 0)
        player.dano_por_turno_veneno = player_data.get("dano_por_turno_veneno", 0)
        player.turnos_buff_defesa = player_data.get("turnos_buff_defesa", 0)
        player.turnos_furia = player_data.get("turnos_furia", 0)
        player.turnos_regeneracao = player_data.get("turnos_regeneracao", 0)

        # Flags
        player.ajudou_marinheiro = player_data.get("ajudou_marinheiro", False)
        if "tutoriais" in player_data:
            player.tutoriais = TutorialFlags.from_dict(player_data["tutoriais"])

        # Equipamentos
        player.arma_equipada = DB_EQUIPAMENTOS.get(player_data.get("arma_equipada"))
        player.armadura_equipada = DB_EQUIPAMENTOS.get(player_data.get("armadura_equipada"))
        player.escudo_equipada = DB_EQUIPAMENTOS.get(player_data.get("escudo_equipada"))

        # Inventário
        player.inventario = []
        for item_data in player_data.get("inventario", []):
            item_template = DB_ITENS.get(item_data["nome"])
            if item_template:
                item = deepcopy(item_template)
                item.quantidade = item_data["quantidade"]
                player.inventario.append(item)

        # Habilidades
        player.habilidades_conhecidas = []
        for skill_name in player_data.get("habilidades_conhecidas", []):
            skill = DB_HABILIDADES.get(skill_name)
            if skill:
                player.habilidades_conhecidas.append(skill)

        return player

    def _create_backup(self) -> None:
        """Cria backup do arquivo de save atual."""
        if not self._save_file.exists():
            return

        backup_dir = self._save_dir / "backups"
        backup_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"zorg_save_{timestamp}.json"

        shutil.copy2(self._save_file, backup_file)
        self.logger.debug(f"Backup criado: {backup_file}")

        # Limpar backups antigos
        self._cleanup_old_backups(backup_dir)

    def _cleanup_old_backups(self, backup_dir: Path) -> None:
        """Remove backups antigos mantendo apenas os mais recentes."""
        max_backups = self._config.get("max_backups", 5)
        backups = sorted(backup_dir.glob("zorg_save_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

        for backup in backups[max_backups:]:
            backup.unlink()
            self.logger.debug(f"Backup antigo removido: {backup}")

    def get_save_info(self) -> Optional[Dict[str, Any]]:
        """Retorna informações sobre o save atual."""
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

    def delete_save(self) -> bool:
        """Remove o arquivo de save."""
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
        """Lista os backups disponíveis."""
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


# Instância global do gerenciador de save
_save_manager = SaveManager()


def get_save_manager() -> SaveManager:
    """Retorna a instância global do gerenciador de save."""
    if not _save_manager.is_initialized():
        _save_manager.initialize()
    return _save_manager