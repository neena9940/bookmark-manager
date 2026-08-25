from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    # This lets us do tag.bookmarks to see all bookmarks with this tag
    bookmarks = relationship("Bookmark", back_populates="tag")
