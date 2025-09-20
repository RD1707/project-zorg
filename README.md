# ZORG - O RPG Épico

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey.svg)

**ZORG** é um RPG épico baseado em texto, desenvolvido com Textual, que conta a história de Manuella em sua jornada heroica para resgatar seu amado Ramon das garras do malévolo feiticeiro Zorg.

## Historia

Em um tempo onde o amor ainda era puro, no tranquilo vilarejo de Coden, dois corações batiam em perfeita sintonia: Manuella, artesã de mãos habilidosas, e Ramon, programador de códigos brilhantes.

Mas nas sombras, o feiticeiro Zorg observava com inveja corrosiva. Incapaz de amar, ele aprisionou Ramon no topo da temível Torre do Ponteiro Nulo. Agora, Manuella deve embarcar em uma jornada épica para salvá-lo.

## Caracteristicas

- **Interface Rica**: Construído com Textual para uma experiência visual impressionante
- **Sistema de Combate**: Combates táticos com habilidades, itens e estratégias
- **Progressão de Personagem**: Sistema de levelup com melhorias de atributos
- **10 Fases Épicas**: Desde florestas sombrias até a Torre do Ponteiro Nulo
- **Sistema de Save/Load**: Salve seu progresso a qualquer momento
- **Arte ASCII**: Elementos visuais únicos e atmosféricos

## Instalacao

### Requisitos
- Python 3.8 ou superior
- Sistema operacional: Windows, Linux ou macOS

### Instalação Rápida
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/zorg-game.git
cd zorg-game

# Instale as dependências
pip install -r requirements.txt

# Execute o jogo
python main.py
```

### Instalação para Desenvolvimento
```bash
# Instale com dependências de desenvolvimento
pip install -e ".[dev]"

# Execute os testes
pytest

# Formatação de código
black .
isort .

# Verificação de tipos
mypy .
```

## Como Jogar

### Controles Básicos
- **Enter/Espaço**: Confirmar ações
- **Setas/Tab**: Navegar pelos menus
- **Q**: Sair do jogo
- **ESC**: Voltar ao menu anterior

### Sistema de Combate
- **Ataque**: Ataque básico com sua arma
- **Habilidades**: Use magias e habilidades especiais
- **Itens**: Consuma poções e outros itens
- **Fuga**: Tente escapar do combate (nem sempre funciona)

### Dicas de Estratégia
- Gerencie seu MP para usar habilidades no momento certo
- Mantenha sempre algumas poções de cura no inventário
- Explore diferentes combinações de equipamentos
- Cada inimigo tem pontos fracos únicos

## Estrutura do Projeto

```
zorg-game/
├── core/                   # Motor do jogo e lógica principal
│   ├── engine.py          # GameEngine principal
│   ├── models.py          # Modelos de dados (Personagem, Item, etc.)
│   └── exceptions.py      # Exceções customizadas
├── data/                  # Banco de dados do jogo
│   ├── abilities.py       # Habilidades e magias
│   ├── enemies.py         # Inimigos e bosses
│   ├── equipment.py       # Armas, armaduras e escudos
│   └── items.py           # Itens consumíveis
├── scenes/                # Scripts das fases
│   └── phase_scripts/     # Scripts individuais das fases
├── screens/               # Telas da interface
│   ├── main_menu.py       # Menu principal
│   ├── game_screen.py     # Tela principal do jogo
│   └── story_screen.py    # Telas de história
├── utils/                 # Utilitários
│   ├── save_load.py       # Sistema de save/load
│   └── logging_config.py  # Configuração de logs
├── widgets/               # Widgets personalizados
└── tests/                 # Testes unitários
```

## Desenvolvimento

### Adicionando Novo Conteúdo

#### Nova Fase
1. Crie um script em `scenes/phase_scripts/phaseN.py`
2. Implemente a função `run_phaseN()` como gerador
3. Adicione inimigos específicos em `data/enemies.py`

#### Novo Item/Equipamento
1. Adicione a definição em `data/items.py` ou `data/equipment.py`
2. Configure os atributos e efeitos
3. Teste a integração no sistema

#### Nova Habilidade
1. Defina a habilidade em `data/abilities.py`
2. Implemente a lógica no `GameEngine`
3. Adicione aos inimigos ou como recompensa

### Executando Testes
```bash
# Todos os testes
pytest

# Testes com cobertura
pytest --cov=core --cov=data --cov=scenes

# Testes específicos
pytest tests/test_engine.py -v
```

## Roadmap

### Versão 1.1
- [ ] Sistema de crafting
- [ ] Mais opções de customização de personagem
- [ ] Modo difícil
- [ ] Achievement system

### Versão 1.2
- [ ] Multiplayer local
- [ ] Editor de fases
- [ ] Suporte a mods
- [ ] Trilha sonora

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Código
- Use Black para formatação
- Siga PEP 8
- Adicione type hints
- Escreva testes para novas funcionalidades
- Documente funções públicas

## Changelog

### v1.0.0 (2024-12-17)
- Lançamento inicial
- 10 fases jogaveis
- Sistema de combate completo
- Sistema de save/load
- Interface rica com Textual

## Licenca

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Agradecimentos

- **Textual**: Framework incrível para aplicações de terminal
- **Rich**: Biblioteca para formatação rica de texto
- **Comunidade Python**: Por todas as ferramentas fantásticas

## Suporte

Se você encontrar bugs ou tiver sugestões:
- Abra uma [issue](https://github.com/seu-usuario/zorg-game/issues)
- Entre em contato: ramon.mendonca.est@email.com

---

*"Onde o codigo encontra a coragem."*