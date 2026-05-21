import json
from httpx import AsyncClient
from config import get_settings

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

SYSTEM_PROMPT = """You are a social media content creator for small fitness studios.
Your job is to generate engaging Instagram captions that feel authentic, not salesy.
Each post should sound like it comes from a real local business owner who loves what they do."""


def _build_user_prompt(brand) -> str:
    return f"""Generate {brand.post_frequency} Instagram captions for a {brand.industry} studio.

Studio name: {brand.name}
Location: {brand.city}, {brand.state}
Brand style: {brand.style}
Brand tone: {brand.tone}

For each day of the week (Mon-Sun, but only {brand.post_frequency} posts), provide:
1. caption (100-200 characters, American English, include 1-2 emojis, end with a CTA)
2. hashtags (8-12 relevant tags)
3. image_prompt (a vivid description for AI image generation, matching the caption)

Output ONLY a JSON array with {brand.post_frequency} objects, no explanation:
[
  {{
    "day": 0,
    "caption": "...",
    "hashtags": ["#tag1", "#tag2"],
    "image_prompt": "..."
  }}
]"""


async def generate_captions(brand) -> list[dict]:
    settings = get_settings()
    prompt = _build_user_prompt(brand)

    async with AsyncClient() as client:
        resp = await client.post(
            settings.deepseek_api_url,
            headers={
                "Authorization": f"Bearer {settings.deepseek_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.deepseek_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
                "max_tokens": 4000,
            },
            timeout=60,
        )

    resp.raise_for_status()
    data = resp.json()
    content = data["choices"][0]["message"]["content"]

    # Extract JSON from response (handle markdown-wrapped json)
    content = content.strip()
    if content.startswith("```"):
        lines = content.split("\n")
        content = "\n".join(lines[1:-1])

    posts = json.loads(content)
    return posts
