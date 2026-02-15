"""
Compile the book and send a ntfy.sh push notification that the entry is ready.
The notification triggers an iPhone Shortcut to pull the entry and send via iMessage.

Usage:
    python scripts/notify_and_compile.py

Environment variables:
    ENTRY_COUNT - Current number of entries (passed from workflow)
"""

import os
import sys
import glob
import urllib.request
import json
from pathlib import Path


MILESTONES = {30, 100, 200, 300, 365}
NTFY_TOPIC = "sefiathan-book"


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


def get_latest_entry() -> tuple[str, str]:
    """Read the most recent chapter entry. Returns (date, content)."""
    chapter_files = sorted(glob.glob("chapters/*.md"))
    if not chapter_files:
        return ("", "")
    date = Path(chapter_files[-1]).stem
    with open(chapter_files[-1], "r") as f:
        return (date, f.read().strip())


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


def send_ntfy(title: str, message: str, tags: str = "star"):
    """Send a push notification via ntfy.sh."""
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    data = json.dumps({
        "topic": NTFY_TOPIC,
        "title": title,
        "message": message,
        "tags": [tags],
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req)
    print(f"ntfy notification sent to topic: {NTFY_TOPIC}")


def main():
    # Compile the book
    compile_book()
    stats = get_stats()
    entry_count = stats["total_entries"]
    date, latest_entry = get_latest_entry()

    # Build the notification
    if entry_count >= 365:
        title = "YOUR BOOK IS DONE"
        message = f"365 days. ~{stats['total_words']:,} words. A Year in the Stars is complete."
        tags = "tada"
    elif entry_count in MILESTONES:
        title = f"MILESTONE: Day {entry_count} of 365!"
        message = f"~{stats['total_words']:,} words so far. Entry ready."
        tags = "trophy"
    else:
        title = f"Day {entry_count} of 365"
        message = f"New Sefiathan entry ready for {date}."
        tags = "star"

    send_ntfy(title, message, tags)


if __name__ == "__main__":
    main()
