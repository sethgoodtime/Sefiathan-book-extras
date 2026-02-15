"""
Compile the book and send a daily text with today's entry via Twilio.

Usage:
    python scripts/notify_and_compile.py

Environment variables required:
    TWILIO_ACCOUNT_SID    - Your Twilio account SID
    TWILIO_AUTH_TOKEN      - Your Twilio auth token
    TWILIO_FROM_NUMBER     - Your Twilio phone number (e.g., +15551234567)
    NOTIFY_TO_NUMBER       - Your personal phone number (e.g., +15559876543)
    GITHUB_REPO_URL        - Your repo URL (e.g., https://github.com/sethgoodtime/Sefiathan-book)
    ENTRY_COUNT            - Current number of entries (passed from workflow)
"""

import os
import sys
import glob
from pathlib import Path

from twilio.rest import Client


MILESTONES = {30, 100, 200, 300, 365}


def get_stats() -> dict:
    """Get current book stats."""
    chapter_files = sorted(glob.glob("chapters/*.md"))
    total_entries = len(chapter_files)

    total_words = 0
    for filepath in chapter_files:
        with open(filepath, "r") as f:
            total_words += len(f.read().split())

    first_date = Path(chapter_files[0]).stem if chapter_files else "N/A"
    last_date = Path(chapter_files[-1]).stem if chapter_files else "N/A"

    return {
        "total_entries": total_entries,
        "total_words": total_words,
        "first_date": first_date,
        "last_date": last_date,
    }


def get_latest_entry() -> str:
    """Read the most recent chapter entry."""
    chapter_files = sorted(glob.glob("chapters/*.md"))
    if not chapter_files:
        return ""
    with open(chapter_files[-1], "r") as f:
        return f.read().strip()


def compile_book() -> str:
    """Compile all chapters into manuscript.md and return the path."""
    chapter_files = sorted(glob.glob("chapters/*.md"))

    if not chapter_files:
        print("No chapters found!")
        sys.exit(1)

    entries = []
    for filepath in chapter_files:
        with open(filepath, "r") as f:
            entries.append(f.read().strip())

    stats = get_stats()

    header = f"""# A Year in the Stars

*A memoir written one Sefiathan at a time.*

*{stats['first_date']} — {stats['last_date']}*
*{stats['total_entries']} days captured · ~{stats['total_words']:,} words*

---

"""

    manuscript = header + "\n\n---\n\n".join(entries)

    output_path = "manuscript.md"
    with open(output_path, "w") as f:
        f.write(manuscript)

    print(f"Compiled: {output_path} ({stats['total_entries']} entries, ~{stats['total_words']:,} words)")
    return output_path


def send_text(message: str):
    """Send a text message via Twilio."""
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")
    to_number = os.environ.get("NOTIFY_TO_NUMBER")

    missing = []
    if not account_sid:
        missing.append("TWILIO_ACCOUNT_SID")
    if not auth_token:
        missing.append("TWILIO_AUTH_TOKEN")
    if not from_number:
        missing.append("TWILIO_FROM_NUMBER")
    if not to_number:
        missing.append("NOTIFY_TO_NUMBER")

    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}")
        print("Set these in your GitHub Secrets or .env file.")
        sys.exit(1)

    client = Client(account_sid, auth_token)

    msg = client.messages.create(
        body=message,
        from_=from_number,
        to=to_number,
    )

    print(f"Text sent! SID: {msg.sid}")


def main():
    # Compile the book
    compile_book()
    stats = get_stats()
    entry_count = stats["total_entries"]

    # Get today's entry to include in the text
    latest_entry = get_latest_entry()

    # Truncate if too long for SMS (1600 char limit, leave room for header)
    max_entry_len = 1200
    if len(latest_entry) > max_entry_len:
        latest_entry = latest_entry[:max_entry_len] + "..."

    # Build the message
    if entry_count >= 365:
        message = (
            f"YOUR BOOK IS DONE.\n\n"
            f"365 days. ~{stats['total_words']:,} words.\n"
            f"A Year in the Stars is complete.\n\n"
            f"{latest_entry}"
        )
    elif entry_count in MILESTONES:
        message = (
            f"MILESTONE: Day {entry_count} of 365!\n\n"
            f"{latest_entry}\n\n"
            f"~{stats['total_words']:,} words so far."
        )
    else:
        message = (
            f"Day {entry_count} of 365\n\n"
            f"{latest_entry}"
        )

    send_text(message)


if __name__ == "__main__":
    main()
