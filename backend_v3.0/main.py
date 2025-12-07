from fastapi import FastAPI
from recommend_local import router as recommend_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Restaurant Recommendation API Running"}

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(recommend_router, prefix="/api")
