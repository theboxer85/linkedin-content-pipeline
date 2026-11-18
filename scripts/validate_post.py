"""Check posts against the playbook rules.

Usage: python scripts/validate_post.py [post folders or post.md files ...]
With no arguments, checks every scheduled post. Errors fail the run; warnings are for the human reviewer.
Writes a markdown report to $GITHUB_STEP_SUMMARY when it exists, and to --report if given.
"""
from __future__ import annotations

import argparse
import ipaddress
import os
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

from common import DATA, DAYS, FORMATS, PILLARS, REQUIRED, STATUSES, load_post, post_files, publish_time, word_count

BANNED = [
    r"sits between", r"\bdelve", r"\blandscape\b", r"\bunlock", r"game[- ]changer", r"navigate the complexit",
    r"fast-paced world", r"in today's", r"let's dive in", r"here's the thing", r"the bottom line\?",
]
NOT_X_ITS_Y = re.compile(r"\b(it's|it is|this is) not (just )?[^.?!]{1,40}[,;] (it's|it is)\b", re.I)
HASHTAG = re.compile(r"(?<![\w&])#[A-Za-z]\w*")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")
IP = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
PLACEHOLDER = re.compile(r"\[\[NEEDS:[^\]]*\]\]")


def allowed_ranges() -> list[ipaddress._BaseNetwork]:
    nets = []
    for line in (DATA / "allowed_ranges.txt").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            nets.append(ipaddress.ip_network(line, strict=False))
    return nets


def check_ips(text: str, where: str, errors: list, warnings: list) -> None:
    allow = allowed_ranges()
    for raw in set(IP.findall(text)):
        try:
            net = ipaddress.ip_network(raw, strict=False)
        except ValueError:
            continue
        if any(net.subnet_of(a) if net.version == a.version else False for a in allow):
            continue
        if net.is_private:
            warnings.append(f"{where}: private range `{raw}`. Confirm it is generic, not the client's real range.")
        else:
            errors.append(f"{where}: public address `{raw}` is not in data/allowed_ranges.txt. Remove it or add it if it is a documented provider range.")


def check_denylist(text: str, where: str, errors: list) -> None:
    raw = os.environ.get("SANITIZE_DENYLIST", "")
    for term in [t.strip() for t in raw.split(",") if t.strip()]:
        if re.search(re.escape(term), text, re.I):
            errors.append(f"{where}: contains a term from the private SANITIZE_DENYLIST secret.")


def check_diagram(folder: pathlib.Path, meta: dict, errors: list, warnings: list) -> None:
    if meta.get("format") == "text":
        return
    path = folder / "diagram.drawio"
    if not path.exists():
        errors.append(f"{folder.name}: format is `{meta.get('format')}` but diagram.drawio is missing.")
        return
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        errors.append(f"{folder.name}: diagram.drawio is not valid XML ({exc}).")
        return
    pages = tree.findall("./diagram")
    if not pages or tree.find(".//mxGraphModel") is None:
        errors.append(f"{folder.name}: diagram.drawio must be uncompressed (mxGraphModel inside each diagram).")
    if meta.get("format") == "document" and not 4 <= len(pages) <= 6:
        warnings.append(f"{folder.name}: carousel has {len(pages)} pages; the playbook asks for 4 to 6.")
    labels = " ".join(c.get("value", "") for c in tree.iter("mxCell"))
    check_ips(labels, f"{folder.name}/diagram", errors, warnings)
    check_denylist(labels, f"{folder.name}/diagram", errors)
    for model in tree.iter("mxGraphModel"):
        if (model.get("pageWidth"), model.get("pageHeight")) != ("1080", "1350"):
            warnings.append(f"{folder.name}: diagram page is not 1080 x 1350.")
            break


