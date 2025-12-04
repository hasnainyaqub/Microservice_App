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


class InputPayload(BaseModel):
    branch: int
    question: Question


# Helper: match mood
def mood_match(item_name, mood):
    if mood.lower() in item_name.lower():
        return 1
    return 0


# Helper: match spice
def spice_match(item_name, spice):
    spice_keywords = {
        "low": ["mild", "light"],
        "medium": ["medium", "regular"],
        "high": ["spicy", "hot"],
    }

    target = spice.lower()
    if target in spice_keywords:
        for word in spice_keywords[target]:
            if word in item_name.lower():
                return 1

    return 0


# Helper: price match with budget
def budget_match(price, budget):
    budget = budget.lower()
    if budget == "tight" and price <= 500:
        return 1
    if budget == "medium" and price <= 1200:
        return 1
    if budget == "comfortable":
        return 1
    return 0


# Main route
@router.post("/recommend")
async def recommend_local(payload: InputPayload):

    branch = payload.branch
    q = payload.question

    # Try to load menu from Redis
    menu = await get_menu_from_cache(branch)

    # If Redis miss, load from MySQL and store in Redis
    if not menu:
        menu = await fetch_menu(branch)
        await store_menu_in_cache(branch, menu)

    # Fetch recent orders for simple popularity scoring
    popularity = await fetch_recent_orders(branch)

    scored_items = []

    for item in menu:
        name = item["name"]
        price = item["price"]

        # 1. Avoid logic
        if q.avoid_anything.lower() in name.lower():
            continue

        # 2. Apply scoring
        s_mood = mood_match(name, q.mood)
        s_spice = spice_match(name, q.spice_lvl)
        s_budget = budget_match(price, q.budget)
        s_pop = popularity.get(name, 0)

        # Final weighted score
        score = (
            (s_spice * 3)
            + (s_budget * 3)
            + (s_mood * 2)
            + (s_pop * 1)
        )

        scored_items.append({
            "name": item["name"],
            "category": item["category"],
            "portion": item["portion"],
            "price": item["price"],
            "score": score,
        })

    # If no items returned
    if not scored_items:
        return {
            "branch": branch,
            "suggestions": []
        }

    # Sort by score descending
    sorted_items = sorted(scored_items, key=lambda x: x["score"], reverse=True)

    # Pick top 3
    top3 = sorted_items[:3]

    return {
        "branch": branch,
        "suggestions": [
            {
                "name": item["name"],
                "category": item["category"],
                "portion": item["portion"],
                "price": item["price"],
                "score": item["score"],
            }
            for item in top3
        ]
    }
