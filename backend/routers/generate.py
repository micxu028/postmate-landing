import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.brand import Brand, BrandImage
from services.auth_service import get_current_user
from services.generator import generate_weekly_content

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

    img_result = await db.execute(select(BrandImage).where(BrandImage.brand_id == brand.id))
    images = img_result.scalars().all()
    image_urls = [img.url for img in images]

    # Run synchronously for now (FastAPI BackgroundTasks sometimes lose DB context)
    await generate_weekly_content(brand.id, user_id, image_urls)

    return {"status": "ok", "message": "Content generated"}
