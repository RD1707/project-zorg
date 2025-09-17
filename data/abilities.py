# Importa a classe Habilidade e tipos do nosso módulo de modelos.
from core.models import Habilidade, TipoHabilidade

# Dicionário com todas as habilidades do jogo.
DB_HABILIDADES = {
    "Golpe Poderoso": Habilidade(
        nome="Golpe Poderoso",
        descricao="Um ataque físico concentrado que causa mais dano.",
        custo_mp=10,
        tipo=TipoHabilidade.ATAQUE,
        valor_efeito=20,
        nivel_requerido=1,
        elemento="físico"
    ),
    "Lanca de Gelo": Habilidade(
        nome="Lanca de Gelo",
        descricao="Cria um espinho de gelo que perfura o inimigo e pode congelar.",
        custo_mp=12,
        tipo=TipoHabilidade.ATAQUE,
        valor_efeito=25
    ),
    "Toque Restaurador": Habilidade(
        nome="Toque Restaurador",
        descricao="Concentra energia para curar ferimentos.",
        custo_mp=15,
        tipo=TipoHabilidade.CURA,
        valor_efeito=50,
        nivel_requerido=2,
        elemento="divino"
    ),
    "Postura Defensiva": Habilidade(
        nome="Postura Defensiva",
        descricao="Aumenta a defesa por 3 turnos.",
        custo_mp=8,
        tipo=TipoHabilidade.BUFF_DEFESA,
        valor_efeito=10,
        nivel_requerido=1,
        elemento="neutro"
    ),
    "Furia Berserker": Habilidade(
        nome="Furia Berserker",
        descricao="Entra em fúria, aumentando ataque por 4 turnos mas perdendo defesa.",
        custo_mp=20,
        tipo=TipoHabilidade.FURIA,
        valor_efeito=0 # O efeito é tratado na lógica de combate, não por um valor direto.
    ),
    "Regeneracao Vital": Habilidade(
        nome="Regeneracao Vital",
        descricao="Ativa regeneração que cura HP a cada turno por 5 turnos.",
        custo_mp=25,
        tipo=TipoHabilidade.REGENERACAO,
        valor_efeito=0
    ),
    "Golpe Flamejante": Habilidade(
        nome="Golpe Flamejante",
        descricao="Ataque de fogo que causa dano contínuo.",
        custo_mp=18,
        tipo=TipoHabilidade.ATAQUE,
        valor_efeito=30
    ),
    "Combo Devastador": Habilidade(
        nome="Combo Devastador",
        descricao="Ataque especial que ganha poder com combos consecutivos.",
        custo_mp=15,
        tipo=TipoHabilidade.COMBO,
        valor_efeito=0
    ),
    "Lâmina Sombria": Habilidade(
        nome="Lâmina Sombria",
        descricao="Ataque das sombras com alta chance de crítico.",
        custo_mp=14,
        tipo=TipoHabilidade.ATAQUE,
        valor_efeito=22
    ),
    "Escudo de Luz": Habilidade(
        nome="Escudo de Luz",
        descricao="Cria barreira mágica que absorve dano e cura simultaneamente.",
        custo_mp=22,
        tipo=TipoHabilidade.CURA,
        valor_efeito=30
    ),
    "Rajada Arcana": Habilidade(
        nome="Rajada Arcana",
        descricao="Múltiplos projéteis mágicos com dano variável.",
        custo_mp=16,
        tipo=TipoHabilidade.ATAQUE,
        valor_efeito=0 # Dano é calculado dinamicamente
    ),
    "Benção da Natureza": Habilidade(
        nome="Benção da Natureza",
        descricao="Remove todos os debuffs e ativa regeneração.",
        custo_mp=20,
        tipo=TipoHabilidade.CURA,
        valor_efeito=25
    )
}