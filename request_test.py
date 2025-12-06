import requests

url = "http://localhost:8004/api/recommend"
payload = {
    "branch": 1,
    "question": {
        "peoples": 6,
        "mood": "happy",
        "spice_lvl": "medium",
        "avoid_anything": "nuts",
        "budget": "tight"
    }
}

try:
    resp = requests.post(url, json=payload, timeout=10)
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print("Error:", e)

