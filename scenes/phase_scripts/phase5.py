def run_phase_5():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 5: O Navio Vingança Espectral.
    """

    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 5: O NAVIO VINGANÇA ESPECTRAL",
        "segments": [
            "Uma névoa sobrenatural ergue-se do nada, engolindo o mundo. O ar fica gelado.",
            "E então ela vê... um navio que não deveria existir. O 'Vingança Espectral' flutua sobre as águas como um pesadelo materializado, com velas rasgadas que tremulam sem vento.",
            "Com o coração acelerado, Manu sobe a prancha que se materializa do navio. No momento em que pisa no convés, a prancha desfaz-se em pó. Não há volta.",
        ],
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "O silêncio no navio é absoluto. Uma figura translúcida materializa-se lentamente: um Pirata Espectral.",
            "'Mortal... em nosso navio...', ele sussurra com uma voz que não vem de lugar nenhum. 'Este lugar... é para os condenados... presos para sempre no mar de lágrimas...'",
            "'Perdão... mortal... mas ordens são ordens... mesmo na morte...'",
        ],
    }

    # Evento 3: Combate com o Pirata Espectral
    yield {
        "type": "combat",
        "enemy_name": "Pirata Espectral",
        "victory_text": "O pirata desvanece-se com um suspiro de alívio, finalmente livre da sua maldição.",
    }

    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "Mais fundo no navio, uma figura de postura ereta bloqueia a porta da cabine do capitão. Um Oficial Fantasma.",
            "'Alto aí', ele diz com voz firme. 'Ainda tenho a minha honra, mesmo na morte. Eu também amei uma vez, antes da maldição nos tomar.'",
            "'Mas o meu dever obriga-me a proteger o meu capitão. Lute com honra, como o seu coração ordena.'",
        ],
    }

    # Evento 5: Combate com o Oficial Fantasma
    yield {
        "type": "combat",
        "enemy_name": "Oficial Fantasma",
        "victory_text": "O oficial faz uma vénia respeitosa antes de desaparecer na névoa.",
    }

    # Evento 6: Texto antes do chefe da fase
    yield {
        "type": "show_text",
        "segments": [
            "A porta da cabine abre-se com um lamento que ecoa por séculos. Lá dentro, cercado por tesouros inúteis, o Capitão Ossos-Secos ergue-se.",
            "'Ah... uma visita. Sabe qual foi o meu crime?', ele pergunta, melancólico. 'Matei por ganância. Destruí o amor... e agora o amor vem libertar-me.'",
            "'Venha então... dê-me o descanso que mereço.'",
        ],
    }

    # Evento 7: Combate com o Capitão Ossos-Secos
    yield {
        "type": "combat",
        "enemy_name": "Capitao Ossos-Secos",
        "victory_text": "O Capitão sorri enquanto se desfaz em luz. 'Obrigado...', ele sussurra. 'Que o seu amor... seja eterno...'",
    }

    # Evento 8: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 5",
        "segments": [
            "Com a tripulação finalmente em paz, a névoa dissipa-se. No baú do capitão, Manu encontra uma Cimitarra Enfeitiçada.",
            "A bússola de Zorg, também no baú, agora aponta para leste, para uma ilha sombria onde a Torre do Ponteiro Nulo perfura os céus.",
            "'Estou a chegar, Ramon... estou a chegar...'",
        ],
    }

    # Evento 9: Dar a recompensa ao jogador (esta lógica será implementada depois)
    yield {"type": "grant_reward", "equipment": "Cimitarra Enfeiticada"}

    # Evento 10: Fim da fase
    yield {"type": "phase_end"}
