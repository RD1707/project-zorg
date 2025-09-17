import json
from pathlib import Path
from typing import Optional
from copy import deepcopy # Import necessário para a cópia profunda

from core.models import Personagem, TutorialFlags
from data.equipment import DB_EQUIPAMENTOS
from data.items import DB_ITENS
from data.abilities import DB_HABILIDADES

# Define o nome do ficheiro de save
SAVE_FILE_NAME = "zorg_save.json"
SAVE_FILE_PATH = Path.home() / SAVE_FILE_NAME # Salva na pasta do utilizador

def salvar_jogo(jogador: Personagem) -> bool:
    """
    Converte o estado do objeto do jogador para um dicionário e salva-o num ficheiro JSON.
    Retorna True se o salvamento for bem-sucedido, False caso contrário.
    """
    try:
        dados_salvar = {
            "nome": jogador.nome,
            "hp": jogador.hp,
            "hp_max": jogador.hp_max,
            "mp": jogador.mp,
            "mp_max": jogador.mp_max,
            "ataque_base": jogador.ataque_base,
            "defesa_base": jogador.defesa_base,
            "nivel": jogador.nivel,
            "xp": jogador.xp,
            "xp_proximo_nivel": jogador.xp_proximo_nivel,
            "ouro": jogador.ouro,
            "fase_atual": jogador.fase_atual,
            "ajudou_marinheiro": jogador.ajudou_marinheiro,
            "tutoriais": jogador.tutoriais.__dict__,
            
            # Salva apenas os nomes dos equipamentos, itens e habilidades
            "arma_equipada": jogador.arma_equipada.nome if jogador.arma_equipada else None,
            "armadura_equipada": jogador.armadura_equipada.nome if jogador.armadura_equipada else None,
            "escudo_equipada": jogador.escudo_equipada.nome if jogador.escudo_equipada else None,
            "inventario": [{"nome": i.nome, "quantidade": i.quantidade} for i in jogador.inventario],
            "habilidades_conhecidas": [h.nome for h in jogador.habilidades_conhecidas],
        }
        
        with open(SAVE_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(dados_salvar, f, indent=4, ensure_ascii=False)
            
        return True
    except Exception:
        return False

def carregar_jogo() -> Optional[Personagem]:
    """
    Lê o ficheiro JSON de save e recria o objeto do jogador.
    Retorna o objeto Personagem se for bem-sucedido, None caso contrário.
    """
    if not SAVE_FILE_PATH.exists():
        return None
        
    try:
        with open(SAVE_FILE_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
        
        # Cria um novo personagem com os dados base
        jogador = Personagem(
            nome=dados["nome"],
            hp_max=dados["hp_max"],
            mp_max=dados["mp_max"],
            ataque_base=dados["ataque_base"],
            defesa_base=dados["defesa_base"]
        )
        
        # Atualiza os atributos variáveis
        jogador.hp = dados["hp"]
        jogador.mp = dados["mp"]
        jogador.nivel = dados["nivel"]
        jogador.xp = dados["xp"]
        jogador.xp_proximo_nivel = dados["xp_proximo_nivel"]
        jogador.ouro = dados["ouro"]
        jogador.fase_atual = dados["fase_atual"]
        jogador.ajudou_marinheiro = dados.get("ajudou_marinheiro", False)
        
        # Carrega os tutoriais
        if "tutoriais" in dados:
            jogador.tutoriais = TutorialFlags(**dados["tutoriais"])

        # Recria os objetos de equipamento, item e habilidade a partir dos nomes
        jogador.arma_equipada = DB_EQUIPAMENTOS.get(dados["arma_equipada"])
        jogador.armadura_equipada = DB_EQUIPAMENTOS.get(dados["armadura_equipada"])
        jogador.escudo_equipada = DB_EQUIPAMENTOS.get(dados["escudo_equipada"])
        
        jogador.inventario = []
        for item_data in dados["inventario"]:
            item_modelo = DB_ITENS.get(item_data["nome"])
            if item_modelo:
                # CORREÇÃO APLICADA: Usa deepcopy para criar uma nova instância do item
                novo_item = deepcopy(item_modelo)
                novo_item.quantidade = item_data["quantidade"]
                jogador.inventario.append(novo_item)
                
        jogador.habilidades_conhecidas = [DB_HABILIDADES.get(hab_nome) for hab_nome in dados["habilidades_conhecidas"] if DB_HABILIDADES.get(hab_nome)]
        
        return jogador
    except Exception:
        return None