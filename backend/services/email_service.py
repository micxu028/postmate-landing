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


BRAND_COLOR = "#7c3aed"
BG_COLOR = "#f9fafb"
CARD_BG = "#ffffff"
TEXT_COLOR = "#1f2937"
MUTED_COLOR = "#6b7280"


def _base_layout(body: str) -> str:
    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:{BG_COLOR};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:{BG_COLOR}">
    <tr><td align="center" style="padding:40px 16px">
      <table role="presentation" width="480" cellpadding="0" cellspacing="0" style="background:{CARD_BG};border-radius:12px;overflow:hidden">
        <!-- Header -->
        <tr>
          <td style="background:{BRAND_COLOR};padding:32px 40px;text-align:center">
            <h1 style="color:#fff;margin:0;font-size:24px;font-weight:700">PostMate</h1>
            <p style="color:rgba(255,255,255,0.8);margin:4px 0 0;font-size:14px">AI-Powered Social Media</p>
          </td>
        </tr>
        <!-- Body -->
        <tr><td style="padding:32px 40px">{body}</td></tr>
        <!-- Footer -->
        <tr>
          <td style="padding:24px 40px;border-top:1px solid #e5e7eb;text-align:center">
            <p style="margin:0;font-size:12px;color:{MUTED_COLOR}">PostMate — AI-generated content for your business</p>
            <p style="margin:4px 0 0;font-size:12px;color:{MUTED_COLOR}">
              <a href="https://postmate.net" style="color:{BRAND_COLOR};text-decoration:none">postmate.net</a>
            </p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""


def build_content_ready_email(brand_name: str, preview_link: str) -> str:
    body = f"""
    <h2 style="color:{TEXT_COLOR};margin:0 0 8px;font-size:20px">Your content is ready! 🎉</h2>
    <p style="color:{MUTED_COLOR};margin:0 0 20px;font-size:15px;line-height:1.5">
      Hi {brand_name}, your next week's Instagram posts have been generated and are waiting for your review.
    </p>
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 24px">
      <tr>
        <td style="background:{BRAND_COLOR};border-radius:8px;padding:12px 28px">
          <a href="{preview_link}" style="color:#fff;text-decoration:none;font-size:15px;font-weight:600;display:block">
            Preview & Approve →
          </a>
        </td>
      </tr>
    </table>
    <p style="color:{MUTED_COLOR};margin:0;font-size:13px">
      You can approve, regenerate, or edit each post before they go live.
    </p>
    """
    return _base_layout(body)


def build_invite_email(invite_link: str) -> str:
    body = f"""
    <h2 style="color:{TEXT_COLOR};margin:0 0 8px;font-size:20px">You're invited to PostMate! 🎉</h2>
    <p style="color:{MUTED_COLOR};margin:0 0 16px;font-size:15px;line-height:1.5">
      Great news — you've been invited to try <strong>PostMate Beta</strong>, the AI-powered social media
      assistant that creates beautiful Instagram content for your business automatically.
    </p>
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 20px">
      <tr>
        <td style="background:{BRAND_COLOR};border-radius:8px;padding:12px 28px">
          <a href="{invite_link}" style="color:#fff;text-decoration:none;font-size:15px;font-weight:600;display:block">
            Accept Invitation →
          </a>
        </td>
      </tr>
    </table>
    <h3 style="color:{TEXT_COLOR};margin:0 0 12px;font-size:15px">What you get:</h3>
    <table role="presentation" cellpadding="0" cellspacing="0" style="margin:0 0 20px">
      <tr><td style="padding:4px 0;color:{MUTED_COLOR};font-size:14px">✓ AI-generated Instagram captions &amp; hashtags</td></tr>
      <tr><td style="padding:4px 0;color:{MUTED_COLOR};font-size:14px">✓ Beautiful stock imagery matched to your brand</td></tr>
      <tr><td style="padding:4px 0;color:{MUTED_COLOR};font-size:14px">✓ Weekly content batches — just review &amp; post</td></tr>
      <tr><td style="padding:4px 0;color:{MUTED_COLOR};font-size:14px">✓ Free during beta — no credit card required</td></tr>
    </table>
    <p style="color:{MUTED_COLOR};margin:0;font-size:13px">
      This invitation link is unique to you. See you inside!
    </p>
    """
    return _base_layout(body)
