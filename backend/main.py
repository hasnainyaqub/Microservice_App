from fastapi import FastAPI
from recommend_groq import router as recommend_router

app = FastAPI(title="Restaurant Recommender Backend")
app.include_router(recommend_router, prefix="/api")



@app.get("/")
async def root():
    return {"message": "Restaurant Recommender Backend is running!"}

@app.get("/health")
async def health():
    return {"status": "ok"}
