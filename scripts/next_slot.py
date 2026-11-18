"""Work out the next Monday or Thursday slot and whether it should be drafted.

Usage: python scripts/next_slot.py monday|thursday
Prints key=value lines and appends them to $GITHUB_OUTPUT:
  slot_date, pillar, skip (empty or a reason), monday_dir (thursday only)
"""
from __future__ import annotations

import datetime as dt
import os
import sys

import yaml

from common import DATA, POSTS, load_post, now_ct, skip_dates

WEEKDAY = {"monday": 0, "thursday": 3}


def next_weekday(today: dt.date, weekday: int) -> dt.date:
    days = (weekday - today.weekday()) % 7
    return today + dt.timedelta(days=days or 7)


def pillar_for(monday: dt.date) -> str:
    rot = yaml.safe_load((DATA / "rotation.yml").read_text())
    anchor = dt.date.fromisoformat(rot["anchor_monday"])
    weeks = (monday - anchor).days // 7
    return rot["cycle"][weeks % len(rot["cycle"])]


def existing_post(date: dt.date, suffix: str) -> str:
    for folder in POSTS.glob(f"{date.isoformat()}-*-{suffix}"):
        return folder.name
    return ""


def main() -> int:
    day = sys.argv[1]
    today = now_ct().date()
    slot = next_weekday(today, WEEKDAY[day])
    monday = slot - dt.timedelta(days=slot.weekday())
    thursday = monday + dt.timedelta(days=3)
    skips = skip_dates()
    out = {"slot_date": slot.isoformat(), "pillar": pillar_for(monday), "skip": "", "monday_dir": ""}

    if slot in skips:
        out["skip"] = f"{slot} is in data/skip_dates.txt"
    elif day == "monday":
        if thursday in skips:
            out["skip"] = f"Thursday {thursday} is a skip date, so the pair can't finish this week"
        elif existing_post(slot, "mon"):
            out["skip"] = f"a Monday post for {slot} is already on main"
    else:
        mon_dir = existing_post(monday, "mon")
        out["monday_dir"] = mon_dir
        if existing_post(slot, "thu"):
            out["skip"] = f"a Thursday post for {slot} is already on main"
        elif not mon_dir:
            out["skip"] = f"no merged Monday post for {monday}, so there is nothing to resolve"
        else:
            meta, _ = load_post(POSTS / mon_dir / "post.md")
            out["pillar"] = meta.get("pillar", out["pillar"])
            if meta.get("status") == "skipped":
                out["skip"] = f"the Monday post {mon_dir} was skipped"

    lines = [f"{k}={v}" for k, v in out.items()]
    print("\n".join(lines))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as fh:
            fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
