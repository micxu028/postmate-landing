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
from config import get_settings
import json, traceback, logging, httpx

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


@app.get("/api/debug/raw")
async def debug_raw():
    """Show raw DeepSeek response using the EXACT generate_captions call."""
    try:
        async with async_session() as db:
            result = await db.execute(select(Brand).limit(1))
            brand = result.scalar_one_or_none()
            if not brand:
                return {"error": "no brand found"}

        from services.ai_text import generate_captions
        result = await generate_captions(brand)
        return {"status": "ok", "count": len(result), "first": result[0] if result else None}
    except Exception as e:
        # Show the raw API response for debugging
        import httpx, traceback
        from config import get_settings
        s = get_settings()
        from services.ai_text import _build_user_prompt
        prompt = _build_user_prompt(brand)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    s.deepseek_api_url,
                    headers={"Authorization": f"Bearer {s.deepseek_api_key}", "Content-Type": "application/json"},
                    json={
                        "model": s.deepseek_model,
                        "messages": [
                            {"role": "system", "content": "You are a social media content creator."},
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.8,
                        "max_tokens": 4000,
                    },
                    timeout=60,
                )
                raw = resp.text[:1000]
        except Exception as e2:
            raw = f"also failed: {e2}"

        return {"error": str(e), "raw": raw, "traceback": traceback.format_exc()}
