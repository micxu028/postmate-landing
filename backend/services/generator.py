"""Orchestrates the full content generation pipeline."""
import asyncio
import json
import logging
from datetime import date, timedelta
from uuid import UUID
from sqlalchemy import select
from database import async_session
from models.post import Post
from models.brand import Brand, BrandImage
from services.ai_text import generate_captions
from services.ai_image import generate_image
from services.email_service import send_email, build_content_ready_email


async def generate_weekly_content(brand_id: UUID, user_id: str, image_urls: list[str]):
    """Background task: generate a full week of content."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Fetch brand with a fresh session
    async with async_session() as db:
        result = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand = result.scalar_one_or_none()
        if not brand:
            return {"error": "brand_not_found"}

        try:
            captions = await generate_captions(brand)
        except Exception as e:
            return {"error": f"ai_failed: {e}"}

        # Delete existing posts for this week (regeneration)
        existing = await db.execute(
            select(Post).where(Post.brand_id == brand.id, Post.week_start == week_start)
        )
        for post in existing.scalars().all():
            await db.delete(post)

        await db.flush()

        # Generate images in parallel
        image_tasks = []
        for item in captions:
            task = generate_image(item.get("image_prompt", ""), brand.style)
            image_tasks.append(task)

        image_results = await asyncio.gather(*image_tasks, return_exceptions=True)

        # Create posts
        for i, item in enumerate(captions):
            img_url = image_results[i] if i < len(image_results) and isinstance(image_results[i], str) else None
            post = Post(
                brand_id=brand.id,
                week_start=week_start,
                day_of_week=item.get("day", i),
                caption=item.get("caption", ""),
                hashtags=json.dumps(item.get("hashtags", [])),
                image_url=img_url,
                status="pending",
            )
            db.add(post)

        await db.commit()

    # Notify user (skip if no email — email service handles this)
    preview_link = f"https://postmate.net/app/dashboard?week={week_start.isoformat()}"
    try:
        await send_email(
            to=None,  # TODO: get user email
            subject=f"Your {brand.name} content is ready!",
            html=build_content_ready_email(brand.name, preview_link),
        )
    except Exception:
        pass  # Email is best-effort

    return {"ok": True, "posts": len(captions)}
