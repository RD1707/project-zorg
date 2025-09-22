"""
Sistema de afinidades elementais para o jogo ZORG.
Implementa fraquezas, resistências e cálculos de dano elemental.
"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

from utils.logging_config import get_logger

logger = get_logger("elemental_system")


class Element(Enum):
    """Elementos disponíveis no jogo."""

    NEUTRO = "neutro"
    FOGO = "fogo"
    GELO = "gelo"
    SOMBRA = "sombra"
    LUZ = "luz"
    NATUREZA = "natureza"
    ARCANO = "arcano"
    FISICO = "físico"
    DIVINO = "divino"


class ElementalAffinity(Enum):
    """Níveis de afinidade elemental."""

    IMMUNITY = "immunity"  # Imune (0% dano)
    STRONG_RESIST = "strong_resist"  # Resistência forte (25% dano)
    RESIST = "resist"  # Resistência (50% dano)
    NEUTRAL = "neutral"  # Neutro (100% dano)
    WEAK = "weak"  # Fraqueza (150% dano)
    VERY_WEAK = "very_weak"  # Fraqueza severa (200% dano)


@dataclass
class ElementalEffect:
    """Efeito elemental aplicado a um ataque."""

    element: Element
    base_damage: int
    additional_effects: List[str] = None

    def __post_init__(self):
        if self.additional_effects is None:
            self.additional_effects = []


@dataclass
class ElementalResistance:
    """Resistência elemental de uma criatura."""

    element: Element
    affinity: ElementalAffinity
    description: str = ""


class ElementalChart:
    """Tabela de efetividade elemental."""

    def __init__(self):
        # Tabela de efetividade: [atacante][defensor] = modificador
        self.effectiveness = self._initialize_chart()

    def _initialize_chart(self) -> Dict[Element, Dict[Element, float]]:
        """Inicializa a tabela de efetividade elemental."""
        chart = {}

        # Inicializar com valores neutros
        for attacker in Element:
            chart[attacker] = {}
            for defender in Element:
                chart[attacker][defender] = 1.0

        # Fogo
        chart[Element.FOGO][Element.GELO] = 1.5  # Fogo > Gelo
        chart[Element.FOGO][Element.NATUREZA] = 1.5  # Fogo > Natureza
        chart[Element.FOGO][Element.FOGO] = 0.5  # Fogo < Fogo
        chart[Element.FOGO][Element.AGUA] = 0.5  # Fogo < Água (se implementado)

        # Gelo
        chart[Element.GELO][Element.FOGO] = 0.5  # Gelo < Fogo
        chart[Element.GELO][Element.NATUREZA] = 1.5  # Gelo > Natureza
        chart[Element.GELO][Element.GELO] = 0.5  # Gelo < Gelo

        # Sombra
        chart[Element.SOMBRA][Element.LUZ] = 1.5  # Sombra > Luz
        chart[Element.SOMBRA][Element.DIVINO] = 1.5  # Sombra > Divino
        chart[Element.SOMBRA][Element.SOMBRA] = 0.5  # Sombra < Sombra

        # Luz
        chart[Element.LUZ][Element.SOMBRA] = 1.5  # Luz > Sombra
        chart[Element.LUZ][Element.ARCANO] = 1.2  # Luz leve vantagem sobre Arcano
        chart[Element.LUZ][Element.LUZ] = 0.5  # Luz < Luz

        # Natureza
        chart[Element.NATUREZA][Element.FISICO] = 0.8  # Natureza resiste ao físico
        chart[Element.NATUREZA][Element.ARCANO] = 1.3  # Natureza > Arcano
        chart[Element.NATUREZA][Element.FOGO] = 0.5  # Natureza < Fogo
        chart[Element.NATUREZA][Element.GELO] = 0.5  # Natureza < Gelo

        # Arcano
        chart[Element.ARCANO][Element.FISICO] = 1.3  # Arcano > Físico
        chart[Element.ARCANO][Element.NATUREZA] = 0.7  # Arcano < Natureza
        chart[Element.ARCANO][Element.ARCANO] = 0.5  # Arcano < Arcano

        # Físico
        chart[Element.FISICO][Element.ARCANO] = 0.7  # Físico < Arcano
        chart[Element.FISICO][Element.NATUREZA] = 1.2  # Físico > Natureza
        chart[Element.FISICO][Element.SOMBRA] = 0.8  # Físico pouco eficaz contra Sombra

        # Divino
        chart[Element.DIVINO][
            Element.SOMBRA
        ] = 2.0  # Divino muito efetivo contra Sombra
        chart[Element.DIVINO][Element.ARCANO] = 1.3  # Divino > Arcano
        chart[Element.DIVINO][Element.DIVINO] = 0.5  # Divino < Divino

        return chart

    def get_effectiveness(
        self, attacker_element: Element, defender_element: Element
    ) -> float:
        """Retorna o modificador de efetividade."""
        return self.effectiveness.get(attacker_element, {}).get(defender_element, 1.0)


class ElementalSystem:
    """Sistema principal de elementos."""

    def __init__(self):
        self.chart = ElementalChart()
        self.element_descriptions = self._initialize_descriptions()

    def _initialize_descriptions(self) -> Dict[Element, str]:
        """Inicializa descrições dos elementos."""
        return {
            Element.NEUTRO: "Elemento neutro sem vantagens ou desvantagens especiais.",
            Element.FOGO: "Elemento ardente que queima inimigos e derrete gelo.",
            Element.GELO: "Elemento congelante que pode reduzir velocidade e apagar fogo.",
            Element.SOMBRA: "Elemento das trevas, especialmente efetivo contra luz.",
            Element.LUZ: "Elemento sagrado que banish as sombras.",
            Element.NATUREZA: "Elemento natural que resiste ataques físicos.",
            Element.ARCANO: "Magia pura que transcende limitações físicas.",
            Element.FISICO: "Força bruta que supera barreiras mágicas naturais.",
            Element.DIVINO: "Poder celestial devastador contra sombras.",
        }

    def calculate_elemental_damage(
        self,
        base_damage: int,
        attacker_element: Element,
        defender_resistances: List[ElementalResistance],
        attacker_level: int = 1,
        critical_hit: bool = False,
    ) -> Tuple[int, List[str]]:
        """
        Calcula dano elemental considerando resistências e efetividade.

        Returns:
            Tuple[int, List[str]]: (dano_final, mensagens_de_combate)
        """
        messages = []
        final_damage = base_damage

        # Encontrar resistência do defensor ao elemento do atacante
        defender_resistance = None
        for resistance in defender_resistances:
            if resistance.element == attacker_element:
                defender_resistance = resistance
                break

        # Aplicar modificador de efetividade da tabela elemental
        if defender_resistance:
            # Usar sistema de afinidade
            affinity_modifier = self._get_affinity_modifier(
                defender_resistance.affinity
            )
            final_damage = int(final_damage * affinity_modifier)

            if affinity_modifier == 0:
                messages.append(f"Imune ao elemento {attacker_element.value}!")
            elif affinity_modifier < 0.6:
                messages.append(f"Resistente ao elemento {attacker_element.value}!")
            elif affinity_modifier > 1.4:
                messages.append(f"Fraco ao elemento {attacker_element.value}!")

        # Adicionar variação aleatória pequena
        variation = random.uniform(0.9, 1.1)
        final_damage = int(final_damage * variation)

        # Aplicar bônus de crítico se aplicável
        if critical_hit:
            final_damage = int(final_damage * 1.5)
            messages.append("Acerto critico elemental!")

        # Aplicar efeitos secundários baseados no elemento
        secondary_effects = self._get_secondary_effects(attacker_element)
        messages.extend(secondary_effects)

        # Garantir dano mínimo
        final_damage = max(1, final_damage)

        return final_damage, messages

    def _get_affinity_modifier(self, affinity: ElementalAffinity) -> float:
        """Converte afinidade em modificador numérico."""
        modifiers = {
            ElementalAffinity.IMMUNITY: 0.0,
            ElementalAffinity.STRONG_RESIST: 0.25,
            ElementalAffinity.RESIST: 0.5,
            ElementalAffinity.NEUTRAL: 1.0,
            ElementalAffinity.WEAK: 1.5,
            ElementalAffinity.VERY_WEAK: 2.0,
        }
        return modifiers.get(affinity, 1.0)

    def _get_secondary_effects(self, element: Element) -> List[str]:
        """Retorna efeitos secundários possíveis de um elemento."""
        effects = []

        effect_chances = {
            Element.FOGO: (0.3, "O alvo comeca a queimar!"),
            Element.GELO: (0.25, "O alvo fica mais lento!"),
            Element.SOMBRA: (0.2, "O alvo e envolto em sombras!"),
            Element.LUZ: (0.2, "O alvo e purificado!"),
            Element.NATUREZA: (0.15, "Espinhos brotam ao redor do alvo!"),
            Element.ARCANO: (0.25, "Energia arcana interfere na magia do alvo!"),
            Element.DIVINO: (0.3, "Poder divino abencoa o ataque!"),
        }

        if element in effect_chances:
            chance, message = effect_chances[element]
            if random.random() < chance:
                effects.append(message)

        return effects

    def get_element_from_string(self, element_str: str) -> Element:
        """Converte string em Element enum."""
        element_map = {
            "neutro": Element.NEUTRO,
            "fogo": Element.FOGO,
            "gelo": Element.GELO,
            "sombra": Element.SOMBRA,
            "sombrio": Element.SOMBRA,  # Alias
            "luz": Element.LUZ,
            "natureza": Element.NATUREZA,
            "arcano": Element.ARCANO,
            "físico": Element.FISICO,
            "fisico": Element.FISICO,  # Sem acento
            "divino": Element.DIVINO,
        }
        return element_map.get(element_str.lower(), Element.NEUTRO)

    def create_resistances_from_json(
        self, resistances_data: Dict[str, str]
    ) -> List[ElementalResistance]:
        """Cria lista de resistências a partir de dados JSON."""
        resistances = []

        affinity_map = {
            "immune": ElementalAffinity.IMMUNITY,
            "strong_resist": ElementalAffinity.STRONG_RESIST,
            "resist": ElementalAffinity.RESIST,
            "neutral": ElementalAffinity.NEUTRAL,
            "weak": ElementalAffinity.WEAK,
            "very_weak": ElementalAffinity.VERY_WEAK,
        }

        for element_str, affinity_str in resistances_data.items():
            element = self.get_element_from_string(element_str)
            affinity = affinity_map.get(affinity_str.lower(), ElementalAffinity.NEUTRAL)

            resistance = ElementalResistance(
                element=element,
                affinity=affinity,
                description=f"{affinity_str} to {element_str}",
            )
            resistances.append(resistance)

        return resistances

    def get_effectiveness_description(
        self, attacker_element: Element, defender_element: Element
    ) -> str:
        """Retorna descrição textual da efetividade."""
        effectiveness = self.chart.get_effectiveness(attacker_element, defender_element)

        if effectiveness >= 1.8:
            return "Super efetivo!"
        elif effectiveness >= 1.3:
            return "Muito efetivo!"
        elif effectiveness >= 1.1:
            return "Efetivo"
        elif effectiveness >= 0.9:
            return "Normal"
        elif effectiveness >= 0.6:
            return "Pouco efetivo"
        elif effectiveness >= 0.3:
            return "Muito pouco efetivo"
        else:
            return "Inefetivo"

    def get_recommended_elements(
        self, enemy_resistances: List[ElementalResistance]
    ) -> List[Element]:
        """Sugere elementos mais efetivos contra um inimigo."""
        recommendations = []

        # Verificar quais elementos o inimigo é fraco
        for resistance in enemy_resistances:
            if resistance.affinity in [
                ElementalAffinity.WEAK,
                ElementalAffinity.VERY_WEAK,
            ]:
                recommendations.append(resistance.element)

        # Se não há fraquezas claras, sugerir elementos neutros
        if not recommendations:
            recommendations = [Element.FISICO, Element.ARCANO]

        return recommendations

    def apply_elemental_weapon_enchantment(
        self, weapon_damage: int, enchantment_element: Element, enchantment_power: int
    ) -> Tuple[int, Element]:
        """Aplica encantamento elemental a uma arma."""
        elemental_bonus = int(weapon_damage * (enchantment_power / 100))
        total_damage = weapon_damage + elemental_bonus

        return total_damage, enchantment_element

    def get_element_color(self, element: Element) -> str:
        """Retorna cor/emoji representativo do elemento."""
        colors = {
            Element.NEUTRO: "O",
            Element.FOGO: "X",
            Element.GELO: "I",
            Element.SOMBRA: "#",
            Element.LUZ: "*",
            Element.NATUREZA: "+",
            Element.ARCANO: "~",
            Element.FISICO: "=",
            Element.DIVINO: "@",
        }
        return colors.get(element, "O")


# Instância global do sistema elemental
elemental_system = ElementalSystem()


def get_elemental_system() -> ElementalSystem:
    """Retorna a instância global do sistema elemental."""
    return elemental_system


def calculate_damage_with_elements(
    base_damage: int,
    attacker_element: Element,
    defender_resistances: List[ElementalResistance],
    **kwargs,
) -> Tuple[int, List[str]]:
    """Função utilitária para calcular dano elemental."""
    return elemental_system.calculate_elemental_damage(
        base_damage, attacker_element, defender_resistances, **kwargs
    )
