def run_phase_7():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 7: O Penhasco Ventoso.
    """

    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 7: O PENHASCO VENTOSO",
        "segments": [
            "A jornada chegou ao seu momento mais brutal. O penhasco ergue-se como uma muralha de pesadelo, mil metros de rocha vertical.",
            "O vento uiva como mil espíritos torturados, tentando arrancá-la da rocha. Mas Manu agarra-se com unhas e dentes.",
            "'Ramon... Ramon está à espera... não posso parar!'",
        ],
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "Um grito perfurante rasga o ar! Das correntes de vento, emerge uma Harpia Esguia, meio mulher, meio abutre, toda maldade.",
            "As suas garras de navalha brilham. Ela mergulha em direção a Manu como um míssil alado, gritando: 'VOCÊ NÃO PASSARÁ! ESTAS ALTURAS SÃO NOSSAS!'",
        ],
    }

    # Evento 3: Combate com a Harpia
    yield {
        "type": "combat",
        "enemy_name": "Harpia Esguia",
        "victory_text": "A primeira harpia cai, mas a escalada está longe de terminar.",
    }

    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "Mais acima, pendurado na face do penhasco, um ninho grotesco feito de ossos. Nele, a companheira da harpia morta espera por vingança.",
            "'ASSASSINA! VOCÊ MATOU A MINHA IRMÃ!', a segunda harpia grita, lançando-se do ninho numa fúria cega.",
            "'Eu entendo a sua dor', Manu sussurra contra o vento, 'mas o amor que me move é mais forte que qualquer ódio!'",
        ],
    }

    # Evento 5: Combate com a segunda Harpia
    yield {
        "type": "combat",
        "enemy_name": "Harpia Esguia",
        "victory_text": "Com o coração pesado, Manu supera a segunda guardiã. O topo está próximo.",
    }

    # Evento 6: Texto antes do chefe da fase
    yield {
        "type": "show_text",
        "segments": [
            "No centro da tempestade no topo, uma presença majestosa e terrível revela-se: UM GRIFO ANCESTRAL!",
            "Corpo de leão dourado, cabeça de águia régia, olhos como sóis flamejantes. Ele observa Manu com respeito e desafio.",
            "A sua voz ecoa como um trovão dourado: 'JOVEM GUERREIRA... O SEU CORAÇÃO É NOBRE, MAS ESTAS ALTURAS SÃO SAGRADAS! PROVE QUE O SEU AMOR MERECE TOCAR O CÉU!'",
        ],
    }

    # Evento 7: Combate com o Grifo Alfa
    yield {
        "type": "combat",
        "enemy_name": "Grifo Alfa",
        "victory_text": "O magnífico Grifo inclina a cabeça, não em derrota, mas em reverência. 'Perdoe-me... eu precisava ter a certeza. Você tem o direito de pisar onde os deuses pisam.'",
    }

    # Evento 8: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 7",
        "segments": [
            "Atrás do ninho do Grifo, os restos de um cavaleiro antigo que falhou nesta mesma jornada. Ao seu lado, um Escudo de Aço.",
            "O vento amaina. E lá... lá estão eles. Os portões negros da Torre do Ponteiro Nulo.",
            "'Eu conquistei terra, mar e céu, meu amor...', Manu sussurra. 'Agora é hora de conquistar as trevas!'",
        ],
    }

    # Evento 9: Dar a recompensa ao jogador
    yield {"type": "grant_reward", "equipment": "Escudo de Aco"}

    # Evento 10: Fim da fase
    yield {"type": "phase_end"}
