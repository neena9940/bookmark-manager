from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic handles the database now, so we just yield
    yield


app = FastAPI(title="Bookmark Manager", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
