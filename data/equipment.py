from core.models import Equipamento, TipoEquipamento

DB_EQUIPAMENTOS = {
    "Adaga Enferrujada": Equipamento(
        nome="Adaga Enferrujada",
        tipo=TipoEquipamento.ARMA,
        bonus_ataque=3,
        bonus_defesa=0,
        descricao="Uma adaga antiga e oxidada, mas ainda afiada.",
        preco=10,
        raridade="comum"
    ),
    "Espada Curta": Equipamento(
        nome="Espada Curta",
        tipo=TipoEquipamento.ARMA,
        bonus_ataque=6,
        bonus_defesa=0,
        descricao="Uma espada bem balanceada, ideal para combate ágil.",
        preco=50,
        raridade="comum"
    ),
    "Cimitarra Enfeiticada": Equipamento(
        nome="Cimitarra Enfeiticada",
        tipo=TipoEquipamento.ARMA,
        bonus_ataque=10,
        bonus_defesa=0,
        descricao="Uma lâmina curva com runas mágicas que brilham fracamente.",
        preco=150,
        raridade="raro"
    ),
    "Espada Runica": Equipamento(
        nome="Espada Runica",
        tipo=TipoEquipamento.ARMA,
        bonus_ataque=15,
        bonus_defesa=0,
        descricao="Uma espada forjada com magia ancestral, pulsa com poder.",
        preco=400,
        raridade="épico"
    ),

    "Roupas de Pano": Equipamento(
        nome="Roupas de Pano",
        tipo=TipoEquipamento.ARMADURA,
        bonus_ataque=0,
        bonus_defesa=1,
        descricao="Roupas simples que oferecem proteção mínima.",
        preco=5,
        raridade="comum"
    ),
    "Armadura de Couro": Equipamento(
        nome="Armadura de Couro",
        tipo=TipoEquipamento.ARMADURA,
        bonus_ataque=0,
        bonus_defesa=3,
        descricao="Armadura flexível feita de couro curtido resistente.",
        preco=25,
        raridade="comum"
    ),
    "Armadura de Aco Reforcado": Equipamento(
        nome="Armadura de Aco Reforcado",
        tipo=TipoEquipamento.ARMADURA,
        bonus_ataque=0,
        bonus_defesa=6,
        descricao="Armadura pesada de aço com reforços estratégicos.",
        preco=100,
        raridade="raro"
    ),

    "Escudo de Madeira": Equipamento(
        nome="Escudo de Madeira",
        tipo=TipoEquipamento.ESCUDO,
        bonus_ataque=0,
        bonus_defesa=2,
        descricao="Um escudo simples mas eficaz, feito de madeira robusta.",
        preco=15,
        raridade="comum"
    ),
    "Escudo de Bronze": Equipamento(
        nome="Escudo de Bronze",
        tipo=TipoEquipamento.ESCUDO,
        bonus_ataque=0,
        bonus_defesa=4,
        descricao="Escudo metálico que oferece boa proteção.",
        preco=40,
        raridade="comum"
    ),
    "Escudo de Aco": Equipamento(
        nome="Escudo de Aco",
        tipo=TipoEquipamento.ESCUDO,
        bonus_ataque=0,
        bonus_defesa=7,
        descricao="Um escudo pesado de aço, quase indestrutível.",
        preco=120,
        raridade="raro"
    )
}