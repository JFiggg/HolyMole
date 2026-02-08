"""
Holy Mole API: inventory, seed, blast-radius, and simulate-rush endpoints.
"""
import random
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db, SessionLocal, Ingredient
from logic import calculate_blast_radius

app = FastAPI(title="Holy Mole API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Seed data for Tex-Mex ingredients -----
SEED_INGREDIENTS = [
    # Produce
    {"name": "Avocados", "category": "Produce", "quantity": 100.0, "unit": "count", "unit_cost": 0.85, "par_level": 50.0, "daily_usage": 30.0},
    {"name": "Lime", "category": "Produce", "quantity": 80.0, "unit": "count", "unit_cost": 0.20, "par_level": 40.0, "daily_usage": 35.0},
    {"name": "Cilantro", "category": "Produce", "quantity": 25.0, "unit": "bunch", "unit_cost": 0.75, "par_level": 12.0, "daily_usage": 10.0},
    {"name": "Onion", "category": "Produce", "quantity": 60.0, "unit": "count", "unit_cost": 0.35, "par_level": 30.0, "daily_usage": 25.0},
    {"name": "Tomato", "category": "Produce", "quantity": 90.0, "unit": "count", "unit_cost": 0.45, "par_level": 45.0, "daily_usage": 40.0},
    {"name": "Jalapeño", "category": "Produce", "quantity": 50.0, "unit": "count", "unit_cost": 0.15, "par_level": 25.0, "daily_usage": 20.0},
    {"name": "Bell Pepper", "category": "Produce", "quantity": 40.0, "unit": "count", "unit_cost": 0.80, "par_level": 20.0, "daily_usage": 15.0},
    {"name": "Corn", "category": "Produce", "quantity": 24.0, "unit": "ear", "unit_cost": 0.40, "par_level": 12.0, "daily_usage": 10.0},
    {"name": "Garlic", "category": "Produce", "quantity": 20.0, "unit": "head", "unit_cost": 0.50, "par_level": 10.0, "daily_usage": 8.0},
    {"name": "Lettuce", "category": "Produce", "quantity": 15.0, "unit": "head", "unit_cost": 1.20, "par_level": 8.0, "daily_usage": 6.0},
    {"name": "Cabbage", "category": "Produce", "quantity": 12.0, "unit": "head", "unit_cost": 0.90, "par_level": 6.0, "daily_usage": 5.0},
    {"name": "Cucumber", "category": "Produce", "quantity": 30.0, "unit": "count", "unit_cost": 0.40, "par_level": 15.0, "daily_usage": 12.0},
    {"name": "Radish", "category": "Produce", "quantity": 20.0, "unit": "bunch", "unit_cost": 0.60, "par_level": 10.0, "daily_usage": 8.0},
    {"name": "Mango", "category": "Produce", "quantity": 24.0, "unit": "count", "unit_cost": 1.00, "par_level": 12.0, "daily_usage": 10.0},
    {"name": "Pineapple", "category": "Produce", "quantity": 8.0, "unit": "count", "unit_cost": 2.50, "par_level": 4.0, "daily_usage": 3.0},
    # Protein
    {"name": "Steak", "category": "Protein", "quantity": 40.0, "unit": "lb", "unit_cost": 8.50, "par_level": 25.0, "daily_usage": 15.0},
    {"name": "Chicken", "category": "Protein", "quantity": 50.0, "unit": "lb", "unit_cost": 3.25, "par_level": 30.0, "daily_usage": 22.0},
    {"name": "Fish", "category": "Protein", "quantity": 25.0, "unit": "lb", "unit_cost": 12.0, "par_level": 15.0, "daily_usage": 10.0},
    {"name": "Shrimp", "category": "Protein", "quantity": 15.0, "unit": "lb", "unit_cost": 14.0, "par_level": 8.0, "daily_usage": 6.0},
    {"name": "Chorizo", "category": "Protein", "quantity": 20.0, "unit": "lb", "unit_cost": 5.50, "par_level": 10.0, "daily_usage": 8.0},
    {"name": "Ground Beef", "category": "Protein", "quantity": 35.0, "unit": "lb", "unit_cost": 4.50, "par_level": 20.0, "daily_usage": 15.0},
    {"name": "Pork", "category": "Protein", "quantity": 30.0, "unit": "lb", "unit_cost": 3.80, "par_level": 18.0, "daily_usage": 12.0},
    {"name": "Bacon", "category": "Protein", "quantity": 18.0, "unit": "lb", "unit_cost": 6.00, "par_level": 10.0, "daily_usage": 7.0},
    # Dairy
    {"name": "Eggs", "category": "Dairy", "quantity": 120.0, "unit": "count", "unit_cost": 0.25, "par_level": 60.0, "daily_usage": 48.0},
    {"name": "Cheese", "category": "Dairy", "quantity": 25.0, "unit": "lb", "unit_cost": 4.50, "par_level": 15.0, "daily_usage": 12.0},
    {"name": "Crema", "category": "Dairy", "quantity": 12.0, "unit": "quart", "unit_cost": 3.50, "par_level": 6.0, "daily_usage": 5.0},
    {"name": "Butter", "category": "Dairy", "quantity": 10.0, "unit": "lb", "unit_cost": 4.00, "par_level": 6.0, "daily_usage": 4.0},
    # Pantry / Bread
    {"name": "Tortilla", "category": "Pantry", "quantity": 200.0, "unit": "count", "unit_cost": 0.08, "par_level": 100.0, "daily_usage": 80.0},
    {"name": "Bun", "category": "Pantry", "quantity": 80.0, "unit": "count", "unit_cost": 0.30, "par_level": 40.0, "daily_usage": 35.0},
    {"name": "Rice", "category": "Pantry", "quantity": 25.0, "unit": "lb", "unit_cost": 0.60, "par_level": 15.0, "daily_usage": 10.0},
    {"name": "Black Beans", "category": "Pantry", "quantity": 15.0, "unit": "lb", "unit_cost": 0.90, "par_level": 10.0, "daily_usage": 6.0},
    {"name": "Pinto Beans", "category": "Pantry", "quantity": 15.0, "unit": "lb", "unit_cost": 0.85, "par_level": 10.0, "daily_usage": 6.0},
    {"name": "Chips", "category": "Pantry", "quantity": 24.0, "unit": "bag", "unit_cost": 2.50, "par_level": 12.0, "daily_usage": 10.0},
    {"name": "Flour", "category": "Pantry", "quantity": 50.0, "unit": "lb", "unit_cost": 0.35, "par_level": 25.0, "daily_usage": 8.0},
    {"name": "Potato", "category": "Produce", "quantity": 40.0, "unit": "lb", "unit_cost": 0.45, "par_level": 25.0, "daily_usage": 15.0},
    {"name": "Chili Powder", "category": "Pantry", "quantity": 5.0, "unit": "lb", "unit_cost": 8.00, "par_level": 3.0, "daily_usage": 0.5},
    # Condiments / Sauces
    {"name": "Mayo", "category": "Condiments", "quantity": 6.0, "unit": "quart", "unit_cost": 5.00, "par_level": 4.0, "daily_usage": 2.0},
    {"name": "Salsa", "category": "Condiments", "quantity": 12.0, "unit": "quart", "unit_cost": 4.00, "par_level": 8.0, "daily_usage": 6.0},
    {"name": "Mole Sauce", "category": "Condiments", "quantity": 8.0, "unit": "quart", "unit_cost": 6.00, "par_level": 5.0, "daily_usage": 3.0},
    {"name": "Hot Sauce", "category": "Condiments", "quantity": 24.0, "unit": "bottle", "unit_cost": 2.00, "par_level": 12.0, "daily_usage": 8.0},
    # Spirits
    {"name": "Tequila", "category": "Spirits", "quantity": 12.0, "unit": "bottle", "unit_cost": 18.0, "par_level": 6.0, "daily_usage": 3.0},
    {"name": "Triple Sec", "category": "Spirits", "quantity": 8.0, "unit": "bottle", "unit_cost": 12.0, "par_level": 4.0, "daily_usage": 2.0},
    {"name": "Grapefruit Soda", "category": "Beverages", "quantity": 24.0, "unit": "bottle", "unit_cost": 1.50, "par_level": 12.0, "daily_usage": 8.0},
    {"name": "Beer", "category": "Beverages", "quantity": 48.0, "unit": "case", "unit_cost": 28.0, "par_level": 24.0, "daily_usage": 18.0},
    {"name": "Clamato", "category": "Beverages", "quantity": 12.0, "unit": "bottle", "unit_cost": 3.50, "par_level": 6.0, "daily_usage": 4.0},
]


@app.on_event("startup")
def startup():
    init_db()


@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    """Return all ingredients from the database, sorted with out-of-stock items first."""
    ingredients = db.query(Ingredient).all()
    
    # Sort: critical items (below par) first, then by days on hand
    def sort_key(i):
        is_critical = i.quantity < i.par_level
        days_on_hand = i.quantity / i.daily_usage if i.daily_usage > 0 else 999.0
        return (
            not is_critical,  # False (critical) comes before True (non-critical)
            days_on_hand,     # Lower days on hand first
        )
    
    sorted_ingredients = sorted(ingredients, key=sort_key)
    
    return [
        {
            "id": i.id,
            "name": i.name,
            "category": i.category,
            "quantity": i.quantity,
            "unit": i.unit,
            "par_level": i.par_level,
            "daily_usage": i.daily_usage,
        }
        for i in sorted_ingredients
    ]


@app.post("/seed")
def seed_db(db: Session = Depends(get_db)):
    """Wipe and reseed the database with Tex-Mex ingredients."""
    db.query(Ingredient).delete()
    db.commit()
    for data in SEED_INGREDIENTS:
        ing = Ingredient(**data)
        db.add(ing)
    db.commit()
    return {"status": "ok", "message": "Database reseeded with Tex-Mex ingredients."}


@app.get("/blast-radius/{ingredient_name:path}")
def blast_radius(ingredient_name: str):
    """Return dependency graph and revenue risk for the given ingredient."""
    return calculate_blast_radius(ingredient_name)


@app.post("/simulate-rush")
def simulate_rush(db: Session = Depends(get_db)):
    """Randomly lower stock of random items to simulate a dinner rush."""
    ingredients = db.query(Ingredient).all()
    if not ingredients:
        return {"status": "ok", "message": "No ingredients to simulate."}
    # Pick 1–3 random ingredients and reduce quantity by 10–40%
    n = min(random.randint(1, 3), len(ingredients))
    chosen = random.sample(ingredients, n)
    for ing in chosen:
        pct = random.uniform(0.10, 0.40)
        new_qty = max(0.0, ing.quantity * (1 - pct))
        ing.quantity = round(new_qty, 2)
    db.commit()
    return {
        "status": "ok",
        "message": "Rush simulated.",
        "updated": [{"name": i.name, "quantity": i.quantity} for i in chosen],
    }


@app.post("/restock/{ingredient_name:path}")
def restock_ingredient(ingredient_name: str, db: Session = Depends(get_db)):
    """Restock a specific ingredient to 2x its par level."""
    # Find the ingredient by name (case-insensitive)
    ingredient = db.query(Ingredient).filter(
        Ingredient.name.ilike(ingredient_name)
    ).first()
    
    if not ingredient:
        return {"status": "error", "message": f"Ingredient '{ingredient_name}' not found."}, 404
    
    # Calculate restock details
    old_quantity = ingredient.quantity
    new_quantity = ingredient.par_level * 2
    quantity_added = new_quantity - old_quantity
    total_cost = quantity_added * ingredient.unit_cost
    
    # Update the quantity
    ingredient.quantity = round(new_quantity, 2)
    db.commit()
    
    return {
        "status": "ok",
        "message": f"Successfully restocked {ingredient.name}.",
        "ingredient": ingredient.name,
        "old_quantity": round(old_quantity, 2),
        "new_quantity": round(new_quantity, 2),
        "quantity_added": round(quantity_added, 2),
        "unit": ingredient.unit,
        "unit_cost": ingredient.unit_cost,
        "total_cost": round(total_cost, 2),
    }
