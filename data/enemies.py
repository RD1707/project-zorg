from core.models import Personagem, Habilidade
from data.abilities import DB_HABILIDADES

DB_INIMIGOS = {
    "Goblin Verdejante": Personagem(
        nome="Goblin Verdejante", hp_max=20, mp_max=10, ataque_base=6, defesa_base=2,
        xp_dado=40, ouro_dado=15, dano_por_turno_veneno=0
    ),
    "Lobo das Sombras": Personagem(
        nome="Lobo das Sombras", hp_max=35, mp_max=0, ataque_base=9, defesa_base=3,
        xp_dado=65, ouro_dado=25
    ),
    "Garg, o Chefe Goblin": Personagem(
        nome="Garg, o Chefe Goblin", hp_max=70, mp_max=20, ataque_base=12, defesa_base=6,
        xp_dado=150, ouro_dado=80,
        habilidades_conhecidas=[DB_HABILIDADES["Golpe Poderoso"]]
    ),
    "Morcego Gigante": Personagem(
        nome="Morcego Gigante", hp_max=40, mp_max=0, ataque_base=14, defesa_base=2,
        xp_dado=80, ouro_dado=30
    ),
    "Slime Acido": Personagem(
        nome="Slime Acido", hp_max=80, mp_max=0, ataque_base=8, defesa_base=8,
        xp_dado=100, ouro_dado=50
    ),
    "Troll da Caverna": Personagem(
        nome="Troll da Caverna", hp_max=120, mp_max=30, ataque_base=16, defesa_base=10,
        xp_dado=300, ouro_dado=150,
        habilidades_conhecidas=[DB_HABILIDADES["Regeneracao Vital"]]
    ),
    "Aranha Peconhenta": Personagem(
        nome="Aranha Peconhenta", hp_max=60, mp_max=0, ataque_base=13, defesa_base=7,
        xp_dado=150, ouro_dado=60, dano_por_turno_veneno=4
    ),
    "Homem-Lagarto Xama": Personagem(
        nome="Homem-Lagarto Xama", hp_max=90, mp_max=40, ataque_base=15, defesa_base=10,
        xp_dado=220, ouro_dado=110, dano_por_turno_veneno=6,
        habilidades_conhecidas=[DB_HABILIDADES["Toque Restaurador"], DB_HABILIDADES["Lanca de Gelo"]]
    ),
    "Hidra do Pantano": Personagem(
        nome="Hidra do Pantano", hp_max=180, mp_max=0, ataque_base=20, defesa_base=13,
        xp_dado=500, ouro_dado=400, dano_por_turno_veneno=8
    ),
    "Pirata Espectral": Personagem(
        nome="Pirata Espectral", hp_max=100, mp_max=0, ataque_base=18, defesa_base=12,
        xp_dado=250, ouro_dado=120
    ),
    "Oficial Fantasma": Personagem(
        nome="Oficial Fantasma", hp_max=140, mp_max=0, ataque_base=22, defesa_base=15,
        xp_dado=350, ouro_dado=180
    ),
    "Capitao Ossos-Secos": Personagem(
        nome="Capitao Ossos-Secos", hp_max=250, mp_max=50, ataque_base=28, defesa_base=18,
        xp_dado=800, ouro_dado=500,
        habilidades_conhecidas=[DB_HABILIDADES["Lâmina Sombria"]]
    ),
    "Caranguejo de Concha-Rocha": Personagem(
        nome="Caranguejo de Concha-Rocha", hp_max=80, mp_max=20, ataque_base=20, defesa_base=25,
        xp_dado=300, ouro_dado=150,
        habilidades_conhecidas=[DB_HABILIDADES["Postura Defensiva"]]
    ),
    "Sereia Agourenta": Personagem(
        nome="Sereia Agourenta", hp_max=120, mp_max=60, ataque_base=30, defesa_base=10,
        xp_dado=400, ouro_dado=200,
        habilidades_conhecidas=[DB_HABILIDADES["Rajada Arcana"]]
    ),
    "Kraken Jovem": Personagem(
        nome="Kraken Jovem", hp_max=350, mp_max=0, ataque_base=32, defesa_base=22,
        xp_dado=1200, ouro_dado=800
    ),
    "Harpia Esguia": Personagem(
        nome="Harpia Esguia", hp_max=150, mp_max=0, ataque_base=35, defesa_base=15,
        xp_dado=500, ouro_dado=250
    ),
    "Grifo Alfa": Personagem(
        nome="Grifo Alfa", hp_max=400, mp_max=80, ataque_base=38, defesa_base=28,
        xp_dado=1500, ouro_dado=1000,
        habilidades_conhecidas=[DB_HABILIDADES["Benção da Natureza"]]
    ),
    "Gargula de Pedra": Personagem(
        nome="Gargula de Pedra", hp_max=120, mp_max=0, ataque_base=30, defesa_base=40,
        xp_dado=600, ouro_dado=300
    ),
    "Golem de Ferro": Personagem(
        nome="Golem de Ferro", hp_max=280, mp_max=0, ataque_base=40, defesa_base=35,
        xp_dado=1800, ouro_dado=1200
    ),
    "Livro Amaldicoado": Personagem(
        nome="Livro Amaldicoado", hp_max=180, mp_max=100, ataque_base=42, defesa_base=20,
        xp_dado=900, ouro_dado=450,
        habilidades_conhecidas=[DB_HABILIDADES["Golpe Flamejante"]]
    ),
    "Mago Sombrio": Personagem(
        nome="Mago Sombrio", hp_max=220, mp_max=150, ataque_base=50, defesa_base=25,
        xp_dado=2500, ouro_dado=1500,
        habilidades_conhecidas=[DB_HABILIDADES["Lanca de Gelo"], DB_HABILIDADES["Escudo de Luz"]]
    ),
    "Feiticeiro Zorg": Personagem(
        nome="Feiticeiro Zorg", hp_max=700, mp_max=200, ataque_base=55, defesa_base=40,
        xp_dado=10000, ouro_dado=5000, dano_por_turno_veneno=10,
        habilidades_conhecidas=[DB_HABILIDADES["Golpe Flamejante"], DB_HABILIDADES["Lâmina Sombria"], DB_HABILIDADES["Toque Restaurador"]]
    )
}