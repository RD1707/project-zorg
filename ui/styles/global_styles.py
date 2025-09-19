"""
Estilos globais consistentes para o jogo ZORG.
"""

# === CORES ===
COLORS = {
    # Cores principais
    "background": "#0d0d0d",
    "surface": "#1e1e1e",
    "surface_variant": "#2a2a2a",
    "border": "#444444",
    "border_active": "#666666",

    # Texto
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
    "text_disabled": "#888888",

    # Estado
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",

    # Elementos especiais
    "accent": "#06b6d4",
    "highlight": "#fbbf24",
    "hp_color": "#22c55e",
    "mp_color": "#3b82f6",
    "xp_color": "#fbbf24",
}

# === DIMENSÕES ===
SIZES = {
    "border_radius": "round",
    "padding_small": "1",
    "padding_medium": "2",
    "padding_large": "3",
    "margin_small": "1",
    "margin_medium": "2",
    "spacing": "1",
}

# === CSS GLOBAL ===
GLOBAL_CSS = f"""
/* === RESET E BASE === */
Screen {{
    background: {COLORS["background"]};
    color: {COLORS["text_primary"]};
}}

/* === CONTAINERS === */
.container {{
    border: {SIZES["border_radius"]} {COLORS["border"]};
    background: {COLORS["surface"]};
    padding: {SIZES["padding_medium"]};
}}

.container_primary {{
    border: {SIZES["border_radius"]} {COLORS["accent"]};
    background: {COLORS["surface"]};
    padding: {SIZES["padding_medium"]};
}}

.container_variant {{
    border: {SIZES["border_radius"]} {COLORS["border"]};
    background: {COLORS["surface_variant"]};
    padding: {SIZES["padding_medium"]};
}}

/* === BOTÕES === */
Button {{
    min-width: 20;
    height: 3;
    margin: {SIZES["margin_small"]};
    border: tall {COLORS["border"]};
    background: {COLORS["surface"]};
    color: {COLORS["text_primary"]};
}}

Button:hover {{
    border: tall {COLORS["border_active"]};
    background: {COLORS["surface_variant"]};
    color: {COLORS["text_primary"]};
}}

Button:focus {{
    border: tall {COLORS["accent"]};
    background: {COLORS["surface_variant"]};
}}

Button.-primary {{
    border: tall {COLORS["accent"]};
    background: {COLORS["accent"]};
    color: {COLORS["background"]};
}}

Button.-primary:hover {{
    background: {COLORS["info"]};
    border: tall {COLORS["info"]};
}}

Button.-success {{
    border: tall {COLORS["success"]};
    background: {COLORS["success"]};
    color: {COLORS["background"]};
}}

Button.-warning {{
    border: tall {COLORS["warning"]};
    background: {COLORS["warning"]};
    color: {COLORS["background"]};
}}

Button.-error {{
    border: tall {COLORS["error"]};
    background: {COLORS["error"]};
    color: {COLORS["text_primary"]};
}}

Button:disabled {{
    border: tall {COLORS["text_disabled"]};
    background: {COLORS["surface"]};
    color: {COLORS["text_disabled"]};
}}

/* === CABEÇALHOS === */
.header {{
    text-style: bold;
    color: {COLORS["accent"]};
    text-align: center;
    margin-bottom: {SIZES["margin_medium"]};
}}

.header_large {{
    text-style: bold;
    color: {COLORS["accent"]};
    text-align: center;
    margin-bottom: {SIZES["margin_medium"]};
    text-size: 2;
}}

.section_header {{
    text-style: bold;
    color: {COLORS["highlight"]};
    margin-top: {SIZES["margin_medium"]};
    margin-bottom: {SIZES["margin_small"]};
}}

/* === ESTATÍSTICAS === */
.stat_hp {{
    color: {COLORS["hp_color"]};
    text-style: bold;
}}

.stat_mp {{
    color: {COLORS["mp_color"]};
    text-style: bold;
}}

.stat_xp {{
    color: {COLORS["xp_color"]};
    text-style: bold;
}}

/* === LISTAS === */
.list_item {{
    height: auto;
    margin-bottom: {SIZES["margin_small"]};
    padding: {SIZES["padding_small"]};
    background: {COLORS["surface_variant"]};
    border: {SIZES["border_radius"]} {COLORS["border"]};
}}

.list_item:hover {{
    border: {SIZES["border_radius"]} {COLORS["border_active"]};
}}

.list_item_selected {{
    border: {SIZES["border_radius"]} {COLORS["accent"]};
}}

/* === FORMULÁRIOS === */
Input {{
    background: {COLORS["surface"]};
    border: tall {COLORS["border"]};
    color: {COLORS["text_primary"]};
}}

Input:focus {{
    border: tall {COLORS["accent"]};
}}

Select {{
    background: {COLORS["surface"]};
    border: tall {COLORS["border"]};
    color: {COLORS["text_primary"]};
}}

Select:focus {{
    border: tall {COLORS["accent"]};
}}

Switch {{
    background: {COLORS["surface"]};
}}

/* === ESTADOS === */
.success {{
    color: {COLORS["success"]};
}}

.warning {{
    color: {COLORS["warning"]};
}}

.error {{
    color: {COLORS["error"]};
}}

.info {{
    color: {COLORS["info"]};
}}

.disabled {{
    color: {COLORS["text_disabled"]};
}}

/* === BARRAS DE PROGRESSO === */
.progress_bar {{
    height: 1;
    background: {COLORS["surface_variant"]};
    border: {SIZES["border_radius"]} {COLORS["border"]};
}}

.progress_hp {{
    background: {COLORS["hp_color"]};
}}

.progress_mp {{
    background: {COLORS["mp_color"]};
}}

.progress_xp {{
    background: {COLORS["xp_color"]};
}}

/* === LAYOUTS === */
.center {{
    align: center middle;
}}

.center_horizontal {{
    align: center top;
}}

.center_vertical {{
    align: left middle;
}}

.full_width {{
    width: 100%;
}}

.full_height {{
    height: 100%;
}}

/* === SCROLLABLE === */
ScrollableContainer {{
    background: {COLORS["surface"]};
    border: {SIZES["border_radius"]} {COLORS["border"]};
}}

/* === FOOTER/HEADER === */
Header {{
    background: {COLORS["surface_variant"]};
    color: {COLORS["text_primary"]};
    text-style: bold;
}}

Footer {{
    background: {COLORS["surface_variant"]};
    color: {COLORS["text_secondary"]};
}}

/* === CLASSES UTILITÁRIAS === */
.hidden {{
    display: none;
}}

.text_center {{
    text-align: center;
}}

.text_right {{
    text-align: right;
}}

.text_bold {{
    text-style: bold;
}}

.text_italic {{
    text-style: italic;
}}

.margin_top {{
    margin-top: {SIZES["margin_medium"]};
}}

.margin_bottom {{
    margin-bottom: {SIZES["margin_medium"]};
}}

.padding_all {{
    padding: {SIZES["padding_medium"]};
}}
"""

