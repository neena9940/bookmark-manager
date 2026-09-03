from contextlib import asynccontextmanager
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.v1.api import api_router
from app.core.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic handles the database now, so we just yield
    yield


app = FastAPI(title="Bookmark Manager", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]



@app.get("/health")
async def health():
    return {"status": "ok"}
