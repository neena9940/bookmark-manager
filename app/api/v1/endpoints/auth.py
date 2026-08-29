from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    create_access_token, create_refresh_token_value, hash_token, verify_token_hash,
    verify_password, get_password_hash
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserResponse
from app.core.limiter import limiter


router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # ... (keep your existing register logic, just make sure to set role="user" if needed) ...
    user = User(email=user_in.email, hashed_password=get_password_hash(user_in.password), role="user")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user




@router.post("/login")
@limiter.limit("5/minute") # ✅ THE MAGIC LINE: Max 5 logins per minute per IP!
async def login(
    request: Request, # ✅ MUST BE FIRST!
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)):

#async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # 1. Verify User
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 2. Create Tokens
    access_token = create_access_token(user.id)
    refresh_token_value = create_refresh_token_value()

    # 3. Save Refresh Token Hash to DB
    refresh_db = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token_value),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_db)
    await db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,  # Send raw token to client ONCE
        "token_type": "bearer"
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Exchange a valid refresh token for a new access token"""
    # 1. Find all tokens for this user (In production, you'd search by token_hash directly)
    result = await db.execute(select(RefreshToken).where(RefreshToken.revoked_at.is_(None)))
    tokens = result.scalars().all()

    valid_token = None
    for t in tokens:
        if verify_token_hash(refresh_token, t.token_hash):
            valid_token = t
            break

    if not valid_token or valid_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # 2. Issue new access token
    new_access = create_access_token(valid_token.user_id)
    return {"access_token": new_access, "token_type": "bearer"}


@router.post("/logout")
async def logout(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Revoke a specific refresh token (Logout from this device)"""
    # Find the token hash and set revoked_at = now
    # (Simplified logic for learning: iterate and revoke matching hash)
    result = await db.execute(select(RefreshToken))
    tokens = result.scalars().all()
    for t in tokens:
        if verify_token_hash(refresh_token, t.token_hash):
            t.revoked_at = datetime.utcnow()
            await db.commit()
            return {"message": "Logged out successfully"}

    raise HTTPException(status_code=400, detail="Invalid token")