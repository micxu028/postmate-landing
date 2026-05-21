from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import get_settings
from routers import auth, brands, posts, generate
from database import init_db, async_session
from uuid import UUID
from sqlalchemy import select
from models.brand import Brand
from models.post import Post
from services.ai_text import generate_captions
import json, traceback, logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(brands.router)
app.include_router(posts.router)
app.include_router(generate.router)

# Serve app frontend (signup, onboarding, dashboard)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/app", StaticFiles(directory=str(static_dir), html=True), name="app")


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/debug/gen")
async def debug_gen():
    """Debug: simulate exactly what background task does."""
    try:
        async with async_session() as db:
            result = await db.execute(select(Brand).limit(1))
            brand = result.scalar_one_or_none()
            if not brand:
                return {"error": "no brand found"}
            bid = brand.id
        # Now simulate background task flow
        async with async_session() as db:
            result = await db.execute(select(Brand).where(Brand.id == bid))
            brand2 = result.scalar_one_or_none()
            if not brand2:
                return {"error": "brand not found in new session"}
            # First get the raw response
            import httpx
            from config import get_settings
            s = get_settings()
            prompt = f"Generate 3 Instagram captions for a {brand2.industry} studio named {brand2.name} in {brand2.city}, {brand2.state}. Style: {brand2.style}, Tone: {brand2.tone}. Return ONLY valid JSON array with objects having day, caption, hashtags, image_prompt fields."
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    s.deepseek_api_url,
                    headers={"Authorization": f"Bearer {s.deepseek_api_key}", "Content-Type": "application/json"},
                    json={
                        "model": s.deepseek_model,
                        "messages": [
                            {"role": "system", "content": "You are a social media content creator. Output ONLY valid JSON, no markdown, no explanation."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.8,
                        "max_tokens": 4000,
                    },
                    timeout=60,
                )
                raw = resp.text[:500]
            try:
                captions = await generate_captions(brand2)
            except Exception as e:
                return {"error": f"AI generation failed: {e}", "raw_response": raw, "traceback": traceback.format_exc()}
            # Delete existing
            from datetime import date, timedelta
            week_start = date.today() - timedelta(days=date.today().weekday())
            existing = await db.execute(select(Post).where(Post.brand_id == brand2.id))
            for post in existing.scalars().all():
                await db.delete(post)
            await db.flush()
            # Create posts
            for i, item in enumerate(captions[:1]):  # just 1 for debug
                post = Post(
                    brand_id=brand2.id,
                    week_start=week_start,
                    day_of_week=item.get("day", i),
                    caption=item.get("caption", ""),
                    hashtags=json.dumps(item.get("hashtags", [])),
                    status="pending",
                )
                db.add(post)
            await db.commit()
            return {"status": "ok", "captions_count": len(captions), "first_caption": captions[0].get("caption", "")[:80]}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}
