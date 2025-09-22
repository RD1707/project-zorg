def run_phase_3():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 3: O Pântano Sombrio de Zorg.
    """

    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 3: O PÂNTANO SOMBRIO DE ZORG",
        "segments": [
            "O ar muda. Torna-se denso, venenoso. Manu sente a presença de Zorg em cada árvore retorcida, em cada poça de água putrefacta.",
            "Pela primeira vez, ela chora. Todo o medo, toda a dor, toda a saudade explodem de uma vez. 'Ramon... por favor... dá-me forças...'",
        ],
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "Do alto das árvores, algo move-se. Oito pernas negras como a noite. Uma Aranha Peçonhenta gigante desce lentamente da sua teia.",
            "Seus olhos múltiplos reflectem o desespero de Manu. 'Sssua dor é deliciosssa...', ela sibila. 'Deixe-me acabar com ssseu ssofrimento...'",
            "'Não!', Manu grita, enxugando as lágrimas. 'A minha dor torna-me forte! Ramon espera por mim!'",
        ],
    }

    # Evento 3: Combate com a Aranha Peçonhenta
    yield {
        "type": "combat",
        "enemy_name": "Aranha Peconhenta",
        "victory_text": "A coragem de Manu, nascida do seu amor, queima mais forte que qualquer veneno.",
    }

    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "Manu avança pela água, a coragem renovada. Das águas turvas, emerge um Homem-Lagarto Xamã, com um cajado de ossos na mão.",
            "'Você traz mais dor ao pântano, criança humana...', ele sibila. 'Zorg prometeu-nos que a dor cessaria quando Ramon fosse dele para sempre.'",
            "'Ramon nunca será de Zorg!', Manu declara. 'Ele é o meu coração, a minha alma, a minha razão de viver!'",
        ],
    }

    # Evento 5: Combate com o Homem-Lagarto Xamã
    yield {
        "type": "combat",
        "enemy_name": "Homem-Lagarto Xama",
        "victory_text": "Cada inimigo que serve Zorg apenas reforça a convicção de Manu.",
    }

    # Evento 6: Texto antes do chefe da fase
    yield {
        "type": "show_text",
        "segments": [
            "No coração do pântano, as águas borbulham violentamente. Múltiplas cabeças emergem da lagoa - a lendária Hidra do Pântano!",
            "'MILÉNIOS A PROTEGER ESTE LUGAR!', as cabeças rugem em uníssono. 'NENHUM AMOR SOBREVIVE AO VENENO DE ZORG!'",
            "Manu sorri. 'Não é só amor. É DEVOÇÃO ETERNA. E nem toda a maldade de Zorg pode quebrar isso!'",
        ],
    }

    # Evento 7: Combate com a Hidra
    yield {
        "type": "combat",
        "enemy_name": "Hidra do Pantano",
        "victory_text": "A Hidra tomba. Com a sua queda, o pântano suspira de alívio. As águas tornam-se mais claras, o ar menos pesado.",
    }

    # Evento 8: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 3",
        "segments": [
            "Uma tabuleta de pedra emerge das águas agora limpas: 'NULLHAVEN - CIDADE DO REFÚGIO'. Manu sente esperança pela primeira vez em dias.",
            "Ela olha para o medalhão, que agora brilha com um calor reconfortante. 'Ramon, estou a tornar-me a heroína que tu sempre disseste que eu era.'",
        ],
    }

    # Evento 9: Dar a recompensa ao jogador (esta lógica será implementada depois)
    yield {"type": "grant_reward", "equipment": "Escudo de Bronze"}

    # Evento 10: Fim da fase
    yield {"type": "phase_end"}
