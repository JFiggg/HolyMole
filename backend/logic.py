"""
Static data and blast-radius logic for Holy Mole.
Menu dependencies (with optional sub-recipe layer), revenue impact; DFS-based blast radius.
"""
from typing import Any

# Sub-recipe -> list of ingredients (or nested sub-recipes) for 3-level depth
# e.g. Sandwich -> Spicy Mayo -> Mayo -> Eggs
SUB_RECIPE_GRAPH: dict[str, list[str]] = {
    "Spicy Mayo": ["Mayo", "Jalapeño"],
    "Mayo": ["Eggs", "Oil"],
}

# Menu Item (root) -> list of ingredients and/or sub-recipe names
MENU_GRAPH: dict[str, list[str]] = {
    # Sandwiches & Burgers (Spicy Mayo is sub-recipe: Mayo -> Eggs)
    "Spicy Chicken Sandwich": ["Bun", "Chicken", "Spicy Mayo", "Lettuce"],
    "Carnitas Burrito": ["Tortilla", "Pork", "Rice", "Black Beans", "Salsa", "Cheese", "Cilantro", "Lime"],
    "Steak Sandwich": ["Bun", "Steak", "Onion", "Bell Pepper", "Cheese"],
    "Fish Taco": ["Tortilla", "Fish", "Cabbage", "Lime", "Crema", "Salsa"],
    # Tacos
    "Steak Tacos": ["Tortilla", "Steak", "Lime", "Onion", "Cilantro"],
    "Chicken Tacos": ["Tortilla", "Chicken", "Lime", "Onion", "Salsa"],
    "Carnitas Tacos": ["Tortilla", "Pork", "Lime", "Onion", "Cilantro", "Salsa"],
    "Shrimp Tacos": ["Tortilla", "Shrimp", "Cabbage", "Lime", "Crema", "Avocados"],
    "Chorizo Tacos": ["Tortilla", "Chorizo", "Eggs", "Onion", "Cilantro"],
    "Baja Fish Tacos": ["Tortilla", "Fish", "Cabbage", "Lime", "Crema", "Hot Sauce"],
    # Burritos & Bowls
    "Breakfast Burrito": ["Tortilla", "Eggs", "Steak", "Avocados", "Salsa", "Cheese"],
    "Vegetarian Burrito": ["Tortilla", "Rice", "Black Beans", "Bell Pepper", "Onion", "Cheese", "Salsa", "Avocados"],
    "Guacamole Bowl": ["Avocados", "Lime", "Cilantro", "Tomato", "Onion", "Jalapeño"],
    "Bowl with Steak": ["Rice", "Black Beans", "Steak", "Salsa", "Cheese", "Avocados", "Cilantro", "Lime"],
    "Chipotle-Style Bowl": ["Rice", "Chicken", "Black Beans", "Salsa", "Cheese", "Lettuce", "Crema"],
    # Quesadillas & More
    "Quesadilla": ["Tortilla", "Cheese", "Chicken"],
    "Veggie Quesadilla": ["Tortilla", "Cheese", "Bell Pepper", "Onion", "Black Beans"],
    "Mole Enchiladas": ["Tortilla", "Chicken", "Mole Sauce", "Cheese", "Crema", "Onion"],
    # Seafood
    "Ceviche": ["Lime", "Avocados", "Fish", "Cilantro", "Onion", "Jalapeño", "Tomato"],
    "Shrimp Ceviche": ["Lime", "Avocados", "Shrimp", "Cilantro", "Onion", "Jalapeño", "Cucumber"],
    "Fish Ceviche": ["Lime", "Fish", "Avocados", "Cilantro", "Onion", "Jalapeño"],
    # Breakfast
    "Huevos Rancheros": ["Eggs", "Tortilla", "Salsa", "Black Beans", "Cheese", "Cilantro"],
    "Chilaquiles": ["Tortilla", "Eggs", "Salsa", "Cheese", "Crema", "Avocados"],
    "Breakfast Tacos": ["Tortilla", "Eggs", "Bacon", "Potato", "Cheese", "Salsa"],
    "Huevos con Chorizo": ["Eggs", "Chorizo", "Tortilla", "Salsa"],
    # Apps & Sides
    "Guac and Chips": ["Avocados", "Lime", "Cilantro", "Tomato", "Onion", "Chips"],
    "Elote": ["Corn", "Cheese", "Crema", "Lime", "Chili Powder"],
    "Street Corn Salad": ["Corn", "Avocados", "Lime", "Cilantro", "Cheese", "Crema"],
    "Queso Fundido": ["Cheese", "Chorizo", "Tortilla", "Jalapeño"],
    "Sopes": ["Flour", "Black Beans", "Chicken", "Lettuce", "Crema", "Cheese"],
    # Drinks
    "Margarita": ["Tequila", "Lime", "Triple Sec"],
    "Paloma": ["Tequila", "Lime", "Grapefruit Soda"],
    "Mango Margarita": ["Tequila", "Lime", "Triple Sec", "Mango"],
    "Pineapple Margarita": ["Tequila", "Lime", "Triple Sec", "Pineapple"],
    "Michelada": ["Beer", "Lime", "Hot Sauce", "Clamato"],
}

