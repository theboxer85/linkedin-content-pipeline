"""Create idea issues from .work/new_ideas.json (written by the triage agent).

Each entry: {"title", "body", "pillar", "source"}. Uses the gh CLI with GH_TOKEN from the workflow.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

PILLARS = {"financial", "adoption", "continuity"}


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".work/new_ideas.json")
    if not path.exists():
        print("no ideas file")
        return 0
    ideas = json.loads(path.read_text() or "[]")[:3]
    for idea in ideas:
        labels = ["idea", "news" if idea.get("source") == "news" else "reddit"]
        if idea.get("pillar") in PILLARS:
            labels.append(f"pillar:{idea['pillar']}")
        title = idea["title"] if idea["title"].lower().startswith("idea:") else f"Idea: {idea['title']}"
        subprocess.run(["gh", "issue", "create", "--title", title[:120], "--body", idea["body"],
                        "--label", ",".join(labels)], check=True)
        print(f"created: {title}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
