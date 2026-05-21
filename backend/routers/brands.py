import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models.brand import Brand, BrandImage
from services.auth_service import get_current_user

router = APIRouter(prefix="/api/brands", tags=["brands"])


class CreateBrandRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: str = Field(..., pattern="^(yoga|fitness|pilates)$")
    style: str = Field(..., pattern="^(professional|warm|energetic|minimalist)$")
    tone: str = Field(..., pattern="^(professional|friendly|humorous|inspirational)$")
    post_frequency: int = Field(default=7, ge=3, le=7)
    city: Optional[str] = None
    state: Optional[str] = None
    image_urls: list[str] = []


class BrandResponse(BaseModel):
    id: str
    name: str
    industry: str
    style: str
    tone: str
    post_frequency: int
    city: Optional[str]
    state: Optional[str]
    has_images: bool

    model_config = {"from_attributes": True}


@router.post("", response_model=BrandResponse)
async def create_brand(req: CreateBrandRequest, user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    brand = Brand(
        user_id=uuid.UUID(user_id),
        name=req.name,
        industry=req.industry,
        style=req.style,
        tone=req.tone,
        post_frequency=req.post_frequency,
        city=req.city,
        state=req.state,
    )
    db.add(brand)
    await db.flush()

    for url in req.image_urls:
        db.add(BrandImage(brand_id=brand.id, url=url))

    await db.commit()
    await db.refresh(brand)

    return BrandResponse(
        id=str(brand.id),
        name=brand.name,
        industry=brand.industry,
        style=brand.style,
        tone=brand.tone,
        post_frequency=brand.post_frequency,
        city=brand.city,
        state=brand.state,
        has_images=len(req.image_urls) > 0,
    )


@router.get("/me", response_model=Optional[BrandResponse])
async def get_my_brand(user_id: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brand).where(Brand.user_id == uuid.UUID(user_id)))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    img_result = await db.execute(select(BrandImage).where(BrandImage.brand_id == brand.id))
    images = img_result.scalars().all()

    return BrandResponse(
        id=str(brand.id),
        name=brand.name,
        industry=brand.industry,
        style=brand.style,
        tone=brand.tone,
        post_frequency=brand.post_frequency,
        city=brand.city,
        state=brand.state,
        has_images=len(images) > 0,
    )
