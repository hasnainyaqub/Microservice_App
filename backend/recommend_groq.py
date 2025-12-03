import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import asyncio

from redis_cache import get_menu_from_cache, store_menu_in_cache
from database import fetch_menu, fetch_recent_orders

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("MODEL", "llama3.1-8b-instant")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not set")

client = Groq(api_key=GROQ_API_KEY)
router = APIRouter()

class Question(BaseModel):
    peoples: int
    mood: str
    spice_lvl: str
    avoid_anything: str
    budget: str

class InputPayload(BaseModel):
    branch: int
    question: Question

def build_prompt(menu, recent, q: Question, branch: int):
    menu_txt = "\n".join([f"{m['name']} | {m['category']} | {m['portion']} | price:{m['price']}" for m in menu])
    recent_txt = ", ".join([f"{k}:{v}" for k, v in recent.items()])

    prompt = f"""
You are a restaurant recommendation assistant.

Branch: {branch}
User preferences:
- people: {q.peoples}
- mood: {q.mood}
- spice: {q.spice_lvl}
- avoid: {q.avoid_anything}
- budget: {q.budget}

Recent popular items: {recent_txt}

Menu:
{menu_txt}

Task:
Return ONLY valid JSON with exactly 3 suggestions:
{{
  "branch": {branch},
  "suggestions": [
    {{
      "name": "<menu item name>",
      "category": "<category>",
      "portion": "<portion>",
      "price": <integer>,
      "reason": "<short reason>"
    }}
  ]
}}
"""
    return prompt

@router.post("/recommend")
async def recommend_groq(payload: InputPayload):
    branch = payload.branch
    q = payload.question

    menu = await get_menu_from_cache(branch)
    if not menu:
        menu = await fetch_menu(branch)
        await store_menu_in_cache(branch, menu)

    recent = await fetch_recent_orders(branch)
    prompt = build_prompt(menu, recent, q, branch)

    try:
        loop = asyncio.get_running_loop()
        resp = await loop.run_in_executor(None, lambda: client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "JSON only"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=512
        ))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Groq API error: {str(e)}")

    try:
        text = resp.choices[0].message["content"]
        parsed = json.loads(text)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed parsing Groq response: {e}")

    suggestions = parsed.get("suggestions", [])[:3]
    clean = []
    for s in suggestions:
        clean.append({
            "name": s.get("name", ""),
            "category": s.get("category", ""),
            "portion": s.get("portion", ""),
            "price": int(s.get("price", 0)),
            "reason": s.get("reason", "")
        })

    return {"branch": branch, "suggestions": clean}

@router.post("/recommendd")
async def recommend_groq(payload: InputPayload):
    # Temporary static sample for testing
    branch = payload.branch
    suggestions = [
        {"name": "Margherita Pizza", "category": "Pizza", "portion": "Medium", "price": 500, "reason": "Popular choice"},
        {"name": "Veggie Burger", "category": "Burger", "portion": "Single", "price": 350, "reason": "Healthy option"},
        {"name": "Caesar Salad", "category": "Salad", "portion": "Large", "price": 400, "reason": "Light meal"}
    ]
    return {"branch": branch, "suggestions": suggestions}