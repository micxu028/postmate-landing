"""Orchestrates the full content generation pipeline with progress tracking."""
import asyncio
import json
import logging
from datetime import date, timedelta
from uuid import UUID
from sqlalchemy import select
from database import async_session
from models.post import Post
from models.brand import Brand, BrandImage
from models.user import User
from services.ai_text import generate_captions
from services.ai_image import generate_image
from services.email_service import send_email, build_content_ready_email
from services.generation_progress import start_generation, update_progress, finish_generation


async def generate_weekly_content(brand_id: UUID, user_id: str, image_urls: list[str]):
    """Generate a full week of content synchronously with progress tracking."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    start_generation(user_id)

    async with async_session() as db:
        result = await db.execute(select(Brand).where(Brand.id == brand_id))
        brand = result.scalar_one_or_none()
        if not brand:
            finish_generation(user_id, error=True)
            return

        # Get user email for notification
        user_result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = user_result.scalar_one_or_none()

        # Stage 1: Analyze brand
        update_progress(user_id, "analyzing", 15, "Analyzing your brand style and tone...")
        await asyncio.sleep(0.3)

        # Stage 2: Generate captions
        update_progress(user_id, "writing", 30, "Writing captions for the week...")
        try:
            captions = await generate_captions(brand)
        except Exception:
            finish_generation(user_id, error=True)
            return
        update_progress(user_id, "writing", 45, f"Generated {len(captions)} posts...")

        # Delete existing posts for this week (regeneration)
        existing = await db.execute(
            select(Post).where(Post.brand_id == brand.id, Post.week_start == week_start)
        )
        for post in existing.scalars().all():
            await db.delete(post)
        await db.flush()

        # Stage 3: Generate images
        update_progress(user_id, "images", 55, "Searching for matching images...")
        image_tasks = []
        for i, item in enumerate(captions):
            task = generate_image(item.get("image_prompt", ""), brand.style)
            image_tasks.append(task)

        # Report image search progress as they complete
        completed = 0
        total = len(image_tasks)
        image_results = []
        for coro in asyncio.as_completed(image_tasks):
            try:
                result = await coro
            except Exception:
                result = None
            image_results.append(result)
            completed += 1
            pct = 55 + int(30 * completed / total)
            update_progress(user_id, "images", pct, f"Found {completed}/{total} images...")

        # Stage 4: Format posts
        update_progress(user_id, "formatting", 88, "Formatting your posts...")
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

    update_progress(user_id, "done", 95, "Finalizing...")
    await asyncio.sleep(0.2)

    # Notify user (best-effort)
    if user:
        preview_link = f"https://postmate.net/app/dashboard?week={week_start.isoformat()}"
        try:
            await send_email(
                to=user.email,
                subject=f"Your {brand.name} content is ready!",
                html=build_content_ready_email(brand.name, preview_link),
            )
        except Exception:
            pass

    finish_generation(user_id)
