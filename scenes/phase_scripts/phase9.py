def run_phase_9():
    """
    Este é o gerador que controla o fluxo de eventos da Fase 9: A Biblioteca Proibida.
    """
    
    # Evento 1: Texto de introdução da fase
    yield {
        "type": "show_text",
        "title": "FASE 9: A BIBLIOTECA PROIBIDA",
        "segments": [
            "Manu sobe os degraus finais. A porta abre-se para o impossível: uma biblioteca que desafia as leis da realidade.",
            "Livros flutuam no ar, prateleiras estendem-se infinitamente, e runas nas paredes pulsam como veias expostas.",
            "'Este é o coração da pesquisa de Zorg...', ela sussurra, horrorizada. 'Aqui ele perverteu a sabedoria em maldição.'"
        ]
    }

    # Evento 2: Texto antes do primeiro combate
    yield {
        "type": "show_text",
        "segments": [
            "De uma prateleira alta, um tomo antigo não cai, mas VOA! As suas páginas transformam-se em lâminas cortantes: um Livro Amaldiçoado!",
            "A voz ecoa das suas páginas: 'VOCÊ NÃO DEVERIA ESTAR AQUI! ESTE CONHECIMENTO NÃO É PARA CORAÇÕES PUROS!'"
        ]
    }

    # Evento 3: Combate com o Livro Amaldiçoado
    yield {
        "type": "combat",
        "enemy_name": "Livro Amaldicoado",
        "victory_text": "O livro desfaz-se em cinzas que sussurram, mas uma presença ainda maior desperta."
    }
    
    # Evento 4: Texto de transição
    yield {
        "type": "show_text",
        "segments": [
            "De trás de uma mesa de obsidiana, uma figura ergue-se. O Mago Sombrio, bibliotecário pessoal de Zorg e guardião dos seus segredos mais negros.",
            "Os seus olhos são vazios como o espaço. 'TOLA MORTAL!', a sua voz soa como páginas a serem queimadas. 'O CONHECIMENTO AQUI CONTIDO DESTRUIRÁ VOCÊ!'",
            "'Eu não busco o seu conhecimento', Manu declara. 'Eu busco amor verdadeiro! Algo que você jamais entenderá!'"
        ]
    }

    # Evento 5: Combate com o Mago Sombrio
    yield {
        "type": "combat",
        "enemy_name": "Mago Sombrio",
        "victory_text": "O Mago Sombrio desfaz-se como pó ao vento. A sua maldição quebra-se, e a biblioteca suspira aliviada."
    }

    # Evento 6: Recompensa e final da fase
    yield {
        "type": "show_text",
        "title": "FIM DA FASE 9",
        "segments": [
            "Na mesa de obsidiana, um único livro permanece, emitindo uma luz suave. É um livro de cura, de restauração, de AMOR. Ao tocá-lo, Manu sente um novo poder fluir através dela.",
            "Num pedestal de cristal, uma Espada Rúnica aguardava. Ao erguê-la, a biblioteca ilumina-se, e as trevas recuam.",
            "À frente, apenas uma escada. A escada final. Para o topo. Para Ramon. Para Zorg. Para o DESTINO."
        ]
    }
    
    # Evento 7: Dar recompensas (lógica a implementar)
    yield { "type": "grant_reward", "ability": "Toque Restaurador" }
    yield { "type": "grant_reward", "equipment": "Espada Runica" }

    # Evento 8: Fim da fase
    yield {
        "type": "phase_end"
    }