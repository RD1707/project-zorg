def run_phase_10():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 10: O Topo da Torre.
    """

    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 10: O TOPO DA TORRE",
        "segments": [
            "O momento chegou. Manu chega ao topo. O céu aqui não é céu, é caos puro. Raios roxos crepitam numa tempestade eterna.",
            "E no centro... RAMON! Ele está lá, a sua forma a piscar dentro de uma jaula de código vivo, consciente mas impotente.",
            "'RAMON!', Manu grita com toda a sua alma. Mas uma risada sinistra ecoa: 'Então... a variável inesperada chegou ao fim da execução...'",
        ],
    }

    # Evento 2: O confronto com Zorg
    yield {
        "type": "show_text",
        "segments": [
            "Zorg vira-se lentamente, os seus olhos ardem com poder absoluto. 'Impressionante, pequena anomalia. Mas todo o LOOP tem um fim... e este termina COMIGO!'",
            "'O único fim aqui será o SEU, Zorg!', Manu grita, erguendo a Espada Rúnica, que brilha com uma luz pura.",
            "'HAHAHA! AMOR?', Zorg ri. 'Não há amor! Há apenas CÓDIGO! Há apenas PODER! E todo o poder do universo é MEU!'",
        ],
    }

    # Evento 3: A Batalha Final
    yield {
        "type": "combat",
        "enemy_name": "Feiticeiro Zorg",
        "victory_text": "'NÃÃÃÃOOOOO!', Zorg grita. 'IMPOSSÍVEL! O AMOR NÃO PODE SER MAIS FORTE QUE O PODER!' Com um grito final, ele desintegra-se, como dados corrompidos a serem apagados para sempre.",
    }

    # Evento 4: O reencontro
    yield {
        "type": "show_text",
        "segments": [
            "A jaula de código ao redor de Ramon estilhaça-se! Ele está livre!",
            "'Manu...', a sua voz é como música. 'Eu sabia... no fundo do meu coração, eu sabia que você viria. Que o nosso amor era mais forte.'",
            "'Não havia nenhuma outra possibilidade, meu amor.' Lágrimas de alegria correm pelo rosto de Manu. 'Nenhuma força no universo poderia impedir-me.'",
        ],
    }

    # Evento 5: O final
    yield {
        "type": "show_text",
        "title": "FIM DE JOGO",
        "segments": [
            "Eles abraçam-se, e nesse abraço, o mundo transforma-se. A tempestade acalma-se, as nuvens negras dispersam-se, e do horizonte nasce o sol mais belo já visto.",
            "A Torre do Ponteiro Nulo desmorona, pedra por pedra, maldição por maldição, até que reste apenas o amor.",
            "Juntos, como sempre deveria ter sido. Fim.",
        ],
    }

    # Evento 6: Fim do jogo
    yield {"type": "game_end"}
