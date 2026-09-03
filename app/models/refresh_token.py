from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from app.core.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # SECURITY: Never store the raw token! Hash it like a password.
    token_hash = Column(String, nullable=False, index=True)

    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True, default=None)  # For "Logout all"
    created_at = Column(DateTime, default=datetime.utcnow)
