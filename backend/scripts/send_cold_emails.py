"""
Cold email sender for PostMate outreach.
Reads leads.csv and sends personalized emails via Resend API.

Usage:
    python scripts/send_cold_emails.py [--dry-run]

Environment variables needed:
    RESEND_API_KEY, EMAIL_FROM
"""

import csv
import os
import time
import argparse
import httpx
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "hello@postmate.net")
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Michael from PostMate")

LEADS_FILE = Path(__file__).parent.parent.parent / "leads.csv"
SENT_FILE = Path(__file__).parent / "sent.txt"
DELAY_SECONDS = 45


# ── Template ────────────────────────────────────────────────
def build_email(studio: str, city: str, state: str) -> tuple[str, str]:
    subject = f"Quick question about {studio}"
    html = f"""<div style="font-family:sans-serif;max-width:480px;margin:0 auto;color:#333">
<p>Hi there,</p>
<p>I help small fitness studios keep Instagram and Facebook active without spending hours on it.</p>
<p>I built a tool that creates and schedules posts automatically using AI — captions, hashtags, and images all done for you.</p>
<p>I'm looking for a few studios in <strong>{city}</strong> to try it free for a month in exchange for feedback.</p>
<p>Would <strong>{studio}</strong> be interested?</p>
<br>
<p>Best,<br>Michael<br><span style="color:#7c3aed">PostMate</span> — AI Social Media for Small Businesses<br>
<a href="https://postmate.net" style="color:#7c3aed">postmate.net</a></p>
</div>"""
    return subject, html


# ── Send ────────────────────────────────────────────────────
def send_email(to: str, subject: str, html: str) -> bool:
    if not RESEND_API_KEY:
        print("  ❌ RESEND_API_KEY not set")
        return False

    try:
        with httpx.Client() as client:
            resp = client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": f"{FROM_NAME} <{EMAIL_FROM}>",
                    "to": [to],
                    "subject": subject,
                    "html": html,
                },
                timeout=30,
            )
            if resp.is_success:
                return True
            print(f"  ❌ Resend error: {resp.status_code} {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


# ── Main ────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no send")
    args = parser.parse_args()

    if not LEADS_FILE.exists():
        print(f"❌ leads.csv not found at {LEADS_FILE}")
        return

    with open(LEADS_FILE) as f:
        leads = list(csv.DictReader(f))

    sent = set()
    if SENT_FILE.exists():
        with open(SENT_FILE) as f:
            sent = set(line.strip() for line in f)

    unsent = [l for l in leads if l["email"] not in sent]
    print(f"\n{len(leads)} leads total")
    print(f"{len(sent)} already sent")
    print(f"{len(unsent)} to send\n")

    if args.dry_run:
        for l in unsent:
            subject, _ = build_email(l["studio"], l["city"], l["state"])
            print(f"  {l['email']:45s} | {subject}")
        print(f"\nDry run — {len(unsent)} emails would be sent")
        return

    for i, l in enumerate(unsent, 1):
        subject, html = build_email(l["studio"], l["city"], l["state"])
        print(f"[{i}/{len(unsent)}] Sending to {l['email']}... ", end="", flush=True)

        if send_email(l["email"], subject, html):
            print("✅")
            with open(SENT_FILE, "a") as f:
                f.write(l["email"] + "\n")
        else:
            print("")

        if i < len(unsent):
            print(f"  ⏳ Waiting {DELAY_SECONDS}s...")
            time.sleep(DELAY_SECONDS)

    print(f"\n✅ Done! Sent {len(unsent)} emails.")


if __name__ == "__main__":
    main()
