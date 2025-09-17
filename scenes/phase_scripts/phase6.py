def run_phase_6():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 6: As Praias Rochosas.
    """
    
    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 6: AS PRAIAS ROCHOSAS",
        "segments": [
            "Finalmente, os pés de Manu tocam a areia negra da ilha amaldiçoada. A areia vulcânica sussurra segredos sombrios sob as suas botas.",
            "E lá está ela... A TORRE DO PONTEIRO NULO. Ela perfura o céu como uma agulha de pesadelo. No topo, está Ramon.",
            "'Aguenta, meu amor', ela sussurra ao vento salgado. 'Este pesadelo está quase no fim.'"
        ]
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "Mas Zorg não deixaria a sua fortaleza desprotegida. A areia treme e uma criatura ancestral emerge, pedra viva nascida do próprio magma.",
            "Um Caranguejo de Concha-Rocha, guardião milenar desta praia, ergue as suas garras de obsidiana."
        ]
    }

    # Evento 3: Combate com o Caranguejo de Concha-Rocha
    yield {
        "type": "combat",
        "enemy_name": "Caranguejo de Concha-Rocha",
        "victory_text": "O caranguejo desfaz-se em fragmentos de rocha, mas o eco da batalha acorda algo mais sinistro."
    }
    
    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "Uma melodia, bela e terrivelmente errada, flutua sobre as ondas. Numa rocha, uma Sereia Agourenta, corrompida pela magia de Zorg, revela-se.",
            "A sua beleza é uma armadilha mortal. 'Mais uma alma perdida...', ela canta. 'O seu amado morrerá enquanto você se afoga no meu canto!'"
        ]
    }

    # Evento 5: Combate com a Sereia Agourenta
    yield {
        "type": "combat",
        "enemy_name": "Sereia Agourenta",
        "victory_text": "O canto mortal cessa, mas as próprias ondas agitam-se violentamente."
    }

    # Evento 6: Texto antes do chefe da fase
    yield {
        "type": "show_text",
        "segments": [
            "Das profundezas, uma lenda viva surge! Tentáculos massivos como torres. Um Kraken Jovem, o guardião supremo das águas de Zorg!",
            "A sua voz ecoa como um trovão submarino: 'JOVEM MANU... VOCÊ OUSA PISAR EM TERRITÓRIO SAGRADO? PROVE QUE O SEU AMOR VALE MAIS QUE A SUA VIDA!'"
        ]
    }

    # Evento 7: Combate com o Kraken Jovem
    yield {
        "type": "combat",
        "enemy_name": "Kraken Jovem",
        "victory_text": "O Kraken recua, não em derrota, mas em respeito. 'O seu coração... é verdadeiro. Nunca vi um amor tão puro...'"
    }

    # Evento 8: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 6",
        "segments": [
            "As ondas acalmam-se, revelando um presente na areia: uma Armadura de Aço Reforçado, a proteção dos antigos que tentaram esta jornada.",
            "'Que ela a proteja na subida que virá...', a voz do Kraken ecoa. 'A Torre espera. O seu destino espera.'"
        ]
    }

    # Evento 9: Dar a recompensa ao jogador
    yield {
        "type": "grant_reward",
        "equipment": "Armadura de Aco Reforcado"
    }

    # Evento 10: Fim da fase
    yield {
        "type": "phase_end"
    }