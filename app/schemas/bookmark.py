from datetime import datetime
from pydantic import BaseModel, HttpUrl

# 1. Tag Schema (for the response)
class TagResponse(BaseModel):
    id: int
    name: str
    slug: str

    class Config:
        from_attributes = True


# 2. Base Schema (Removed tag_id, we use tag_names now)
class BookmarkBase(BaseModel):
    title: str
    url: HttpUrl
    notes: str | None = None


# 3. Create Schema (Fixed the typo: 'Non' -> 'None')
class BookmarkCreate(BookmarkBase):
    tag_names: list[str] | None = None


# 4. Update Schema (Removed tag_id)
class BookmarkUpdate(BaseModel):
    title: str | None = None
    url: HttpUrl | None = None
    notes: str | None = None
    tag_names: list[str] | None = None


# 5. Response Schema (Added deleted_at and tags)
class BookmarkResponse(BookmarkBase):
    id: int
    owner_id: int
    created_at: datetime
    deleted_at: datetime | None = None  # For soft deletes
    tags: list[TagResponse] = []  # For many-to-many tags

    class Config:
        from_attributes = True
