def run_phase_4():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 4: Nullhaven.
    """

    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 4: NULLHAVEN - CIDADE DO REFÚGIO",
        "segments": [
            "Após dias de terror e solidão, Manu finalmente vê sinais de vida civilizada. O cheiro de sal misturado com pão fresco, vozes humanas, risos de crianças...",
            "Nullhaven estende-se diante dela como um oásis. Pela primeira vez desde que a jornada começou, Manu sorri. Um sorriso pequeno, mas real.",
            "'Ramon adoraria este lugar', ela pensa, tocando o medalhão. No horizonte, porém, a Torre do Ponteiro Nulo ainda projeta a sua sombra sinistra.",
        ],
    }

    # Evento 2: Entrar no modo "hub" da cidade
    # Este é um novo tipo de evento que dirá ao GameScreen para abrir a tela da cidade.
    yield {"type": "enter_hub", "hub_name": "nullhaven"}
