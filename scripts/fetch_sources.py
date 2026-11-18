"""Collect new items from CSP feeds and subreddits into .work/digest.json for the triage agent.

Keeps only items matching the networking keywords in data/sources.yml, and remembers what it has
already seen in data/seen.json so nothing is triaged twice. Reddit often blocks cloud runners; failures
are logged and skipped, never fatal.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import requests
import yaml

from common import DATA

UA = {"User-Agent": "linkedin-content-pipeline/1.0 (personal research feed reader)"}
MAX_AGE = dt.timedelta(days=3)
OUT = ".work/digest.json"


def strip_html(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def parse_feed(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    items = []
    for it in root.iter():
        tag = it.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        get = lambda name: next((c for c in it if c.tag.split("}")[-1] == name), None)  # noqa: E731
        title = (get("title").text if get("title") is not None else "") or ""
        link_el = get("link")
        link = (link_el.get("href") or link_el.text or "") if link_el is not None else ""
        summary_el = next((e for e in (get("description"), get("summary"), get("content")) if e is not None), None)
        summary = strip_html(summary_el.text if summary_el is not None else "")[:600]
        guid_el = get("guid") if get("guid") is not None else get("id")
        guid = (guid_el.text if guid_el is not None else None) or link or title
        items.append({"id": guid.strip(), "title": strip_html(title), "link": link.strip(), "summary": summary})
    return items


def reddit(sub: str) -> list[dict]:
    r = requests.get(f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=25", headers=UA, timeout=20)
    r.raise_for_status()
    out = []
    for child in r.json()["data"]["children"]:
        d = child["data"]
        out.append({"id": f"reddit:{d['id']}", "title": d["title"], "link": f"https://www.reddit.com{d['permalink']}",
                    "summary": (d.get("selftext") or "")[:600], "score": d.get("score", 0)})
    return out


def main() -> int:
    cfg = yaml.safe_load((DATA / "sources.yml").read_text())
    keywords = [k.lower() for k in cfg["keywords"]]
    seen_path = DATA / "seen.json"
    seen = json.loads(seen_path.read_text() or "{}")
    now = dt.datetime.now(dt.timezone.utc)
    fresh, log = [], []

    def consider(source: str, items: list[dict]) -> None:
        for it in items:
            if it["id"] in seen:
                continue
            seen[it["id"]] = now.date().isoformat()
            text = f"{it['title']} {it['summary']}".lower()
            if any(k in text for k in keywords):
                fresh.append({"source": source, **it})

    for feed in cfg["feeds"]:
        try:
            r = requests.get(feed["url"], headers=UA, timeout=30)
            r.raise_for_status()
            items = parse_feed(r.text)
            consider(f"news: {feed['name']}", items)
            log.append(f"{feed['name']}: {len(items)} items")
        except Exception as exc:  # noqa: BLE001
            log.append(f"{feed['name']}: failed ({exc})")
    for sub in cfg["subreddits"]:
        try:
            items = reddit(sub)
            consider(f"reddit: r/{sub}", items)
            log.append(f"r/{sub}: {len(items)} items")
        except Exception as exc:  # noqa: BLE001
            log.append(f"r/{sub}: failed ({exc})")

    # Forget seen ids older than 60 days so the file stays small.
    cutoff = (now - dt.timedelta(days=60)).date().isoformat()
    seen = {k: v for k, v in seen.items() if v >= cutoff}
    seen_path.write_text(json.dumps(seen, indent=0, sort_keys=True) + "\n")
    os.makedirs(".work", exist_ok=True)
    json.dump(fresh[:40], open(OUT, "w"), indent=2)
    print("\n".join(log))
    print(f"{len(fresh)} new matching items -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