# Menu Item -> hourly revenue loss if unavailable ($)
REVENUE_IMPACT: dict[str, float] = {
    "Spicy Chicken Sandwich": 150.0,
    "Carnitas Burrito": 165.0,
    "Steak Sandwich": 140.0,
    "Fish Taco": 95.0,
    "Steak Tacos": 180.0,
    "Chicken Tacos": 130.0,
    "Carnitas Tacos": 155.0,
    "Shrimp Tacos": 120.0,
    "Chorizo Tacos": 100.0,
    "Baja Fish Tacos": 105.0,
    "Breakfast Burrito": 140.0,
    "Vegetarian Burrito": 90.0,
    "Guacamole Bowl": 120.0,
    "Bowl with Steak": 135.0,
    "Chipotle-Style Bowl": 125.0,
    "Quesadilla": 110.0,
    "Veggie Quesadilla": 75.0,
    "Mole Enchiladas": 145.0,
    "Ceviche": 90.0,
    "Shrimp Ceviche": 100.0,
    "Fish Ceviche": 85.0,
    "Huevos Rancheros": 95.0,
    "Chilaquiles": 105.0,
    "Breakfast Tacos": 115.0,
    "Huevos con Chorizo": 88.0,
    "Guac and Chips": 85.0,
    "Elote": 55.0,
    "Street Corn Salad": 70.0,
    "Queso Fundido": 80.0,
    "Sopes": 65.0,
    "Margarita": 200.0,
    "Paloma": 95.0,
    "Mango Margarita": 115.0,
    "Pineapple Margarita": 110.0,
    "Michelada": 75.0,
}


def _build_reverse_graph() -> dict[str, list[str]]:
    """Build reverse graph: node -> list of nodes that depend on it (menu items or sub-recipes)."""
    rev: dict[str, list[str]] = {}
    for menu_item, deps in MENU_GRAPH.items():
        for node in deps:
            rev.setdefault(node, []).append(menu_item)
    for sub_recipe, deps in SUB_RECIPE_GRAPH.items():
        for node in deps:
            rev.setdefault(node, []).append(sub_recipe)
    return rev


def _node_type(name: str) -> str:
    if name in MENU_GRAPH:
        return "menu_item"
    if name in SUB_RECIPE_GRAPH:
        return "sub_recipe"
    return "ingredient"


def calculate_blast_radius(ingredient_name: str) -> dict[str, Any]:
    """
    DFS from the given ingredient UP to all affected menu items (and sub-recipes).
    Returns nodes (with type), edges, and total revenue at risk.
    """
    rev = _build_reverse_graph()
    ingredient_name = ingredient_name.strip()
    if not ingredient_name:
        return {
            "ingredient": ingredient_name,
            "nodes": [],
            "edges": [],
            "affected_menu_items": [],
            "affected_with_revenue": [],
            "total_menu_count": len(MENU_GRAPH),
            "total_revenue_risk_per_hour": 0.0,
        }

    # Normalize key lookup
    key = next((k for k in rev if k.lower() == ingredient_name.lower()), None)
    if key is None:
        # Also check if it's a sub-recipe or menu item (e.g. user typed "Mayo")
        key = next(
            (k for k in (list(MENU_GRAPH) + list(SUB_RECIPE_GRAPH)) if k.lower() == ingredient_name.lower()),
            None,
        )
        if key is None:
            return {
                "ingredient": ingredient_name,
                "nodes": [],
                "edges": [],
                "affected_menu_items": [],
                "affected_with_revenue": [],
                "total_menu_count": len(MENU_GRAPH),
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
        for dependent in rev.get(node, []):
            edges.append({"from": node, "to": dependent})
            if dependent not in visited:
                stack.append(dependent)

    # Affected menu items = reachable menu-item nodes
    menu_items_set = set(MENU_GRAPH)
    affected = [n for n in visited if n in menu_items_set]
    total_risk = sum(REVENUE_IMPACT.get(m, 0.0) for m in affected)
    total_menu_count = len(MENU_GRAPH)
    affected_with_revenue = [
        {"menu_item": m, "revenue_per_hour": REVENUE_IMPACT.get(m, 0.0)}
        for m in affected
    ]

    nodes = [
        {"id": n, "label": n, "type": _node_type(n)}
        for n in visited
    ]

    return {
        "ingredient": key,
        "nodes": nodes,
        "edges": edges,
        "affected_menu_items": affected,
        "affected_with_revenue": affected_with_revenue,
        "total_menu_count": total_menu_count,
        "total_revenue_risk_per_hour": round(total_risk, 2),
    }
