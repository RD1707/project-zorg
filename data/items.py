from core.models import Item
DB_ITENS = {
    "Pocao de Cura": Item(
        nome="Pocao de Cura",
        descricao="Uma pocao simples que restaura 30 pontos de vida.",
        cura_hp=30,
        cura_mp=0,
        cura_veneno=0, 
        preco_venda=25
    ),
    "Antidoto": Item(
        nome="Antidoto",
        descricao="Uma erva amarga que neutraliza venenos.",
        cura_hp=0,
        cura_mp=0,
        cura_veneno=1, 
        preco_venda=40
    ),
    "Pocao de Mana": Item(
        nome="Pocao de Mana",
        descricao="Um liquido azul cintilante que restaura 25 pontos de mana.",
        cura_hp=0,
        cura_mp=25,
        cura_veneno=0,
        preco_venda=30
    )
}