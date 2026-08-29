from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# Junction table for Many-to-Many
bookmark_tag = Table(
    "bookmark_tag",
    Base.metadata,
    Column("bookmark_id", Integer, ForeignKey("bookmarks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


    slug = Column(String, unique=True, index=True, nullable=False)

    # Relationship to Bookmarks
    bookmarks = relationship(
        "Bookmark",
        secondary=bookmark_tag,
        back_populates="tags",
        lazy="selectin"
    )