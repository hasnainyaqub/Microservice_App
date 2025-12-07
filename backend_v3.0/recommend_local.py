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
    budget: str
    meal_time: str          # breakfast, lunch, dinner


class InputPayload(BaseModel):
    branch: int
    question: Question


# CATEGORY PRIORITY BY MEAL TIME
MEAL_PRIORITY = {
    "breakfast": ["Sandwich", "Omelette", "Paratha", "Tea", "Coffee", "Dessert"],
    "lunch": ["Rice", "Karahi", "BBQ", "Curry", "Appetizer", "Drink"],
    "dinner": ["Pizza", "Burger", "Roll", "Karahi", "BBQ", "Appetizer", "Drink", "Dessert"]
}

# fallback if no meal_time provided
DEFAULT_PRIORITY = [
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


# Peoples + Budget + Mood based budget calculator
def get_budget_range(peoples, budget, mood):

    if peoples == 1:
        base = 600
    elif peoples == 2:
        base = 1200
    elif peoples == 3:
        base = 1800
    elif peoples == 4:
        base = 2500
    elif peoples == 5:
        base = 3200
    else:
        base = peoples * 600

    if budget == "tight":
        base *= 1.0
    elif budget == "medium":
        base *= 1.4
    elif budget == "comfortable":
        base *= 1.8

    mood_factor = {
        "spicy_craving": 1.3,
        "cheesy_mood": 1.3,
        "sweet_craving": 1.1,
        "healthy_choice": 0.9,
        "heavy_meal": 1.5,
        "light_meal": 0.8
    }

    factor = mood_factor.get(mood, 1.0)
    final = base * factor

    return int(final * 0.7), int(final), int(final * 1.3)


# Mood scoring
def mood_match(name, mood):
    mood_keywords = {
        "spicy_craving": ["spicy", "hot"],
        "cheesy_mood": ["cheese", "cheesy"],
        "sweet_craving": ["sweet", "dessert", "cake", "brownie"],
        "healthy_choice": ["salad", "grill", "low fat"],
        "heavy_meal": ["karahi", "biryani", "handi", "qorma"],
        "light_meal": ["soup", "salad", "fries"]
    }

    if mood not in mood_keywords:
        return 0

    for w in mood_keywords[mood]:
        if w.lower() in name.lower():
            return 1
    return 0


# Spice scoring
def spice_match(name, spice):
    levels = {
        "low": ["mild", "light"],
        "medium": ["regular", "medium"],
        "high": ["hot", "spicy"]
    }

    if spice not in levels:
        return 0

    for w in levels[spice]:
        if w.lower() in name.lower():
            return 1
    return 0


# Build a single deal
def build_deal(scored, peoples, ideal_budget, hard_budget, cat_priority, shift=0):

    grouped = {}
    for item in scored:
        cat = item["category"]
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(item)

    deal = []
    total_cost = 0

    priority = cat_priority[shift:] + cat_priority[:shift]

    for cat in priority:
        if cat not in grouped:
            continue

        best = grouped[cat][0]

        qty = peoples
        cost = qty * best["price"]

        if total_cost + cost > hard_budget:
            continue

        deal.append({
            "name": best["name"],
            "category": best["category"],
            "qty": qty,
            "unit_price": best["price"],
            "total_price": cost
        })

        total_cost += cost

        if total_cost >= ideal_budget:
            break

    return deal, total_cost


@router.post("/recommend")
async def recommend_local(payload: InputPayload):

    q = payload.question
    branch = payload.branch

    min_budget, ideal_budget, hard_budget = get_budget_range(q.peoples, q.budget, q.mood)

    menu = await get_menu_from_cache(branch)
    if not menu:
        menu = await fetch_menu(branch)
        await store_menu_in_cache(branch, menu)

    popularity = await fetch_recent_orders(branch)

    # Apply avoid filter
    filtered = []
    for item in menu:
        if q.avoid_anything.lower() in item["name"].lower():
            continue
        filtered.append(item)

    # Scoring
    scored = []
    for item in filtered:
        score = (
            mood_match(item["name"], q.mood) * 2 +
            spice_match(item["name"], q.spice_lvl) * 3 +
            popularity.get(item["name"], 0)
        )

        scored.append({
            "name": item["name"],
            "category": item["category"],
            "portion": item["portion"],
            "price": item["price"],
            "score": score
        })

    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    # Decide category priority based on meal time
    cat_priority = MEAL_PRIORITY.get(q.meal_time, DEFAULT_PRIORITY)

    # Generate 3 unique deals
    deal1, cost1 = build_deal(scored, q.peoples, ideal_budget, hard_budget, cat_priority, shift=0)
    deal2, cost2 = build_deal(scored, q.peoples, ideal_budget, hard_budget, cat_priority, shift=2)
    deal3, cost3 = build_deal(scored, q.peoples, ideal_budget, hard_budget, cat_priority, shift=4)

    return {
        "branch": branch,
        "peoples": q.peoples,
        "mood": q.mood,
        "meal_time": q.meal_time,
        "budget_type": q.budget,
        "budget_limit": hard_budget,
        "deals": [
            {"deal_number": 1, "items": deal1, "total_cost": cost1},
            {"deal_number": 2, "items": deal2, "total_cost": cost2},
            {"deal_number": 3, "items": deal3, "total_cost": cost3}
        ]
    }
