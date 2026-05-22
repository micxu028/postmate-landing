import uuid
import asyncio
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.brand import Brand, BrandImage
from services.auth_service import get_current_user
from services.generator import generate_weekly_content
from services.generation_progress import get_progress, start_generation

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("")
async def trigger_generation(
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Brand).where(Brand.user_id == uuid.UUID(user_id)))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=400, detail="Complete onboarding first")

    # Check if already generating
    current = get_progress(user_id)
    if current.stage in ("analyzing", "writing", "images", "formatting"):
        return {"status": "ok", "message": "Already generating"}

    start_generation(user_id)

    img_result = await db.execute(select(BrandImage).where(BrandImage.brand_id == brand.id))
    images = img_result.scalars().all()
    image_urls = [img.url for img in images]

    background_tasks.add_task(generate_weekly_content, brand.id, user_id, image_urls)

    return {"status": "ok", "message": "Generation started"}


@router.get("/status")
async def generation_status(user_id: str = Depends(get_current_user)):
    progress = get_progress(user_id)
    return {
        "stage": progress.stage,
        "progress": progress.progress,
        "message": progress.message,
    }
