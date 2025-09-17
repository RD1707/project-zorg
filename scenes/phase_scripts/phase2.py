def run_phase_2():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 2: As Cavernas Ecoantes.
    """
    
    yield {
        "type": "show_text",
        "title": "FASE 2: AS CAVERNAS ECOANTES",
        "segments": [
            "Manu segura o mapa de Garg com mãos trêmulas. A caverna à sua frente é uma boca negra e silenciosa.",
            "O eco de sua própria respiração retorna distorcido. As paredes parecem fechar-se a cada passo, mas o pensamento em Ramon a impulsiona para a escuridão."
        ]
    }

    yield {
        "type": "show_text",
        "segments": [
            "Um sussurro de asas corta o silêncio sepulcral. Manu levanta a espada, mas a luz da sua lâmina rúnica mal perfura a escuridão.",
            "De repente, algo imenso despenca das sombras! Um Morcego Gigante, com olhos vermelhos fixos nela, faminto."
        ]
    }

    yield {
        "type": "combat",
        "enemy_name": "Morcego Gigante",
        "victory_text": "Manu encosta-se na parede, ofegante. Por um momento, o medo ameaça consumi-la, mas a lembrança das palavras de Ramon ecoa mais forte: 'Coragem é fazer o que é certo mesmo com medo.'"
    }
    
    yield {
        "type": "show_text",
        "segments": [
            "O túnel estreita-se. As paredes gotejam algo verde e viscoso, e o chão torna-se pegajoso. Vivo.",
            "A própria poça de lodo ergue-se, tomando forma. Um Slime Ácido, cujos olhos são piscinas de ódio líquido, sibila: 'Ninguém... passa... Ramon... é nosso...'",
            "'RAMON É MEU!', Manu grita, com uma fúria que não sabia possuir."
        ]
    }

    # Evento 5: Combate com o Slime Ácido
    yield {
        "type": "combat",
        "enemy_name": "Slime Acido",
        "victory_text": "A cada vitória, a determinação de Manu transforma o medo em força."
    }

    # Evento 6: Texto antes do chefe da fase
    yield {
        "type": "show_text",
        "segments": [
            "A caverna abre-se numa câmara majestosa. Cristais azuis pulsam como corações. No centro, uma sombra colossal ergue-se.",
            "O Troll da Caverna rosna com uma voz que abala as pedras: 'PEQUENA HUMANA... NÃO VAIS PROFANAR... O MEU LAR...'",
            "Manu posiciona-se, com lágrimas nos olhos. 'Eu entendo a sua dor. Mas Ramon é a minha casa. E eu lutarei até ao meu último suspiro por ele!'"
        ]
    }

    # Evento 7: Combate com o chefe da fase
    yield {
        "type": "combat",
        "enemy_name": "Troll da Caverna",
        "victory_text": "O Troll cai como uma montanha. Com um último suspiro, ele sussurra: 'Você... luta... por amor... Eu... compreendo... Pegue... meu presente...'"
    }

    # Evento 8: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 2",
        "segments": [
            "Na parede atrás do Troll, runas antigas brilham com uma nova luz: 'O CAMINHO PARA O MESTRE PASSA PELO VENENO DO PÂNTANO'.",
            "Manu toca as runas quentes e sente o caminho a seguir. 'Obrigada', ela sussurra ao guardião caído. 'Ramon, estou a chegar. As cavernas não me pararam.'"
        ]
    }

    # Evento 9: Dar a recompensa ao jogador (esta lógica será implementada depois)
    yield {
        "type": "grant_reward",
        "equipment": "Armadura de Couro"
    }

    # Evento 10: Fim da fase
    yield {
        "type": "phase_end"
    }