"""
NPCs da cidade de Nullhaven com diálogos e missões.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class NPCType(Enum):
    MERCHANT = "merchant"
    GUARD = "guard"
    CITIZEN = "citizen"
    QUESTGIVER = "questgiver"


class QuestStatus(Enum):
    AVAILABLE = "available"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Quest:
    id: str
    name: str
    description: str
    objective: str
    reward_xp: int
    reward_gold: int
    reward_items: List[str]
    status: QuestStatus = QuestStatus.AVAILABLE
    progress: int = 0
    max_progress: int = 1

    def is_complete(self) -> bool:
        return self.progress >= self.max_progress

    def complete_quest(self) -> None:
        self.status = QuestStatus.COMPLETED
        self.progress = self.max_progress


@dataclass
class DialogOption:
    text: str
    response: str
    action: Optional[str] = None  # Ação especial como "give_quest", "complete_quest"
    quest_id: Optional[str] = None


@dataclass
class NPC:
    id: str
    name: str
    description: str
    npc_type: NPCType
    greeting: str
    dialog_options: List[DialogOption]
    quests: List[Quest]
    location: str

    def get_available_quests(self) -> List[Quest]:
        return [q for q in self.quests if q.status == QuestStatus.AVAILABLE]

    def get_active_quests(self) -> List[Quest]:
        return [q for q in self.quests if q.status == QuestStatus.ACTIVE]

    def get_completed_quests(self) -> List[Quest]:
        return [q for q in self.quests if q.status == QuestStatus.COMPLETED]


# NPCs de Nullhaven
DB_NPCS = {
    "capitao_porto": NPC(
        id="capitao_porto",
        name="Capitão Maré",
        description="Um velho marinheiro com cicatrizes de batalhas antigas. Seus olhos experientes observam o horizonte constantemente.",
        npc_type=NPCType.QUESTGIVER,
        greeting="Ahoy, jovem aventureira! Os mares têm estado agitados ultimamente...",
        location="docas",
        dialog_options=[
            DialogOption(
                text="O que você sabe sobre a Torre do Ponteiro Nulo?",
                response="A torre... *suspira* Muitos marinheiros corajosos partiram para lá. Poucos voltaram. Dizem que lá dentro há criaturas que não deveriam existir."
            ),
            DialogOption(
                text="Precisa de ajuda com alguma coisa?",
                response="Na verdade, sim! Tenho recebido relatos de criaturas estranhas nas docas à noite. Se você pudesse investigar...",
                action="give_quest",
                quest_id="investigar_docas"
            ),
            DialogOption(
                text="Tchau!",
                response="Que os ventos te favoreçam, jovem!"
            )
        ],
        quests=[
            Quest(
                id="investigar_docas",
                name="Mistérios das Docas",
                description="O Capitão Maré relatou atividades estranhas nas docas durante a noite.",
                objective="Investigate the docks at night and defeat any creatures found",
                reward_xp=150,
                reward_gold=75,
                reward_items=["Pocao de Cura", "Antidoto"],
                max_progress=3
            )
        ]
    ),

    "elena_curandeira": NPC(
        id="elena_curandeira",
        name="Elena, a Curandeira",
        description="Uma mulher gentil com mãos calejadas de anos preparando poções e curando ferimentos.",
        npc_type=NPCType.MERCHANT,
        greeting="Olá, querida! Você parece precisar de cuidados. Posso ajudar?",
        location="praca_central",
        dialog_options=[
            DialogOption(
                text="Você tem poções para vender?",
                response="Claro! Tenho as melhores poções de cura da cidade. Cada uma feita com amor e ingredientes frescos."
            ),
            DialogOption(
                text="Me fale sobre Nullhaven.",
                response="Esta cidade já foi próspera, mas a aparição da Torre mudou tudo. Agora vivemos com medo, mas ainda temos esperança."
            ),
            DialogOption(
                text="Você conhece alguma receita especial?",
                response="Ah, sim! Se você me trouxer 3 Ervas Raras, posso te ensinar a fazer uma Poção de Vigor Supremo!",
                action="give_quest",
                quest_id="ervas_raras"
            )
        ],
        quests=[
            Quest(
                id="ervas_raras",
                name="Coletora de Ervas",
                description="Elena precisa de 3 Ervas Raras para uma receita especial.",
                objective="Collect 3 Rare Herbs from battles or exploration",
                reward_xp=100,
                reward_gold=50,
                reward_items=["Pocao de Vigor Supremo"],
                max_progress=3
            )
        ]
    ),

    "joao_pescador": NPC(
        id="joao_pescador",
        name="João, o Pescador",
        description="Um pescador robusto com roupas simples e um sorriso caloroso, apesar das dificuldades.",
        npc_type=NPCType.CITIZEN,
        greeting="Oi! Você deve ser nova por aqui. Bem-vinda a Nullhaven!",
        location="taverna",
        dialog_options=[
            DialogOption(
                text="Como está a pesca?",
                response="Terrível! Os peixes fugiram quando a Torre apareceu. Algo na água os assusta. Às vezes vejo sombras estranhas se movendo nas profundezas."
            ),
            DialogOption(
                text="Você tem alguma dica para aventureiros?",
                response="*sussurra* Se for à Torre, leve muitas poções. E cuidado com os espelhos... eles mostram coisas que não deveriam existir."
            ),
            DialogOption(
                text="Obrigada pelas dicas!",
                response="De nada! E boa sorte, jovem heroína!"
            )
        ],
        quests=[]
    ),

    "marcus_guarda": NPC(
        id="marcus_guarda",
        name="Guarda Marcus",
        description="Um guarda experiente com armadura bem cuidada. Sua postura alerta sugere anos de treinamento.",
        npc_type=NPCType.GUARD,
        greeting="Cidadã, mantenha-se segura. A cidade não é mais como era antes.",
        location="entrada_cidade",
        dialog_options=[
            DialogOption(
                text="A cidade está segura?",
                response="Fazemos o nosso melhor, mas as criaturas da Torre às vezes se aventuram até aqui. Fique alerta, especialmente à noite."
            ),
            DialogOption(
                text="Precisa de ajuda para patrulhar?",
                response="Na verdade... temos tido problemas com lobos corrompidos nos arredores. Se você pudesse lidar com eles...",
                action="give_quest",
                quest_id="lobos_corrompidos"
            ),
            DialogOption(
                text="Entendido, obrigada.",
                response="Mantenha-se vigilante, aventureira."
            )
        ],
        quests=[
            Quest(
                id="lobos_corrompidos",
                name="Caça aos Lobos Corrompidos",
                description="O Guarda Marcus precisa de ajuda para eliminar lobos corrompidos nos arredores da cidade.",
                objective="Defeat 5 corrupted wolves around the city outskirts",
                reward_xp=200,
                reward_gold=100,
                reward_items=["Espada de Ferro", "Escudo de Ferro"],
                max_progress=5
            )
        ]
    ),

    "sabio_aldric": NPC(
        id="sabio_aldric",
        name="Sábio Aldric",
        description="Um homem idoso com longas barbas brancas e olhos que brilham com conhecimento ancestral.",
        npc_type=NPCType.QUESTGIVER,
        greeting="Ah, uma nova face... Os ventos do destino sopram forte hoje.",
        location="biblioteca",
        dialog_options=[
            DialogOption(
                text="O que você sabe sobre a Torre?",
                response="A Torre do Ponteiro Nulo é uma aberração no tecido da realidade. Ela apareceu de repente, trazendo consigo horrores inimagináveis."
            ),
            DialogOption(
                text="Como posso me preparar para enfrentá-la?",
                response="Conhecimento é poder, jovem. Se você puder me trazer 3 Pergaminhos Antigos, posso te ensinar magias poderosas.",
                action="give_quest",
                quest_id="pergaminhos_antigos"
            ),
            DialogOption(
                text="Tem algum conselho sábio?",
                response="Lembre-se: nem sempre a força bruta resolve. Às vezes, a inteligência e a compaixão são as armas mais poderosas."
            )
        ],
        quests=[
            Quest(
                id="pergaminhos_antigos",
                name="Conhecimento Perdido",
                description="O Sábio Aldric pode ensinar magias poderosas em troca de pergaminhos antigos.",
                objective="Find 3 Ancient Scrolls in the Tower or from defeated enemies",
                reward_xp=300,
                reward_gold=0,
                reward_items=["Habilidade: Bola de Fogo", "Habilidade: Escudo Mágico"],
                max_progress=3
            )
        ]
    )
}