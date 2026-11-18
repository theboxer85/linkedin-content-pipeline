"""Shared helpers: post files, front matter, time zone."""
from __future__ import annotations

import datetime as dt
import pathlib
import re
from zoneinfo import ZoneInfo

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTS = ROOT / "posts"
DATA = ROOT / "data"
CT = ZoneInfo("America/Chicago")

FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
REQUIRED = ["id", "publish_at", "day", "pillar", "scenario", "format", "alt_text", "test_variable", "status"]
PILLARS = {"financial", "adoption", "continuity"}
DAYS = {"monday", "thursday", "standalone"}
FORMATS = {"image", "document", "text"}
STATUSES = {"scheduled", "published", "skipped"}


def load_post(path: pathlib.Path) -> tuple[dict, str]:
    """Return (front matter, body) for a post.md file."""
    text = path.read_text(encoding="utf-8")
    m = FRONT_MATTER.match(text)
    if not m:
        raise ValueError(f"{path}: missing --- front matter block")
    meta = yaml.safe_load(m.group(1)) or {}
    return meta, m.group(2).strip() + "\n"


def save_post(path: pathlib.Path, meta: dict, body: str) -> None:
    fm = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True, width=1000).strip()
    path.write_text(f"---\n{fm}\n---\n{body.strip()}\n", encoding="utf-8")


def post_files() -> list[pathlib.Path]:
    return sorted(POSTS.glob("*/post.md"))


def parse_ct(value) -> dt.datetime:
    """Read a Central-time 'YYYY-MM-DD HH:MM' (seconds optional; YAML may already have made it a datetime)."""
    if isinstance(value, dt.datetime):
        naive = value.replace(tzinfo=None)
    else:
        text = str(value).strip().replace("T", " ")
        naive = dt.datetime.strptime(text[:16], "%Y-%m-%d %H:%M")
    return naive.replace(tzinfo=CT)


def publish_time(meta: dict) -> dt.datetime:
    """publish_at is America/Chicago local time, 'YYYY-MM-DD HH:MM'."""
    return parse_ct(meta["publish_at"])


def now_ct() -> dt.datetime:
    return dt.datetime.now(tz=CT)


def skip_dates() -> set[dt.date]:
    out = set()
    for line in (DATA / "skip_dates.txt").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.add(dt.date.fromisoformat(line))
    return out


def word_count(body: str) -> int:
    return len(re.findall(r"\b[\w'./-]+\b", body))
