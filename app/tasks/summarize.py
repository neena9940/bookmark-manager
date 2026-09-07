from sqlalchemy import select
from app.core.ai_service import generate_bookmark_summary
from app.core.database import AsyncSessionLocal
from app.models.bookmark import Bookmark


async def summarize_bookmark(ctx, bookmark_id: int):
    """
    Background task: fetch bookmark, call AI service, save summary.
    """
    # 1. Create a new DB session for this background process
    async with AsyncSessionLocal() as db:
        # 2. Fetch the bookmark from the database
        result = await db.execute(select(Bookmark).where(Bookmark.id == bookmark_id))
        bookmark = result.scalar_one_or_none()

        # 3. Safety check: Did the user soft-delete it while it was in the queue?
        if not bookmark or bookmark.deleted_at is not None:
            print(f"Task aborted: Bookmark {bookmark_id} not found or deleted.")
            return

        try:

            # This replaces all the raw httpx code you had before.
            summary = await generate_bookmark_summary(bookmark.title, bookmark.url)

            # 5. Save the summary to the database
            bookmark.notes = summary
            await db.commit()
            print(f"✅ Successfully summarized bookmark {bookmark_id}!")

        except Exception as e:
            print(f"❌ Failed to summarize bookmark {bookmark_id}: {e}")
            await db.rollback()  # Undo any partial changes if it failed