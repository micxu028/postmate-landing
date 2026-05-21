"""
Cold email sender for PostMate outreach.
Reads leads.csv and sends personalized emails via Brevo SMTP.

Usage:
    python scripts/send_cold_emails.py [--dry-run]

Environment variables needed:
    SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM
"""

import csv
import os
import smtplib
import time
import argparse
from email.mime.text import MIMEText
from pathlib import Path

# ── Config ──────────────────────────────────────────────────
SMTP_HOST = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USERNAME", "")
SMTP_PASS = os.getenv("SMTP_PASSWORD", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "hello@postmate.net")
FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Michael from PostMate")

LEADS_FILE = Path(__file__).parent.parent.parent / "leads.csv"
SENT_FILE = Path(__file__).parent / "sent.txt"
DELAY_SECONDS = 45  # between each email


# ── Template ────────────────────────────────────────────────
def build_email(studio: str, city: str, state: str) -> tuple[str, str]:
    subject = f"Quick question about {studio}"
    body = f"""Hi there,

I help small fitness studios keep Instagram and Facebook active without spending hours on it.

I built a tool that creates and schedules posts automatically using AI — captions, hashtags, and images all done for you.

I'm looking for a few studios in {city} to try it free for a month in exchange for feedback.

Would {studio} be interested?

Best,
Michael
PostMate — AI Social Media for Small Businesses
postmate.net"""

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
    msg = MIMEText(html, "html", "utf-8")
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{EMAIL_FROM}>"
    msg["To"] = to

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  ❌ Failed: {e}")
        return False


# ── Main ────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no send")
    args = parser.parse_args()

    # Load leads
    if not LEADS_FILE.exists():
        print(f"❌ leads.csv not found at {LEADS_FILE}")
        return

    with open(LEADS_FILE) as f:
        leads = list(csv.DictReader(f))

    # Load already sent
    sent = set()
    if SENT_FILE.exists():
        with open(SENT_FILE) as f:
            sent = set(line.strip() for line in f)

    unsent = [l for l in leads if l["email"] not in sent]
    print(f"\n📋 {len(leads)} leads total")
    print(f"✅ {len(sent)} already sent")
    print(f"📤 {len(unsent)} to send\n")

    if args.dry_run:
        for l in unsent:
            subject, _ = build_email(l["studio"], l["city"], l["state"])
            print(f"  📧 {l['email']:45s} | {subject}")
        print(f"\nDry run — {len(unsent)} emails would be sent")
        return

    # Send
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
