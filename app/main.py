from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic handles the database now, so we just yield
    yield

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Bookmark Manager", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok"}
