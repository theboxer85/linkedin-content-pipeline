"""Publish due posts from main to LinkedIn.

Only posts on main with status `scheduled` whose publish_at has passed are published. A post more than
LATE_LIMIT late is marked `skipped` instead, so a missed slot is never filled at an odd hour.

Env: LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_URN (urn:li:person:...), LINKEDIN_VERSION (YYYYMM, default 202608)
Usage: python scripts/publish.py [--dry-run] [--post ID] [--now "YYYY-MM-DD HH:MM"]
Writes a summary of what happened to /tmp/publish_report.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

import requests

from common import CT, load_post, now_ct, post_files, publish_time, save_post

API = "https://api.linkedin.com/rest"
LATE_LIMIT = dt.timedelta(hours=6)
RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")
REPORT = pathlib.Path("/tmp/publish_report.md")


def little_text(body: str) -> str:
    """LinkedIn's commentary field uses 'little text' markup; reserved characters must be escaped or the post is cut short."""
    return RESERVED.sub(r"\\\1", body.strip())


class LinkedIn:
    def __init__(self, token: str, author: str, version: str):
        self.author = author
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        })

    def _check(self, r: requests.Response, what: str) -> requests.Response:
        if r.status_code >= 300:
            raise RuntimeError(f"{what} failed: HTTP {r.status_code} {r.text[:500]}")
        return r

    def upload(self, kind: str, path: pathlib.Path) -> str:
        """kind is 'images' or 'documents'. Returns the asset URN."""
        r = self._check(self.s.post(f"{API}/{kind}?action=initializeUpload",
                                    data=json.dumps({"initializeUploadRequest": {"owner": self.author}})),
                        f"initialize {kind} upload")
        value = r.json()["value"]
        urn = value["image"] if kind == "images" else value["document"]
        put = requests.put(value["uploadUrl"], data=path.read_bytes(),
                           headers={"Authorization": self.s.headers["Authorization"],
                                    "Content-Type": "application/octet-stream"})
        self._check(put, f"upload {path.name}")
        return urn

    def create_post(self, commentary: str, content: dict | None) -> str:
        payload = {
            "author": self.author,
            "commentary": commentary,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        if content:
            payload["content"] = content
        r = self._check(self.s.post(f"{API}/posts", data=json.dumps(payload)), "create post")
        return r.headers.get("x-restli-id", "")


def build_content(folder: pathlib.Path, meta: dict, li: LinkedIn | None) -> tuple[dict | None, str]:
    fmt = meta["format"]
    if fmt == "text":
        return None, "text only"
    if fmt == "image":
        asset = folder / "diagram.png"
        kind = "images"
    else:
        asset = folder / "carousel.pdf"
        kind = "documents"
    if not asset.exists():
        raise RuntimeError(f"{folder.name}: {asset.name} is missing. The render step should have created it in the PR.")
    if li is None:
        return {"media": {"id": f"<{kind} urn>"}}, f"would upload {asset.name} ({asset.stat().st_size} bytes)"
    urn = li.upload(kind, asset)
    media = {"id": urn}
    if fmt == "image":
        media["altText"] = meta.get("alt_text", "")[:4086]
    else:
        media["title"] = meta.get("document_title") or meta["id"]
    return {"media": media}, f"uploaded {asset.name} as {urn}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--post", help="only consider this post id")
    ap.add_argument("--now", help="pretend the current Central time is this (testing)")
    args = ap.parse_args()

    now = (dt.datetime.strptime(args.now, "%Y-%m-%d %H:%M").replace(tzinfo=CT) if args.now else now_ct())
    li = None
    if not args.dry_run:
        token, author = os.environ.get("LINKEDIN_ACCESS_TOKEN"), os.environ.get("LINKEDIN_PERSON_URN")
        if not token or not author:
            print("LINKEDIN_ACCESS_TOKEN and LINKEDIN_PERSON_URN must be set.", file=sys.stderr)
            return 2
        li = LinkedIn(token, author, os.environ.get("LINKEDIN_VERSION") or "202608")

    published_today = {
        str(load_post(p)[0].get("published_at", ""))[:10] for p in post_files()
        if load_post(p)[0].get("status") == "published"
    }
    report, failures = [], 0
    for post_md in post_files():
        meta, body = load_post(post_md)
        if meta.get("status") != "scheduled" or (args.post and meta.get("id") != args.post):
            continue
        when = publish_time(meta)
        if when > now:
            continue
        folder = post_md.parent
        if now - when > LATE_LIMIT:
            meta["status"] = "skipped"
            meta["skip_reason"] = f"not published by {(when + LATE_LIMIT).strftime('%Y-%m-%d %H:%M')} CT"
            if not args.dry_run:
                save_post(post_md, meta, body)
            report.append(f"- Skipped **{meta['id']}**: {meta['skip_reason']}.")
            continue
        if now.date().isoformat() in published_today:
            report.append(f"- Held **{meta['id']}**: a post already went out today (one post per day).")
            continue
        try:
            content, note = build_content(folder, meta, li)
            commentary = little_text(body)
            if args.dry_run:
                report.append(f"- Dry run **{meta['id']}**: {note}; {len(commentary)} characters.")
                print(json.dumps({"commentary": commentary, "content": content}, indent=2))
                continue
            urn = li.create_post(commentary, content)
            meta["status"] = "published"
            meta["linkedin_urn"] = urn
            meta["published_at"] = now_ct().strftime("%Y-%m-%d %H:%M")
            save_post(post_md, meta, body)
            published_today.add(now.date().isoformat())
            report.append(f"- Published **{meta['id']}** ({urn}). {note}.")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            report.append(f"- Failed **{meta['id']}**: {exc}")

    text = "\n".join(report) if report else "- Nothing due."
    print(text)
    REPORT.write_text(text + "\n")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
