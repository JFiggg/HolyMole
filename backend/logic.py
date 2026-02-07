"""
Static data and blast-radius logic for Holy Mole.
Menu dependencies and revenue impact; DFS-based blast radius calculation.
"""
from typing import Any

# Menu Item -> list of ingredient names it depends on
MENU_GRAPH: dict[str, list[str]] = {
    "Spicy Chicken": ["Bun", "Chicken", "Mayo"],
    "Guacamole Bowl": ["Avocados", "Lime", "Cilantro"],
    "Steak Tacos": ["Tortilla", "Steak", "Lime", "Onion"],
    "Breakfast Burrito": ["Tortilla", "Eggs", "Steak", "Avocados"],
    "Margarita": ["Tequila", "Lime", "Triple Sec"],
    "Ceviche": ["Lime", "Avocados", "Fish"],
    "Quesadilla": ["Tortilla", "Cheese", "Chicken"],
    "Huevos Rancheros": ["Eggs", "Tortilla", "Salsa"],
}

# Menu Item -> hourly revenue loss if unavailable ($)
REVENUE_IMPACT: dict[str, float] = {
    "Spicy Chicken": 150.0,
    "Guacamole Bowl": 120.0,
    "Steak Tacos": 180.0,
    "Breakfast Burrito": 140.0,
    "Margarita": 200.0,
    "Ceviche": 90.0,
    "Quesadilla": 110.0,
    "Huevos Rancheros": 95.0,
}


def _ingredient_to_menu_items() -> dict[str, list[str]]:
    """Invert MENU_GRAPH: ingredient name -> list of menu items that use it."""
    inv: dict[str, list[str]] = {}
    for menu_item, ingredients in MENU_GRAPH.items():
        for ing in ingredients:
            inv.setdefault(ing, []).append(menu_item)
    return inv


def calculate_blast_radius(ingredient_name: str) -> dict[str, Any]:
    """
    DFS from the given ingredient to all menu items that depend on it.
    Returns dependency graph (edges + affected items) and total revenue risk.
    """
    inv = _ingredient_to_menu_items()
    ingredient_name = ingredient_name.strip()
    if not ingredient_name:
        return {
            "ingredient": ingredient_name,
            "affected_menu_items": [],
            "edges": [],
            "total_revenue_risk_per_hour": 0.0,
        }

    # Normalize key lookup (MENU_GRAPH uses capitalized names; accept any case)
    key = next((k for k in inv if k.lower() == ingredient_name.lower()), None)
    if key is None:
        return {
            "ingredient": ingredient_name,
            "affected_menu_items": [],
            "edges": [],
            "total_revenue_risk_per_hour": 0.0,
        }

    visited: set[str] = set()
    stack = [key]
    edges: list[dict[str, str]] = []

    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        # node is an ingredient; get menu items that use it
        for menu_item in inv.get(node, []):
            edges.append({"from": node, "to": menu_item})
            if menu_item not in visited:
                stack.append(menu_item)

    # Affected menu items = all "to" nodes in edges (menu items that use this ingredient)
    affected = list({e["to"] for e in edges})
    total_risk = sum(REVENUE_IMPACT.get(m, 0.0) for m in affected)

    return {
        "ingredient": key,
        "affected_menu_items": affected,
        "edges": edges,
        "total_revenue_risk_per_hour": round(total_risk, 2),
    }
