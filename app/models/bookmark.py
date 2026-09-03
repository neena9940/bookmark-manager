from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.tag import bookmark_tag


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    url = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 2. Soft Delete Column (Phase 1.2)
    deleted_at = Column(DateTime, nullable=True, default=None)

    # Foreign Keys
    owner_id = Column(Integer, ForeignKey("users.id"))

    # ✅ NEW: Stores the S3 path, NOT the actual file
    screenshot_key = Column(String, nullable=True)

    # Normalization - Removed
    # tag_id = Column(Integer, ForeignKey("tags.id"))
    # (Removed - using many-to-many relationship instead)

    # 3. Relationships
    owner = relationship("User", back_populates="bookmarks")
    # The new Many-to-Many relationship
    tags = relationship(
        "Tag", secondary=bookmark_tag, back_populates="bookmarks", lazy="selectin"
    )
