from typing import Optional
from httpx import AsyncClient
from config import get_settings


async def generate_image(image_prompt: str, brand_style: str) -> Optional[str]:
    """Generate image via MJ proxy. Returns image URL or None on failure."""
    settings = get_settings()
    if not settings.mj_api_url:
        # No MJ proxy configured — return placeholder
        return None

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
            # MJ proxy unreliable — return None and let caller handle
            return None
