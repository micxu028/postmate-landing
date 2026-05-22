import json
from httpx import AsyncClient
from config import get_settings

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

SYSTEM_PROMPT = """You are a social media content creator for small fitness studios.
Your job is to generate engaging Instagram captions that feel authentic, not salesy.
Each post should sound like it comes from a real local business owner who loves what they do.

You ALWAYS output the exact JSON format requested, with no extra text, no markdown, no backticks."""


def _build_user_prompt(brand) -> str:
    return f"""Generate {brand.post_frequency} Instagram posts for a {brand.industry} studio.

Studio name: {brand.name}
Location: {brand.city}, {brand.state}
Brand style: {brand.style}
Brand tone: {brand.tone}

Each post object must have these exact fields:
- "day": integer 0-6 (0=Monday)
- "caption": 100-200 characters, American English, include 1-2 emojis, end with a CTA
- "hashtags": array of 8-12 strings like ["#tag1", "#tag2"]
- "image_prompt": vivid English description for AI image generation matching the caption

Output {brand.post_frequency} objects in this exact JSON format, no other text:
[{{"day":0,"caption":"...","hashtags":["#tag"],"image_prompt":"..."}}]"""


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

    posts = _parse_json_response(content)

    return posts


def _parse_json_response(content: str) -> list[dict]:
    """Extract and parse JSON array from LLM response text."""
    # Extract JSON array from response (handle any wrapping)
    content = content.strip()
    start = content.find("[")
    end = content.rfind("]")
    if start != -1 and end != -1 and end > start:
        content = content[start:end + 1]

    # Clean common JSON issues
    content = content.replace("```json", "").replace("```", "").replace("``", "")

    content = content.strip()
    if content.startswith("json"):
        content = content[4:].strip()

    import re
    # Remove trailing commas before closing bracket
    content = re.sub(r',\s*([\]}])', r'\1', content)

    return json.loads(content)
