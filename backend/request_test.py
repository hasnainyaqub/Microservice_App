import requests

url = "http://localhost:8003/api/recommend"
payload = {
    "branch": 1,
    "question": {
        "peoples": 2,
        "mood": "happy",
        "spice_lvl": "medium",
        "avoid_anything": "nuts",
        "budget": "medium"
    }
}

try:
    resp = requests.post(url, json=payload, timeout=10)
    print(resp.status_code)
    print(resp.text)
except Exception as e:
    print("Error:", e)

