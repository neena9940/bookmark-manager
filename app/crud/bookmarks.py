from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bookmark import Bookmark


async def get_bookmark_by_id(db: AsyncSession, bookmark_id: int, owner_id: int):
    """
    Fetches a single bookmark from the database.
    Returns None if not found or if it belongs to another user.
    """
    # 1. Build the query
    query = select(Bookmark).where(
        Bookmark.id == bookmark_id,
        Bookmark.owner_id == owner_id,
        Bookmark.deleted_at.is_(None),  # Don't return soft-deleted items
    )

    # 2. Execute and return
    result = await db.execute(query)
    return result.scalar_one_or_none()
