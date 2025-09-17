def run_phase_1():
    """
    Este é um gerador que controla o fluxo de eventos da Fase 1.
    Ele 'yield' (produz) um evento de cada vez (ex: 'show_text', 'combat'),
    permitindo que a interface do usuário processe cada um separadamente.
    """
    
    yield {
        "type": "show_text",
        "title": "FASE 1: A FLOREsta DOS SUSSURROS",
        "segments": [
            "Manu aperta o medalhão no peito - um presente de Ramon. Sua última lembrança dele. 'Eu vou te encontrar, meu amor... Prometo.', ela sussurra para a floresta sombria.",
            "A floresta parece viva, sussurrando segredos antigos. O amor que sente por Ramon arde como uma chama inextinguível em seu peito.",
            "De repente, um arbusto range. Um ser repugnante salta das moitas - pele verde escamosa, olhos famintos de maldade!",
            "'Carne fresca! Zorg vai adorar seus ossos!', rosna o Goblin Verdejante. Manu sente o medalhão aquecer. Ramon... ela lutará por ele!"
        ]
    }

    yield {
        "type": "combat",
        "enemy_name": "Goblin Verdejante",
        "victory_text": "Manu olha para suas mãos trêmulas. Nunca havia ferido ninguém antes. Mas o pensamento de Ramon aprisionado endurece seu coração. 'Nada vai me impedir de salvá-lo.'"
    }
    
    yield {
        "type": "show_text",
        "segments": [
            "Mais profundo na floresta, as sombras ganham vida própria. Um uivo cortante perfura a noite.",
            "Olhos vermelhos como brasas emergem da escuridão. Um Lobo das Sombras rosna baixo, como se sussurrasse: 'Você não pertence aqui...'",
            "'Talvez não', Manu responde, 'mas Ramon precisa de mim.'"
        ]
    }

    yield {
        "type": "combat",
        "enemy_name": "Lobo das Sombras",
        "victory_text": "A coragem de Manu cresce a cada vitória. O medo dá lugar à determinação."
    }

    yield {
        "type": "show_text",
        "segments": [
            "Em uma clareira banhada por uma lua vermelha, uma figura massiva bloqueia o caminho.",
            "'EU SOU GARG! NINGUÉM PASSA!', berra o chefe goblin, batendo um porrete no chão. 'Esta floresta pertence ao GRANDE ZORG!'",
            "Manu fecha os olhos e vê Ramon sorrindo para ela. 'Ramon está esperando por mim', ela diz, com voz firme como aço. 'E nem você, nem Zorg, nem o próprio inferno vão me parar.'"
        ]
    }

    yield {
        "type": "combat",
        "enemy_name": "Garg, o Chefe Goblin",
        "victory_text": "Com Garg derrotado, a floresta suspira de alívio. As sombras recuam."
    }

    yield {
        "type": "show_text",
        "title": "FIM DA FASE 1",
        "segments": [
            "Ao lado do goblin caído, algo brilha. Uma espada curta, ainda afiada. Nos pertences de Garg, Manu encontra também um mapa esbocado em couro velho.",
            "Ele aponta para um único destino: as Cavernas Ecoantes.",
            "Manu guarda o mapa e olha para o céu noturno. 'Estou chegando, meu amor. Um passo de cada vez.'"
        ]
    }

    yield {
        "type": "grant_reward",
        "equipment": "Espada Curta"
    }

    yield {
        "type": "phase_end"
    }