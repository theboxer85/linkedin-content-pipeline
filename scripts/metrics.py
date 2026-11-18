"""Manual metrics loop.

  python scripts/metrics.py remind          open a Metrics issue for each 24h / 7d read that is due
  python scripts/metrics.py record <issue>  copy a closed Metrics issue's table into data/scoreboard.csv

LinkedIn doesn't give personal-profile analytics to self-serve apps, so the numbers are typed in by hand
from the post's analytics page. Also warns when the LinkedIn token is about to expire.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import os
import re
import subprocess
import sys

from common import DATA, load_post, now_ct, parse_ct, post_files, save_post

FIELDS = ["impressions", "reactions", "comments", "reposts", "saves", "sends", "pct_manager_plus", "top_titles",
          "followers_gained", "profile_views_week", "decision_maker_conversations", "notes"]
COLUMNS = ["post_id", "date", "day", "pillar", "scenario", "test_variable", "read"] + FIELDS
READS = {"24h": dt.timedelta(hours=24), "7d": dt.timedelta(days=7)}
SCOREBOARD = DATA / "scoreboard.csv"


def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout


def issue_body(meta: dict, read: str) -> str:
    url = f"https://www.linkedin.com/feed/update/{meta.get('linkedin_urn', '')}/"
    rows = "\n".join(f"| {f} | |" for f in FIELDS)
    return (f"Fill in the numbers from the post's analytics page, then close this issue. "
            f"Leave a value blank if LinkedIn doesn't show it. Never estimate.\n\n"
            f"Post: {url}\n\n<!-- post_id: {meta['id']} -->\n<!-- read: {read} -->\n\n"
            f"| Metric | Value |\n| --- | --- |\n{rows}\n\n"
            f"`pct_manager_plus` is the share of viewers at manager level or above. "
            f"`decision_maker_conversations` is a count; put sanitized details in `notes`.")


def remind() -> int:
    now = now_ct()
    for post_md in post_files():
        meta, body = load_post(post_md)
        if meta.get("status") != "published" or not meta.get("published_at"):
            continue
        published = parse_ct(meta["published_at"])
        changed = False
        for read, delta in READS.items():
            key = f"metrics_{read}_issue"
            if meta.get(key) or now < published + delta:
                continue
            url = gh("issue", "create", "--title", f"Metrics: {meta['id']} ({read})",
                     "--label", "metrics", "--body", issue_body(meta, read)).strip()
            meta[key] = int(url.rstrip("/").split("/")[-1])
            changed = True
            print(f"opened {read} metrics issue for {meta['id']}: {url}")
        if changed:
            save_post(post_md, meta, body)

    expires = os.environ.get("LINKEDIN_TOKEN_EXPIRES", "")
    if expires:
        days_left = (dt.date.fromisoformat(expires) - now.date()).days
        if days_left <= 7:
            existing = json.loads(gh("issue", "list", "--state", "open", "--search", "LinkedIn token expires in:title",
                                     "--json", "number"))
            if not existing:
                gh("issue", "create", "--title", f"LinkedIn token expires {expires}",
                   "--body", "Run `python scripts/linkedin_auth.py` on your laptop to renew it (see README). "
                             "Posts can't publish after the token expires.")
                print("opened token expiry issue")
    return 0


def record(number: str) -> int:
    issue = json.loads(gh("issue", "view", number, "--json", "body,title"))
    body = issue["body"]
    m_id, m_read = re.search(r"post_id: (\S+)", body), re.search(r"read: (\S+)", body)
    if not m_id or not m_read:
        print("not a metrics issue")
        return 0
    post_id, read = m_id.group(1), m_read.group(1)
    values = {}
    for line in body.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 2 and cells[0] in FIELDS:
            values[cells[0]] = cells[1]
    meta, _ = load_post(next(p for p in post_files() if p.parent.name == post_id))
    row = {"post_id": post_id, "date": str(meta.get("published_at", ""))[:10], "day": meta.get("day", ""),
           "pillar": meta.get("pillar", ""), "scenario": meta.get("scenario", ""),
           "test_variable": meta.get("test_variable", ""), "read": read, **values}

    rows = list(csv.DictReader(SCOREBOARD.open())) if SCOREBOARD.exists() else []
    rows = [r for r in rows if not (r["post_id"] == post_id and r["read"] == read)] + [row]
    with SCOREBOARD.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"recorded {post_id} {read}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("remind", "record"):
        print(__doc__)
        sys.exit(2)
    sys.exit(remind() if sys.argv[1] == "remind" else record(sys.argv[2]))
