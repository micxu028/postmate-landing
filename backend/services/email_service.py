import httpx
from config import get_settings


async def send_email(to: str, subject: str, html: str) -> bool:
    settings = get_settings()
    if not settings.resend_api_key:
        return False

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {settings.resend_api_key}"},
            json={
                "from": f"{settings.email_from_name} <{settings.email_from}>",
                "to": [to],
                "subject": subject,
                "html": html,
            },
            timeout=30,
        )
        return resp.is_success


def build_content_ready_email(brand_name: str, preview_link: str) -> str:
    return f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto">
  <h2 style="color:#7c3aed">Your weekly content is ready!</h2>
  <p>Hi {brand_name}, your next week's Instagram posts are generated and waiting for you.</p>
  <a href="{preview_link}" style="display:inline-block;padding:12px 24px;background:#7c3aed;color:#fff;text-decoration:none;border-radius:8px;margin:16px 0">
    Preview & Approve
  </a>
  <p style="color:#6b7280;font-size:14px">— PostMate Team</p>
</div>"""
