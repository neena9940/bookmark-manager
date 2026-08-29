from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.storage import upload_file, get_presigned_url
from app.models.bookmark import Bookmark
from app.models.user import User
from sqlalchemy.orm import selectinload

router = APIRouter()


@router.post("/bookmarks/{bookmark_id}/screenshot")
async def upload_screenshot(
        bookmark_id: int,
        file: UploadFile = File(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    # 1. Security: Verify the bookmark exists and belongs to this user
    # 1. Security: Verify the bookmark exists and belongs to this user
    result = await db.execute(
        select(Bookmark)
        .where(
            Bookmark.id == bookmark_id,
            Bookmark.owner_id == current_user.id,
            Bookmark.deleted_at.is_(None),
        )
        .options(selectinload(Bookmark.tags))  # Eager load tags for the response
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    # 2. Validation: Only allow images, max 5MB
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only PNG and JPEG images are allowed")

    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:  # 5 Megabytes
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    # 3. Create a unique path in the bucket
    # Example: "screenshots/user_1/bookmark_2.png"
    key = f"screenshots/{current_user.id}/{bookmark.id}.png"

    # 4. Upload to MinIO/S3
    await upload_file(key, contents, file.content_type)

    # 5. Save the key to the database
    bookmark.screenshot_key = key
    await db.commit()
    await db.refresh(bookmark)

    # 6. Generate a temporary URL so the user can view it immediately
    screenshot_url = await get_presigned_url(key)

    return {"message": "Screenshot uploaded", "screenshot_url": screenshot_url}