def validate(post_md: pathlib.Path) -> tuple[list, list]:
    errors, warnings = [], []
    folder = post_md.parent
    try:
        meta, body = load_post(post_md)
    except Exception as exc:  # noqa: BLE001
        return [str(exc)], []

    for key in REQUIRED:
        if meta.get(key) in (None, ""):
            errors.append(f"{folder.name}: missing front matter field `{key}`.")
    if meta.get("id") and meta["id"] != folder.name:
        errors.append(f"{folder.name}: `id` must equal the folder name.")
    if meta.get("pillar") not in PILLARS:
        errors.append(f"{folder.name}: pillar must be one of {sorted(PILLARS)}.")
    if meta.get("day") not in DAYS:
        errors.append(f"{folder.name}: day must be one of {sorted(DAYS)}.")
    if meta.get("format") not in FORMATS:
        errors.append(f"{folder.name}: format must be one of {sorted(FORMATS)}.")
    if meta.get("status") not in STATUSES:
        errors.append(f"{folder.name}: status must be one of {sorted(STATUSES)}.")
    if meta.get("format") == "document" and not meta.get("document_title"):
        errors.append(f"{folder.name}: document posts need `document_title`.")
    try:
        when = publish_time(meta)
        weekday = when.strftime("%A").lower()
        if meta.get("day") in ("monday", "thursday") and weekday != meta["day"]:
            errors.append(f"{folder.name}: publish_at falls on a {weekday}, but day is {meta['day']}.")
        if not folder.name.startswith(when.strftime("%Y-%m-%d")):
            errors.append(f"{folder.name}: folder date must match publish_at.")
    except Exception:  # noqa: BLE001
        errors.append(f"{folder.name}: publish_at must look like \"2026-12-07 07:45\".")

    if PLACEHOLDER.search(body):
        errors.append(f"{folder.name}: unresolved [[NEEDS: ...]] placeholders. Fill them in before merging.")
    if HASHTAG.search(body):
        errors.append(f"{folder.name}: hashtags are not used.")
    if EMOJI.search(body):
        errors.append(f"{folder.name}: emojis are not used.")
    lower = body.lower()
    for pattern in BANNED:
        if re.search(pattern, lower):
            errors.append(f"{folder.name}: banned phrase matching `{pattern}`.")
    if NOT_X_ITS_Y.search(body):
        warnings.append(f"{folder.name}: looks like an \"it's not X, it's Y\" construction.")
    words = word_count(body)
    if words > 250:
        errors.append(f"{folder.name}: {words} words. The limit is 200 (hard stop at 250).")
    elif not 80 <= words <= 200:
        warnings.append(f"{folder.name}: {words} words. Target is 100 to 200 (80 is fine when the story is short).")
    if body.count("—") > 1:
        warnings.append(f"{folder.name}: {body.count(chr(0x2014))} em dashes. Use periods or commas instead.")
    first_sentence = re.split(r"(?<=[.?!])\s", body.strip(), maxsplit=1)[0]
    if first_sentence.endswith("?"):
        warnings.append(f"{folder.name}: opens with a question. The hook should state the consequence.")
    if len(body.split("\n")[0]) > 210:
        warnings.append(f"{folder.name}: first line is long. LinkedIn shows about three lines before \"see more\".")

    check_ips(body, folder.name, errors, warnings)
    check_denylist(body + " " + str(meta.get("alt_text", "")), folder.name, errors)
    check_diagram(folder, meta, errors, warnings)
    return errors, warnings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--report")
    args = ap.parse_args()

    targets = []
    for p in args.paths:
        path = pathlib.Path(p)
        targets.append(path / "post.md" if path.is_dir() else path)
    if not targets:
        targets = [p for p in post_files() if load_post(p)[0].get("status") == "scheduled"]

    lines, failed = ["## Post checks", ""], False
    for post_md in targets:
        if not post_md.exists():
            continue
        errors, warnings = validate(post_md)
        failed |= bool(errors)
        status = "fails" if errors else ("passes with notes" if warnings else "passes")
        lines.append(f"**{post_md.parent.name}** {status}")
        lines += [f"- Error: {e}" for e in errors] + [f"- Check: {w}" for w in warnings]
        lines.append("")
    report = "\n".join(lines)
    print(report)
    for out in filter(None, [args.report, os.environ.get("GITHUB_STEP_SUMMARY")]):
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(report + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
