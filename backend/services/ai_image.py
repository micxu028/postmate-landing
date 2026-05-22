from typing import Optional
from httpx import AsyncClient
from config import get_settings


async def generate_image(image_prompt: str, brand_style: str) -> Optional[str]:
    """Generate image URL. Uses MJ proxy if configured, otherwise falls back to Unsplash."""
    settings = get_settings()
    if settings.mj_api_url:
        return await _mj_generate(image_prompt, brand_style, settings)
    return await _unsplash_fallback(image_prompt, brand_style)


async def _mj_generate(image_prompt: str, brand_style: str, settings) -> Optional[str]:
    """Generate via MJ proxy."""
    enhanced_prompt = f"{image_prompt}, {brand_style} style, clean composition, soft lighting --ar 1:1 --v 6"
    async with AsyncClient() as client:
        try:
            resp = await client.post(
                f"{settings.mj_api_url}/imagine",
                headers={"Authorization": f"Bearer {settings.mj_api_key}"},
                json={"prompt": enhanced_prompt},
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("image_url") or data.get("url")
        except Exception:
            return None


def _unsplash_url(image_prompt: str) -> Optional[str]:
    """Build a LoremFlickr URL from the prompt keywords (free, no API key needed)."""
    from urllib.parse import quote
    words = image_prompt[:120].replace(",", " ").split()
    stopwords = {"a","an","the","with","in","on","at","for","of","to","and","is","that","this","style","shot","photo","photography","view","close","up","wide","angle","soft","clean","lighting"}
    keywords = [w for w in words if w.lower() not in stopwords and len(w) > 3][:3]
    query = ",".join(keywords) if keywords else "fitness"
    return f"https://loremflickr.com/400/400/{quote(query)}"

async def _unsplash_fallback(image_prompt: str, brand_style: str) -> Optional[str]:
    """Get an Unsplash image URL for the given prompt (no API key needed)."""
    return _unsplash_url(image_prompt)
