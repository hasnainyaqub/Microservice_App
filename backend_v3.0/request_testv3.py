import requests
import json

payload = {
    "branch": 1,
    "question": {
        "peoples": 2,
        "mood": "spicy_craving",
        "spice_lvl": "medium",
        "avoid_anything": "nuts",
        "budget": "tight",
        "meal_time": "lunch",
    }
}

resp = requests.post("http://localhost:8004/api/recommend", json=payload)
print(resp.status_code)
print(resp.text)
