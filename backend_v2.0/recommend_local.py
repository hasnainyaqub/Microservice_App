from fastapi import APIRouter
from pydantic import BaseModel

from database import fetch_menu, fetch_recent_orders
from redis_cache import get_menu_from_cache, store_menu_in_cache

router = APIRouter()


# Input schema
class Question(BaseModel):
    peoples: int
    mood: str
    spice_lvl: str
    avoid_anything: str
    budget: str  # tight, medium, comfortable


class InputPayload(BaseModel):
    branch: int
    question: Question


# New Budget Logic Based on Peoples + Budget Type
def get_budget_range(peoples, budget):
    # Base values depending on peoples
    if peoples == 1:
        base_tight = 500
        base_medium = 800
        base_comfort = 1200
    elif peoples == 2:
        base_tight = 1200
        base_medium = 1800
        base_comfort = 2500
    elif peoples == 3:
        base_tight = 1500
        base_medium = 2500
        base_comfort = 3500
    elif peoples == 5:
        base_tight = 2500
        base_medium = 3500
        base_comfort = 5000
    else:
        base_tight = peoples * 500
        base_medium = peoples * 800
        base_comfort = peoples * 1200

    if budget == "tight":
        return (base_tight, base_tight + 300, base_tight + 600)

    if budget == "medium":
        return (base_medium, base_medium + 400, base_medium + 800)

    if budget == "comfortable":
        return (base_comfort, base_comfort + 600, base_comfort + 1200)

    return (base_medium, base_medium + 400, base_medium + 800)


CATEGORY_PRIORITY = [
    "Pizza",
    "Burger",
    "Roll",
    "Rice",
    "Karahi",
    "BBQ",
    "Appetizer",
    "Fries",
    "Drink",
    "Dessert",
]


def mood_match(name, mood):
    return 1 if mood.lower() in name.lower() else 0


def spice_match(name, spice):
    keywords = {
        "low": ["mild", "light"],
        "medium": ["medium", "regular"],
        "high": ["spicy", "hot"]
    }

    if spice.lower() not in keywords:
        return 0

    for k in keywords[spice.lower()]:
        if k in name.lower():
            return 1
    return 0


# BUILD A SINGLE DEAL
def build_deal(scored_items, peoples, ideal_budget, hard_budget, priority_shift=0):
    grouped = {}

    # Group items by category
    for item in scored_items:
        cat = item["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)

    deal_items = []
    total_cost = 0

    # SHIFT CATEGORY PRIORITY FOR UNIQUE DEALS
    shifted_priority = CATEGORY_PRIORITY[priority_shift:] + CATEGORY_PRIORITY[:priority_shift]

    for cat in shifted_priority:
        if cat not in grouped:
            continue

        best_item = grouped[cat][0]

        qty = max(1, peoples)
        cost = qty * best_item["price"]

        if total_cost + cost > hard_budget:
            continue

        deal_items.append({
            "name": best_item["name"],
            "category": best_item["category"],
            "qty": qty,
            "unit_price": best_item["price"],
            "total_price": cost
        })

        total_cost += cost

        if total_cost >= ideal_budget:
            break

    return deal_items, total_cost


# MAIN ROUTE
@router.post("/recommend")
async def recommend_local(payload: InputPayload):

    branch = payload.branch
    q = payload.question

    # Get budget limits
    min_budget, ideal_budget, hard_budget = get_budget_range(q.peoples, q.budget)

    # MENU LOADING (redis → db)
    menu = await get_menu_from_cache(branch)
    if not menu:
        menu = await fetch_menu(branch)
        await store_menu_in_cache(branch, menu)

    popularity = await fetch_recent_orders(branch)

    # REMOVE AVOID ITEMS
    filtered = []
    for item in menu:
        if q.avoid_anything.lower() in item["name"].lower():
            continue
        filtered.append(item)

    # SCORING
    scored = []
    for item in filtered:
        score = (
            mood_match(item["name"], q.mood) * 2
            + spice_match(item["name"], q.spice_lvl) * 3
            + popularity.get(item["name"], 0)
        )

        scored.append({
            "name": item["name"],
            "category": item["category"],
            "portion": item["portion"],
            "price": item["price"],
            "score": score
        })

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    # BUILD 3 UNIQUE DEALS
    deal1, cost1 = build_deal(scored, q.peoples, ideal_budget, hard_budget, priority_shift=0)
    deal2, cost2 = build_deal(scored, q.peoples, ideal_budget, hard_budget, priority_shift=2)
    deal3, cost3 = build_deal(scored, q.peoples, ideal_budget, hard_budget, priority_shift=4)

    return {
        "branch": branch,
        "peoples": q.peoples,
        "budget_type": q.budget,
        "budget_limit": hard_budget,
        "deals": [
            {"deal_number": 1, "items": deal1, "total_cost": cost1},
            {"deal_number": 2, "items": deal2, "total_cost": cost2},
            {"deal_number": 3, "items": deal3, "total_cost": cost3},
        ]
    }

