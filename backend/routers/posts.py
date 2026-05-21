import json
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from datetime import date, timedelta
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.post import Post
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


class PostResponse(BaseModel):
    id: str
    day_of_week: int
    caption: str
    hashtags: list[str]
    image_url: Optional[str]
    status: str

    model_config = {"from_attributes": True}


@router.get("")
async def get_posts(
    week: Optional[str] = None,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if week:
        try:
            week_start = date.fromisoformat(week)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid week format, use YYYY-MM-DD")
    else:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    # Get brand for this user
    from models.brand import Brand
    result = await db.execute(select(Brand).where(Brand.user_id == uuid.UUID(user_id)))
    brand = result.scalar_one_or_none()
    if not brand:
        return {"week_start": week_start.isoformat(), "posts": [], "generating": False}

    result = await db.execute(
        select(Post)
        .where(Post.brand_id == brand.id, Post.week_start == week_start)
        .order_by(Post.day_of_week)
    )
    posts = result.scalars().all()

    return {
        "week_start": week_start.isoformat(),
        "posts": [
            PostResponse(
                id=str(p.id),
                day_of_week=p.day_of_week,
                caption=p.caption,
                hashtags=json.loads(p.hashtags) if isinstance(p.hashtags, str) else (p.hashtags or []),
                image_url=p.image_url,
                status=p.status,
            )
            for p in posts
        ],
        "generating": any(p.status == "generating" for p in posts),
    }


@router.put("/{post_id}/approve")
async def approve_post(post_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "approved"
    post.approved_at = date.today()
    await db.commit()
    return {"status": "ok"}


@router.put("/{post_id}/regenerate")
async def regenerate_post(post_id: str, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post.status = "rejected"
    await db.commit()
    return {"status": "ok", "message": "Marked for regeneration"}
