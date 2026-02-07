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
    {"name": "Avocados", "category": "Produce", "quantity": 100.0, "unit": "count", "unit_cost": 0.85, "par_level": 50.0, "daily_usage": 30.0},
    {"name": "Steak", "category": "Protein", "quantity": 40.0, "unit": "lb", "unit_cost": 8.50, "par_level": 25.0, "daily_usage": 15.0},
    {"name": "Eggs", "category": "Dairy", "quantity": 120.0, "unit": "count", "unit_cost": 0.25, "par_level": 60.0, "daily_usage": 48.0},
    {"name": "Lime", "category": "Produce", "quantity": 80.0, "unit": "count", "unit_cost": 0.20, "par_level": 40.0, "daily_usage": 35.0},
    {"name": "Tequila", "category": "Spirits", "quantity": 12.0, "unit": "bottle", "unit_cost": 18.0, "par_level": 6.0, "daily_usage": 3.0},
]


@app.on_event("startup")
def startup():
    init_db()


@app.get("/inventory")
def get_inventory(db: Session = Depends(get_db)):
    """Return all ingredients from the database."""
    ingredients = db.query(Ingredient).all()
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
        for i in ingredients
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
