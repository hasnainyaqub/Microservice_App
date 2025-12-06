from fastapi import FastAPI
from recommend_local import router as recommend_router

app = FastAPI(
    title="Local Restaurant Recommender",
    version="1.0"
)

app.include_router(recommend_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Local Recommendation Backend Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
