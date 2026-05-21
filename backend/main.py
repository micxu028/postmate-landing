from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import get_settings
from routers import auth, brands, posts, generate
from database import init_db
from services.ai_text import generate_captions
from models.brand import Brand
import traceback

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


@app.get("/api/debug/generate")
async def debug_generate():
    """Debug endpoint to test DeepSeek integration directly."""
    try:
        # Create a minimal brand-like object for testing
        class FakeBrand:
            post_frequency = 3
            industry = "yoga"
            name = "Debug Studio"
            city = "Austin"
            state = "TX"
            style = "warm"
            tone = "friendly"

        captions = await generate_captions(FakeBrand())
        return {"status": "ok", "captions": captions}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