# === COMPONENTES REUTILIZÁVEIS ===
COMPONENT_STYLES = {
    "game_panel": f"""
    #game_panel {{
        width: 90%;
        height: 85%;
        margin-top: {SIZES["margin_medium"]};
        border: {SIZES["border_radius"]} {COLORS["border"]};
        background: {COLORS["surface"]};
        padding: {SIZES["padding_medium"]};
    }}
    """,

    "status_display": f"""
    .status_row {{
        height: 3;
        margin-bottom: {SIZES["margin_small"]};
        padding: {SIZES["padding_small"]};
    }}

    .status_label {{
        width: 30%;
        color: {COLORS["text_secondary"]};
    }}

    .status_value {{
        width: 70%;
        color: {COLORS["text_primary"]};
        text-style: bold;
    }}
    """,

    "dialog_box": f"""
    .dialog_container {{
        width: 80%;
        max-width: 100;
        border: {SIZES["border_radius"]} {COLORS["border"]};
        background: {COLORS["surface"]};
        padding: {SIZES["padding_large"]};
    }}

    .dialog_title {{
        text-style: bold;
        color: {COLORS["accent"]};
        text-align: center;
        margin-bottom: {SIZES["margin_medium"]};
    }}

    .dialog_content {{
        color: {COLORS["text_primary"]};
        margin-bottom: {SIZES["margin_medium"]};
    }}
    """,

    "menu_list": f"""
    .menu_container {{
        width: 60%;
        height: auto;
        border: {SIZES["border_radius"]} {COLORS["border"]};
        background: {COLORS["surface"]};
        padding: {SIZES["padding_medium"]};
    }}

    .menu_item {{
        width: 100%;
        margin-bottom: {SIZES["margin_small"]};
    }}
    """,
}

def get_global_css() -> str:
    """Retorna o CSS global completo."""
    return GLOBAL_CSS

def get_component_css(component_name: str) -> str:
    """Retorna o CSS de um componente específico."""
    return COMPONENT_STYLES.get(component_name, "")

def get_all_component_css() -> str:
    """Retorna todos os estilos de componentes combinados."""
    return "\n".join(COMPONENT_STYLES.values())

def get_color(color_name: str) -> str:
    """Retorna uma cor específica."""
    return COLORS.get(color_name, "#ffffff")

def get_size(size_name: str) -> str:
    """Retorna um tamanho específico."""
    return SIZES.get(size_name, "1")