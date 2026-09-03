from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    # ✅ NEW: Default role is "user". Admins will be "admin".
    role = Column(String, default="user", nullable=False)
    bookmarks = relationship("Bookmark", back_populates="owner")
