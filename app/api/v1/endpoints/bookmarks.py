from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.cache import get_cache, set_cache  # Make sure this is imported!
from app.core.database import get_db
from app.core.limiter import limiter
from app.core.worker import REDIS_SETTINGS, create_pool  # NEW IMPORTS
from app.crud.bookmarks import get_bookmark_by_id
from app.models.bookmark import Bookmark
from app.models.tag import Tag
from app.models.user import User
from app.schemas.bookmark import BookmarkCreate, BookmarkResponse, BookmarkUpdate
from app.schemas.common import PaginatedResponse

router = APIRouter()


# ✅ ADD THIS HELPER FUNCTION (from Phase 1)
async def get_or_create_tags(db: AsyncSession, tag_names: list[str]) -> list[Tag]:
    """
    For each tag name, find it in the DB or create it.
    Returns the list of Tag objects.
    """
    tags = []
    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue
        # Try to find existing tag
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if not tag:
            # Create new tag with URL-friendly slug
            tag = Tag(name=name, slug=slugify(name))
            db.add(tag)
            await db.flush()  # send to DB to get the ID, but don't commit yet
        tags.append(tag)
    return tags


@router.post("/", response_model=BookmarkResponse)
async def create_bookmark(
    bookmark_in: BookmarkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Create the bookmark with a placeholder note
    bookmark = Bookmark(
        title=bookmark_in.title,
        url=str(bookmark_in.url),
        notes="⏳ AI is generating your summary...",  # Placeholder!
        owner_id=current_user.id,
    )

    # 2. Handle tags (from Phase 1)
    if bookmark_in.tag_names:
        bookmark.tags = await get_or_create_tags(db, bookmark_in.tag_names)

    # 3. Save to database FIRST
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)

    # 4. QUEUE THE BACKGROUND JOB (AFTER COMMIT!)
    redis_pool = await create_pool(REDIS_SETTINGS)
    await redis_pool.enqueue_job("summarize_bookmark", bookmark.id)

    # 5. Return immediately to the user
    return bookmark


@router.get("/", response_model=PaginatedResponse[BookmarkResponse])
@limiter.limit("30/minute")
async def get_bookmarks(
    request: Request,
    search: str | None = None,
    tag_id: int | None = None,
    page: int = 1,  # ✅ NEW: Default to page 1
    size: int = 20,  # ✅ NEW: Default to 20 items per page
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Create cache key (include page and size!)
    cache_key = f"bookmarks:{current_user.id}:{search}:{tag_id}:{page}:{size}"

    # 2. Check cache (same as before)
    cached_data = await get_cache(cache_key)
    if cached_data:
        print("✅ Cache HIT (Paginated)")
        return cached_data

    print(" Cache MISS. Querying database...")

    # 3. Build the base query
    query = select(Bookmark).where(
        Bookmark.owner_id == current_user.id, Bookmark.deleted_at.is_(None)
    )

    if search:
        search_term = f"%{search}%"
        query = query.where(
            (Bookmark.title.ilike(search_term)) | (Bookmark.notes.ilike(search_term))
        )

    if tag_id:
        query = query.join(Bookmark.tags).where(Tag.id == tag_id)

    # 4. COUNT TOTAL ITEMS (Before applying pagination)
    # We create a separate query just to count: SELECT COUNT(*) FROM ...
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # 5. APPLY PAGINATION
    # Calculate OFFSET: (Page 1 = offset 0, Page 2 = offset 20, etc.)
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # 6. Execute the paginated query
    result = await db.execute(query)
    bookmarks = result.scalars().all()

    # 7. Convert to JSON
    bookmark_dicts = [
        BookmarkResponse.model_validate(b).model_dump(mode="json") for b in bookmarks
    ]

    # 8. Calculate total pages
    total_pages = (total + size - 1) // size  # Ceiling division

    # 9. Build the response
    response = PaginatedResponse(
        items=bookmark_dicts, total=total, page=page, size=size, pages=total_pages
    )

    # 10. Save to cache
    await set_cache(cache_key, response.model_dump(mode="json"), expire=60)

    return response


@router.get("/{bookmark_id}", response_model=BookmarkResponse)
async def read_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ✅ ONE CLEAN LINE using our new CRUD function!
    bookmark = await get_bookmark_by_id(db, bookmark_id, current_user.id)

    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    return bookmark


@router.put("/{bookmark_id}", response_model=BookmarkResponse)
async def update_bookmark(
    bookmark_id: int,
    bookmark_in: BookmarkUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.owner_id == current_user.id,
            Bookmark.deleted_at.is_(None),  # ✅ SOFT DELETE CHECK
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    update_data = bookmark_in.model_dump(exclude_unset=True)

    # Handle tag updates if provided
    if "tag_names" in update_data:
        tag_names = update_data.pop("tag_names")
        if tag_names is not None:
            bookmark.tags = await get_or_create_tags(db, tag_names)

    if "url" in update_data:
        update_data["url"] = str(update_data["url"])
    for field, value in update_data.items():
        setattr(bookmark, field, value)

    await db.commit()
    await db.refresh(bookmark)
    return bookmark


@router.delete("/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.owner_id == current_user.id,
            Bookmark.deleted_at.is_(None),  # ✅ SOFT DELETE CHECK
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # ✅ SOFT DELETE: set deleted_at instead of removing the row
    bookmark.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Bookmark deleted"}
