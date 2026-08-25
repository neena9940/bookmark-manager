from datetime import datetime

from pydantic import BaseModel, HttpUrl


class BookmarkBase(BaseModel):
    title: str
    url: HttpUrl
    notes: str | None = None
    tag_id: int | None = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    title: str | None = None
    url: HttpUrl | None = None
    notes: str | None = None
    tag_id: int | None = None


class BookmarkResponse(BookmarkBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True
