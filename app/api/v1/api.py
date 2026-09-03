from fastapi import APIRouter
from app.api.v1.endpoints import auth, bookmarks, tags, uploads

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(bookmarks.router, prefix="/bookmarks", tags=["bookmarks"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
