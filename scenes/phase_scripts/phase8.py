def run_phase_8():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 8: O Saguão Sombrio.
    """
    
    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 8: O SAGUÃO SOMBRIO",
        "segments": [
            "Os portões massivos abrem-se com um rangido que ecoa como um gemido. Manu pisa no limiar do inferno.",
            "O ar aqui dentro é frio como gelo e pesado como chumbo. O saguão estende-se como uma catedral do mal, com pilares negros como ossos gigantescos.",
            "Por toda parte, estátuas de guerreiros e monstros observam-na em silêncio eterno. Algo está errado."
        ]
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "*CRACK*. Um som de pedra a rachar. Uma das estátuas moveu-se! Fragmentos de pedra caem e da poeira nasce o pesadelo: uma Gárgula de Pedra!",
            "Asas de granito estendem-se, e os seus olhos são brasas vermelhas. 'INTRUSA!', a sua voz ecoa como rocha a quebrar. 'VOCÊ PROFANA O SANTUÁRIO DO MESTRE!'"
        ]
    }

    # Evento 3: Combate com a Gárgula
    yield {
        "type": "combat",
        "enemy_name": "Gargula de Pedra",
        "victory_text": "A gárgula despedaça-se, mas o eco da sua queda desperta algo muito pior."
    }
    
    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "*CLANK... CLANK... CLANK...* O som de metal pesado a mover-se lentamente. Do fundo do saguão, uma presença titânica ergue-se.",
            "UM GOLEM DE FERRO! Três metros de músculos de aço forjado, construído para uma única função: DESTRUIR.",
            "Os seus olhos acendem-se como fornalhas. 'SISTEMA... ATIVADO... PROTOCOLO... ELIMINAR... INTRUSO...'"
        ]
    }

    # Evento 5: Combate com o Golem de Ferro
    yield {
        "type": "combat",
        "enemy_name": "Golem de Ferro",
        "victory_text": "*BOOOOOOM!* O Golem tomba como uma montanha. O estrondo abala toda a Torre."
    }

    # Evento 6: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 8",
        "segments": [
            "O silêncio da vitória retorna ao saguão. Nos destroços fumegantes do guardião caído, uma Poção de Mana reluz com uma luz azul.",
            "À frente, uma escadaria em espiral perde-se na escuridão, rumo à Biblioteca Proibida, onde os segredos mais sombrios de Zorg aguardam.",
            "'Estou a chegar, Ramon...', Manu sussurra. 'Cada degrau leva-me mais perto de ti!'"
        ]
    }

    # Evento 7: Fim da fase
    yield {
        "type": "phase_end"
    }